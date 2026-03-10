---
name: maestro-scenario-gen
description: |
  Generate Maestro E2E test scenarios from Flutter code with self-healing capabilities.

  Use this skill when the user wants to:
  - Generate Maestro YAML test flows and scenarios from existing Flutter/Dart code
  - Create E2E tests for mobile apps using Maestro
  - Organize tests into flows (reusable sequences) and scenarios (AAA user stories)
  - Fix failing Maestro tests by adjusting code or scenarios
  - Add semantic identifiers to Flutter widgets for testing
  - Debug why Maestro cannot find elements
  - Self-heal broken test scenarios
  - Analyze Flutter widgets for Maestro testability issues
  - Run Maestro tests against Flutter apps

  The skill prioritizes text-based selectors over coordinates and helps wrap widgets
  with Semantics when needed for reliable element identification.
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

## Test Organization: Flows vs Scenarios

Maestro tests are organized into two types: **flows** (reusable sequences) and **scenarios** (full user stories with assertions).

### Folder Structure

Mirror the app's feature structure:

```
maestro/
├── auth/
│   ├── flows/
│   │   ├── login.yaml
│   │   └── logout.yaml
│   └── scenarios/
│       ├── login-success.yaml
│       └── invalid-email-error.yaml
├── cart/
│   ├── flows/
│   │   ├── add-item.yaml
│   │   └── remove-item.yaml
│   └── scenarios/
│       ├── checkout-guest.yaml
│       └── checkout-with-discount.yaml
├── profile/
│   ├── flows/
│   │   └── navigate-to-profile.yaml
│   └── scenarios/
│       └── update-avatar.yaml
└── shared/
    └── flows/
        ├── launch-app.yaml
        └── accept-permissions.yaml
```

### Flows (Reusable Sequences)

Flows are **reusable action sequences** with **no assertions**. They set up state or perform common actions.

**When to create a flow:**
- Login/logout sequences
- Navigation to a screen
- Adding items to cart
- Form filling
- Accepting permissions

**Flow template:**
```yaml
appId: com.example.app
name: Login
# Standard login flow with valid credentials
tags:
  - auth
  - smoke
---
- tapOn:
    id: "email_field"
- inputText: "user@example.com"
- tapOn:
    id: "password_field"
- inputText: "password123"
- tapOn: "Sign In"
- waitForAnimationToEnd:
    timeout: 2000
```

**Rules for flows:**
1. No `assertVisible` or `assertNotVisible`
2. End with `waitForAnimationToEnd` if state change occurs
3. Keep focused on one action sequence
4. Can be composed into other flows or scenarios

### Scenarios (Full User Stories)

Scenarios are **complete test cases** with **Arrange-Act-Assert** structure and **at least one assertion**.

**When to create a scenario:**
- Testing a user story
- Validating error handling
- Edge case testing
- Happy path + assertions

**Scenario template (explicit AAA):**
```yaml
appId: com.example.app
name: Guest checkout with items
# As a guest, I want to checkout so I can purchase without an account
tags:
  - cart
  - checkout
properties:
  priority: high
---
# Arrange
- runFlow: ../flows/add-item.yaml

# Act
- tapOn: "Checkout"
- tapOn: "Continue as Guest"

# Assert
- assertVisible: "Shipping Address"
- assertVisible: "Payment Method"
- assertNotVisible: "Login Required"
```

**Rules for scenarios:**
1. Always have explicit `# Arrange`, `# Act`, `# Assert` comments
2. Must include at least one assertion
3. Use `runFlow` to include reusable flows
4. One scenario = one user story
5. Name file after the story: `guest-checkout.yaml`, `invalid-email-error.yaml`

### Header Fields Reference

Maestro supports these header fields (before `---`):

| Field | Required | Purpose | Example |
|-------|----------|---------|---------|
| `appId` | Yes* | Mobile app package ID | `com.example.app` |
| `url` | Yes* | Web app URL (alternative to appId) | `https://example.com` |
| `name` | No | Human-readable flow/scenario name | `Login flow` |
| `tags` | No | Tags for filtering and reports | `[auth, smoke]` |
| `properties` | No | Custom metadata for reports | `priority: high` |
| `env` | No | Environment variables | `USERNAME: test` |
| `onFlowStart` | No | Commands to run before flow | `- launchApp` |
| `onFlowComplete` | No | Commands to run after flow | `- killApp` |

*Either `appId` or `url` is required.

**Description convention:** Use a comment line directly under `name` for human-readable description.

### Arrange-Act-Assert Breakdown

| Section | Purpose | Typical Commands |
|---------|---------|------------------|
| **Arrange** | Set up preconditions | `launchApp`, `runFlow`, `inputText`, navigation |
| **Act** | Perform the action being tested | `tapOn`, `swipe`, `inputText` on target element |
| **Assert** | Verify expected outcome | `assertVisible`, `assertNotVisible`, `extendedWaitUntil` |

### Composing Flows into Scenarios

