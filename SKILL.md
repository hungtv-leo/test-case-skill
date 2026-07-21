---
name: self-test-cases
description: >-
  Đọc yêu cầu tính năng, viết test-case tự động theo test framework của project,
  tự self-test, báo lỗi cho dev nếu còn case fail/chưa hoàn thiện, và xuất file
  Excel bàn giao cho tester khi tất cả case pass; tùy chọn comment kết quả +
  đính kèm Excel lên Jira. Portable - dùng được cho mọi project (Python/Node/Go/
  Java/Remix/...). Use when the user asks to write test cases, self-test a feature,
  verify a task, or export test cases for handover / bàn giao tester. Ưu tiên
  dùng codegraph để lấy context liên quan, giảm token.
disable-model-invocation: true
---

# Self-test cases (portable)

Hỗ trợ dev trên MỌI project: đọc yêu cầu → viết test-case (dùng đúng framework
của project) → tự self-test → báo lỗi hoặc xuất Excel bàn giao → (tùy chọn)
comment lên Jira. Mục tiêu MINIMIZE token: ưu tiên codegraph, và cache thông tin
project vào `reference.local.md` để không phải dò lại mỗi lần.

## Portable hoạt động thế nào

Skill này KHÔNG gắn cứng vào framework nào. Có 2 lớp:
- **Lớp bất biến** (có sẵn trong skill): workflow, schema `cases.json`/`results.json`,
  script convert/validate/export/Jira.
- **Lớp theo project** (agent tự sinh lần đầu): framework test, lệnh chạy test,
  cách mock, kiến trúc → ghi vào `reference.local.md` (thuộc project, không sửa
  file gốc của skill).

Điểm nối 2 lớp: agent chạy test bằng framework của project, convert kết quả về
`results.json` theo ĐỊNH DẠNG CHUẨN (dùng `convert_results.py` nếu cần). Script
export/Jira chỉ đọc `results.json` + `cases.json` nên dùng được cho mọi ngôn ngữ.

## Ma trận hỗ trợ framework (core)

| Nhóm | Framework | Adapter | Ghi chú |
|------|-----------|---------|---------|
| Python | pytest | `pytest` | pytest-json-report |
| Node | jest / vitest | `jest` / `vitest` | JSON reporter |
| Remix | vitest + Playwright | `remix` | `--mode unit` hoặc `--mode e2e` |
| E2E | Playwright | `playwright` | JSON report |
| Go | go test | `go` | `go test -json` |
| Java | Spring Boot + JUnit | `spring-boot` | JUnit XML Surefire/Gradle |

Mẫu format: [templates/cases.example.json](templates/cases.example.json),
[templates/results.example.json](templates/results.example.json).

## Workflow

Copy checklist này và cập nhật khi làm:

```
- [ ] B0: Bootstrap - detect stack, viết reference.local.md (chỉ lần đầu)
- [ ] B1: Đọc yêu cầu dev paste
- [ ] B2: Dùng codegraph lấy code liên quan (KHÔNG đọc cả project)
- [ ] B3: Viết test-case + cases.json (khóa theo test id)
- [ ] B4: Chạy test (self-test) -> convert/tao results.json chuẩn
- [ ] B4b: Validate cases.json + results.json (khuyến dùng)
- [ ] B5: Nếu còn fail/chưa hoàn thiện -> báo dev sửa, quay lại B3
- [ ] B6: Nếu tất cả pass -> xuất Excel bàn giao
- [ ] B7: (Tùy chọn) Comment kết quả + đính kèm Excel lên Jira
```

### B0: Bootstrap (chỉ lần đầu mỗi project)

Nếu đã có `.cursor/skills/self-test-cases/reference.local.md` → đọc nó rồi bỏ qua B0.

Nếu chưa có, hãy detect và GHI vào `reference.local.md` (copy từ
[reference.template.md](reference.template.md) rồi điền):
- Ngôn ngữ + test framework (pytest / jest / vitest / go test / JUnit / Playwright / Remix...).
- Lệnh chạy test + cách xuất report và convert sang `results.json`.
- Cách khởi tạo app/server để test (app factory, TestClient, supertest, MockMvc...).
- Kiến trúc tầng: router/controller → service → repository → DB client.
- Auth/middleware và cách override/mock trong test.
- Các kết nối ngoài (SQL/Mongo/Redis/HTTP) và cách mock để KHÔNG chạm thật.
- Thư mục test chuẩn + file config/fixture có sẵn.

Cài dependency cho script (chỉ cần lần đầu):

```bash
pip install -r .cursor/skills/self-test-cases/scripts/requirements.txt
```

Nếu KHÔNG có thư mục `.codegraph`: báo dev chạy `codegraph init` ở thư mục gốc
rồi mở session mới. KHÔNG tự chạy giúp dev. Nếu dev chưa kịp setup, được phép
fallback đọc trực tiếp file liên quan (không đọc cả project).

### B1: Đọc yêu cầu

Dev paste mô tả tính năng. Xác định: endpoint/service/module liên quan; các nhánh
logic (happy path, validate lỗi, phân quyền, edge case); kết quả mong đợi từng
nhánh. Yêu cầu mơ hồ → HỎI dev trước khi viết.

### B2: Dùng codegraph lấy context (ưu tiên)

Query symbol liên quan (service/repository/router/model) thay vì đọc cả project.
Không có `.codegraph` → báo dev `codegraph init`. Chỉ đọc file trực tiếp khi
codegraph không đủ context.

### B3: Viết test-case

- Đặt test trong thư mục test chuẩn của project theo `<feature>` (xem
  `reference.local.md`).
- Viết test theo đúng framework + pattern mock trong `reference.local.md`. Mỗi
  test PHẢI mock, KHÔNG chạm DB/hạ tầng thật. Bao phủ đầy đủ nhánh: happy path +
  lỗi validate + phân quyền + edge case.
