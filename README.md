# self-test-cases (portable Cursor skill)

Cursor Agent Skill giup dev tren **moi project**: doc yeu cau tinh nang -> viet
test-case theo dung test framework cua project -> tu self-test -> bao loi neu con
case fail -> khi 100% pass thi xuat Excel ban giao tester -> (tuy chon) comment
ket qua + dinh kem Excel len Jira.

Portable: khong gan cung vao framework nao. Chi tiet rieng cua project duoc agent
tu detect o lan chay dau va cache vao `reference.local.md`.

## Cai dat

### Cach 1 - Git clone (khuyen dung, de update)

Clone thang vao thu muc skill cua project:

```bash
git clone <URL-repo-nay> .cursor/skills/self-test-cases
```

Update ve sau:

```bash
cd .cursor/skills/self-test-cases && git pull
```

### Cach 2 - Tai file .zip

1. Tai file zip cua repo nay, giai nen.
2. Copy thu muc noi dung vao project sao cho co duong dan:
   `.cursor/skills/self-test-cases/SKILL.md`

### Sau khi cai (ca 2 cach)

Cai dependency cho script (chi lan dau):

```bash
pip install -r .cursor/skills/self-test-cases/scripts/requirements.txt
```

(Tuy chon) Cau hinh Jira trong `.env` o goc project neu muon comment ket qua:

```env
JIRA_BASE_URL=https://jira.congty.com
JIRA_AUTH_MODE=bearer   # bearer = PAT (Server/DC); basic = Cloud (email + API token)
JIRA_TOKEN=xxxxx
# JIRA_USER=you@congty.com   # chi can khi JIRA_AUTH_MODE=basic
```

> Khong commit `.env` va file `.xlsx` ban giao.

## Su dung

Trong Cursor, goi skill bang ten (skill dat `disable-model-invocation: true` nen
chi load khi duoc nhac ten):

```
/self-test-cases  Viet test cho tinh nang <mo ta yeu cau>
```

Lan chay dau, agent se detect stack va tao `reference.local.md`. Cac lan sau doc
thang file do.

## Cau truc

```
self-test-cases/
├── SKILL.md               # workflow + huong dan (lop bat bien)
├── reference.template.md  # template -> copy thanh reference.local.md (lop project)
├── scripts/
│   ├── export_test_cases.py   # xuat Excel, gate 100% pass
│   ├── jira_notify.py         # comment + dinh kem len Jira
│   └── requirements.txt
└── templates/
    └── cases.example.json     # mau metadata case (khoa theo test id)
```

## Dinh dang ket qua test (results.json)

Script doc `results.json` CHUAN, dung cho moi ngon ngu:

```json
{
  "<test id 1>": "passed",
  "<test id 2>": "failed"
}
```

Gia tri: `passed` | `failed` | `error` | `skipped` (cac bien the pass/ok/success
duoc chuan hoa). Rieng Python + pytest co the truyen thang file
`--json-report-file=.report.json`; script tu hieu format pytest-json-report.

`cases.json` phai khoa theo cung **test id** voi `results.json`.

## Ghi chu

- File `reference.local.md` la rieng cua tung project -> nen commit vao project
  do, KHONG commit nguoc lai repo skill.
- Khong dat skill trong `~/.cursor/skills-cursor/` (chi danh cho Cursor).
