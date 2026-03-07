#!/usr/bin/env python3
"""
Analyze Flutter widgets and suggest Semantics improvements for Maestro testing.

This script scans Dart files to find widgets that may need semantic identifiers
for reliable Maestro testing. It tracks context across method calls and recognizes
custom wrapper patterns to avoid false positives.
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Set


@dataclass
class WidgetIssue:
    file: str
    line: int
    widget: str
    issue: str
    suggestion: str
    context: str  # Code snippet for context


# Widgets that typically need semantic identifiers (no visible text)
WIDGETS_NEEDING_SEMANTICS = [
    'IconButton',
    'FloatingActionButton',
    'GestureDetector',
    'InkWell',
    'InkResponse',
    'PopupMenuButton',
    'Checkbox',
    'Radio',
    'Switch',
    'Slider',
    'CircularProgressIndicator',
    'LinearProgressIndicator',
    'BackButton',
    'CloseButton',
    'DrawerButton',
]

# Patterns that indicate Semantics is already applied
SEMANTICS_INDICATORS = [
    r'Semantics\s*\(',
    r'identifier\s*:',
    r'semanticsLabel\s*:',
]

# Methods that commonly wrap widgets with Semantics
SEMANTICS_WRAPPER_METHODS = [
    r'_build\w+Button',
    r'_build\w+Widget',
    r'_build\w+Card',
    r'_build\w+Item',
]


@dataclass
class AnalysisContext:
    """Tracks analysis state across the file."""
    in_semantics: bool = False
    semantics_depth: int = 0
    in_method_with_semantics: bool = False
    current_method: Optional[str] = None
    methods_returning_semantics: Set[str] = None

    def __post_init__(self):
        if self.methods_returning_semantics is None:
            self.methods_returning_semantics = set()


def find_methods_that_return_semantics(content: str) -> Set[str]:
    """
    Pre-scan to find methods that return widgets wrapped in Semantics.
    This helps avoid false positives for custom wrapper methods.
    """
    methods = set()

    # Find method definitions that contain Semantics in their return
    method_pattern = r'(Widget\s+(_\w+)|_\w+\s*\([^)]*\)\s*(?:async\s*)?(?:\{|\=>))'
    matches = list(re.finditer(method_pattern, content))

    for match in matches:
        method_name = match.group(2) or match.group(0).split('(')[0].strip().split()[-1]
        if not method_name.startswith('_'):
            continue

        # Find the method body
        start = match.end()
        if '=>' in match.group(0):
            # Arrow function - find semicolon
            end_match = re.search(r';', content[start:])
            if end_match:
                method_body = content[start:start + end_match.start()]
            else:
                continue
        else:
            # Regular function - find matching brace
            brace_count = 1
            pos = start
            while pos < len(content) and brace_count > 0:
                if content[pos] == '{':
                    brace_count += 1
                elif content[pos] == '}':
                    brace_count -= 1
                pos += 1
            method_body = content[start:pos]

        # Check if method returns a Semantics widget
        if re.search(r'return\s+Semantics\s*\(', method_body) or \
           re.search(r'=>\s*Semantics\s*\(', method_body):
            methods.add(method_name)

    return methods


def find_widget_issues(content: str, filepath: str) -> List[WidgetIssue]:
    """Find widgets that may need semantic improvements."""
    issues = []
    lines = content.split('\n')

    # Pre-scan for methods that return Semantics
    methods_with_semantics = find_methods_that_return_semantics(content)

    context = AnalysisContext(methods_returning_semantics=methods_with_semantics.copy())

    # Track if we're inside a Semantics widget (proper brace tracking)
    brace_stack = []  # Stack of (char, line_num)

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Skip comments
        if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
            continue

        # Track method definitions
        method_match = re.search(r'Widget\s+(_\w+)', stripped)
        if method_match:
            context.current_method = method_match.group(1)
            if context.current_method in methods_with_semantics:
                context.in_method_with_semantics = True

        # Reset method context when leaving method (simplified)
        if stripped.startswith('}') and context.current_method:
            context.current_method = None
            context.in_method_with_semantics = False

        # Track brace depth for Semantics detection
        for char_idx, char in enumerate(line):
            if char in '({[':
                # Check if this is a Semantics opening
                before = line[:char_idx]
                if 'Semantics' in before or 'semantics' in before.lower():
                    brace_stack.append((char, i, True))
                else:
                    brace_stack.append((char, i, False))
            elif char in ')}]':
                if brace_stack:
                    brace_stack.pop()

        # Check if currently inside a Semantics widget
        in_semantics_scope = any(is_sem for _, _, is_sem in brace_stack)

        # Check if this line calls a method that returns Semantics
        calls_semantics_method = False
        for method in methods_with_semantics:
            if re.search(rf'{method}\s*\(', stripped):
                calls_semantics_method = True
                break

        # Skip if in Semantics scope or calling a semantics-returning method
        if in_semantics_scope or calls_semantics_method:
            continue

        # Check if line has explicit identifier
        if re.search(r'identifier\s*:', stripped):
            continue

        # Check for widgets needing semantics
        for widget in WIDGETS_NEEDING_SEMANTICS:
            # Match widget with opening paren or brace
            pattern = rf'{widget}\s*[\({{]'
            if re.search(pattern, stripped):
                # Additional check: look ahead for identifier in child tree
                # (check next few lines for identifier)
                look_ahead = '\n'.join(lines[i:i+5]) if i < len(lines) else ''
                if re.search(r'identifier\s*:', look_ahead):
                    continue

                # Skip if this is a child of a Semantics widget (look behind)
                look_behind = '\n'.join(lines[max(0, i-10):i])
                if re.search(r'Semantics\s*\(', look_behind):
                    # Check if the Semantics is still open
                    open_count = len(re.findall(r'[{\[(]', look_behind))
                    close_count = len(re.findall(r'[}\])]', look_behind))
                    if open_count > close_count:
                        continue

                # Get context for the issue
                context_start = max(0, i-2)
                context_end = min(len(lines), i+3)
                code_context = '\n'.join(
                    f"  {context_start + j + 1}: {lines[context_start + j]}"
                    for j in range(context_end - context_start)
                )

                issues.append(WidgetIssue(
                    file=filepath,
                    line=i,
                    widget=widget,
                    issue=f'{widget} without semantic identifier',
                    suggestion=f"Wrap with Semantics(identifier: 'descriptive_id', child: {widget}(...))",
                    context=code_context
                ))

    return issues


def analyze_flutter_widgets(content: str, filepath: str) -> List[WidgetIssue]:
    """
    Analyze Flutter widgets for Maestro testability issues.
    Returns list of issues found.
    """
    issues = []

    # Check for widgets without semantic identifiers
    issues.extend(find_widget_issues(content, filepath))

    # Check for text widgets without semanticsLabel (accessibility concern)
    text_pattern = r'Text\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
    for match in re.finditer(text_pattern, content):
        # Check if there's a semanticsLabel nearby
        line_num = content[:match.start()].count('\n') + 1
        line = content.split('\n')[line_num - 1]

        # Skip if this is inside a Semantics with label
        look_behind = content[max(0, match.start() - 200):match.start()]
        if 'Semantics(' in look_behind and ('label:' in look_behind or 'container:' in look_behind):
            continue

    return issues


def analyze_file(filepath: str) -> List[WidgetIssue]:
    """Analyze a single Dart file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return find_widget_issues(content, filepath)
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return []


