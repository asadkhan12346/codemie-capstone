# Implementation Plan — FLASKR-2

Jira baseUrl: https://khanasad1105.atlassian.net

Repo: https://github.com/asadkhan12346/codemie-capstone (default branch: `main`)

Epic: **FLASKR-2** — **Production Hardening & Scalable Post Listing (Top 3 Gap Fixes)**

Goal: Improve security configuration, robustness of input handling, and scalability of the post listing page.

In-scope (approved Top 3):
- SECRET_KEY handling improvements + production configuration documentation
- Safer form field access + validation for auth and blog forms
- Pagination on blog index

Out of scope (per Epic): CSRF, new error pages/handlers, delete confirmation flow, password policy/confirm password, logging, Ruff config changes.

---

## Decisions

1. **Relaxed Q3 interpretation (approved by human):** up to **10 acceptance criteria per endpoint group** in a single task row.

---

## A. Summary

### Stories in this Epic (label: AI-SDLC)

All stories currently show Jira priority = Medium.

1. **FLASKR-3** — US-1.1 Require safe SECRET_KEY configuration for non-debug, non-test runs
2. **FLASKR-4** — US-1.2 Validate missing vs empty fields and enforce title length
3. **FLASKR-5** — US-1.3 Paginate the blog post list (page size 10)

### Implementation order (Q1)

1) **FLASKR-3** first because it changes application startup (`flaskr/__init__.py`) and can affect *all* subsequent runs/tests.

2) **FLASKR-4** next because it changes request handling/validation and shares `flaskr/blog.py` with pagination.

3) **FLASKR-5** last because it also modifies `flaskr/blog.py` and the blog index template; doing it last reduces merge conflicts.

---

## B. Task Sequence

| Order | Jira key (story) | Sub-task key | Task | Files likely to change | Depends on | Effort | Acceptance criteria covered |
|---:|---|---|---|---|---|---|---|
| 1 | FLASKR-3 | FLASKR-6 | Enforce non-dev `SECRET_KEY` when not `debug` and not `testing`; fail fast with clear message; allow missing key in debug/testing | `flaskr/__init__.py` | - | S | FLASKR-3 AC 1,2,3 |
| 2 | FLASKR-3 | FLASKR-7 | Document production `SECRET_KEY` setup (env var and/or instance config) and ensure README steps result in successful startup | `README.rst` | 1 | S | FLASKR-3 AC 4 |
| 3 | FLASKR-3 | FLASKR-8 | Add tests verifying: debug/testing allows missing key; non-debug/non-test without key fails; configured key succeeds | `tests/test_factory.py` (and/or new test module), possibly `tests/conftest.py` | 2 | S | FLASKR-3 AC 1,2,3 |
| 4 | FLASKR-4 | **FLASKR-9** | **Auth endpoints**: implement missing-vs-empty validation for `/auth/register` and `/auth/login` | `flaskr/auth.py` | 3 | M | FLASKR-4 AC 1–8 |
| 5 | FLASKR-4 | **FLASKR-14** | **Blog endpoints**: implement missing-vs-empty validation for `/create` and `/<id>/update` + enforce title length ≤ 100 | `flaskr/blog.py` | 4 | M | FLASKR-4 AC 9–18 |
| 6 | FLASKR-4 | **FLASKR-10** | **Tests (auth validation)**: add tests for missing-field=400 and empty/whitespace-field=200 with flashed msg for register/login | `tests/test_auth.py` | 5 | S | FLASKR-4 AC 1–8 |
| 7 | FLASKR-4 | **FLASKR-10** | **Tests (blog create validation + success paths)**: add tests for `/create` missing/empty fields + title length > 100, and also validate success-path behavior | `tests/test_blog.py` | 6 | M | FLASKR-4 AC 9–13,19 |
| 8 | FLASKR-4 | **FLASKR-10** | **Tests (blog update validation)**: add tests for `/<id>/update` missing/empty fields + title length > 100 | `tests/test_blog.py` | 7 | M | FLASKR-4 AC 14–18 |
| 9 | FLASKR-5 | FLASKR-11 | Implement pagination on `/` using `LIMIT/OFFSET` with page size 10; parse/normalize `page` param (invalid→1) | `flaskr/blog.py` | 8 | M | FLASKR-5 AC 1–4 |
| 10 | FLASKR-5 | FLASKR-12 | Add pagination controls to blog index template | `flaskr/templates/blog/index.html` | 9 | S | FLASKR-5 AC 5 |
| 11 | FLASKR-5 | FLASKR-13 | Add tests for default page=1, invalid page→1, page too high→empty list with 200, ordering/no overlap | `tests/test_blog.py`, possibly `tests/data.sql` | 10 | M | FLASKR-5 AC 1–4 |

