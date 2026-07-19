# API contract

本文件是前端與後端之間的共同契約。技術棧決定後，由前後端成員一起補齊內容；API 實作與前端呼叫都應以此文件為準。

## 共通約定（待確認）

- Base URL：`TBD`
- API version：`TBD`
- Content type：`application/json`
- 錯誤格式：`TBD`

## Endpoint 範本

新增 endpoint 時，至少記錄以下資訊：

```text
Method and path:
Purpose:
Request parameters/body:
Success status and response body:
Error statuses and response body:
```

## 預計功能（尚未定案）

| 功能 | Method | Path | 狀態 |
| --- | --- | --- | --- |
| 取得學校清單 | TBD | TBD | 待前後端確認 |
| 提交學生成績資料 | TBD | TBD | 待前後端確認 |
## Recommendation agent

`POST /v1/recommendations` is the only boundary for final programme
recommendations. The browser never imports OpenAI packages or receives an API
key. It may perform its local transparent precheck, then sends the selected
programmes to this endpoint for the final result.

Request body:

```json
{
  "transcript": { "student_id": "S001", "...": "full transcript fixture" },
  "programmes": [
    {
      "school": "Aarberg Institute of Digital Systems (Fictional)",
      "program": "MSc Applied Data Science"
    }
  ]
}
```

`programmes` must contain between 1 and 12 unique catalogue entries. The
backend loads school requirements itself, converts local graduation credits to
ECTS using `ects_multiplier`, and runs the OpenAI Agents SDK in two
structured-output stages: course allocation and final ranking. Credit totals,
language checks, and eligibility aggregation remain deterministic Python code.

The response is a JSON object with `recommendations` and `not_recommended`
arrays. A `503` response means the backend has no `OPENAI_API_KEY` configured
or the Agents SDK dependency is unavailable; `404` means a selected programme
is not in the server catalogue; and `422` means invalid request data or an
invalid model output. `GET /health` returns `{ "status": "ok" }`.
| 取得選校推薦 | TBD | TBD | 待前後端確認 |

