@FLASKR-3
Feature: Require safe SECRET_KEY configuration for non-debug, non-test runs
  The application must not run in non-debug, non-testing mode without an explicit SECRET_KEY.

  Background:
    Given the Flask application factory exists

  @AC1
  Scenario: App starts in debug or testing even without an explicit SECRET_KEY
    Given the app is starting with debug enabled or testing enabled
    When the application initializes without an explicitly configured SECRET_KEY
    Then the app starts normally

  @AC2
  Scenario: App startup fails in production mode when SECRET_KEY is not provided
    Given the app is starting with debug disabled and testing disabled
    And no SECRET_KEY is provided via environment or instance config
    When the application initializes
    Then startup fails with an error message describing how to set SECRET_KEY

  @AC3
  Scenario: App starts in production mode when SECRET_KEY is provided
    Given the app is starting with debug disabled and testing disabled
    And SECRET_KEY is provided via environment or instance config
    When the application initializes
    Then the app starts successfully using the configured key and not the default "dev"

  @AC4
  Scenario: App starts successfully when README steps for configuring SECRET_KEY are followed
    Given the operator follows the README instructions to configure SECRET_KEY
    When the operator starts the app
    Then the app starts successfully
