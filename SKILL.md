---
name: maestro-scenario-gen
description: |
  Generate Maestro E2E test scenarios from Flutter code with self-healing capabilities.

  Use this skill when the user wants to:
  - Generate Maestro YAML test flows from existing Flutter/Dart code
  - Create E2E tests for mobile apps using Maestro
  - Fix failing Maestro tests by adjusting code or scenarios
  - Add semantic identifiers to Flutter widgets for testing
  - Debug why Maestro cannot find elements
  - Self-heal broken test scenarios
  - Analyze Flutter widgets for Maestro testability issues
  - Run Maestro tests against Flutter apps

  The skill prioritizes text-based selectors over coordinates and helps wrap widgets
  with Semantics when needed for reliable element identification.

  Includes helper scripts:
  - scripts/analyze_widgets.py: Detect widgets needing semantic identifiers
  - scripts/generate_scenario.py: Generate YAML scenarios from templates

  Supports flow types: login, signup, game, resource, navigation, form, list, undo-redo, dialog
---

# Maestro Scenario Generator

A skill for generating Maestro E2E test scenarios from Flutter code with self-healing capabilities. This skill ensures reliable, maintainable tests by preferring text-based selectors and semantic identifiers over fragile coordinate-based interactions.

## Core Principles

### The Golden Rule: Never Use Point Coordinates

Point coordinates (`point: 50%, 50%` or `point: 100, 200`) are fragile and break when:
- Screen sizes change
- Layouts are modified
- Fonts render differently
- Apps are localized

**Always prefer text or semantic identifier selectors.**

## Selector Priority Hierarchy

When generating Maestro scenarios, follow this priority order:

1. **Text selector** - Use when element has visible, stable text
   ```yaml
   - tapOn: "Submit"
   - assertVisible: "Welcome Back"
   ```

2. **Semantic identifier** - Use when element lacks visible text but needs interaction
   ```yaml
   - tapOn:
       id: "login_button"
   ```

3. **Relative positioning** - Use when text/ID alone isn't unique
   ```yaml
   - tapOn:
       text: "Button"
       below: "Section Header"
   ```

4. **Traits** - Use for generic element types
   ```yaml
   - tapOn:
       traits: text
   ```

**NEVER resort to point coordinates.** If an element cannot be identified, fix the code.

## When Code Needs Modification

### Scenario A: Element has no text and needs interaction

Wrap the widget with `Semantics` and add an `identifier`:

```dart
// Before: Icon button with no text
IconButton(
  onPressed: _handleSubmit,
  icon: const Icon(Icons.send),
)

// After: Add semantic identifier
Semantics(
  identifier: 'send_button',
  child: IconButton(
    onPressed: _handleSubmit,
    icon: const Icon(Icons.send),
  ),
)
```

Then in Maestro:
```yaml
- tapOn:
    id: "send_button"
```

### Scenario B: Element has text but Maestro cannot detect it

This typically happens with custom widgets that don't expose text accessibly. Wrap with `Semantics(container: true)`:

```dart
// Before: Custom widget with text that isn't detectable
CustomCard(
  title: "Premium Plan",
  subtitle: "\$9.99/month",
)

// After: Make text accessible
Semantics(
  container: true,
  child: CustomCard(
    title: "Premium Plan",
    subtitle: "\$9.99/month",
  ),
)
```

Now Maestro can find:
```yaml
- assertVisible: "Premium Plan"
- assertVisible: ".*\\\$9\\.99.*"
```

### Scenario C: Multiple elements with same text

Use relative positioning or identifiers:

```dart
// Multiple "Delete" buttons - add unique identifiers
Semantics(
  identifier: 'delete_item_1',
  child: TextButton(child: Text("Delete")),
),
Semantics(
  identifier: 'delete_item_2',
  child: TextButton(child: Text("Delete")),
),
```

Or use relative positioning:
```yaml
- tapOn:
    text: "Delete"
    below: "Item 1"
```

## Self-Healing Workflow

When a Maestro test fails, follow this diagnostic process:

### Step 1: Identify the Failure Type

| Error Message | Likely Cause | Fix |
|---------------|--------------|-----|
| "No element found with text 'X'" | Text not visible/accessibly exposed | Add `Semantics(container: true)` |
| "No element found with id 'X'" | Identifier not set | Add `Semantics(identifier: 'X')` |
| "Multiple elements match" | Selector not unique | Add relative positioning or more specific selector |
| "Timeout waiting for element" | Element not visible/animated | Add `waitForAnimationToEnd` |

### Step 2: Analyze the Widget

Check the Flutter widget for:
1. Does it have visible text? → Use text selector
2. Is it an icon/image button? → Add semantic identifier
3. Is it a custom composite widget? → Add `Semantics(container: true)`
4. Does it animate? → Add wait commands

### Step 3: Apply Fix

Choose the minimal fix:
1. **Scenario fix** - Adjust YAML to use correct selector
2. **Code fix** - Add Semantics wrapper
3. **Both** - Sometimes both need adjustment

## Maestro Command Reference

### Navigation & Interaction

```yaml
# Launch app
- launchApp

# Tap by text
- tapOn: "Button Text"

# Tap by ID
- tapOn:
    id: "button_id"

# Tap with relative positioning
- tapOn:
    text: "Submit"
    below: "Email Field"

# Input text
- inputText: "Hello World"

# Tap then input
- tapOn:
    id: "email_field"
- inputText: "user@example.com"

# Random data input
- inputRandomEmail
- inputRandomPersonName
- inputRandomNumber
```

### Assertions