def analyze_directory(directory: str) -> List[WidgetIssue]:
    """Recursively analyze all Dart files in a directory."""
    all_issues = []
    dir_path = Path(directory)

    if not dir_path.exists():
        print(f"Directory not found: {directory}", file=sys.stderr)
        return []

    for dart_file in dir_path.rglob('*.dart'):
        # Skip generated files
        if '.g.dart' in str(dart_file) or '.freezed.dart' in str(dart_file):
            continue
        issues = analyze_file(str(dart_file))
        all_issues.extend(issues)

    return all_issues


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_widgets.py <directory>")
        print("Analyzes Flutter widgets and suggests semantic improvements.")
        print("\nOptions:")
        print("  --json    Output results as JSON")
        print("  --quiet   Only show issues, no summary")
        sys.exit(1)

    directory = sys.argv[1]
    output_json = '--json' in sys.argv
    quiet = '--quiet' in sys.argv

    issues = analyze_directory(directory)

    if not issues:
        if not quiet:
            print("✅ No widget issues found. Your code looks good for Maestro testing!")
        return

    if output_json:
        import json
        print(json.dumps([{
            'file': i.file,
            'line': i.line,
            'widget': i.widget,
            'issue': i.issue,
            'suggestion': i.suggestion
        } for i in issues], indent=2))
    else:
        print(f"\n⚠️  Found {len(issues)} widget(s) that may need semantic improvements:\n")

        for issue in issues:
            print(f"📁 {issue.file}:{issue.line}")
            print(f"   Widget: {issue.widget}")
            print(f"   Issue: {issue.issue}")
            print(f"   💡 {issue.suggestion}")
            print(f"\n   Context:\n{issue.context}")
            print()


if __name__ == '__main__':
    main()
