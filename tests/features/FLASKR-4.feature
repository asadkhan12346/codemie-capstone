@FLASKR-4
Feature: Validate missing vs empty fields and enforce title length
  As a user
  I want the app to handle malformed form submissions predictably
  So that missing fields are rejected and empty fields show clear messages naming the field

  Background:
    Given the Flaskr app is available

  # /auth/register (POST)
  @AC1
  Scenario: Register rejects when username field is missing
    When I POST "/auth/register" with form data:
      | password | a |
    Then the response status code is 400
    And the response body includes "Missing required field: username."

  @AC2
  Scenario: Register rejects when password field is missing
    When I POST "/auth/register" with form data:
      | username | a |
    Then the response status code is 400
    And the response body includes "Missing required field: password."

  @AC3
  Scenario: Register flashes message when username is empty or whitespace
    When I POST "/auth/register" with form data:
      | username |    |
      | password | a  |
    Then the response status code is 200
    And a flashed message equals "Username is required."

  @AC4
  Scenario: Register flashes message when password is empty or whitespace
    When I POST "/auth/register" with form data:
      | username | a  |
      | password |    |
    Then the response status code is 200
    And a flashed message equals "Password is required."

  # /auth/login (POST)
  @AC5
  Scenario: Login rejects when username field is missing
    When I POST "/auth/login" with form data:
      | password | test |
    Then the response status code is 400
    And the response body includes "Missing required field: username."

  @AC6
  Scenario: Login rejects when password field is missing
    When I POST "/auth/login" with form data:
      | username | test |
    Then the response status code is 400
    And the response body includes "Missing required field: password."

  @AC7
  Scenario: Login flashes message when username is empty or whitespace
    When I POST "/auth/login" with form data:
      | username |    |
      | password | test |
    Then the response status code is 200
    And a flashed message equals "Username is required."

  @AC8
  Scenario: Login flashes message when password is empty or whitespace
    When I POST "/auth/login" with form data:
      | username | test |
      | password |     |
    Then the response status code is 200
    And a flashed message equals "Password is required."

  # /create (POST)
  @AC9
  Scenario: Create rejects when title field is missing
    Given I am logged in
    When I POST "/create" with form data:
      | body | hello |
    Then the response status code is 400
    And the response body includes "Missing required field: title."

  @AC10
  Scenario: Create rejects when body field is missing
    Given I am logged in
    When I POST "/create" with form data:
      | title | hello |
    Then the response status code is 400
    And the response body includes "Missing required field: body."

  @AC11
  Scenario: Create flashes message when title is empty or whitespace
    Given I am logged in
    When I POST "/create" with form data:
      | title |   |
      | body  | x |
    Then the response status code is 200
    And a flashed message equals "Title is required."

  @AC12
  Scenario: Create flashes message when body is empty or whitespace
    Given I am logged in
    When I POST "/create" with form data:
      | title | hi |
      | body  |   |
    Then the response status code is 200
    And a flashed message equals "Body is required."

  @AC13
  Scenario: Create flashes message when title length is greater than 100
    Given I am logged in
    When I POST "/create" with a title longer than 100 characters and body "x"
    Then the response status code is 200
    And a flashed message equals "Title must be at most 100 characters."

  # /<id>/update (POST)
  @AC14
  Scenario: Update rejects when title field is missing
    Given I am logged in
    And a post exists with id 1
    When I POST "/1/update" with form data:
      | body | hello |
    Then the response status code is 400
    And the response body includes "Missing required field: title."

  @AC15
  Scenario: Update rejects when body field is missing
    Given I am logged in
    And a post exists with id 1
    When I POST "/1/update" with form data:
      | title | hello |
    Then the response status code is 400
    And the response body includes "Missing required field: body."

  @AC16
  Scenario: Update flashes message when title is empty or whitespace
    Given I am logged in
    And a post exists with id 1
    When I POST "/1/update" with form data:
      | title |   |
      | body  | x |
    Then the response status code is 200
    And a flashed message equals "Title is required."

  @AC17
  Scenario: Update flashes message when body is empty or whitespace
    Given I am logged in
    And a post exists with id 1
    When I POST "/1/update" with form data:
      | title | hi |
      | body  |   |
    Then the response status code is 200
    And a flashed message equals "Body is required."

  @AC18
  Scenario: Update flashes message when title length is greater than 100
    Given I am logged in
    And a post exists with id 1
    When I POST "/1/update" with a title longer than 100 characters and body "x"
    Then the response status code is 200
    And a flashed message equals "Title must be at most 100 characters."

  @AC19
  Scenario: Valid submissions preserve current success paths
    Given I am logged in
    When I POST "/auth/register" with valid username and password
    Then the response redirects to "/auth/login"
    When I POST "/auth/login" with valid username and password
    Then the response redirects to "/"
    When I POST "/create" with title length <= 100 and non-empty body
    Then the response redirects to "/"
    When I POST "/1/update" with title length <= 100 and non-empty body
    Then the response redirects to "/"