```yaml
# Assert visible
- assertVisible: "Welcome"

# Assert with regex
- assertVisible: ".*\\\$[0-9]+\\.[0-9]{2}.*"

# Assert not visible
- assertNotVisible: "Error Message"

# Assert element state
- assertVisible:
    text: "Submit"
    enabled: true
```

### Waiting

```yaml
# Wait for animations
- waitForAnimationToEnd:
    timeout: 5000

# Wait for specific text
- extendedWaitUntil:
    visible: "Loaded Content"
    timeout: 10000
```

### Swiping & Scrolling

```yaml
# Swipe up (scroll down)
- swipe:
    direction: UP

# Swipe with element
- swipe:
    from:
      id: "scrollable_list"
    direction: DOWN
```

## Scenario Generation Process

When asked to generate a Maestro scenario from code:

### 1. Analyze the User Flow
- Identify the starting screen
- Map each user action (tap, input, swipe)
- Identify expected outcomes (assertions)

### 2. For Each Interactive Element
- Check if it has visible text → use text selector
- Check if it's an icon/image → ensure semantic identifier exists
- Check if it's custom → ensure `Semantics(container: true)`

### 3. Generate the YAML
- Start with `appId` and `---`
- Add `launchApp` if needed
- Add interaction steps
- Add assertions for verification
- Add waits for animations

### 4. Review for Fragility
- No point coordinates? ✓
- No hardcoded timeouts? ✓
- Selectors are unique? ✓
- Animations handled? ✓

## Example: Login Flow

Given Flutter code for a login screen:

```dart
class LoginScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          Text('Welcome Back', style: headlineLarge),
          TextField(
            decoration: InputDecoration(hintText: 'Email'),
            // Should add: key or semantic identifier
          ),
          TextField(
            decoration: InputDecoration(hintText: 'Password'),
            obscureText: true,
          ),
          ElevatedButton(
            onPressed: _login,
            child: Text('Sign In'),
          ),
          TextButton(
            onPressed: _forgotPassword,
            child: Text('Forgot Password?'),
          ),
        ],
      ),
    );
  }
}
```

Generated Maestro scenario:

```yaml
appId: com.example.app
---
- launchApp
- assertVisible: "Welcome Back"
- tapOn:
    text: ".*Email.*"
- inputText: "test@example.com"
- tapOn:
    text: ".*Password.*"
- inputText: "securepassword123"
- tapOn: "Sign In"
- waitForAnimationToEnd:
    timeout: 3000
- assertVisible: "Dashboard"
```

If the text fields don't have detectable text, the code fix would be:

```dart
Semantics(
  identifier: 'email_field',
  container: true,
  child: TextField(
    decoration: InputDecoration(hintText: 'Email'),
  ),
),
```

## Common Patterns

### List Item Interaction
```yaml
- tapOn:
    text: "Delete"
    below: "Item Name"
```

### Form Submission
```yaml
- tapOn:
    id: "submit_button"
- waitForAnimationToEnd:
    timeout: 2000
- assertNotVisible:
    id: "loading_spinner"
- assertVisible: "Success"
```

### Navigation
```yaml
- tapOn:
    id: "menu_button"
- assertVisible: "Settings"
- tapOn: "Settings"
```

## Files to Check

When debugging test failures:
1. `maestro/` - Test scenario YAML files
2. `lib/` - Flutter widget code
3. Check for `Semantics` widgets around interactive elements
4. Verify `identifier` values match what's in YAML

## Tips for Reliable Tests

1. **Use regex for dynamic text** - `.*` for partial matches
2. **Handle loading states** - Wait for spinners to disappear
3. **Test the happy path first** - Add error cases later
4. **Keep scenarios focused** - One user flow per file
5. **Name identifiers descriptively** - `submit_order_button` not `btn1`

## Helper Scripts

### analyze_widgets.py

Analyzes Flutter code to find widgets that may need semantic identifiers:

```bash
python scripts/analyze_widgets.py lib/

# Options:
# --json    Output as JSON for further processing
# --quiet   Only show issues, no summary
```

The script:
- Detects widgets without semantic identifiers
- Recognizes custom wrapper methods to avoid false positives
- Suggests fixes for each issue found

### generate_scenario.py

Generates Maestro YAML scenarios from templates:

```bash
# List available flow types
python scripts/generate_scenario.py --list

# Generate a specific flow
python scripts/generate_scenario.py com.example.app login
python scripts/generate_scenario.py com.example.app game
python scripts/generate_scenario.py com.example.app undo-redo

# Generate from analysis output
python scripts/generate_scenario.py com.example.app --from-analysis analysis.json
```

Available flow types:
- `login` - Standard login flow
- `signup` - Standard signup/registration flow
- `game` - Game smoke test (verify UI loads)
- `resource` - Resource management test (increment/decrement)
- `undo-redo` - Undo/redo functionality test
- `navigation` - Navigation between screens
- `form` - Form input and submission
- `list` - List scrolling and item interaction
- `dialog` - Dialog display and interaction

## Running Maestro Tests

```bash
# Run a single test
maestro test -e APP_ID=com.example.app scenario.yaml

# Run all tests in a directory
maestro test -e APP_ID=com.example.app maestro/

# Run with specific device
maestro test -e APP_ID=com.example.app --udid emulator-5554 scenario.yaml
```

## Evaluating Test Quality

A good Maestro test suite should:
1. Have no point coordinates (all text or ID based)
2. Use semantic identifiers for icon-only buttons
3. Wait for animations before assertions
4. Test one user flow per file
5. Have clear, descriptive identifiers

Use `maestro hierarchy` to verify elements are detectable.
