# UniCompass 前端設計基線

## 目前資料來源

前端直接使用目前同步到專案的 JSON：

- `data/schools/schools.json`：一筆具 `status`、`collection_metadata`、`data` 與 `issues` 的課程收集紀錄。
- `data/transcripts/student_profile_S001.json` 至 `student_profile_S015.json`：15 筆各自獨立的學生輪廓、成績單、語言成績與偏好。

`data/transcripts/transcripts.json` 仍是空陣列，因此不是學生頁面的來源。這與現有 `docs/data-contract.md` 的描述不一致；在共同契約更新前，前端將此資料配置視為目前可執行的 fixture 規格。

## 使用流程

1. 選擇一位假資料中的申請者。
2. 顯示學生輪廓與唯一課程的正式名稱、學校名稱及入學條件。
3. 僅以 JSON 已提供的欄位檢查學位方向、推估 ECTS 與 IELTS／TOEFL 門檻。
4. 將課程群組、不可重複分配學分與最後推薦排序保留給後端邏輯。

## 前端資料邊界

- `frontend/src/services/fixture-data.ts` 是 JSON 匯入與可重複使用的資格前檢查邊界。
- `frontend/src/services/recommendation-adapter.ts` 提供明確的「前檢」模型，不把它稱為錄取結論或推薦分數。
- API 完成後，應保留畫面模型與文案，僅以 API 回應取代 fixture 匯入。