---

## C. Dependencies and Shared Files (Q4)

### Hard dependencies
- FLASKR-3 must land first because startup config affects all tests and app runs.
- FLASKR-4 must land before FLASKR-5 because both change `flaskr/blog.py`.

### Shared files touched by more than one story + merge order
- `flaskr/blog.py` shared by **FLASKR-4** (task 5) and **FLASKR-5** (task 9)
  - Merge order: task 5 → task 9
- `tests/test_blog.py` shared by **FLASKR-4** (tasks 7–8) and **FLASKR-5** (task 11)
  - Merge order: task 7 → task 8 → task 11

### Parallelization guidance
Work can be parallelized only when it doesn’t touch shared files; however, this plan sequences all tasks to avoid conflicts and to keep endpoint behavior changes easy to review.

---

## D. Risks and Mitigations (Q5)

| Risk | Impact | Mitigation |
|---|---|---|
| Existing tests broken by startup `SECRET_KEY` enforcement | Test suite may fail if `create_app` raises under conditions used by tests | Ensure enforcement explicitly exempts `app.testing` and `app.debug`; add/adjust tests in FLASKR-8 |
| Test setup/fixtures affected | `tests/conftest.py` creates app with `TESTING=True`; any new checks could break | Keep enforcement dependent on `app.testing`; avoid requiring env vars in tests |
| Config/startup behavior changes | Non-debug/non-test runs will now fail fast without `SECRET_KEY` | Provide clear error message and update README with exact setup steps |
| Data/schema impact | Pagination changes query behavior; no schema change intended | Keep pagination query-only (`LIMIT/OFFSET`); extend `tests/data.sql` only if more posts needed |
| Documentation going out of date | README currently focuses on debug run | Update README per FLASKR-7 and keep it aligned with behavior |
| Validation semantics change (400 vs 200) | Clients/UI might not expect new status codes | Implement exactly per AC; lock behavior with explicit tests |
| Pagination navigation edge cases | Broken/odd navigation links (e.g., Next shown with no next page) | Compute prev/next flags and render conditionally; test too-high/invalid pages |

---

## E. Definition of Done (per story)

### FLASKR-3
- [ ] Code: `create_app` enforces safe `SECRET_KEY` for non-debug/non-test runs (AC 1–3)
- [ ] Tests: cover enforcement cases (AC 1–3)
- [ ] Docs: README documents production `SECRET_KEY` configuration (AC 4)
- [ ] Review: PR references FLASKR-3 and passes tests

### FLASKR-4
- [ ] Code: auth + blog validation behavior implemented (AC 1–18)
- [ ] Tests:
  - auth validation tests (AC 1–8)
  - blog create validation tests (AC 9–13) **and** success-path coverage (AC 19)
  - blog update validation tests (AC 14–18)
- [ ] Review: PR references FLASKR-4 and passes tests

### FLASKR-5
- [ ] Code: `/` supports `?page=` with size 10, invalid handling, too-high handling (AC 1–4)
- [ ] UI: index template includes pagination navigation controls (AC 5)
- [ ] Tests: pagination covered (AC 1–4)
- [ ] Review: PR references FLASKR-5 and passes tests

---

## F. Branching and PR Strategy (Q7)

