---
name: self-test-cases
description: >-
  Từ code tính năng mới: tìm case có thể xảy ra (kể cả case “không thể ngờ tới”)
  mà code chưa check, tự verify các nhánh đã có, bàn giao Excel cho tester
  (sheet Đã verify + Gap - Rủi ro), tùy chọn comment Jira. Không phải self-test
  chất lượng code/coverage %. Portable (Python/Node/Go/Java/Remix/...). Use when
  user asks to write test cases, self-test a feature, hunt unchecked scenarios,
  verify a task, or export handover for tester / bàn giao tester. Ưu tiên codegraph.
disable-model-invocation: true
---

# Self-test cases (gap-hunt + bàn giao tester)

## Sứ mệnh (ĐỌC TRƯỚC)

Skill này **KHÔNG** nhằm:
- Đo coverage %, style, refactor, “viết unit test cho có”.
- Chỉ assert đúng behavior hiện tại rồi đóng băng bug.

Skill này **NHẰM**:
1. Đọc **code tính năng mới** (+ yêu cầu nếu có).
2. Suy ra các tình huống **thật sự có thể xảy ra** (user / data / state / race…).
3. Phân loại:
   - `verified` — code **đã** có nhánh xử lý → viết test tự động, **phải pass**.
   - `gap` / `exploratory` / `needs-product-decision` — case có thể xảy ra nhưng
     **code chưa check / chưa rõ** → ghi nhận cho **tester + dev**, kèm bằng chứng code.
4. Bàn giao Excel **2 sheet**: Đã verify + Gap - Rủi ro.

> Gap **không** chặn bàn giao. Chỉ case `verified` fail mới chặn Excel/Jira.

## Artifact map (BẮT BUỘC)

`SKILL_ROOT` = `.cursor/skills/self-test-cases`

| Artifact | Path BẮT BUỘC | CẤM ghi ở |
|----------|---------------|-----------|
| `reference.local.md` | `$SKILL_ROOT/reference.local.md` | gốc project |
| Test files | `$SKILL_ROOT/workdir/tests/<feature>/` | `tests/` project |
| `cases.json` | `$SKILL_ROOT/workdir/tests/<feature>/cases.json` | ngoài workdir |
| Report / `results.json` | `$SKILL_ROOT/workdir/` | gốc project |
| Excel / `gaps.json` | `$SKILL_ROOT/workdir/.selftest_tmp/` | gốc project |

```
.cursor/skills/self-test-cases/
├── SKILL.md
├── reference.local.md          # cache project (KHÔNG commit)
└── workdir/
    ├── tests/<feature>/
    │   ├── test_*.py           # chỉ cho case verified (và gap nếu automate được)
    │   └── cases.json
    ├── .report.json
    ├── results.json            # chỉ bắt buộc cho verified
    └── .selftest_tmp/
        ├── handover_<feature>.xlsx
        └── gaps_<feature>.json
```

> **KHÔNG commit** `.cursor/skills/self-test-cases/`. Thêm vào `.gitignore` của project.

## 2 lớp case

| coverage | Ý nghĩa | Key trong cases.json | Có trong results.json? | Gate Excel |
|----------|---------|----------------------|------------------------|------------|
| `verified` | Code đã check; có test tự động | Test id framework (nodeid/fullName/…) | **Bắt buộc**, phải `passed` | Fail → **chặn** |
| `gap` | Có thể xảy ra; code chưa xử lý rõ | `gap:<case_id>` hoặc test id nếu đã viết test fail | Tuỳ chọn | **Không chặn** |
| `exploratory` | Cần tester khám phá trên môi trường thật | `gap:<case_id>` | Tuỳ chọn | Không chặn |
| `needs-product-decision` | Chưa rõ expected đúng/sai — hỏi PO/dev | `gap:<case_id>` | Tuỳ chọn | Không chặn |

Field bắt buộc mọi case: `case_id`, `description`, `precondition`, `steps`,
`expected`, `coverage`.

Field bắt buộc với gap/exploratory/needs-product-decision: `code_evidence`, `risk`.

