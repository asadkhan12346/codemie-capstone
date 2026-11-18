@FLASKR-5
Feature: Paginate the blog post list (page size 10)
  As a reader
  I want to view posts in pages of 10
  So that the index remains usable and efficient as posts grow

  Background:
    Given more than 10 posts exist

  @AC1
  Scenario: Requesting the index without a page parameter shows the newest 10 posts
    When I GET "/"
    Then the response status code is 200
    And I see exactly 10 posts ordered by created DESC

  @AC2
  Scenario: Requesting page 2 shows the next posts with no overlap
    When I GET "/?page=2"
    Then the response status code is 200
    And I see posts from the next page ordered by created DESC with no overlap with page 1

  @AC3
  Scenario Outline: Invalid page values default to page 1
    When I GET "/?page=<invalid>"
    Then the response status code is 200
    And the page content matches page 1

    Examples:
      | invalid |
      | abc     |
      | 0       |

  @AC4
  Scenario: Requesting a page higher than max returns an empty list and renders without error
    When I GET "/?page=9999"
    Then the response status code is 200
    And I see an empty list of posts

  @AC5
  Scenario: UI includes navigation links for pagination
    When I view the index page
    Then I see pagination navigation links such as Next or Previous
