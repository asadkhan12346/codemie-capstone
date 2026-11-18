@FLASKR-3
Feature: Require safe SECRET_KEY configuration for non-debug, non-test runs
  As an operator/developer
  I want the app to avoid running in non-debug and non-testing mode with a predictable or missing SECRET_KEY
  So that sessions are not vulnerable in production

  Background:
    Given the Flaskr app is available

  @AC1
  Scenario: App starts in debug or testing even if SECRET_KEY is not explicitly configured
    Given the app is starting with debug enabled
    When the app initializes
    Then the app starts normally

  @AC2
  Scenario: Startup fails in non-debug and non-test when no SECRET_KEY is provided
    Given the app is starting in production mode
    And no SECRET_KEY is provided via instance config or environment
    When the app initializes
    Then startup fails with a clear error message describing how to set SECRET_KEY

  @AC3
  Scenario: App starts in non-debug and non-test when SECRET_KEY is configured
    Given the app is starting in production mode
    And SECRET_KEY is provided via environment or instance config.py
    When the app initializes
    Then the app starts successfully using the configured key

  @AC4
  Scenario: README-documented SECRET_KEY configuration allows the app to start
    Given the operator follows the README to configure SECRET_KEY
    When the operator starts the app
    Then the app starts successfully
