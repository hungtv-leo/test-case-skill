# self-test-cases (portable Cursor skill)

A Cursor Agent Skill that helps developers on **any project**: read a feature
requirement → write test cases using the project's own test framework →
self-test → report failures if any case fails → when 100% pass, export an Excel
handover file for testers → (optional) comment results and attach the Excel file
to Jira.

Portable: not tied to any single framework. Project-specific details are detected
on the first run and cached in `reference.local.md`.

## Installation

### Option 1 - Git clone (recommended, easy to update)

Clone directly into the project's skill directory:

```bash
git clone <URL-of-this-repo> .cursor/skills/self-test-cases
```

Update later:

```bash
cd .cursor/skills/self-test-cases && git pull
```

### Option 2 - Download .zip

1. Download the zip of this repo and extract it.
2. Copy the contents into the project so this path exists:
   `.cursor/skills/self-test-cases/SKILL.md`

### After installation (both options)

Install script dependencies (first time only):

```bash
pip install -r .cursor/skills/self-test-cases/scripts/requirements.txt
```

(Optional) Configure Jira in a `.env` file at the project root if you want result
comments:

```env
JIRA_BASE_URL=https://jira.company.com
JIRA_AUTH_MODE=bearer   # bearer = PAT (Server/DC); basic = Cloud (email + API token)
JIRA_TOKEN=xxxxx
# JIRA_USER=you@company.com   # required only when JIRA_AUTH_MODE=basic
```

> Do not commit `.env` or handover `.xlsx` files.

## Usage

In Cursor, invoke the skill by name (the skill sets `disable-model-invocation: true`,
so it only loads when mentioned):

```
/self-test-cases  Write tests for feature <requirement description>
```

On the first run, the agent detects the stack and creates `reference.local.md`.
Later runs read that file directly.

## Supported frameworks (core)

| Group | Framework | Adapter | Notes |
|-------|-----------|---------|-------|
| Python | pytest | `pytest` | Native pytest-json-report support |
| Node | jest / vitest | `jest` / `vitest` | JSON reporter |
| Remix | vitest + Playwright | `remix` | `--mode unit` or `--mode e2e` |
| E2E | Playwright | `playwright` | JSON report |
| Go | go test | `go` | `-json` output |
| Java | Spring Boot + JUnit | `spring-boot` / `junit` | Parse JUnit XML (Surefire/Gradle) |

Other frameworks: build `results.json` yourself from the schema, or add a new
adapter.

## Structure

```
self-test-cases/
├── SKILL.md                    # workflow + guide (stable layer)
├── reference.template.md       # template -> copied to reference.local.md
├── schemas/
│   ├── cases.schema.json       # schema for cases.json
│   └── results.schema.json     # schema for results.json
├── scripts/
│   ├── convert_results.py      # framework adapter -> results.json
│   ├── validate_test_cases.py  # validate cases/results + alignment
│   ├── export_test_cases.py    # Excel export, 100% pass gate
│   ├── jira_notify.py          # comment + attachment to Jira
│   └── requirements.txt
└── templates/
    ├── cases.example.json      # sample case metadata (keyed by test id)
    └── results.example.json    # sample results.json format
```

## Data formats

### `cases.json`

Test case metadata, keyed by the framework **test id**. Schema:
`schemas/cases.schema.json`. Each case includes: `case_id`, `description`,
`precondition`, `steps`, `data`, `expected`.

### `results.json`

Standard test results format for every language:

```json
{
  "<test id 1>": "passed",
  "<test id 2>": "failed"
}
```

Values: `passed` | `failed` | `error` | `skipped`. For Python + pytest you can
also pass `--json-report-file=.report.json` directly; the script understands the
pytest-json-report format.

### Convert framework results

```bash
python .cursor/skills/self-test-cases/scripts/convert_results.py \
  --framework vitest --input .vitest-report.json --output results.json
```

### Validate before Excel export

```bash
python .cursor/skills/self-test-cases/scripts/validate_test_cases.py \
  --cases tests/feature/cases.json --results results.json
```

## Notes

- `reference.local.md` is project-specific → commit it in that project,
  **do not** commit it back into the skill repo.
- Do not place this skill under `~/.cursor/skills-cursor/` (reserved for Cursor).