- Plan branch: `plan/FLASKR-2`
- Feature branches:
  - `feature/FLASKR-3`
  - `feature/FLASKR-4`
  - `feature/FLASKR-5`
- Commit messages start with the Jira key (e.g., `FLASKR-4: validate missing vs empty fields`)
- One Pull Request per feature branch, each referencing its story key.

---

## G. Test Strategy (Q6)

### Commands (from `README.rst`)
- Install test deps: `pip install '.[test]'`
- Run tests: `pytest`
- Coverage:
  - `coverage run -m pytest`
  - `coverage report`
  - `coverage html`

### Lint
- Not documented in README.
- **Assumption (optional):** `ruff check .` (Ruff is configured in `pyproject.toml` under `[tool.ruff]`, but the command isn’t documented in README.)

### Tests to add/update
- FLASKR-3: startup/secret key behavior tests (likely `tests/test_factory.py`)
- FLASKR-4:
  - auth validation tests in `tests/test_auth.py`
  - blog validation tests in `tests/test_blog.py` (including success-path assertions for AC 19 on the create-focused test row)
- FLASKR-5: pagination tests in `tests/test_blog.py` (and potentially extend `tests/data.sql` to exceed 10 posts)

---

## H. Demo Order

1. FLASKR-3: show startup behavior across debug/testing vs non-debug/non-test with and without `SECRET_KEY`.
2. FLASKR-4: show 400 for missing fields, 200 + flash for empty/whitespace, title length > 100 rejected, valid flows preserved.
3. FLASKR-5: show `/` page 1 (10 newest), `?page=2`, invalid page defaults to 1, too-high page returns 200 with empty list; show navigation links.

---

## Evidence: `flaskr/templates/blog/index.html` excerpt (read via GitHub)

```jinja2
{% extends 'base.html' %}

{% block header %}
  <h1>{% block title %}Posts{% endblock %}</h1>
  {% if g.user %}
    <a class="action" href="{{ url_for('blog.create') }}">New</a>
  {% endif %}
{% endblock %}

{% block content %}
  {% for post in posts %}
    <article class="post">
      <header>
        <div>
          <h1>{{ post['title'] }}</h1>
          <div class="about">by {{ post['username'] }} on {{ post['created'].strftime('%Y-%m-%d') }}</div>
        </div>
        {% if g.user['id'] == post['author_id'] %}
          <a class="action" href="{{ url_for('blog.update', id=post['id']) }}">Edit</a>
        {% endif %}
      </header>
      <p class="body">{{ post['body'] }}</p>
    </article>
    {% if not loop.last %}
      <hr>
    {% endif %}
  {% endfor %}
{% endblock %}
```

---

## I. Quality check (Q8)

### Q3 row-by-row counts (endpoint group(s) + criteria count)
1. FLASKR-3 startup config (`create_app` / startup): **3 criteria** (AC 1–3)
2. FLASKR-3 docs (README): **1 criterion** (AC 4)
3. FLASKR-3 tests (startup): **3 criteria** (AC 1–3)
4. FLASKR-4 auth endpoints (`/auth/register`, `/auth/login`): **8 criteria** (AC 1–8)
5. FLASKR-4 blog endpoints (`/create`, `/<id>/update`): **10 criteria** (AC 9–18)
6. FLASKR-4 tests (auth validation): **8 criteria** (AC 1–8)
7. FLASKR-4 tests (blog create + success paths): **6 criteria** (AC 9–13,19)
8. FLASKR-4 tests (blog update): **5 criteria** (AC 14–18)
9. FLASKR-5 blog index endpoint (`/` pagination): **4 criteria** (AC 1–4)
10. FLASKR-5 template (`index.html` pagination controls): **1 criterion** (AC 5)
11. FLASKR-5 tests (pagination): **4 criteria** (AC 1–4)

Quality check: **Q1 PASS, Q2 PASS, Q3 PASS, Q4 PASS, Q5 PASS, Q6 PASS, Q7 PASS**