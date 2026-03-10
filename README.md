# Maestro Scenario Generator

A Claude Code skill for generating Maestro E2E test scenarios from Flutter code with self-healing capabilities.

## Features

- **Scenario Generation**: Generate Maestro YAML flows from Flutter/Dart code
- **Self-Healing Guidance**: Diagnostic help for fixing failing tests
- **Edge Case Testing**: Comprehensive patterns for invalid input, loading states, error handling
- **Best Practices**: Text-based selectors, semantic identifiers, never coordinates

## Installation

### Using OpenSkills (Recommended)

```bash
npx openskills install iqbalmineraltown/maestro-scenario-gen
```

### Manual Install

```bash
git clone https://github.com/iqbalmineraltown/maestro-scenario-gen.git
cp -r maestro-scenario-gen/* ~/.claude/skills/maestro-scenario-gen/
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
└── references/
    ├── commands.md       # Maestro command reference
    └── flutter-semantics.md  # Flutter Semantics guide
```

## License

MIT
