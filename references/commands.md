# Maestro Command Reference

Complete reference for Maestro YAML commands.

## Interaction Commands

### tapOn
Tap on a UI element.

```yaml
# Simple text tap
- tapOn: "Button"

# With ID
- tapOn:
    id: "button_id"

# With options
- tapOn:
    text: "Submit"
    repeat: 2
    delay: 500
    retryTapIfNoChange: true
    waitToSettleTimeoutMs: 1000

# Relative position
- tapOn:
    text: "Button"
    below: "Header"
    above: "Footer"
```

### longPressOn
Long press on a UI element.

```yaml
- longPressOn: "Item"
```

### pressBack
Press the back button.

```yaml
- pressBack
```

### pressKey
Press a specific key.

```yaml
- pressKey: Enter
- pressKey: Backspace
```

## Input Commands

### inputText
Input text (works regardless of focus).

```yaml
- inputText: "Hello World"
```

### inputRandomText
Input random text of specified length.

```yaml
- inputRandomText:
    length: 10
```

### inputRandomEmail
Input a random email address.

```yaml
- inputRandomEmail
```

### inputRandomPersonName
Input a random person name.

```yaml
- inputRandomPersonName
```

### inputRandomNumber
Input a random number.

```yaml
- inputRandomNumber:
    from: 1
    to: 100
```

## Swipe Commands

### swipe
Perform a swipe gesture.

```yaml
# Directional swipe
- swipe:
    direction: DOWN
    duration: 1000

# Swipe from element
- swipe:
    from:
      id: "scrollable_list"
    direction: DOWN
```

### scroll
Scroll until element is visible.

```yaml
- scrollUntil:
    visible: "Target Element"
```

## Assertion Commands

### assertVisible
Assert element is visible.

```yaml
# Simple
- assertVisible: "Text"

# With properties
- assertVisible:
    text: "Button"
    enabled: true
    checked: false
    focused: true
    selected: false
```

### assertNotVisible
Assert element is NOT visible.

```yaml
- assertNotVisible: "Error Message"
```

### assertTrue
Assert condition is true.

```yaml
- assertTrue:
    condition: "${maestro.copiedText} == 'Expected'"
```

## Wait Commands

### waitForAnimationToEnd
Wait for animations to complete.

```yaml
- waitForAnimationToEnd:
    timeout: 5000
```

### extendedWaitUntil
Wait with timeout for condition.

```yaml
- extendedWaitUntil:
    visible: "Element"
    timeout: 10000
```

## Text Operations

### copyTextFrom
Copy text from element to variable.

```yaml
- copyTextFrom:
    id: "price_label"
```

### pasteText
Paste copied text.

```yaml
- pasteText
```

## App Control

### launchApp
Launch the app.

```yaml
- launchApp
```

### killApp
Kill the app.

```yaml
- killApp
```

### clearState
Clear app state.

```yaml
- clearState
```

### runFlow
Run another flow file.

```yaml
- runFlow: ../common/login.yaml
```

## Environment & Variables

### Define environment variables

```yaml
appId: com.example.app
env:
  USERNAME: testuser
  PASSWORD: testpass123
---
- inputText: ${USERNAME}
```

### Use copied text

```yaml
- copyTextFrom:
    id: "generated_code"
- assertVisible: ${maestro.copiedText}
```

## Selectors Reference

### Text Selector
Match by visible text (supports regex).

```yaml
- tapOn: "Button"
- tapOn: ".*Submit.*"
```

### ID Selector
Match by semantic identifier.

```yaml
- tapOn:
    id: "login_button"
```

### Relative Position

```yaml
- tapOn:
    text: "Button"
    below: "Header"
    above: "Footer"
    leftOf: "Right Element"
    rightOf: "Left Element"
```

### Child/Parent Relationships

```yaml
- tapOn:
    text: "Button"
    childOf:
      id: "parent_container"
```

### Element State

```yaml
- tapOn:
    text: "Button"
    enabled: true
    checked: false
```

### Traits

```yaml
- tapOn:
    traits: text
- tapOn:
    traits: square
```
