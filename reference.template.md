# Reference (template) - dien vao reference.local.md

Day la TEMPLATE. O lan bootstrap (B0), COPY file nay thanh `reference.local.md`
trong cung thu muc, roi dien thong tin THUC TE cua project. `reference.local.md`
thuoc project, KHONG sua file template goc.

> Muc tieu: sau khi dien xong, moi lan viet test chi can doc `reference.local.md`
> la du context, khong phai do lai ca project.

---

## 1. Stack & lenh (BAT BUOC dien)

- Ngon ngu: `<vd: Python 3.12 / Node 20 / Go 1.22>`
- Test framework: `<vd: pytest / jest / vitest / go test / JUnit>`
- Test id la gi: `<vd: pytest nodeid "path::test_name" / jest full test name / "pkg::TestName">`
- Thu muc test: `<vd: tests/<feature>/ | __tests__/ | ..._test.go>`
- Lenh chay test 1 feature:
  ```bash
  <vd: pytest tests/<feature> | npx jest <feature> | go test ./<pkg>/...>
  ```
- Cach xuat results.json chuan (map test id -> passed|failed|error|skipped):
  ```bash
  <vd Python: pytest --json-report --json-report-file=.report.json tests/<feature>  (truyen thang .report.json)>
  <vd khac: chay test --json roi convert sang results.json>
  ```

## 2. Khoi tao app de test (dien)

- App/server factory: `<vd: create_app() trong app/main.py / app express export>`
- Client goi thu: `<vd: FastAPI TestClient / supertest(app) / httptest>`
- Env dummy truoc khi import app: `<vd: conftest set os.environ; hoac .env.test>`

## 3. Kien truc (dien)

- Router/Controller: `<...>`
- Service: `<vd: static method, async, tra dict {status, success, data}>`
- Repository: `<...>`
- DB/ket noi ngoai: `<vd: Postgres get_db, Mongo motor, Redis, HTTP client>`

## 4. Auth / phan quyen (dien)

- Co che: `<vd: dependency get_current_user / middleware JWT>`
- Cach override user trong test: `<vd: app.dependency_overrides / fixture override_user>`

## 5. Pattern mock (dien theo project - vi du chung ben duoi)

Nguyen tac: patch tai NOI SU DUNG, khong tai noi dinh nghia. Mock o tang cao nhat
co the (service) truoc; xuong repository/DB getter khi can.

### Python / pytest (vi du)
```python
from unittest.mock import AsyncMock, patch

def test_get_ok(client):
    with patch("app.api.v1.users.router.UserService.get_info",
               new=AsyncMock(return_value={"id": "1"})):
        r = client.get("/api/v1/users/info", headers={"tnv-token": "dummy"})
    assert r.status_code == 200
```

### Node / jest (vi du)
```js
jest.mock("../services/userService");
const { getInfo } = require("../services/userService");
getInfo.mockResolvedValue({ id: "1" });
const res = await request(app).get("/api/v1/users/info");
expect(res.status).toBe(200);
```

### Go (vi du: interface + fake)
```go
svc := &fakeUserService{info: User{ID: "1"}}
h := NewHandler(svc)
// goi httptest, assert status
```

## 6. Xu ly loi khoi tao/import (dien neu gap)

`<vd: import app fail vi module DB ket noi luc import -> them env dummy vao conftest; hoac monkeypatch client truoc import>`

## 7. Vi tri file khi chay skill

- `cases.json`: dat canh test cua feature, khoa theo test id.
- `results.json`: tao tam o thu muc goc (hoac .selftest_tmp/), khong commit.
- Excel ban giao: `.selftest_tmp/handover_<feature>.xlsx`, xoa sau khi len Jira.