Khuyến dùng: `category`, `priority` (`P0`–`P3`), `tester_note`.

`category`: `happy` | `validate` | `auth` | `state` | `race` | `boundary` |
`side-effect` | `dependency` | `other`.

## Checklist “case không thể ngờ tới” (BẮT BUỘC quét ở B2.5)

Sau khi đọc code, agent **phải** đi qua checklist; mỗi mục thiếu trong code →
tạo case `gap` (hoặc `needs-product-decision` nếu chưa rõ expected):

1. **Input bẩn**: null, `""`, khoảng trắng, sai type, thiếu field, field thừa,
   enum lạ, Unicode/emoji, độ dài max+1.
2. **Boundary**: 0, âm, max int, ngày hết hạn ±1s, timezone.
3. **State**: gọi 2 lần (idempotent?), session hết giữa chừng, soft-delete,
   data cũ sau update, thứ tự bước đảo.
4. **Auth/ACL**: thiếu token, hết hạn, đúng token sai role, IDOR (đổi id người khác).
5. **Luồng / race**: double-submit, 2 request song song, retry sau timeout.
6. **Phụ thuộc ngoài**: timeout, 5xx, payload lệch schema.
7. **Side-effect**: ghi DB một phần, gửi mail/notify 2 lần, cache stale.

**CẤM** chỉ liệt kê happy path + 1–2 validate rồi dừng.

## Workflow

```
- [ ] B0: Bootstrap → reference.local.md (lần đầu)
- [ ] B1: Đọc yêu cầu (nếu có) + xác định feature
- [ ] B2: Codegraph lấy code liên quan (không đọc cả project)
- [ ] B2.5: Gap hunt — checklist rủi ro + liệt kê verified vs gap
- [ ] B3: Viết test verified + cases.json (cả verified lẫn gap)
- [ ] B4: Chạy test verified → results.json
- [ ] B4b: Validate schema + alignment (verified bắt buộc có kết quả)
- [ ] B5: Verified fail → báo dev; Gap → báo riêng (không chặn bàn giao)
- [ ] B6: Verified đều pass → Excel 2 sheet + (tuỳ chọn) report_gaps.py
- [ ] B7: (Tuỳ chọn) Jira comment + đính kèm Excel
```

### B0: Bootstrap (chỉ lần đầu)

Nếu đã có `reference.local.md` → đọc rồi bỏ qua B0.
Nếu chưa: copy [reference.template.md](reference.template.md) → điền stack,
lệnh test, mock, kiến trúc. Cài:

```bash
pip install --user -r .cursor/skills/self-test-cases/scripts/requirements.txt
```

CodeGraph chưa sẵn sàng → hỏi user có muốn cài/index; đồng ý thì chạy installer
CodeGraph + `codegraph init`/`index`; từ chối → fallback đọc file liên quan.

### B1: Đọc yêu cầu

Xác định endpoint/module, nhánh mong muốn. Yêu cầu mơ hồ → HỎI trước.
Thiếu yêu cầu nhưng có code → vẫn làm được: lấy hành vi từ code + gap hunt.

### B2: Context (codegraph-first)

Query symbol liên quan. Không đọc cả project.

### B2.5: Gap hunt (QUAN TRỌNG)

1. Liệt kê những gì code **đang** validate/nhánh `if`/permission/lock.
2. Chạy checklist “không thể ngờ tới” ở trên.
3. Mỗi mục checklist mà code **không** xử lý → draft case `gap` với
   `code_evidence` (file/symbol/điều thiếu) + `risk` + `priority`.
4. Những nhánh code **đã** có → sẽ thành `verified` ở B3.
5. Không chắc expected đúng/sai → `needs-product-decision`, hỏi user/PO.

In tóm tắt cho user trước khi viết test hàng loạt:
`Verified dự kiến: N | Gap dự kiến: M (P0: …)`.

### B3: Viết test + cases.json

Sandbox bắt buộc dưới `workdir/` (xem artifact map). Chạy test từ **gốc project**.

**Verified:**
- Viết test framework của project, mock hạ tầng thật.
- Key = test id thật (pytest nodeid có tiền tố workdir…).
- `coverage: "verified"`.

