# Hướng dẫn cài đặt và sử dụng (nội bộ)

Tài liệu này dành cho team: cách **cài đúng** skill `self-test-cases` vào project app, rồi **dùng đúng** trong Cursor.

Repo GitHub: https://github.com/hungtv-leo/test-case-skill

> Đây **không phải** app cần chạy server. Đây là **Cursor Agent Skill**: cài vào **project đích** (app cần test), mở Cursor tại project đó, gọi `/self-test-cases`.

README tiếng Anh (GitHub): [README.md](README.md)

---

## 1. Skill này làm gì / không làm gì

**Làm:**

1. Đọc code tính năng mới (và yêu cầu nếu có).
2. Săn case thật sự có thể xảy ra mà code **chưa check** (`gap` / `exploratory` / `needs-product-decision`).
3. Viết test tự động cho nhánh code **đã** xử lý (`verified`) — các case này **phải pass**.
4. Khi mọi case verified pass → xuất Excel bàn giao tester: sheet **Đã verify** + **Gap - Rủi ro**.
5. (Tùy chọn) comment kết quả + đính kèm Excel lên Jira.

**Không làm:**

- Đo coverage %, style, refactor.
- Chỉ assert đúng behavior hiện tại rồi “đóng băng bug”.
- Viết unit test cho có.

**Đối tượng:** dev cài skill vào **project app** của mình. Không chạy skill trên chính repo `self-test-cases` trừ khi đang maintain skill.

---

## 2. Điều kiện trước khi cài

Mọi lệnh bên dưới chạy tại **gốc project đích** (nơi có `package.json` / `pyproject.toml` / `go.mod` / `pom.xml`…), **không** phải trong repo skill.

