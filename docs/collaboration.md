# 協作方式

## 責任邊界

每位成員原則上只修改自己的主要工作目錄。`README.md`、`docs/` 或其他成員目錄屬於共同範圍，修改前應先在團隊內確認。

| 目錄 | 主要負責人 |
| --- | --- |
| `frontend/` | 前端成員 |
| `backend/` | 後端成員 |
| `data/schools/` | 學校假資料成員 |
| `data/transcripts/` | 成績單假資料成員 |
| `docs/` | 全員共同維護 |

## 建議工作流程

1. 每項工作從主分支建立自己的 feature branch。
2. 只提交該任務需要的檔案，不順手修改其他人的目錄。
3. 會改變 API 或資料欄位時，先修改契約並讓受影響成員確認。
4. 合併前執行自己目錄中的測試，並確認 JSON 資料可被解析。
5. 透過 pull request 合併，避免四位成員直接同時修改主分支。

建議 branch 名稱：

- `feature/frontend-<內容>`
- `feature/backend-<內容>`
- `data/schools-<內容>`
- `data/transcripts-<內容>`

