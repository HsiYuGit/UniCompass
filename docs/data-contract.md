# Data contract

本文件是兩位假資料成員與後端之間的共同契約。目前尚未決定實際欄位，因此資料檔先使用合法的空 JSON array，避免過早固定格式。

## 學校資料

- 檔案：`data/schools/schools.json`
- 根節點型別：JSON array
- 單筆學校／科系欄位：`TBD`，由學校資料成員與後端成員共同確認。

## 學生成績單資料

- 檔案：`data/transcripts/transcripts.json`
- 根節點型別：JSON array
- 單筆學生／成績欄位：`TBD`，由成績單資料成員與後端成員共同確認。
- 隱私限制：只可使用虛構人物，不可提交真實個人資料。

## 變更規則

欄位名稱、型別、必填狀態或巢狀結構若有變更，必須在同一個 pull request 更新本文件。後端資料模型與測試應一併更新；若 API response 也受到影響，還要更新 `docs/api-contract.md`。