**Gap:**
- Ưu tiên ghi `gap:<case_id>` trong `cases.json` **không bắt buộc** có file test.
- Nếu viết được test chứng minh thiếu xử lý (fail có chủ đích) → vẫn để
  `coverage: "gap"`; fail **không** chặn Excel.
- `steps`/`data`/`expected`/`tester_note` phải tester đọc là làm được (đủ
  method, URL, body; không `...`).

Pytest (từ gốc project):

```bash
WORKDIR=.cursor/skills/self-test-cases/workdir
pytest $WORKDIR/tests/<feature> --rootdir=. -o pythonpath=. \
  --json-report --json-report-file=$WORKDIR/.report.json
```

### B4 → results.json

Chỉ **bắt buộc** có kết quả cho mọi case `verified`. Convert bằng
`scripts/convert_results.py` vào `workdir/results.json`.

### B4b: Validate

```bash
python .cursor/skills/self-test-cases/scripts/validate_test_cases.py \
  --cases .cursor/skills/self-test-cases/workdir/tests/<feature>/cases.json \
  --results .cursor/skills/self-test-cases/workdir/results.json
```

(Gap thiếu trong results là OK.)

### B5: Báo cáo

- **Verified fail** → liệt kê case_id + lý do; **KHÔNG** Excel; quay B3/dev sửa code hoặc sửa test.
- **Gap** → liệt kê riêng cho tester/dev (“code chưa check”); **không** block B6.

```bash
python .cursor/skills/self-test-cases/scripts/report_gaps.py \
  --cases .cursor/skills/self-test-cases/workdir/tests/<feature>/cases.json \
  --results .cursor/skills/self-test-cases/workdir/results.json \
  --json-out .cursor/skills/self-test-cases/workdir/.selftest_tmp/gaps_<feature>.json
```

### B6: Excel bàn giao

Gate: mọi `verified` = `passed`. Gap không cần pass.

```bash
python .cursor/skills/self-test-cases/scripts/export_test_cases.py \
  --results .cursor/skills/self-test-cases/workdir/results.json \
  --cases .cursor/skills/self-test-cases/workdir/tests/<feature>/cases.json \
  --out .cursor/skills/self-test-cases/workdir/.selftest_tmp/handover_<feature>.xlsx
```

Excel có 2 sheet:
- **Đã verify** — case code đã xử lý, đã chạy test tự động và **pass**. Tester dùng làm checklist regression.
- **Gap - Rủi ro** — case **có thể xảy ra** nhưng code **chưa check** (hoặc chưa rõ expected). Không phải “fail test”; đây là danh sách rủi ro để tester kiểm tra tay + dev bổ sung xử lý. Kèm bằng chứng code, ghi chú tester, mức ưu tiên.

Cột **Phân loại** trên Excel ghi tiếng Việt có dấu (`Lỗ hổng`, `Khám phá`, `Chờ quyết định`). Trong `cases.json` vẫn dùng enum máy: `gap` / `exploratory` / `needs-product-decision`.

### B7: Jira (tuỳ chọn)

Cùng gate verified. Comment nêu số gap + danh sách mã case gap.

## Ma trận framework

| Nhóm | Framework | Adapter |
|------|-----------|---------|
| Python | pytest | `pytest` |
| Node | jest / vitest | `jest` / `vitest` |
| Remix | vitest + Playwright | `remix` |
| E2E | Playwright | `playwright` |
| Go | go test | `go` |
| Java | Spring Boot + JUnit | `spring-boot` / `junit` |

Mẫu: [templates/cases.example.json](templates/cases.example.json),
[templates/results.example.json](templates/results.example.json).

## Nguyên tắc

- Gap-hunt trước, automate sau — đừng chỉ mirror code hiện tại.
- Sandbox trong skill folder; không commit skill/workdir.
- Mock hạ tầng thật khi chạy verified.
- Excel/Jira chỉ khi mọi **verified** pass; gap vẫn nằm trong bàn giao.
- Ngôn ngữ case/Excel: tiếng Việt.
- Codegraph-first; validate schema trước khi export.
