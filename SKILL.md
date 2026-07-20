---
name: self-test-cases
description: >-
  Doc yeu cau tinh nang, viet test-case tu dong theo test framework cua project,
  tu self-test, bao loi cho dev neu con case fail/chua hoan thien, va xuat file
  Excel ban giao cho tester khi tat ca case pass; tuy chon comment ket qua +
  dinh kem Excel len Jira. Portable - dung duoc cho moi project (Python/Node/Go/
  Java/...). Use when the user asks to write test cases, self-test a feature,
  verify a task, or export test cases for handover / ban giao tester. Uu tien
  dung codegraph de lay context lien quan, giam token.
disable-model-invocation: true
---

# Self-test cases (portable)

Ho tro dev tren MOI project: doc yeu cau -> viet test-case (dung dung framework
cua project) -> tu self-test -> bao loi hoac xuat Excel ban giao -> (tuy chon)
comment len Jira. Muc tieu MINIMIZE token: uu tien codegraph, va cache thong tin
project vao `reference.local.md` de khong phai do lai moi lan.

## Portable hoat dong the nao

Skill nay KHONG gan cung vao framework nao. Co 2 lop:
- **Lop bat bien** (co san trong skill): workflow, schema `cases.json`, dinh dang
  `results.json` chuan, script xuat Excel va Jira.
- **Lop theo project** (agent tu sinh lan dau): framework test, lenh chay test,
  cach mock, kien truc -> ghi vao `reference.local.md` (thuoc project, khong sua
  file goc cua skill).

Diem noi 2 lop: agent chay test bang framework cua project, roi tao file
`results.json` theo DINH DANG CHUAN. Script chi doc `results.json` + `cases.json`
nen dung duoc cho moi ngon ngu.

## Workflow

Copy checklist nay va cap nhat khi lam:

```
- [ ] B0: Bootstrap - detect stack, viet reference.local.md (chi lan dau)
- [ ] B1: Doc yeu cau dev paste
- [ ] B2: Dung codegraph lay code lien quan (KHONG doc ca project)
- [ ] B3: Viet test-case + cases.json (khoa theo test id)
- [ ] B4: Chay test (self-test) -> tao results.json chuan
- [ ] B5: Neu con fail/chua hoan thien -> bao dev sua, quay lai B3
- [ ] B6: Neu tat ca pass -> xuat Excel ban giao
- [ ] B7: (Tuy chon) Comment ket qua + dinh kem Excel len Jira
```

### B0: Bootstrap (chi lan dau moi project)

Neu da co `.cursor/skills/self-test-cases/reference.local.md` -> doc no roi bo qua B0.

Neu chua co, hay detect va GHI vao `reference.local.md` (copy tu
[reference.template.md](reference.template.md) roi dien):
- Ngon ngu + test framework (pytest / jest / vitest / go test / junit / ...).
- Lenh chay test + cach xuat report may doc duoc.
- Cach khoi tao app/server de test (app factory, TestClient, supertest, ...).
- Kien truc tang: router/controller -> service -> repository -> DB client.
- Auth/middleware va cach override/mock trong test.
- Cac ket noi ngoai (SQL/Mongo/Redis/HTTP) va cach mock de KHONG cham that.
- Thu muc test chuan + file config/fixture co san.

Cai dependency cho script (chi can lan dau):

```bash
pip install -r .cursor/skills/self-test-cases/scripts/requirements.txt
```

Neu KHONG co thu muc `.codegraph`: bao dev chay `codegraph init` o thu muc goc
roi mo session moi. KHONG tu chay giup dev.

### B1: Doc yeu cau

Dev paste mo ta tinh nang. Xac dinh: endpoint/service/module lien quan; cac nhanh
logic (happy path, validate loi, phan quyen, edge case); ket qua mong doi tung
nhanh. Yeu cau mo ho -> HOI dev truoc khi viet.

### B2: Dung codegraph lay context (bat buoc, uu tien)

Query symbol lien quan (service/repository/router/model) thay vi doc ca project.
Khong co `.codegraph` -> bao dev `codegraph init`. Chi doc file truc tiep khi
codegraph khong du context.

### B3: Viet test-case

- Dat test trong thu muc test chuan cua project theo `<feature>` (xem
  `reference.local.md`).
