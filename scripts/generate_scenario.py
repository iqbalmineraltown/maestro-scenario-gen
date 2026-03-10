#!/usr/bin/env python3
"""
Generate Maestro YAML scenarios from Flutter widget analysis.

This script generates Maestro test scenarios based on widget analysis output.
It does NOT use templates - scenarios are generated from actual code analysis.

Usage:
    python generate_scenario.py --list
    python generate_scenario.py com.example.app --from-analysis analysis.json
"""

import sys
import re
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class TestStep:
    action: str  # tapOn, assertVisible, inputText, etc.
    target: str  # text or id
    target_type: str  # 'text' or 'id'
    value: Optional[str] = None  # for inputText
    wait_after: Optional[int] = None  # milliseconds
    comment: Optional[str] = None


def _step_to_yaml(step: TestStep) -> str:
    """Convert a test step to YAML format."""
    if step.action == 'launchApp':
        return '- launchApp'

    if step.action == 'killApp':
        return '- killApp'

    if step.action == 'clearState':
        return '- clearState'

    if step.action == 'tapOn':
        if step.target_type == 'text':
            return f'- tapOn: "{step.target}"'
        else:
            return f'- tapOn:\n    id: "{step.target}"'

    if step.action == 'longPressOn':
        if step.target_type == 'text':
            return f'- longPressOn: "{step.target}"'
        else:
            return f'- longPressOn:\n    id: "{step.target}"'

    if step.action == 'inputText':
        return f'- inputText: "{step.value}"'

    if step.action == 'inputRandomEmail':
        return '- inputRandomEmail'

    if step.action == 'inputRandomPersonName':
        return '- inputRandomPersonName'

    if step.action == 'inputRandomNumber':
        if step.value:
            return f'- inputRandomNumber:\n    {step.value}'
        return '- inputRandomNumber'

    if step.action == 'tapAndInput':
        lines = []
        if step.target_type == 'text':
            lines.append(f'- tapOn: "{step.target}"')
        else:
            lines.append(f'- tapOn:\n    id: "{step.target}"')
        lines.append(f'- inputText: "{step.value}"')
        return '\n'.join(lines)

    if step.action == 'assertVisible':
        if step.target_type == 'text':
            return f'- assertVisible: "{step.target}"'
        else:
            return f'- assertVisible:\n    id: "{step.target}"'

    if step.action == 'assertNotVisible':
        if step.target_type == 'text':
            return f'- assertNotVisible: "{step.target}"'
        else:
            return f'- assertNotVisible:\n    id: "{step.target}"'

    if step.action == 'assertTrue':
        return f'- assertTrue:\n    condition: {step.target}'

    if step.action == 'waitForAnimationToEnd':
        timeout = step.wait_after or 5000
        return f'- waitForAnimationToEnd:\n    timeout: {timeout}'

    if step.action == 'extendedWaitUntil':
        timeout = step.wait_after or 10000
        if step.target_type == 'text':
            return f'- extendedWaitUntil:\n    visible: "{step.target}"\n    timeout: {timeout}'
        else:
            return f'- extendedWaitUntil:\n    visible:\n      id: "{step.target}"\n    timeout: {timeout}'

    if step.action == 'swipe':
        return f'- swipe:\n    direction: {step.target}'

    if step.action == 'scrollUntil':
        return f'- scrollUntil:\n    visible: "{step.target}"'

    if step.action == 'back':
        return '- pressBack'

    if step.action == 'pressKey':
        return f'- pressKey: {step.target}'

    if step.action == 'runFlow':
        return f'- runFlow: {step.target}'

    if step.action == 'copyTextFrom':
        return f'- copyTextFrom:\n    id: "{step.target}"'

    if step.action == 'pasteText':
        return '- pasteText'

    return f'# Unknown action: {step.action}'


def generate_from_analysis(app_id: str, analysis_file: str) -> str:
    """
    Generate a scenario based on widget analysis output.
    Reads JSON output from analyze_widgets.py and generates relevant tests.
    """
    try:
        with open(analysis_file, 'r') as f:
            analysis = json.load(f)
    except Exception as e:
        return f"# Error reading analysis file: {e}"

    lines = [
        f"appId: {app_id}",
        "---",
        "- launchApp",
        "- waitForAnimationToEnd:",
        "    timeout: 3000",
    ]

    # Track seen identifiers to avoid duplicates
    seen_widgets = set()
    
    for issue in analysis:
        if 'identifier' in issue.get('suggestion', ''):
            # Extract identifier from suggestion
            match = re.search(r"identifier:\s*'([^']+)'", issue['suggestion'])
            if match:
                identifier = match.group(1)
                if identifier not in seen_widgets:
                    seen_widgets.add(identifier)
                    widget_name = issue.get('widget', 'widget')
                    lines.append(f"# Verify {widget_name}")
                    lines.append(f"- assertVisible:")
                    lines.append(f"    id: \"{identifier}\"")

    return '\n'.join(lines)


def list_maestro_commands():
    """Print Maestro command reference."""
    print("""
Maestro Commands Reference
==========================

Actions:
  launchApp              Launch the app
  killApp                Kill the app
  clearState             Clear app state
  tapOn                  Tap on element (text or id)
  longPressOn            Long press on element
  inputText              Input text string
  inputRandomEmail       Input random email
  inputRandomPersonName  Input random name
  inputRandomNumber      Input random number
  swipe                  Swipe in direction (UP, DOWN, LEFT, RIGHT)
  scrollUntil            Scroll until element visible
  pressBack              Press back button
  pressKey               Press specific key

Assertions:
  assertVisible          Assert element is visible
  assertNotVisible       Assert element is not visible
  assertTrue             Assert condition is true

Waiting:
  waitForAnimationToEnd  Wait for animations to complete
  extendedWaitUntil      Wait until element is visible

Advanced:
  runFlow                Run a sub-flow
  copyTextFrom           Copy text from element
  pasteText              Paste text

See SKILL.md for usage patterns and examples.
""")


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_scenario.py <app_id> --from-analysis analysis.json")
        print("       python generate_scenario.py --list")
        sys.exit(1)

    # Check for list command
    if '--list' in sys.argv or '-l' in sys.argv:
        list_maestro_commands()
        return

    app_id = sys.argv[1]

    # Check for analysis file input
    if '--from-analysis' in sys.argv:
        idx = sys.argv.index('--from-analysis')
        if idx + 1 < len(sys.argv):
            analysis_file = sys.argv[idx + 1]
            print(generate_from_analysis(app_id, analysis_file))
            return

    print("Usage: python generate_scenario.py <app_id> --from-analysis analysis.json")
    print("       python generate_scenario.py --list")
    sys.exit(1)


if __name__ == '__main__':
    main()