```yaml
appId: com.example.app
name: Update profile and verify changes
# User updates their display name and sees the change reflected
tags:
  - profile
  - settings
---
# Arrange
- runFlow: ../shared/flows/launch-app.yaml
- runFlow: ../flows/login.yaml
- runFlow: ../flows/navigate-to-profile.yaml

# Act
- tapOn:
    id: "edit_profile_button"
- tapOn:
    id: "display_name_field"
- inputText: "New Name"
- tapOn: "Save"

# Assert
- assertVisible: "Profile updated"
- assertVisible: "New Name"
```

### Generation Rules

When generating Maestro tests from code:

1. **Analyze feature folder** → Mirror structure in `maestro/<feature>/`
2. **Identify reusable sequences** → Extract to `flows/`
3. **Each scenario** → One user story with explicit AAA sections
4. **Flows end** → When state is ready, no assertions
5. **Scenarios end** → With assertions proving the story

### Quick Reference

| Type | Assertions | Reusable | Purpose |
|------|------------|----------|---------|
| Flow | ❌ No | ✅ Yes | Reusable action sequence |
| Scenario | ✅ Yes | ❌ No | Test a user story |

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

# Back navigation
- pressBack
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

# Conditional wait
- runFlow:
    when:
      visible: "Loading"
    commands:
      - waitForAnimationToEnd:
          timeout: 5000
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

When asked to generate a Maestro test from code:

### 1. Identify the Test Type
- **Is it reusable?** → Create a **flow** (login, navigation, form fill)
- **Does it verify behavior?** → Create a **scenario** with AAA structure

### 2. Analyze the Feature
- Find corresponding feature folder in codebase
- Mirror structure in `maestro/<feature>/flows/` or `maestro/<feature>/scenarios/`
- Check for existing flows that can be reused

### 3. For Each Interactive Element
- Check if it has visible text → use text selector
- Check if it's an icon/image → ensure semantic identifier exists
- Check if it's custom → ensure `Semantics(container: true)`

### 4. Generate the YAML

**For flows:**
```yaml
appId: com.example.app
name: [short name]
# [description as comment]
tags:
  - [feature]
---
- [actions only, no assertions]
- waitForAnimationToEnd  # if state changes
```

**For scenarios:**
```yaml
appId: com.example.app
name: [short name]
# [user story as comment]
tags:
  - [feature]
properties:
  priority: [low|medium|high]
---
# Arrange
- [setup steps, runFlow]

# Act
- [the action being tested]

# Assert
- [verify expected outcome]
```

### 5. Review for Quality
- No point coordinates? ✓
- Flows have no assertions? ✓
- Scenarios have explicit AAA? ✓
- Selectors are unique? ✓
- Animations handled? ✓

## Edge Case Testing

Edge cases are critical for robust E2E tests. Always consider these scenarios:

### Invalid Input Handling

Test how the app responds to invalid data:

```yaml
# Invalid email format
- tapOn:
    id: "email_field"
- inputText: "notanemail"
- tapOn: "Submit"
- assertVisible: "Invalid email"  # Error message should appear
- assertVisible: "Submit"         # Button still visible (form not submitted)

# Invalid password (too short)
- tapOn:
    id: "password_field"
- inputText: "123"
- tapOn: "Submit"
- assertVisible: "Password must be at least 8 characters"

# Special characters in input
- tapOn:
    id: "name_field"
- inputText: "<script>alert('xss')</script>"
- tapOn: "Submit"
- assertVisible: "Invalid characters"  # Or verify sanitization

# Empty required field
- tapOn:
    id: "email_field"
- inputText: ""
- tapOn: "Submit"
- assertVisible: "Email is required"
```

### Incomplete Form Handling

Test form validation with partially filled fields:

```yaml
# Submit empty form
- tapOn: "Submit"
- assertVisible: "Please fill all required fields"

# Partially filled form
- tapOn:
    id: "name_field"
- inputText: "John Doe"
- tapOn: "Submit"
- assertVisible: "Email is required"
- assertNotVisible: "Success"  # Ensure form wasn't submitted

# Field cleared after error
- tapOn:
    id: "email_field"
- inputText: "invalid"
- tapOn: "Submit"
- assertVisible: "Invalid email"
- tapOn:  # Tap field again
    id: "email_field"
- inputText: "valid@email.com"  # User corrects input
- tapOn: "Submit"
- assertVisible: "Success"
```

### Loading State Interactions

Test behavior during async operations:

```yaml
# Tap button during loading
- tapOn:
    id: "submit_button"
- assertVisible: "Loading..."  # Or loading spinner
# Try to tap again - should be disabled or ignored
- tapOn:
    id: "submit_button"
- waitForAnimationToEnd:
    timeout: 5000
- assertVisible: "Success"

# Navigate away during loading
- tapOn:
    id: "load_data_button"
- assertVisible: "Loading"
- pressBack  # User navigates away
- assertVisible: "Home Screen"  # Loading should be cancelled or handled

# Timeout handling
- tapOn:
    id: "slow_request_button"
- extendedWaitUntil:
    visible: "Result"
    timeout: 30000  # Long timeout for slow network
- assertNotVisible: "Error"  # Should succeed, not timeout
```

### Network/Async Error States