- Song song, tạo `cases.json` mô tả metadata từng case, KHÓA theo **test id**
  (nodeid pytest / fullName vitest / package::Test go / class::method JUnit...).
  Schema: [schemas/cases.schema.json](schemas/cases.schema.json). Mẫu:
  [templates/cases.example.json](templates/cases.example.json).

`cases.json` khóa theo test id, mỗi case gồm: `case_id`, `description`,
`precondition`, `steps` (list), `data`, `expected`.

QUAN TRỌNG - `steps`/`data`/`expected` phải TESTER-FRIENDLY (người test đọc là làm
được ngay):
- Viết ĐẦY ĐỦ đường dẫn endpoint, method và body. KHÔNG dùng `...` để rút gọn.
- Nếu dùng ID ví dụ (vd `cfg-1`), chú thích rõ đó là gì + cách thay bằng giá trị thật.
- `expected`: nếu trả HTTP lỗi thì ghi rõ status code + nội dung message thật.

### B4: Self-test → results.json chuẩn

Chạy test bằng lệnh trong `reference.local.md`, rồi tạo `results.json` theo ĐỊNH
DẠNG CHUẨN: map test id → kết quả. Schema:
[schemas/results.schema.json](schemas/results.schema.json).

```json
{
  "<test id 1>": "passed",
  "<test id 2>": "failed"
}
```

Giá trị hợp lệ: `passed` | `failed` | `error` | `skipped`.

**Convert từ report framework** (khuyến dùng):

```bash
# Python + pytest
pytest --json-report --json-report-file=.report.json tests/<feature>
python .cursor/skills/self-test-cases/scripts/convert_results.py \
  --framework pytest --input .report.json --output results.json

# Vitest / Jest
npx vitest run <feature> --reporter=json --outputFile=.vitest-report.json
python .cursor/skills/self-test-cases/scripts/convert_results.py \
  --framework vitest --input .vitest-report.json --output results.json

# Remix unit
python .cursor/skills/self-test-cases/scripts/convert_results.py \
  --framework remix --mode unit --input .vitest-report.json --output results.json

# Remix E2E / Playwright
python .cursor/skills/self-test-cases/scripts/convert_results.py \
  --framework remix --mode e2e --input playwright-report.json --output results.json

# Go
go test ./<pkg>/... -json > .go-report.jsonl
python .cursor/skills/self-test-cases/scripts/convert_results.py \
  --framework go --input .go-report.jsonl --output results.json

# Spring Boot + JUnit
python .cursor/skills/self-test-cases/scripts/convert_results.py \
  --framework spring-boot --input target/surefire-reports/TEST-*.xml --output results.json
```

### B4b: Validate (khuyến dùng)

```bash
python .cursor/skills/self-test-cases/scripts/validate_test_cases.py \
  --cases <path>/cases.json --results results.json
```

### B5: Nếu còn lỗi → báo dev

Nếu bất kỳ case fail/error, HOẶC test chưa bao phủ hết nhánh:
- Liệt kê từng case lỗi: test id + case_id + lý do (assert nào, exception gì).
- Bug code → mô tả rõ để dev sửa. Test thiếu case → bổ sung.
- KHÔNG xuất Excel. Quay lại B3 đến khi tất cả pass.

### B6: Xuất Excel bàn giao (chỉ khi tất cả pass)

Xuất ra file TẠM (KHÔNG lưu trong repo), vì file bàn giao sẽ đính kèm lên Jira ở
B7 rồi xóa.

```bash
python .cursor/skills/self-test-cases/scripts/export_test_cases.py \
  --results results.json \
  --cases <đường-dẫn>/cases.json \
  --out .selftest_tmp/handover_<feature>.xlsx
```

Script tự chặn (exit code 2) nếu còn case chưa pass → không tạo file. File Excel
có cột tiếng Việt: `Mã case`, `Mô tả`, `Điều kiện tiên đề`, `Các bước`,
`Dữ liệu`, `Kết quả mong đợi`, `Kết quả thực tế`, `Trạng thái`.

### B7: (Tùy chọn) Comment kết quả lên Jira

Chỉ chạy khi dev cung cấp issue key và đã cấu hình credentials Jira trong `.env`.
Script tự chặn nếu còn case fail (exit 2).

Env cần có (KHÔNG hardcode, KHÔNG commit): `JIRA_BASE_URL`, `JIRA_AUTH_MODE`
(`bearer` cho PAT Server/DC, `basic` cho Cloud/user-pass), `JIRA_TOKEN`, và
`JIRA_USER` (chỉ khi mode `basic`).

```bash
# Kiểm tra kết nối + nhận diện loại Jira:
python .cursor/skills/self-test-cases/scripts/jira_notify.py --check

# Comment + đính kèm Excel:
python .cursor/skills/self-test-cases/scripts/jira_notify.py \
  --issue <ISSUE_KEY> \
  --results results.json \
  --cases <đường-dẫn>/cases.json \
  --xlsx .selftest_tmp/handover_<feature>.xlsx \
  --feature <feature>
```

Sau khi đính kèm thành công lên Jira, XÓA file tạm và thư mục `.selftest_tmp/`.

## Nguyên tắc

- Portable: không hardcode framework/path; chi tiết project nằm trong `reference.local.md`.
- Codegraph-first, đọc file là phương án cuối → giảm token.
- Test không chạm DB/hạ tầng thật (luôn mock).
- Excel chỉ xuất khi 100% pass (gate cứng).
- Ngôn ngữ case/Excel: tiếng Việt.
- Không commit file `.xlsx` / `.env` / credentials.
- Validate `cases.json` và `results.json` theo schema trước khi export.