| Bắt buộc | Để làm gì | Kiểm tra nhanh |
|----------|-----------|----------------|
| [Cursor](https://cursor.com) | Load skill từ `.cursor/skills/` | Mở được project trong Cursor |
| Git | Clone repo skill (maintainer) / một số máy cần Git | `git --version` |
| Python 3.10+ và `pip` | Chạy script export / validate / convert | `py -3 --version` |
| Mạng tới GitHub | Installer tải zip `hungtv-leo/test-case-skill` | Mở được github.com |
| PowerShell 5.1+ | Chạy `install.ps1` trên Windows | `$PSVersionTable.PSVersion` |

Khuyến nghị:

| Công cụ | Để làm gì |
|---------|-----------|
| [CodeGraph](https://github.com/colbymchenry/codegraph) | Index code → agent lấy đúng symbol, ít đọc lung tung |

Tùy chọn:

| Công cụ | Để làm gì |
|---------|-----------|
| File `.env` Jira ở **gốc project đích** | Comment + đính kèm Excel lên issue |

Windows: nếu `python` không nhận, dùng `py -3` / `py -3 -m pip`.

---

## 3. Cài đặt đúng (Windows — cách khuyến dùng)

Luồng đúng:

```text
Mở Cursor / terminal tại gốc project đích
  → cài runtime skill (install.ps1)
  → cài deps skill (xem Bước 3: có .venv thì KHÔNG dùng --user)
  → CodeGraph CLI + index project
  → Restart Cursor
  → Gọi /self-test-cases
```

### Bước 1 — Vào gốc project đích

```powershell
cd C:\path\to\your-app
```

Phải đứng đúng thư mục app cần test. **Không** chạy installer khi đang ở repo `self-test-cases` trừ khi bạn truyền `-ProjectRoot`.

### Bước 2 — Cài runtime skill

Cách khuyến dùng: installer chỉ copy file runtime (xem `install.manifest`). Không copy README, installer, `scripts/tests/`, `.git`.

```powershell
irm https://raw.githubusercontent.com/hungtv-leo/test-case-skill/main/install.ps1 | iex
```

Nếu PowerShell chặn script:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Rồi chạy lại lệnh `irm ... | iex`.

**Offline / đã clone repo skill trên máy:**

```powershell
# Chạy từ trong repo skill, trỏ sang app
.\install.ps1 -ProjectRoot C:\path\to\your-app
```

Hoặc cài vào thư mục hiện tại từ source local:

```powershell
.\install.ps1 -Source .
```

Cài lại = **xóa rồi copy mới** thư mục `.cursor/skills/self-test-cases/`. Artifact trong `workdir/` sẽ mất — copy Excel ra ngoài trước nếu cần giữ.

### Bước 3 — Cài Python deps của skill

Gói bắt buộc: `openpyxl`, `jsonschema`. **Không** thêm chúng vào `requirements.txt` / `poetry.lock` / `package.json` của app.

Nhìn prompt terminal: có `(.venv)` hay không.

**A. Prompt đang có `(.venv)` — cài vào venv, bỏ `--user`**

Đây là trường hợp project Python (vd. `cms-trang-nguyen-api`). Pip **từ chối** `--user` vì user site-packages không nhìn thấy trong venv:

```text
ERROR: Can not perform a '--user' install. User site-packages are not visible in this virtualenv.
```

Đừng `deactivate`. Chạy đúng:

```powershell
pip install -r .cursor\skills\self-test-cases\scripts\requirements.txt
```

Jira (nếu dùng):

```powershell
pip install -r .cursor\skills\self-test-cases\scripts\requirements-jira.txt
```

`.venv` đã gitignore — gói nằm local trên máy, không commit vào lockfile app. Agent sau này cũng dùng Python của venv nên **phải** cài vào đây, nếu không `export_test_cases.py` sẽ thiếu `openpyxl`.

**B. Không dùng venv — mới dùng `--user`**

```powershell
pip install --user -r .cursor\skills\self-test-cases\scripts\requirements.txt
```

Python 3.10+ chắc chắn:

```powershell
py -3 -m pip install --user -r .cursor\skills\self-test-cases\scripts\requirements.txt
```

> Chạy **test của app** thì dùng runner/venv của **app**, không dùng deps skill. Python + pytest cần thêm plugin JSON report:
>
> ```powershell
> pip install pytest pytest-json-report
> ```
>
> (cài trong venv của app, vì lệnh `pytest` chạy test app). Node/Go/Java: dùng tooling sẵn có của project.

### Bước 4 — CodeGraph (khuyến dùng)

Skill vẫn chạy thiếu CodeGraph (fallback: đọc file liên quan). Có index thì case tốt hơn, tốn ít token hơn.

**4.1 Cài CLI (một lần / máy)**

```powershell
irm https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.ps1 | iex
```

Hoặc nếu đã có Node:

```powershell
npm i -g @colbymchenry/codegraph
```

Mở **terminal mới**, kiểm tra:

```powershell
codegraph --version
```

**4.2 Gắn vào Cursor (một lần / máy)**

```powershell
codegraph install --target=cursor --yes
```

**4.3 Index project (một lần / project)** — vẫn đứng ở gốc project đích:

```powershell
codegraph init
```

Nếu báo đã init nhưng skill nói “chỉ có `.gitignore`”:

```powershell
codegraph index
```

Sau này làm tươi:

```powershell
codegraph sync
codegraph status
```

Trong `.codegraph/` phải có nhiều hơn mỗi file `.gitignore`.

Nếu lúc chạy `/self-test-cases` mà CodeGraph chưa sẵn, agent sẽ hỏi có muốn cài/index giúp không.

### Bước 5 — Kiểm tra layout sau cài

Phải có **đúng** cấu trúc runtime:

```text
your-app/
└── .cursor/
    └── skills/
        └── self-test-cases/
            ├── SKILL.md
            ├── reference.template.md
            ├── schemas/
            ├── scripts/          # adapters + CLI — KHÔNG có scripts/tests
            ├── templates/
            └── workdir/          # sandbox rỗng, agent sẽ ghi vào đây
```

```powershell
Test-Path .cursor\skills\self-test-cases\SKILL.md          # True
Test-Path .cursor\skills\self-test-cases\README.md         # False
Test-Path .cursor\skills\self-test-cases\install.ps1       # False
Test-Path .cursor\skills\self-test-cases\scripts\tests     # False
Get-ChildItem .cursor\skills\self-test-cases
```

Nếu `README.md` / `install.ps1` / `scripts\tests` hiện `True` → đã clone nhầm cả repo. Xóa thư mục skill rồi cài lại bằng installer.

### Bước 6 — Gitignore project đích

Thêm vào `.gitignore` của **app** (không phải của repo skill):

```gitignore
# Cursor skill (tooling local, không commit)
.cursor/skills/self-test-cases/

# CodeGraph index local
.codegraph/
```

**Không commit:** skill, `reference.local.md`, `workdir/`, Excel, `.env`.

### Bước 7 — Restart Cursor rồi dùng

1. Restart Cursor (để skill + CodeGraph MCP load).
2. Mở **đúng project đích**.
3. Chat Agent **mới**.
4. Gọi:

```text
/self-test-cases Write tests for feature <mô tả yêu cầu>
```

---

## 4. Những cách SAI cần tránh

| Sai | Đúng |
|-----|------|
| `git clone` cả repo vào `.cursor/skills/self-test-cases` khi dùng hàng ngày | Dùng `install.ps1` (chỉ runtime) |
| `pip install --user` khi prompt có `(.venv)` | Bỏ `--user`, cài vào venv đang bật; **không** ghi vào `requirements.txt` của app |
| Commit `.cursor/skills/self-test-cases/` / Excel / `.env` | Thêm gitignore như Bước 6 |
| Đặt skill vào `%USERPROFILE%\.cursor\skills-cursor\` | Path đúng: `project\.cursor\skills\self-test-cases\` |
| `cd .cursor\skills\self-test-cases` rồi `git pull` sau khi cài bằng installer | Thư mục đó **không có `.git`**. Cập nhật = chạy lại `install.ps1` |
| Để test / `results.json` / Excel ở gốc project | Mọi artifact nằm trong `workdir/` của skill |
| Chạy skill trên chính repo `self-test-cases` như thể đó là app | Cài skill **vào app** cần test |
| Gõ chat thường, không có `/self-test-cases` | Skill chỉ load khi gõ slash command |

Clone full repo chỉ dành cho **maintainer** (sửa adapter, chạy unit test skill).

---

## 5. Cách sử dụng đúng

Skill **chỉ load** khi gõ `/self-test-cases` (`disable-model-invocation: true`). Không gõ slash thì Cursor không gắn workflow này.

### Prompt

```text
/self-test-cases Write tests for feature <mô tả yêu cầu>
```

Ví dụ:

```text
/self-test-cases Write tests for API create exam session location.
Include happy path, validation errors, and permission checks.
```

Càng rõ endpoint / module / nhánh mong muốn thì càng ít hỏi lại. Thiếu yêu cầu nhưng có code → skill vẫn làm được (lấy hành vi từ code + gap hunt).

### Agent sẽ làm gì

```text
B0   Bootstrap (lần đầu) → reference.local.md
B1   Đọc yêu cầu + xác định feature
B2   CodeGraph lấy code liên quan (không đọc cả project)
B2.5 Gap hunt — checklist rủi ro; phân verified vs gap
B3   Viết test verified + cases.json (cả verified lẫn gap)
B4   Chạy test verified → results.json
B4b  Validate schema + khớp test id
B5   Verified fail → báo dev, KHÔNG Excel
     Gap → báo riêng, không chặn bàn giao
B6   Mọi verified pass → Excel 2 sheet
B7   (Tùy chọn) Jira comment + đính kèm Excel
```

Lần đầu: detect stack, copy `reference.template.md` → `reference.local.md`, điền lệnh test / mock / kiến trúc của **app**. Các lần sau đọc cache này, không dò lại cả project.

Trước khi viết test hàng loạt, agent in tóm tắt: `Verified dự kiến: N | Gap dự kiến: M (P0: …)`.

### Hai lớp case

| `coverage` | Ý nghĩa | Có trong `results.json`? | Chặn Excel / Jira? |
|------------|---------|--------------------------|--------------------|
| `verified` | Code đã check; có test tự động | Bắt buộc, phải `passed` | Fail → **chặn** |
| `gap` | Có thể xảy ra; code chưa xử lý rõ | Tùy chọn | Không chặn |
| `exploratory` | Tester khám phá trên môi trường thật | Tùy chọn | Không chặn |
| `needs-product-decision` | Chưa rõ expected — hỏi PO/dev | Tùy chọn | Không chặn |

Gap **không** phải “test fail”. Đó là danh sách rủi ro để tester check tay + dev bổ sung xử lý.

Mọi case cần: `case_id`, `description`, `precondition`, `steps`, `expected`, `coverage`.

Gap / exploratory / needs-product-decision thêm: `code_evidence`, `risk`.

Khuyến dùng: `category`, `priority` (`P0`–`P3`), `tester_note`.

`category`: `happy` | `validate` | `auth` | `state` | `race` | `boundary` | `side-effect` | `dependency` | `other`.

**Ngôn ngữ:** mô tả case và Excel = **tiếng Việt**. Enum trong JSON giữ tiếng Anh (`verified`, `gap`, …).

`steps` / `data` / `expected` / `tester_note` phải tester đọc là làm được: đủ method, URL, body — không viết `...`.

### Checklist gap (agent bắt buộc quét)

Mỗi mục mà code **không** xử lý → case `gap` (hoặc `needs-product-decision` nếu chưa rõ expected):

1. **Input bẩn:** null, `""`, khoảng trắng, sai type, thiếu/thừa field, enum lạ, Unicode, độ dài max+1.
2. **Boundary:** 0, âm, max int, ngày hết hạn ±1s, timezone.
3. **State:** gọi 2 lần, session hết, soft-delete, data cũ sau update, đảo thứ tự bước.
4. **Auth/ACL:** thiếu token, hết hạn, đúng token sai role, IDOR.
5. **Luồng / race:** double-submit, 2 request song song, retry sau timeout.
6. **Phụ thuộc ngoài:** timeout, 5xx, payload lệch schema.
7. **Side-effect:** ghi DB một phần, notify 2 lần, cache stale.

Cấm chỉ liệt kê happy path + 1–2 validate rồi dừng.

### Artifact — path bắt buộc

`SKILL_ROOT` = `.cursor/skills/self-test-cases`

```text
.cursor/skills/self-test-cases/
├── SKILL.md
├── reference.local.md          # cache project, KHÔNG commit
└── workdir/
    ├── tests/<feature>/
    │   ├── test_*.py           # (hoặc file tương đương framework app)
    │   └── cases.json
    ├── pytest.ini              # chỉ khi cần, KHÔNG ở gốc app
    ├── .report.json
    ├── results.json            # bắt buộc cho mọi verified
    └── .selftest_tmp/
        ├── handover_<feature>.xlsx
        └── gaps_<feature>.json
```

| Artifact | Path bắt buộc | Cấm ghi ở |
|----------|---------------|-----------|
| `reference.local.md` | `$SKILL_ROOT/reference.local.md` | gốc project |
| Test files | `$SKILL_ROOT/workdir/tests/<feature>/` | `tests/` của app |
| `cases.json` | `$SKILL_ROOT/workdir/tests/<feature>/cases.json` | ngoài workdir |
| Report / `results.json` | `$SKILL_ROOT/workdir/` | gốc project |
| Excel / `gaps.json` | `$SKILL_ROOT/workdir/.selftest_tmp/` | gốc project |

Test **chạy từ gốc project đích**, nhưng file test nằm trong sandbox skill. Pytest (ví dụ):

```powershell
$WORKDIR = ".cursor\skills\self-test-cases\workdir"
pytest $WORKDIR\tests\<feature> --rootdir=. -o pythonpath=. `
  --json-report --json-report-file=$WORKDIR\.report.json
```

Nodeid pytest sẽ có tiền tố `.cursor/skills/self-test-cases/workdir/...` — dùng **đúng** nodeid đó làm key trong `cases.json`.

### Excel bàn giao

Gate: mọi `verified` = `passed`. Gap không cần pass.

- **Đã verify** — code đã xử lý, test tự động đã pass. Tester dùng làm checklist regression.
- **Gap - Rủi ro** — case có thể xảy ra nhưng code chưa check (hoặc chưa rõ expected). Cột **Phân loại** tiếng Việt: `Lỗ hổng` / `Khám phá` / `Chờ quyết định`.

File: `workdir/.selftest_tmp/handover_<feature>.xlsx`.

### Framework được hỗ trợ (core)

| Nhóm | Framework | Adapter |
|------|-----------|---------|
| Python | pytest | `pytest` |
| Node | jest / vitest | `jest` / `vitest` |
| Remix | vitest + Playwright | `remix` (`--mode unit` hoặc `--mode e2e`) |
| E2E | Playwright | `playwright` |
| Go | go test | `go` |
| Java | Spring Boot + JUnit | `spring-boot` / `junit` |

Framework khác: tự tổng hợp `results.json` theo `schemas/results.schema.json`, hoặc thêm adapter (maintainer).

### Script tay (khi cần, từ gốc project đích)

```powershell
$SKILL = ".cursor\skills\self-test-cases"
$WORKDIR = "$SKILL\workdir"

python $SKILL\scripts\convert_results.py `
  --framework pytest --input $WORKDIR\.report.json --output $WORKDIR\results.json

python $SKILL\scripts\validate_test_cases.py `
  --cases $WORKDIR\tests\<feature>\cases.json --results $WORKDIR\results.json

python $SKILL\scripts\report_gaps.py `
  --cases $WORKDIR\tests\<feature>\cases.json `
  --results $WORKDIR\results.json `
  --json-out $WORKDIR\.selftest_tmp\gaps_<feature>.json

python $SKILL\scripts\export_test_cases.py `
  --results $WORKDIR\results.json `
  --cases $WORKDIR\tests\<feature>\cases.json `
  --out $WORKDIR\.selftest_tmp\handover_<feature>.xlsx
```

Exit code export: `0` = xuất được; `2` = còn verified fail (không xuất Excel); `3` = lỗi input.

---

## 6. Jira (tùy chọn)

Tạo `.env` ở **gốc project đích** (không trong thư mục skill), **không commit**.

**Jira Server / Data Center (PAT):**

```env
JIRA_BASE_URL=https://jira.congty.com
JIRA_AUTH_MODE=bearer
JIRA_TOKEN=xxxxx
```

**Jira Cloud (email + API token):**

```env
JIRA_BASE_URL=https://xxx.atlassian.net
JIRA_AUTH_MODE=basic
JIRA_USER=you@company.com
JIRA_TOKEN=xxxxx
```

Kiểm tra kết nối:

```powershell
python .cursor\skills\self-test-cases\scripts\jira_notify.py --check
```

Comment + đính kèm (cùng gate: mọi verified phải pass):

```powershell
python .cursor\skills\self-test-cases\scripts\jira_notify.py `
  --issue TNV-123 `
  --results .cursor\skills\self-test-cases\workdir\results.json `
  --cases .cursor\skills\self-test-cases\workdir\tests\<feature>\cases.json `
  --xlsx .cursor\skills\self-test-cases\workdir\.selftest_tmp\handover_<feature>.xlsx `
  --feature <ten-tinh-nang>
```

Cần cài `requirements-jira.txt` trước (`requests`, `python-dotenv`).

---

## 7. Cập nhật skill

Bản cài bằng installer **không có `.git`**. Đừng `git pull` trong `.cursor/skills/self-test-cases`.

Đứng ở gốc project đích, chạy lại:

```powershell
irm https://raw.githubusercontent.com/hungtv-leo/test-case-skill/main/install.ps1 | iex
# Có (.venv): bỏ --user. Không venv: thêm --user.
pip install -r .cursor\skills\self-test-cases\scripts\requirements.txt
```

Installer **xóa rồi cài lại** thư mục skill → `workdir/` bị mất. Copy Excel ra ngoài trước nếu cần giữ.

Cập nhật CodeGraph CLI (khi cần):

```powershell
codegraph upgrade
```

---

## 8. Troubleshooting

| Vấn đề | Cách xử |
|--------|---------|
| `SKILL.md` không thấy | Đứng đúng gốc app; `Test-Path .cursor\skills\self-test-cases\SKILL.md` |
| `/self-test-cases` không có trong Cursor | Restart / Reload Window; đúng path `.cursor/skills/self-test-cases/SKILL.md`; gõ đúng slash command |
| `irm \| iex` bị chặn | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `python` / `pip` không nhận, hoặc sai version | `py -3 --version` phải ≥ 3.10; không venv thì `py -3 -m pip install --user ...` |
| `Can not perform a '--user' install` | Prompt đang `(.venv)` → bỏ `--user`: `pip install -r ...\scripts\requirements.txt` |
| `codegraph` không có lệnh | Chạy lại installer CodeGraph; **mở terminal mới**; `codegraph --version` |
| CodeGraph “chỉ `.gitignore`” / chưa index | `codegraph index` (hoặc `codegraph init`) tại gốc app |
| CodeGraph MCP chưa nối trong Cursor | `codegraph install --target=cursor --yes`, restart Cursor |
| File test / Excel / `results.json` nằm ở gốc app | Kéo bản skill mới; artifact phải trong `workdir/` |
| Excel không ra | Còn case `verified` fail/error → sửa code hoặc test, chạy lại. Gap không chặn nhưng verified fail thì chặn |
| Jira 401 | Server/DC: `bearer` + PAT. Cloud: `basic` + `JIRA_USER` (email) + API token |
| Cài xong vẫn thấy `README.md` / `scripts\tests` trong skill | Đã clone nhầm cả repo — xóa folder skill, cài lại bằng installer |

---

## 9. Phụ lục

### macOS / Linux

Tại gốc project đích:

```bash
curl -fsSL https://raw.githubusercontent.com/hungtv-leo/test-case-skill/main/install.sh | bash
# Có (.venv): bỏ --user. Không venv: thêm --user.
pip install -r .cursor/skills/self-test-cases/scripts/requirements.txt
```

Từ checkout local:

```bash
./install.sh --source /path/to/skill-repo --project /path/to/your-app
```

Cần `curl` và `unzip`. CodeGraph:

```bash
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh
codegraph install --target=cursor --yes
codegraph init
```

### Maintainer (sửa skill, không phải dùng hàng ngày)

```powershell
git clone https://github.com/hungtv-leo/test-case-skill.git
cd test-case-skill
pip install -r scripts/requirements.txt
pytest scripts/tests
```

Thêm script/adapter mà **end user cần** → phải ghi path vào `install.manifest`, nếu không installer sẽ không copy sang project đích.
