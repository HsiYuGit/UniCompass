# Backend

此目錄由後端成員主要負責。

- `src/api/`：HTTP route、request 與 response 處理。
## Recommendation API

Install the backend dependencies with `pip install -r backend/requirements.txt`,
set `OPENAI_API_KEY` in the backend environment, then run the service from the
repository root:

```text
python -m uvicorn src.api.recommendations:app --app-dir backend --port 8000
```

The browser calls `POST /v1/recommendations`; it must not import OpenAI SDKs or
hold an API key. See `docs/api-contract.md` for the request and response shape.
- `src/models/`：後端使用的資料模型與驗證規則。
- `src/services/`：推薦、篩選及資料讀取等商業邏輯。
- `tests/`：後端單元測試與 API 整合測試。

後端讀取的假資料位於 repository 根目錄的 `data/`，不應在 `backend/` 內複製另一份。對外 API 必須與 `docs/api-contract.md` 一致。

