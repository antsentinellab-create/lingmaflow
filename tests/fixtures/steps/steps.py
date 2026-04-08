"""Step definitions for test_passing.feature and test_failing.feature."""

from behave import given, when, then


@given('a simple test')
def step_given_simple_test(context):
    """Given step that always passes."""
    pass


@when('I run the test')
def step_when_run_test(context):
    """When step that always passes."""
    pass


@then('it should pass')
def step_then_should_pass(context):
    """Then step that always passes."""
    assert True


@then('it should fail intentionally')
def step_then_should_fail(context):
    """Then step that always fails (for testing failure scenarios)."""
    assert False, "This step is designed to fail for testing purposes"
