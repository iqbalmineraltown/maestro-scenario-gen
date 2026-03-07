# Maestro Scenario Generator

A Claude Code skill for generating Maestro E2E test scenarios from Flutter code with self-healing capabilities.

## Features

- **Widget Analysis**: Detects Flutter widgets that need semantic identifiers for Maestro testing
- **Scenario Generation**: Creates Maestro YAML test flows from templates
- **Self-Healing Guidance**: Diagnostic help for fixing failing tests
- **Multiple Flow Types**: login, signup, game, resource, navigation, form, list, undo-redo, dialog

## Installation

### Using OpenSkills (Recommended)

```bash
npx openskills install iqbalmineraltown/maestro-scenario-gen
```

That's it! The skill will be installed and ready to use in Claude Code.

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

### Generate Scenarios

```bash
# List available flow types
python ~/.claude/skills/maestro-scenario-gen/scripts/generate_scenario.py --list

# Generate a specific flow
python ~/.claude/skills/maestro-scenario-gen/scripts/generate_scenario.py com.example.app login
python ~/.claude/skills/maestro-scenario-gen/scripts/generate_scenario.py com.example.app game
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
│   ├── analyze_widgets.py    # Widget analysis script
│   └── generate_scenario.py  # Scenario generation script
└── references/
    ├── commands.md           # Maestro command reference
    └── flutter-semantics.md  # Flutter Semantics guide
```

## License

MIT
