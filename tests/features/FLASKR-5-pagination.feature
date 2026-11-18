@FLASKR-5
Feature: Paginate the blog post list (page size 10)
  Posts should be displayed in pages of 10 ordered by created DESC.

  @AC1
  Scenario: Default request shows newest 10 posts when there are more than 10
    Given there are more than 10 posts
    When I request "/" with no page parameter
    Then I see exactly 10 posts
    And the posts are ordered by created descending

  @AC2
  Scenario: Page 2 shows next posts with no overlap
    Given there are at least 11 posts
    When I request "/?page=2"
    Then I see the next 10 posts or fewer
    And there is no overlap with page 1
    And the posts are ordered by created descending

  @AC3
  Scenario: Invalid page values default to page 1
    Given there are more than 10 posts
    When I request "/?page=abc"
    Then the response status code is 200
    And the response is the same as requesting page 1
    When I request "/?page=0"
    Then the response status code is 200
    And the response is the same as requesting page 1

  @AC4
  Scenario: Page higher than maximum shows empty list without error
    Given there are more than 10 posts
    When I request a page higher than the maximum
    Then the response status code is 200
    And the page renders without error
    And I see an empty list of posts

  @AC5
  Scenario: UI provides navigation links for pagination
    Given there are more than 10 posts
    When I view the index page
    Then I see pagination navigation links (Next/Previous) or equivalent
