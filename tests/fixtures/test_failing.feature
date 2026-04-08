Feature: Test failing scenario

  Scenario: Simple failing test
    Given a simple test
    When I run the test
    Then it should fail intentionally