```yaml
# Network error
- tapOn:
    id: "fetch_data_button"
- extendedWaitUntil:
    visible: "Network Error"
    timeout: 10000
- assertVisible: "Retry"
- tapOn: "Retry"  # User can retry
- waitForAnimationToEnd:
    timeout: 5000
- assertVisible: "Data Loaded"

# Server error
- tapOn:
    id: "submit_form"
- extendedWaitUntil:
    visible: "Something went wrong"
    timeout: 10000
- assertVisible: "Try Again"
```

### Rapid/Repeated Interactions

```yaml
# Rapid button taps
- repeat:
    times: 5
    commands:
      - tapOn:
          id: "submit_button"
- assertVisible: "Success"  # Only one submission should occur

# Spam refresh
- repeat:
    times: 10
    commands:
      - tapOn:
          id: "refresh_button"
- assertVisible: "Content"  # App should handle gracefully
```

### Boundary Values

```yaml
# Minimum value (should not go negative)
- repeat:
    times: 5
    commands:
      - tapOn:
          id: "quantity_decrement"
- assertVisible:
    id: "quantity_value"  # Should be 0, not negative

# Maximum value / overflow
- repeat:
    times: 100
    commands:
      - tapOn:
          id: "quantity_increment"
- assertVisible:
    id: "quantity_value"  # Should cap at max, not overflow
```

### Empty States

```yaml
# Empty list
- tapOn:
    id: "orders_tab"
- assertVisible: "No orders yet"
- assertVisible: "Start Shopping"  # Call to action

# Empty search results
- tapOn:
    id: "search_field"
- inputText: "zzzzzzzzz"
- tapOn: "Search"
- assertVisible: "No results found"
- assertVisible: "Try different keywords"
```

### Session/State Edge Cases

```yaml
# Session expired during use
- launchApp
- # ... some actions
- killApp
- launchApp
- assertVisible: "Login"  # Session expired, redirect to login

# State persistence
- tapOn:
    id: "add_to_cart"
- killApp
- launchApp
- tapOn:
    id: "cart_icon"
- assertVisible: "1 item"  # Cart persisted

# Concurrent state changes
- tapOn:
    id: "item_1"
- tapOn: "Add to Cart"
- pressBack
- tapOn:
    id: "item_2"
- tapOn: "Add to Cart"
- tapOn:
    id: "cart_icon"
- assertVisible: "2 items"
```

### Dialog/Modal Edge Cases

```yaml
# Dismiss dialog with back button
- tapOn:
    id: "delete_button"
- assertVisible: "Delete Item?"
- pressBack
- assertNotVisible: "Delete Item?"
- assertVisible: "Item"  # Item still exists

# Dialog during loading
- tapOn:
    id: "submit_button"
- assertVisible: "Loading"
- pressBack  # Try to dismiss
- assertVisible: "Loading"  # Should still be visible (can't dismiss during load)
- waitForAnimationToEnd:
    timeout: 5000
- assertVisible: "Success"
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

### Dialog Interaction
```yaml
- tapOn:
    id: "delete_button"
- assertVisible: "Delete Item?"
- tapOn: "Cancel"
- assertNotVisible: "Delete Item?"
```

### Counter/Value Controls
```yaml
- tapOn:
    id: "quantity_increment"
- tapOn:
    id: "quantity_decrement"
- assertVisible:
    id: "quantity_display"
```

## Self-Healing Patterns

### Element Not Found After State Change
```yaml
- extendedWaitUntil:
    visible:
      id: "updated_content"
    timeout: 5000
```

### Conditional Execution
```yaml
- runFlow:
    when:
      visible: "Loading"
    commands:
      - waitForAnimationToEnd:
          timeout: 2000
```

### Retry for Flaky Elements
```yaml
- runFlow:
    when:
      visible: "Confirm"
    commands:
      - tapOn: "Confirm"
```

## Running Maestro Tests

```bash
# Run a single test
maestro test -e APP_ID=com.example.app scenario.yaml

# Run all tests in a directory
maestro test -e APP_ID=com.example.app maestro/

# Run with specific device
maestro test -e APP_ID=com.example.app --udid emulator-5554 scenario.yaml

# Debug element hierarchy
maestro hierarchy
```

## Debugging Tips

When debugging test failures:
1. Check `maestro/` - Test scenario YAML files
2. Check `lib/` - Flutter widget code
3. Use `maestro hierarchy` to verify elements are detectable
4. Verify `Semantics` widgets wrap interactive elements
5. Check that `identifier` values match between code and YAML

## Quality Checklist

A good Maestro test suite should:

### Structure
1. **Flows vs Scenarios** - Flows are reusable (no assertions), scenarios test stories (with assertions)
2. **Feature folders** - Mirror app structure in `maestro/<feature>/flows/` and `scenarios/`
3. **Explicit AAA** - Scenarios have Arrange, Act, Assert sections

### Selectors
4. No point coordinates (all text or ID based)
5. Use semantic identifiers for icon-only buttons
6. Clear, descriptive identifiers matching code

### Reliability
7. Wait for animations before assertions
8. One user story per scenario file
9. Cover edge cases - invalid input, incomplete forms, loading states
10. Handle error states gracefully - network errors, validation errors
