@FLASKR-4
Feature: Validate missing vs empty fields and enforce title length
  The application must distinguish missing fields (HTTP 400) from empty fields (HTTP 200 + flash) and enforce title length.

  @AC1
  Scenario: Register returns 400 when username field is missing
    When I POST to "/auth/register" without the "username" field
    Then the response status code is 400
    And the response body contains "Missing required field: username."

  @AC2
  Scenario: Register returns 400 when password field is missing
    When I POST to "/auth/register" without the "password" field
    Then the response status code is 400
    And the response body contains "Missing required field: password."

  @AC3
  Scenario: Register returns 200 and flashes when username is empty
    When I POST to "/auth/register" with "username" set to whitespace and a non-empty password
    Then the response status code is 200
    And a flashed message equals "Username is required."

  @AC4
  Scenario: Register returns 200 and flashes when password is empty
    When I POST to "/auth/register" with non-empty username and "password" set to whitespace
    Then the response status code is 200
    And a flashed message equals "Password is required."

  @AC5
  Scenario: Login returns 400 when username field is missing
    When I POST to "/auth/login" without the "username" field
    Then the response status code is 400
    And the response body contains "Missing required field: username."

  @AC6
  Scenario: Login returns 400 when password field is missing
    When I POST to "/auth/login" without the "password" field
    Then the response status code is 400
    And the response body contains "Missing required field: password."

  @AC7
  Scenario: Login returns 200 and flashes when username is empty
    When I POST to "/auth/login" with "username" set to whitespace and a non-empty password
    Then the response status code is 200
    And a flashed message equals "Username is required."

  @AC8
  Scenario: Login returns 200 and flashes when password is empty
    When I POST to "/auth/login" with non-empty username and "password" set to whitespace
    Then the response status code is 200
    And a flashed message equals "Password is required."

  @AC9
  Scenario: Create returns 400 when title field is missing
    Given I am logged in
    When I POST to "/create" without the "title" field
    Then the response status code is 400
    And the response body contains "Missing required field: title."

  @AC10
  Scenario: Create returns 400 when body field is missing
    Given I am logged in
    When I POST to "/create" without the "body" field
    Then the response status code is 400
    And the response body contains "Missing required field: body."

  @AC11
  Scenario: Create returns 200 and flashes when title is empty
    Given I am logged in
    When I POST to "/create" with "title" set to whitespace and non-empty body
    Then the response status code is 200
    And a flashed message equals "Title is required."

  @AC12
  Scenario: Create returns 200 and flashes when body is empty
    Given I am logged in
    When I POST to "/create" with non-empty title and "body" set to whitespace
    Then the response status code is 200
    And a flashed message equals "Body is required."

  @AC13
  Scenario: Create returns 200 and flashes when title is longer than 100 characters
    Given I am logged in
    When I POST to "/create" with title longer than 100 characters and non-empty body
    Then the response status code is 200
    And a flashed message equals "Title must be at most 100 characters."

  @AC14
  Scenario: Update returns 400 when title field is missing
    Given I am logged in
    And a post exists
    When I POST to the post update endpoint without the "title" field
    Then the response status code is 400
    And the response body contains "Missing required field: title."

  @AC15
  Scenario: Update returns 400 when body field is missing
    Given I am logged in
    And a post exists
    When I POST to the post update endpoint without the "body" field
    Then the response status code is 400
    And the response body contains "Missing required field: body."

  @AC16
  Scenario: Update returns 200 and flashes when title is empty
    Given I am logged in
    And a post exists
    When I POST to the post update endpoint with "title" set to whitespace and non-empty body
    Then the response status code is 200
    And a flashed message equals "Title is required."

  @AC17
  Scenario: Update returns 200 and flashes when body is empty
    Given I am logged in
    And a post exists
    When I POST to the post update endpoint with non-empty title and "body" set to whitespace
    Then the response status code is 200
    And a flashed message equals "Body is required."

  @AC18
  Scenario: Update returns 200 and flashes when title is longer than 100 characters
    Given I am logged in
    And a post exists
    When I POST to the post update endpoint with title longer than 100 characters and non-empty body
    Then the response status code is 200
    And a flashed message equals "Title must be at most 100 characters."

  @AC19
  Scenario: Valid submissions preserve existing successful behavior
    Given I am logged in
    When I submit valid values to register and login
    And I submit valid values to create and update
    Then register and login redirect
    And create and update persist and redirect
