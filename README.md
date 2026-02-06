# Data Engineering GitHub Actions

[![Ministry of Justice Repository Compliance Badge](https://github-community.service.justice.gov.uk/repository-standards/api/data-engineering-github-actions/badge)](https://github-community.service.justice.gov.uk/repository-standards/data-engineering-github-actions)

A collection of reusable GitHub Actions workflows maintained by the Data Engineering team.

## Why use these workflows?

Using these centralised reusable workflows provides consistent version management of GitHub Actions across all repositories. Using these ensures consistency of how these workflows are applied across the team. Additionally, if there is a security incident which requires an action version to be updated, the fix only needs to be applied in this repository, with all the reposotiries consuming the afflicted workflows automatically receiving the update.

**Always reference `@main` when using these workflows** to ensure you receive the latest security patches and updates:

```yaml
uses: ministryofjustice/data-engineering-github-actions/.github/workflows/reusable-example.yml@main
```

## Reusable Workflows

### List Open PRs

Posts a summary of open pull requests to a Slack channel, including how long each PR has been open.

**Inputs:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `tag` | string | No | - | Label to filter PRs on |
| `dry_run` | boolean | No | `false` | If true, prints PRs to logs instead of sending Slack alerts |

**Secrets:**

| Name | Required | Description |
|------|----------|-------------|
| `slack_workflow_url` | Yes | Slack Incoming Webhook URL used to send alerts |

**Usage:**

```yaml
name: List Open PRs
on:
  schedule:
    - cron: "0 9 * * 1-5" # Weekdays at 9am
  workflow_dispatch:
    inputs:
      dry_run:
        description: "Run in dry-run mode (skip Slack alert)?"
        type: boolean
        default: false

permissions:
  contents: read
  pull-requests: read

jobs:
  list-open-prs:
    uses: ministryofjustice/data-engineering-github-actions/.github/workflows/reusable-list-open-prs.yml@main
    with:
      tag: "needs-review"
      dry_run: ${{ github.event_name == 'workflow_dispatch' && github.event.inputs.dry_run == 'true' || false }}
    secrets:
      slack_workflow_url: ${{ secrets.SLACK_WEBHOOK_URL }}

```

---

### Pre-commit (Prek)

Runs pre-commit hooks using [prek-action](https://github.com/j178/prek-action).

**Usage:**

```yaml
name: Pre-commit
on:
  pull_request:
    types: [opened, edited, reopened, synchronize]

permissions:
  contents: read

jobs:
  pre-commit:
    uses: ministryofjustice/data-engineering-github-actions/.github/workflows/reusable-pre-commit.yml@main
```

---

### Python Lint

Lints Python code using [Ruff](https://github.com/astral-sh/ruff) for both linting and formatting checks.

**Usage:**

```yaml
name: Python Lint
on:
  pull_request:
    types: [opened, edited, reopened, synchronize]

permissions:
  contents: read

jobs:
  python-lint:
    uses: ministryofjustice/data-engineering-github-actions/.github/workflows/reusable-python-lint.yml@main
```

---

### Python Unit Test

Runs Python unit tests using pytest with [uv](https://github.com/astral-sh/uv) for dependency management.

**Inputs:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `uv_test_group_name` | string | No | `test` | Name of the uv dependency group containing test dependencies |

**Usage:**

```yaml
name: Python Unit Test
on:
  pull_request:
    types: [opened, edited, reopened, synchronize]

permissions:
  contents: read

jobs:
  python-unit-test:
    uses: ministryofjustice/data-engineering-github-actions/.github/workflows/reusable-python-unit-test.yml@main
    with:
      uv_test_group_name: test
```

---

### YAML Lint

Lints YAML files using [yamllint](https://github.com/adrienverge/yamllint).

**Inputs:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `uv_lint_group_name` | string | No | `""` | Optional uv dependency group. If provided, runs `uv sync` with this group before linting |

**Usage:**

```yaml
name: YAML Lint
on:
  pull_request:
    types: [opened, edited, reopened, synchronize]

permissions:
  contents: read

jobs:
  yaml-lint:
    uses: ministryofjustice/data-engineering-github-actions/.github/workflows/reusable-yaml-lint.yml@main
```
