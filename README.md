# self-test-cases (portable Cursor skill)

A Cursor Agent Skill that helps developers on **any project**: read a feature
requirement → write test cases using the project's own test framework →
self-test → report failures if any case fails → when 100% pass, export an Excel
handover file for testers → (optional) comment results and attach the Excel file
to Jira.

Portable: not tied to any single framework. Project-specific details are detected
on the first run and cached in `reference.local.md`.

**GitHub:** https://github.com/hungtv-leo/test-case-skill

---

## Quick start (Windows / PowerShell)

Open a terminal at your **target project root** (the app you want to test), then
run:

```powershell
# 1) Create skill folder
New-Item -ItemType Directory -Force -Path .cursor\skills | Out-Null

# 2) Download skill only (shallow clone)
git clone --depth 1 https://github.com/hungtv-leo/test-case-skill.git .cursor/skills/self-test-cases

# 3) Install skill script dependencies (user-level, does NOT touch project deps)
pip install --user -r .cursor\skills\self-test-cases\scripts\requirements.txt

# 4) (Recommended) Install + wire CodeGraph for Cursor, then index this project
#    Skip if `codegraph` is already installed and `.codegraph/` is indexed.
irm https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.ps1 | iex
# Open a NEW terminal after CLI install, then:
codegraph install --target=cursor --yes
codegraph init
# If folder exists but index is empty:
# codegraph index

# 5) Verify skill install
Test-Path .cursor\skills\self-test-cases\SKILL.md
```

If step 5 prints `True`, **restart Cursor** (so CodeGraph MCP loads), open the
project, and run:

```text
/self-test-cases Write tests for feature <your requirement>
```

---

## Detailed setup guide

### Prerequisites

