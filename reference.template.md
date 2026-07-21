# Reference (template) - điền vào reference.local.md

Đây là **TEMPLATE**. Ở lần bootstrap (B0), COPY file này thành `reference.local.md`
trong cùng thư mục skill, rồi điền thông tin **THỰC TẾ** của project. `reference.local.md`
thuộc project, **KHÔNG** sửa file template gốc.

> Mục tiêu: sau khi điền xong, mỗi lần viết test chỉ cần đọc `reference.local.md`
> là đủ context, không phải dò lại cả project.

---

## 1. Stack & lệnh (BẮT BUỘC điền)

- Ngôn ngữ: `<vd: Python 3.12 / Node 20 / Go 1.22 / Java 21>`
- Test framework: `<vd: pytest / jest / vitest / go test / JUnit / Playwright>`
- Test id là gì: `<vd: pytest nodeid "path::test_name" / jest fullName / "pkg::TestName" / JUnit "class::method">`
- Thư mục test **của skill** (sandbox, BẮT BUỘC):
  `.cursor/skills/self-test-cases/workdir/tests/<feature>/`
- Thư mục test chuẩn của project (chỉ để tham khảo pattern, KHÔNG ghi vào đây trừ khi user yêu cầu promote):
  `<vd: tests/<feature>/ | __tests__/ | ...>`
- Lệnh chạy test 1 feature (từ **gốc project**, trỏ vào workdir):
  ```bash
  <vd: pytest .cursor/skills/self-test-cases/workdir/tests/<feature> -o pythonpath=.>
  ```
- Cách xuất `results.json` chuẩn (map test id -> passed|failed|error|skipped):
  ```bash
  WORKDIR=.cursor/skills/self-test-cases/workdir

  # Python + pytest (khuyến dùng)
  pytest $WORKDIR/tests/<feature> -o pythonpath=. \
    --json-report --json-report-file=$WORKDIR/.report.json
  python .cursor/skills/self-test-cases/scripts/convert_results.py \
    --framework pytest --input $WORKDIR/.report.json --output $WORKDIR/results.json
  ```

---

## 2. Ma trận hỗ trợ framework (core)

| Nhóm | Framework | Adapter | Ghi chú |
|------|-----------|---------|---------|
| Python | pytest | `pytest` | Hỗ trợ trực tiếp pytest-json-report |
| Node | jest / vitest | `jest` / `vitest` | Dùng JSON reporter |
| Remix | vitest + Playwright | `remix` | `--mode unit` hoặc `--mode e2e` |
| E2E | Playwright | `playwright` | JSON report |
| Go | go test | `go` | Output `-json` (line-delimited) |
| Java | Spring Boot + JUnit | `spring-boot` / `junit` | Parse JUnit XML từ Surefire/Gradle |

Framework khác: thêm adapter mới hoặc tự tổng hợp `results.json` theo schema trong `schemas/results.schema.json`.

---

## 3. Quy ước test id & naming

- Test id trong `cases.json` **PHẢI trùng** key trong `results.json`.
- Đặt tên test rõ ràng theo nhánh logic: `test_<action>_<condition>`.
- Mỗi nhánh logic quan trọng = 1 test id riêng (happy path, validate lỗi, phân quyền, edge case).
- Không dùng key metadata dạng `__NOTE__` trong file production (chỉ dùng ở file mẫu).

---

## 4. Khởi tạo app để test (điền)

- App/server factory: `<vd: create_app() trong app/main.py / Remix buildApp / Spring @SpringBootTest>`
- Client gọi thử: `<vd: FastAPI TestClient / supertest(app) / MockMvc / Playwright page>`
- Env dummy trước khi import app: `<vd: conftest set os.environ; .env.test; @TestPropertySource>`

---

## 5. Kiến trúc (điền)

- Router/Controller: `<...>`
- Service: `<vd: static method, async, trả dict {status, success, data}>`
- Repository: `<...>`
- DB/kết nối ngoài: `<vd: Postgres get_db, Mongo motor, Redis, HTTP client>`

---

## 6. Auth / phân quyền (điền)

- Cơ chế: `<vd: dependency get_current_user / middleware JWT / Spring Security>`
- Cách override user trong test: `<vd: app.dependency_overrides / fixture override_user / @WithMockUser>`

---

## 7. Pattern mock & fixture (điền theo project)

Nguyên tắc: patch tại **NƠI SỬ DỤNG**, không tại nơi định nghĩa. Mock ở tầng cao nhất
có thể (service) trước; xuống repository/DB getter khi cần. **KHÔNG** chạm DB/hạ tầng thật.

### Python / pytest
```python
from unittest.mock import AsyncMock, patch

def test_get_ok(client):
    with patch("app.api.v1.users.router.UserService.get_info",
               new=AsyncMock(return_value={"id": "1"})):
        r = client.get("/api/v1/users/info", headers={"tnv-token": "dummy"})
    assert r.status_code == 200
```

### Node / jest / vitest
```js
vi.mock("../services/userService");
const { getInfo } = await import("../services/userService");
getInfo.mockResolvedValue({ id: "1" });
const res = await request(app).get("/api/v1/users/info");
expect(res.status).toBe(200);
```

### Remix (loader/action)
```ts
import { createRemixStub } from "@remix-run/testing";
// mock service/repository truoc khi goi loader/action
```

### Spring Boot + JUnit
```java
@WebMvcTest(UserController.class)
@MockBean
private UserService userService;
```

### Go (interface + fake)
```go
svc := &fakeUserService{info: User{ID: "1"}}
h := NewHandler(svc)
// gọi httptest, assert status
```

---

## 8. Codegraph & fallback đọc file

- **Ưu tiên**: dùng codegraph query symbol liên quan (service/repository/router/model).
- **Bắt buộc hỏi dev** chạy `codegraph init` nếu chưa có `.codegraph/`.
- **Fallback**: được phép đọc trực tiếp file liên quan khi codegraph thiếu context hoặc dev chưa kịp index.
- **Không** đọc cả project nếu không cần thiết.

---

## 9. Xử lý lỗi khởi tạo/import (điền nếu gặp)

`<vd: import app fail vì module DB kết nối lúc import -> thêm env dummy vào conftest; hoặc monkeypatch client trước import>`

---

## 10. Vị trí file khi chạy skill (sandbox)

Tất cả artifact skill sinh ra nằm trong:
`.cursor/skills/self-test-cases/workdir/`

- Test + `cases.json`: `workdir/tests/<feature>/`
- Config tạm (`pytest.ini`, ...): chỉ trong `workdir/`, **không** ở gốc project
- `results.json` / report: `workdir/`
- Excel bàn giao: `workdir/.selftest_tmp/handover_<feature>.xlsx` (xóa sau khi lên Jira)

Validate:

```bash
python .cursor/skills/self-test-cases/scripts/validate_test_cases.py \
  --cases .cursor/skills/self-test-cases/workdir/tests/<feature>/cases.json \
  --results .cursor/skills/self-test-cases/workdir/results.json
```

`workdir/` đã có trong `.gitignore` của skill → không commit nhầm.
