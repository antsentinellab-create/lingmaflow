"""Step definitions for test_passing.feature (integration tests)."""

from behave import given, when, then


@given('the system is initialized')
def step_given_system_initialized(context):
    """Given step that always passes."""
    pass


@when('I run a basic test')
def step_when_run_basic_test(context):
    """When step that always passes."""
    pass


@then('it should pass successfully')
def step_then_should_pass_successfully(context):
    """Then step that always passes."""
    assert True
