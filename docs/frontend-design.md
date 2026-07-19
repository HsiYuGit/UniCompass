# UniCompass 前端設計基線

## 正式資料來源

`data/` 是目前前端的唯一資料契約：

- `data/schools/*.json`：每個檔案是一個學校／碩士學程，使用 `status`、`collection_metadata`、`data` 與 `issues` 根結構。
- `data/transcripts/*_experience.json`：每個檔案是一個虛構申請者，包含學歷、成績單、語言、經驗、偏好與預算。

前端以 Vite 的 eager glob 載入所有這些 JSON，不依賴檔名清單或 `transcripts.json`。

## 現有互動

1. 在 15 位申請者中選擇一位。
2. 搜尋並瀏覽 100 個學程，選取一個後查看可由前端直接判定的前檢。
3. 前端僅呈現學位方向、總 ECTS 與英文證明；課程分組、硬資格與 Safety／Match／Reach 排序交由後端 recommendation agent。

## 整合邊界

`fixture-data.ts` 將資料夾內容轉成畫面模型；將來後端提供 API 時，可保留頁面與前檢文案，僅替換該服務邊界的資料來源。
