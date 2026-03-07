#!/usr/bin/env python3
"""
Generate Maestro YAML scenarios from Flutter widget analysis.

This script helps generate initial Maestro test scenarios based on
widget analysis and user flow descriptions. Supports multiple flow types
including authentication, game, resource management, and custom flows.
"""

import sys
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class TestStep:
    action: str  # tapOn, assertVisible, inputText, etc.
    target: str  # text or id
    target_type: str  # 'text' or 'id'
    value: Optional[str] = None  # for inputText
    wait_after: Optional[int] = None  # milliseconds
    comment: Optional[str] = None  # optional comment for the step


@dataclass
class ScenarioConfig:
    app_id: str
    name: str
    description: str = ""
    env: Dict[str, str] = field(default_factory=dict)
    steps: List[TestStep] = field(default_factory=list)


def generate_scenario(config: ScenarioConfig) -> str:
    """Generate a Maestro YAML scenario from configuration."""
    yaml_lines = [f"appId: {config.app_id}"]

    if config.env:
        yaml_lines.append("env:")
        for key, value in config.env.items():
            yaml_lines.append(f"  {key}: {value}")

    yaml_lines.append("---")

    # Add comment header if description provided
    if config.description:
        yaml_lines.append(f"# {config.description}")
        yaml_lines.append("")

    for step in config.steps:
        if step.comment:
            yaml_lines.append(f"# {step.comment}")
        yaml_content = _step_to_yaml(step)
        yaml_lines.append(yaml_content)

    return '\n'.join(yaml_lines)


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


# =============================================================================
# FLOW TEMPLATES
# =============================================================================

def generate_login_flow(app_id: str) -> str:
    """Generate a standard login flow scenario."""
    config = ScenarioConfig(
        app_id=app_id,
        name="Login Flow",
        description="Standard login flow test",
        env={'EMAIL': 'test@example.com', 'PASSWORD': 'password123'},
        steps=[
            TestStep(action='launchApp', target='', target_type='text'),
            TestStep(action='assertVisible', target='Welcome', target_type='text', comment='Verify login screen'),
            TestStep(action='tapAndInput', target='email_field', target_type='id', value='${EMAIL}'),
            TestStep(action='tapAndInput', target='password_field', target_type='id', value='${PASSWORD}'),
            TestStep(action='tapOn', target='login_button', target_type='id'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=3000),
            TestStep(action='assertVisible', target='Dashboard', target_type='text', comment='Verify successful login'),
        ]
    )
    return generate_scenario(config)


def generate_signup_flow(app_id: str) -> str:
    """Generate a standard signup flow scenario."""
    config = ScenarioConfig(
        app_id=app_id,
        name="Signup Flow",
        description="Standard signup/registration flow test",
        env={'NAME': 'Test User', 'EMAIL': 'test@example.com', 'PASSWORD': 'password123'},
        steps=[
            TestStep(action='launchApp', target='', target_type='text'),
            TestStep(action='tapOn', target='Sign Up', target_type='text'),
            TestStep(action='tapAndInput', target='name_field', target_type='id', value='${NAME}'),
            TestStep(action='tapAndInput', target='email_field', target_type='id', value='${EMAIL}'),
            TestStep(action='tapAndInput', target='password_field', target_type='id', value='${PASSWORD}'),
            TestStep(action='tapOn', target='signup_button', target_type='id'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=3000),
            TestStep(action='assertVisible', target='Account Created', target_type='text'),
        ]
    )
    return generate_scenario(config)


def generate_game_smoke_test(app_id: str) -> str:
    """Generate a smoke test for game/board game apps."""
    config = ScenarioConfig(
        app_id=app_id,
        name="Game Smoke Test",
        description="Basic smoke test to verify game UI loads correctly",
        steps=[
            TestStep(action='launchApp', target='', target_type='text'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=3000),
            TestStep(action='assertVisible', target='game_board', target_type='id', comment='Verify game board'),
            TestStep(action='assertVisible', target='score_display', target_type='id', comment='Verify score display'),
            TestStep(action='assertVisible', target='start_button', target_type='id', comment='Verify start button'),
        ]
    )
    return generate_scenario(config)


def generate_resource_management_flow(app_id: str) -> str:
    """Generate a resource management test flow for games with resources."""
    config = ScenarioConfig(
        app_id=app_id,
        name="Resource Management Test",
        description="Test resource increment/decrement functionality",
        steps=[
            TestStep(action='launchApp', target='', target_type='text'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=3000),
            TestStep(action='tapOn', target='resource_inc_1', target_type='id', comment='Increment resource by 1'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='tapOn', target='resource_inc_5', target_type='id', comment='Increment resource by 5'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='tapOn', target='resource_dec_1', target_type='id', comment='Decrement resource by 1'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='assertVisible', target='resource_display', target_type='id', comment='Verify resource display'),
        ]
    )
    return generate_scenario(config)