- Viet test theo dung framework + pattern mock trong `reference.local.md`. Moi
  test PHAI mock, KHONG cham DB/ha tang that. Bao phu day du nhanh: happy path +
  loi validate + phan quyen + edge case.
- Song song, tao `cases.json` mo ta metadata tung case, KHOA theo **test id**
  (nodeid pytest / full test name jest / package::Test go...). Mau:
  [templates/cases.example.json](templates/cases.example.json).

`cases.json` khoa theo test id, moi case gom: `case_id`, `description`,
`precondition`, `steps` (list), `data`, `expected`.

QUAN TRONG - `steps`/`data`/`expected` phai TESTER-FRIENDLY (nguoi test doc la lam
duoc ngay):
- Viet DAY DU duong dan endpoint, method va body. KHONG dung `...` de rut gon.
- Neu dung ID vi du (vd `cfg-1`), chu thich ro do la gi + cach thay bang gia tri that.
- `expected`: neu tra HTTP loi thi ghi ro status code + noi dung message that.

### B4: Self-test -> results.json chuan

Chay test bang lenh trong `reference.local.md`, roi tao `results.json` theo DINH
DANG CHUAN: map test id -> ket qua.

```json
{
  "<test id 1>": "passed",
  "<test id 2>": "failed"
}
```

Gia tri hop le: `passed` | `failed` | `error` | `skipped`. (Cac bien the
`pass`/`ok`/`success`/`true` se duoc chuan hoa thanh `passed`.)

Neu project la Python + pytest: co the chay
`pytest --json-report --json-report-file=.report.json <thu-muc-test>` va truyen
thang `.report.json` cho script (script tu hieu format pytest-json-report). Cac
framework khac: tu tong hop `results.json` tu output test.

### B5: Neu con loi -> bao dev

Neu bat ky case fail/error, HOAC test chua bao phu het nhanh:
- Liet ke tung case loi: test id + case_id + ly do (assert nao, exception gi).
- Bug code -> mo ta ro de dev sua. Test thieu case -> bo sung.
- KHONG xuat Excel. Quay lai B3 den khi tat ca pass.

### B6: Xuat Excel ban giao (chi khi tat ca pass)

Xuat ra file TAM (KHONG luu trong repo), vi file ban giao se dinh kem len Jira o
B7 roi xoa.

```bash
python .cursor/skills/self-test-cases/scripts/export_test_cases.py \
  --results results.json \
  --cases <duong-dan>/cases.json \
  --out .selftest_tmp/handover_<feature>.xlsx
```

Script tu chan (exit code 2) neu con case chua pass -> khong tao file. File Excel
co cot tieng Viet: `Ma case`, `Mo ta`, `Dieu kien tien de`, `Cac buoc`,
`Du lieu`, `Ket qua mong doi`, `Ket qua thuc te`, `Trang thai`.

### B7: (Tuy chon) Comment ket qua len Jira

Chi chay khi dev cung cap issue key va da cau hinh credentials Jira trong `.env`.
Script tu chan neu con case fail (exit 2).

Env can co (KHONG hardcode, KHONG commit): `JIRA_BASE_URL`, `JIRA_AUTH_MODE`
(`bearer` cho PAT Server/DC, `basic` cho Cloud/user-pass), `JIRA_TOKEN`, va
`JIRA_USER` (chi khi mode `basic`).

```bash
# Kiem tra ket noi + nhan dien loai Jira:
python .cursor/skills/self-test-cases/scripts/jira_notify.py --check

# Comment + dinh kem Excel:
python .cursor/skills/self-test-cases/scripts/jira_notify.py \
  --issue <ISSUE_KEY> \
  --results results.json \
  --cases <duong-dan>/cases.json \
  --xlsx .selftest_tmp/handover_<feature>.xlsx \
  --feature <feature>
```

Sau khi dinh kem thanh cong len Jira, XOA file tam va thu muc `.selftest_tmp/`.

## Nguyen tac

- Portable: khong hardcode framework/path; chi tiet project nam trong `reference.local.md`.
- Codegraph-first, doc file la phuong an cuoi -> giam token.
- Test khong cham DB/ha tang that (luon mock).
- Excel chi xuat khi 100% pass (gate cung).
- Ngon ngu case/Excel: tieng Viet.
- Khong commit file `.xlsx` / `.env` / credentials.