| Requirement | Why |
|-------------|-----|
| [Cursor](https://cursor.com) | Loads skills from `.cursor/skills/` |
| Git | To clone this repo |
| Python 3.10+ + `pip` | Runs export / validate / convert scripts |
| [CodeGraph](https://github.com/colbymchenry/codegraph) (recommended) | Indexed code context → fewer tokens, better tests |

Optional:

| Requirement | Why |
|-------------|-----|
| Jira credentials in `.env` | Comment + attach Excel to an issue |

### Step 1 — Go to the target project

```powershell
cd C:\path\to\your-project
```

You must be at the project root (where `README`, `package.json`, `pyproject.toml`,
`go.mod`, etc. usually live).

### Step 2 — Download the skill into Cursor skills folder

**Option A — Git clone (recommended)**

```powershell
New-Item -ItemType Directory -Force -Path .cursor\skills | Out-Null
git clone --depth 1 https://github.com/hungtv-leo/test-case-skill.git .cursor/skills/self-test-cases
```

macOS / Linux:

```bash
mkdir -p .cursor/skills
git clone --depth 1 https://github.com/hungtv-leo/test-case-skill.git .cursor/skills/self-test-cases
```

**Option B — ZIP (no nested `.git`)**

1. Download: https://github.com/hungtv-leo/test-case-skill/archive/refs/heads/main.zip
2. Extract the zip.
3. Rename the extracted folder to `self-test-cases`.
4. Move it so this file exists:

```text
your-project/.cursor/skills/self-test-cases/SKILL.md
```

### Step 3 — Confirm folder layout

After install you should have:

```text
your-project/
└── .cursor/
    └── skills/
        └── self-test-cases/
            ├── SKILL.md
            ├── README.md
            ├── reference.template.md
            ├── schemas/
            ├── scripts/
            ├── templates/
            └── workdir/
```

Check:

```powershell
Test-Path .cursor\skills\self-test-cases\SKILL.md
Get-ChildItem .cursor\skills\self-test-cases
```

### Step 4 — Install Python dependencies for skill scripts

Install with `--user` so packages go to your machine Python, **not** into the
project virtualenv / `requirements.txt` / `poetry.lock`.

```powershell
# Required: validate + Excel export
pip install --user -r .cursor\skills\self-test-cases\scripts\requirements.txt

# Optional: only if you will use Jira notify
pip install --user -r .cursor\skills\self-test-cases\scripts\requirements-jira.txt
```

Core packages: `openpyxl`, `jsonschema`  
Optional Jira packages: `requests`, `python-dotenv`

### Step 5 — Install CodeGraph (recommended)

This skill works best with [CodeGraph](https://github.com/colbymchenry/codegraph):
a local code knowledge graph for Cursor. Install once on your machine, then
initialize each project.

Official docs: https://colbymchenry.github.io/codegraph/getting-started/installation/

#### 5.1 Install the CodeGraph CLI (once per machine)

**Windows (PowerShell):**

```powershell
irm https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.ps1 | iex
```

**macOS / Linux:**

```bash
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh
```

**Or via npm (any OS, if you already have Node):**

```bash
npm i -g @colbymchenry/codegraph
```

Open a **new terminal** so `codegraph` is on your `PATH`, then check:

```powershell
codegraph --version
```

#### 5.2 Wire CodeGraph into Cursor (once per machine)

```powershell
# Interactive (asks which agents to configure)
codegraph install

# Or non-interactive for Cursor only
codegraph install --target=cursor --yes
```

Shortcut (downloads + runs installer in one go):

```bash
npx @colbymchenry/codegraph
```

Then **restart Cursor** so the MCP server is loaded.

#### 5.3 Index the current project (once per project)

From the **target project root**:

```powershell
codegraph init
```

`codegraph init` creates `.codegraph/` and builds the graph.

If it says already initialized but the skill still reports
“only `.gitignore` present”, re-index:

```powershell
codegraph index
# or keep it fresh later:
codegraph sync
```

Verify:

```powershell
Get-ChildItem .codegraph -Force
codegraph status
```

You should see more than just `.gitignore` inside `.codegraph/`.

#### 5.4 Let the skill agent install CodeGraph for you

If CodeGraph is missing when you run `/self-test-cases`, the agent will ask
whether to install/index it for you. If you say yes, it can run the commands
above (CLI install may still need you to approve the shell command / open a new
terminal once).

Without CodeGraph, the skill still works — it falls back to reading related
files only (not the whole project).

### Step 6 — (Optional) Configure Jira

Create a `.env` file at the **project root** (not inside the skill folder):

```env
JIRA_BASE_URL=https://jira.company.com
JIRA_AUTH_MODE=bearer
JIRA_TOKEN=xxxxx
# JIRA_USER=you@company.com   # only when JIRA_AUTH_MODE=basic
```

```powershell
# Test Jira connection
python .cursor\skills\self-test-cases\scripts\jira_notify.py --check
```

Do **not** commit `.env`.

### Step 7 — (Recommended) Avoid committing the skill / sandbox by mistake

Add to the **project** `.gitignore`:

```gitignore
# Cursor skill installed locally
.cursor/skills/self-test-cases/

# CodeGraph local index (usually should not be committed)
.codegraph/

# If you keep reference.local.md elsewhere, ignore runtime outputs
**/.selftest_tmp/
**/results.json
**/.report.json
```

Runtime outputs already live under
`.cursor/skills/self-test-cases/workdir/` and are gitignored by the skill itself.

### Step 8 — Use the skill in Cursor

1. Open the **same project** in Cursor.
2. Start a new Agent chat.
3. Invoke:

```text
/self-test-cases Write tests for feature <requirement description>
```

Example:

```text
/self-test-cases Write tests for API create exam session location.
Include happy path, validation errors, and permission checks.
```

First run will:

1. Detect stack / framework
2. Create `reference.local.md`
3. Write tests + `cases.json` under `workdir/`
4. Self-test → `results.json`
5. Export Excel only if **100% pass**

### Step 9 — Update the skill later

```powershell
cd .cursor\skills\self-test-cases
git pull
pip install --user -r scripts\requirements.txt
```

Update CodeGraph CLI later (if needed):

```powershell
codegraph upgrade
# or: npm i -g @colbymchenry/codegraph@latest
```

---

## Where generated files go

Everything the skill creates stays inside the skill folder (not project root):

```text
.cursor/skills/self-test-cases/
├── reference.local.md                 # project cache (first run)
└── workdir/                           # all runtime artifacts
    ├── tests/<feature>/
    │   ├── test_*.py (or equiv.)
    │   └── cases.json
    ├── pytest.ini                     # only if needed
    ├── .report.json
    ├── results.json
    └── .selftest_tmp/
        └── handover_<feature>.xlsx
```

The skill must **not** create `tests/`, `pytest.ini`, `results.json`, or
`.selftest_tmp/` at the project root.

---

## Usage tips

- Skill loads only when you type `/self-test-cases` (`disable-model-invocation: true`).
- Prefer CodeGraph indexed (`codegraph init` / `codegraph index`) for better context.
  See [CodeGraph](https://github.com/colbymchenry/codegraph).
- If CodeGraph is missing/empty, the skill can install it for you (after you confirm)
  or fall back to reading related files only.

---

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

---

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
│   ├── requirements.txt        # core deps only
│   └── requirements-jira.txt   # optional Jira deps
├── templates/
│   ├── cases.example.json      # sample case metadata (keyed by test id)
│   └── results.example.json    # sample results.json format
└── workdir/                    # runtime sandbox (gitignored except README)
    └── README.md
```

---

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

Values: `passed` | `failed` | `error` | `skipped`.

### Convert / validate (paths inside workdir)

```powershell
$WORKDIR = ".cursor\skills\self-test-cases\workdir"

python .cursor\skills\self-test-cases\scripts\convert_results.py `
  --framework pytest --input $WORKDIR\.report.json --output $WORKDIR\results.json

python .cursor\skills\self-test-cases\scripts\validate_test_cases.py `
  --cases $WORKDIR\tests\feature\cases.json --results $WORKDIR\results.json
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `SKILL.md` not found | Re-check path: `.cursor/skills/self-test-cases/SKILL.md` |
| `/self-test-cases` not listed in Cursor | Reload Cursor window; confirm skill folder path |
| `pip` installs into project venv | Use `pip install --user ...` or deactivate project venv first |
| CodeGraph "only .gitignore" / not indexed | Run `codegraph index` (or `codegraph init`), then restart Cursor |
| `codegraph` command not found | Re-run installer; open a **new** terminal; check `codegraph --version` |
| CodeGraph MCP not connected in Cursor | Run `codegraph install --target=cursor --yes`, restart Cursor |
| Files appear at project root | Pull latest skill; generated files must stay under `workdir/` |
| Old clone missing updates | `cd .cursor/skills/self-test-cases && git pull` |

---

## Notes

- Install **only** this skill into `.cursor/skills/self-test-cases/`.
- Do **not** mix skill Python packages into the app's dependency files.
- Do **not** place this skill under `~/.cursor/skills-cursor/` (reserved for Cursor).
- `reference.local.md` is project-specific; do not commit it back into the skill repo.
- Do not commit `.env`, Excel handover files, or `workdir/` runtime outputs.