def generate_navigation_flow(app_id: str) -> str:
    """Generate a navigation test flow."""
    config = ScenarioConfig(
        app_id=app_id,
        name="Navigation Test",
        description="Test navigation between screens",
        steps=[
            TestStep(action='launchApp', target='', target_type='text'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=2000),
            TestStep(action='tapOn', target='menu_button', target_type='id', comment='Open menu'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='assertVisible', target='Settings', target_type='text'),
            TestStep(action='tapOn', target='Settings', target_type='text'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=1000),
            TestStep(action='assertVisible', target='settings_screen', target_type='id'),
            TestStep(action='back', target='', target_type='text', comment='Go back'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
        ]
    )
    return generate_scenario(config)


def generate_form_submission_flow(app_id: str) -> str:
    """Generate a form submission test flow."""
    config = ScenarioConfig(
        app_id=app_id,
        name="Form Submission Test",
        description="Test form input and submission",
        env={'NAME': 'Test User', 'EMAIL': 'test@example.com'},
        steps=[
            TestStep(action='launchApp', target='', target_type='text'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=2000),
            TestStep(action='tapAndInput', target='name_field', target_type='id', value='${NAME}'),
            TestStep(action='tapAndInput', target='email_field', target_type='id', value='${EMAIL}'),
            TestStep(action='tapOn', target='submit_button', target_type='id', comment='Submit form'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=2000),
            TestStep(action='assertVisible', target='Success', target_type='text', comment='Verify success'),
        ]
    )
    return generate_scenario(config)


def generate_list_interaction_flow(app_id: str) -> str:
    """Generate a list interaction test flow."""
    config = ScenarioConfig(
        app_id=app_id,
        name="List Interaction Test",
        description="Test scrolling and item interaction in lists",
        steps=[
            TestStep(action='launchApp', target='', target_type='text'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=2000),
            TestStep(action='assertVisible', target='list_view', target_type='id'),
            TestStep(action='swipe', target='UP', target_type='text', comment='Scroll down'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='tapOn', target='list_item_1', target_type='id', comment='Tap first item'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='assertVisible', target='item_detail', target_type='id'),
            TestStep(action='back', target='', target_type='text'),
        ]
    )
    return generate_scenario(config)


def generate_undo_redo_flow(app_id: str) -> str:
    """Generate an undo/redo test flow."""
    config = ScenarioConfig(
        app_id=app_id,
        name="Undo/Redo Test",
        description="Test undo and redo functionality",
        steps=[
            TestStep(action='launchApp', target='', target_type='text'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=2000),
            TestStep(action='tapOn', target='action_button', target_type='id', comment='Perform action'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='tapOn', target='undo_button', target_type='id', comment='Undo action'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='tapOn', target='redo_button', target_type='id', comment='Redo action'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
        ]
    )
    return generate_scenario(config)


def generate_dialog_flow(app_id: str) -> str:
    """Generate a dialog interaction test flow."""
    config = ScenarioConfig(
        app_id=app_id,
        name="Dialog Test",
        description="Test dialog display and interaction",
        steps=[
            TestStep(action='launchApp', target='', target_type='text'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=2000),
            TestStep(action='tapOn', target='show_dialog_button', target_type='id', comment='Open dialog'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='assertVisible', target='dialog_title', target_type='id'),
            TestStep(action='tapOn', target='Confirm', target_type='text', comment='Confirm dialog'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='assertNotVisible', target='dialog_title', target_type='id', comment='Dialog dismissed'),
        ]
    )
    return generate_scenario(config)


# =============================================================================
# FLOW TYPE REGISTRY
# =============================================================================

FLOW_GENERATORS = {
    'login': generate_login_flow,
    'signup': generate_signup_flow,
    'game': generate_game_smoke_test,
    'resource': generate_resource_management_flow,
    'navigation': generate_navigation_flow,
    'form': generate_form_submission_flow,
    'list': generate_list_interaction_flow,
    'undo-redo': generate_undo_redo_flow,
    'dialog': generate_dialog_flow,
    # Game-specific flows for Terraforming Mars Player Board
    'production-phase': generate_production_phase_flow,
    'game-reset': generate_game_reset_flow,
    'history': generate_history_navigation_flow,
    'boundary': generate_boundary_test_flow,
    'state-persistence': generate_state_persistence_flow,
    'accessibility': generate_accessibility_flow,
    'conditional': generate_conditional_flow,
    'rapid-ops': generate_rapid_operations_flow,
    'cancel-dialog': generate_cancel_dialog_flow,
}


# =============================================================================
# GAME-SPECIFIC FLOW TEMPLATES (Terraforming Mars)
# =============================================================================

def generate_production_phase_flow(app_id: str) -> str:
    """Generate a production phase flow for Terraforming Mars."""
    config = ScenarioConfig(
        app_id=app_id,
        name="Production Phase Flow",
        description="Test production phase with resource collection",
        steps=[
            TestStep(action='launchApp', target='', target_type='text'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=3000),
            # Setup: Add some production values
            TestStep(action='tapOn', target='mc_prod_inc_1', target_type='id', comment='Set MC production'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='tapOn', target='steel_prod_inc_1', target_type='id', comment='Set Steel production'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='tapOn', target='energy_prod_inc_1', target_type='id', comment='Set Energy production'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            # Trigger production phase
            TestStep(action='tapOn', target='generation_increment', target_type='id', comment='Start production phase'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='assertVisible', target='Production Phase', target_type='text', comment='Verify dialog shown'),
            TestStep(action='tapOn', target='Confirm', target_type='text', comment='Confirm production phase'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=1000),
            # Verify generation incremented
            TestStep(action='assertVisible', target='generation_display', target_type='id', comment='Verify generation display'),
        ]
    )
    return generate_scenario(config)


def generate_game_reset_flow(app_id: str) -> str:
    """Generate a game reset flow with confirmation dialog."""
    config = ScenarioConfig(
        app_id=app_id,
        name="Game Reset Flow",
        description="Test game reset with confirmation dialog",
        steps=[
            TestStep(action='launchApp', target='', target_type='text'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=3000),
            # Make some changes first
            TestStep(action='tapOn', target='mc_amount_inc_10', target_type='id', comment='Add MC'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='tapOn', target='tr_increment', target_type='id', comment='Increase TR'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            # Trigger reset
            TestStep(action='tapOn', target='reset_button', target_type='id', comment='Tap reset button'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='assertVisible', target='Reset Game?', target_type='text', comment='Verify dialog'),
            TestStep(action='tapOn', target='reset_confirm_button', target_type='id', comment='Confirm reset'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            # Verify state is reset
            TestStep(action='assertVisible', target='generation_display', target_type='id', comment='Verify game reset'),
        ]
    )
    return generate_scenario(config)


def generate_history_navigation_flow(app_id: str) -> str:
    """Generate a history navigation flow."""
    config = ScenarioConfig(
        app_id=app_id,
        name="History Navigation Flow",
        description="Test action history screen navigation",
        steps=[
            TestStep(action='launchApp', target='', target_type='text'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=3000),
            # Make some actions to populate history
            TestStep(action='tapOn', target='mc_amount_inc_10', target_type='id', comment='Action 1'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=300),
            TestStep(action='tapOn', target='steel_amount_inc_5', target_type='id', comment='Action 2'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=300),
            # Navigate to history
            TestStep(action='tapOn', target='history_button', target_type='id', comment='Open history'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='assertVisible', target='Action History', target_type='text', comment='Verify history screen'),
            # Navigate back
            TestStep(action='back', target='', target_type='text', comment='Go back'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='assertVisible', target='generation_display', target_type='id', comment='Back on main screen'),
        ]
    )
    return generate_scenario(config)


def generate_boundary_test_flow(app_id: str) -> str:
    """Generate a boundary value test flow."""
    config = ScenarioConfig(
        app_id=app_id,
        name="Boundary Value Tests",
        description="Test minimum and maximum resource values",
        steps=[
            TestStep(action='launchApp', target='', target_type='text'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=3000),
            # Test minimum boundary (decrement from 0)
            TestStep(action='tapOn', target='mc_amount_dec_10', target_type='id', comment='Decrement from 0'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            # Test large value increment
            TestStep(action='tapOn', target='mc_amount_inc_10', target_type='id', comment='Add 10'),
            TestStep(action='tapOn', target='mc_amount_inc_10', target_type='id'),
            TestStep(action='tapOn', target='mc_amount_inc_10', target_type='id'),
            TestStep(action='tapOn', target='mc_amount_inc_10', target_type='id'),
            TestStep(action='tapOn', target='mc_amount_inc_10', target_type='id', comment='Add 50 total'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            # Test production boundaries
            TestStep(action='tapOn', target='steel_prod_inc_1', target_type='id', comment='Increment production'),
            TestStep(action='tapOn', target='steel_prod_inc_1', target_type='id'),
            TestStep(action='tapOn', target='steel_prod_inc_1', target_type='id'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='tapOn', target='steel_prod_dec_1', target_type='id', comment='Decrement production'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
        ]
    )
    return generate_scenario(config)


def generate_state_persistence_flow(app_id: str) -> str:
    """Generate a state persistence test flow."""
    config = ScenarioConfig(
        app_id=app_id,
        name="State Persistence Test",
        description="Verify state persists across app restart",
        steps=[
            TestStep(action='launchApp', target='', target_type='text'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=3000),
            # Make changes
            TestStep(action='tapOn', target='mc_amount_inc_10', target_type='id', comment='Add MC'),
            TestStep(action='tapOn', target='steel_amount_inc_5', target_type='id', comment='Add Steel'),
            TestStep(action='tapOn', target='tr_increment', target_type='id', comment='Increase TR'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            # Kill and restart app
            TestStep(action='killApp', target='', target_type='text', comment='Kill app'),
            TestStep(action='launchApp', target='', target_type='text', comment='Restart app'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=3000),
            # Verify state persisted
            TestStep(action='assertVisible', target='generation_display', target_type='id', comment='Verify state loaded'),
        ]
    )
    return generate_scenario(config)


def generate_accessibility_flow(app_id: str) -> str:
    """Generate an accessibility test flow for screen readers."""
    config = ScenarioConfig(
        app_id=app_id,
        name="Accessibility Test",
        description="Verify screen reader accessibility",
        steps=[
            TestStep(action='launchApp', target='', target_type='text'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=3000),
            # Verify semantic labels exist
            TestStep(action='assertVisible', target='generation_display', target_type='id', comment='Generation display has semantics'),
            TestStep(action='assertVisible', target='tr_display', target_type='id', comment='TR display has semantics'),
            TestStep(action='assertVisible', target='undo_button', target_type='id', comment='Undo button has semantics'),
            TestStep(action='assertVisible', target='redo_button', target_type='id', comment='Redo button has semantics'),
            TestStep(action='assertVisible', target='reset_button', target_type='id', comment='Reset button has semantics'),
            TestStep(action='assertVisible', target='history_button', target_type='id', comment='History button has semantics'),
            # Verify resource cards have semantic identifiers
            TestStep(action='assertVisible', target='resource_card_mc', target_type='id', comment='MC card has semantics'),
            TestStep(action='assertVisible', target='resource_card_steel', target_type='id', comment='Steel card has semantics'),
            TestStep(action='assertVisible', target='resource_card_titanium', target_type='id', comment='Titanium card has semantics'),
        ]
    )
    return generate_scenario(config)


def generate_conditional_flow(app_id: str) -> str:
    """Generate a conditional flow test (when X vs when not)."""
    config = ScenarioConfig(
        app_id=app_id,
        name="Conditional Flow Test",
        description="Test conditional logic branches",
        steps=[
            TestStep(action='launchApp', target='', target_type='text'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=3000),
            # Test: When undo is NOT available (no actions yet)
            TestStep(action='assertVisible', target='undo_button', target_type='id', comment='Undo button visible'),
            # Make an action
            TestStep(action='tapOn', target='mc_amount_inc_10', target_type='id', comment='Make an action'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            # Now undo should be available
            TestStep(action='tapOn', target='undo_button', target_type='id', comment='Undo available now'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            # Now redo should be available
            TestStep(action='tapOn', target='redo_button', target_type='id', comment='Redo available now'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
        ]
    )
    return generate_scenario(config)


def generate_rapid_operations_flow(app_id: str) -> str:
    """Generate a rapid operations test flow."""
    config = ScenarioConfig(
        app_id=app_id,
        name="Rapid Operations Test",
        description="Test rapid button tapping",
        steps=[
            TestStep(action='launchApp', target='', target_type='text'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=3000),
            # Rapid tapping without waits
            TestStep(action='tapOn', target='mc_amount_inc_1', target_type='id'),
            TestStep(action='tapOn', target='mc_amount_inc_1', target_type='id'),
            TestStep(action='tapOn', target='mc_amount_inc_1', target_type='id'),
            TestStep(action='tapOn', target='mc_amount_inc_1', target_type='id'),
            TestStep(action='tapOn', target='mc_amount_inc_1', target_type='id'),
            # Wait for all operations to settle
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=1000),
            # Rapid decrement operations
            TestStep(action='tapOn', target='mc_amount_dec_1', target_type='id'),
            TestStep(action='tapOn', target='mc_amount_dec_1', target_type='id'),
            TestStep(action='tapOn', target='mc_amount_dec_1', target_type='id'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=1000),
            # Verify UI is still responsive
            TestStep(action='assertVisible', target='generation_display', target_type='id', comment='UI still responsive'),
        ]
    )
    return generate_scenario(config)


def generate_cancel_dialog_flow(app_id: str) -> str:
    """Generate a cancel dialog test flow."""
    config = ScenarioConfig(
        app_id=app_id,
        name="Cancel Dialog Test",
        description="Test canceling confirmation dialogs",
        steps=[
            TestStep(action='launchApp', target='', target_type='text'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=3000),
            # Test canceling production phase dialog
            TestStep(action='tapOn', target='generation_increment', target_type='id', comment='Open production dialog'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='assertVisible', target='Production Phase', target_type='text', comment='Verify dialog'),
            TestStep(action='tapOn', target='Cancel', target_type='text', comment='Cancel dialog'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='assertNotVisible', target='Production Phase', target_type='text', comment='Dialog dismissed'),
            # Test canceling reset dialog
            TestStep(action='tapOn', target='reset_button', target_type='id', comment='Open reset dialog'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='assertVisible', target='Reset Game?', target_type='text', comment='Verify dialog'),
            TestStep(action='tapOn', target='reset_cancel_button', target_type='id', comment='Cancel reset'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=500),
            TestStep(action='assertNotVisible', target='Reset Game?', target_type='text', comment='Dialog dismissed'),
        ]
    )
    return generate_scenario(config)


def list_available_flows():
    """Print available flow types."""
    print("Available flow types:")
    print("\n  Authentication:")
    print("    login    - Standard login flow")
    print("    signup   - Standard signup/registration flow")
    print("\n  Game/Board Game:")
    print("    game     - Game smoke test (verify UI loads)")
    print("    resource - Resource management test (increment/decrement)")
    print("    undo-redo - Undo/redo functionality test")
    print("\n  General UI:")
    print("    navigation - Navigation between screens")
    print("    form     - Form input and submission")
    print("    list     - List scrolling and item interaction")
    print("    dialog   - Dialog display and interaction")
    print("\n  Terraforming Mars Specific:")
    print("    production-phase - Production phase flow")
    print("    game-reset       - Game reset with confirmation")
    print("    history          - History screen navigation")
    print("    boundary         - Boundary value testing")
    print("    state-persistence - App state persistence")
    print("    accessibility    - Screen reader testing")
    print("    conditional      - When X vs when not to test")
    print("    rapid-ops        - Rapid button tapping")
    print("    cancel-dialog    - Cancel confirmation dialogs")


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

    config = ScenarioConfig(
        app_id=app_id,
        name="Generated from Analysis",
        description="Auto-generated scenario based on widget analysis",
        steps=[
            TestStep(action='launchApp', target='', target_type='text'),
            TestStep(action='waitForAnimationToEnd', target='', target_type='text', wait_after=3000),
        ]
    )

    # Add assertions for widgets with identifiers
    seen_widgets = set()
    for issue in analysis:
        if 'identifier' in issue.get('suggestion', ''):
            # Extract identifier from suggestion
            match = re.search(r"identifier:\s*'([^']+)'", issue['suggestion'])
            if match:
                identifier = match.group(1)
                if identifier not in seen_widgets:
                    seen_widgets.add(identifier)
                    config.steps.append(TestStep(
                        action='assertVisible',
                        target=identifier,
                        target_type='id',
                        comment=f"Verify {issue['widget']} is visible"
                    ))

    return generate_scenario(config)


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_scenario.py <app_id> [flow_type]")
        print("\nGenerate Maestro YAML test scenarios.")
        list_available_flows()
        print("\nExamples:")
        print("  python generate_scenario.py com.example.app login")
        print("  python generate_scenario.py com.example.app game")
        print("  python generate_scenario.py com.example.app --from-analysis analysis.json")
        sys.exit(1)

    app_id = sys.argv[1]

    # Check for analysis file input
    if '--from-analysis' in sys.argv:
        idx = sys.argv.index('--from-analysis')
        if idx + 1 < len(sys.argv):
            analysis_file = sys.argv[idx + 1]
            print(generate_from_analysis(app_id, analysis_file))
            return

    # Check for list command
    if '--list' in sys.argv or '-l' in sys.argv:
        list_available_flows()
        return

    flow_type = sys.argv[2] if len(sys.argv) > 2 else 'login'

    generator = FLOW_GENERATORS.get(flow_type)
    if generator:
        print(generator(app_id))
    else:
        print(f"Unknown flow type: {flow_type}")
        list_available_flows()
        sys.exit(1)


if __name__ == '__main__':
    main()
