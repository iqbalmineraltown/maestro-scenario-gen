# Maestro Widget Analyzer

A Claude Code skill for analyzing Flutter widgets and ensuring they have proper semantic identifiers for Maestro E2E testing.

## Features

- **Widget Analysis**: Detects Flutter widgets that need semantic identifiers for Maestro testing
- **Self-Healing Guidance**: Diagnostic help for fixing failing tests
- **Context-Aware**: Recognizes custom wrapper patterns to avoid false positives

## Installation

### Using OpenSkills (Recommended)

```bash
npx openskills install iqbalmineraltown/maestro-scenario-gen
```

### Manual Install

```bash
# Clone the repository
git clone https://github.com/iqbalmineraltown/maestro-scenario-gen.git
cp -r maestro-scenario-gen/* ~/.claude/skills/maestro-scenario-gen/
```

## Usage

### Analyze Widgets

```bash
python ~/.claude/skills/maestro-scenario-gen/scripts/analyze_widgets.py path/to/flutter/lib/

# Options:
# --json    Output as JSON for further processing
# --quiet   Only show issues, no summary
```

## Selector Priority

1. **Text selector** - Use when element has visible, stable text
2. **Semantic identifier** - Use when element lacks visible text
3. **Relative positioning** - Use when text/ID alone isn't unique
4. **Traits** - Use for generic element types

**Never use point coordinates** - they're fragile and break with layout changes.

## Project Structure

```
maestro-scenario-gen/
├── SKILL.md              # Main skill documentation
├── README.md             # This file
├── scripts/
│   └── analyze_widgets.py    # Widget analysis script
└── references/
    ├── commands.md           # Maestro command reference
    └── flutter-semantics.md  # Flutter Semantics guide
```

## License

MIT
