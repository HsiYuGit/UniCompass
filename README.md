# UniCompass

UniCompass 是一個德國選校系統。本 repository 先以責任邊界建立骨架，讓四位成員可以平行開發，再透過共同契約整合。

## 任務與目錄

| 成員 | 主要責任 | 主要工作目錄 |
| --- | --- | --- |
| 前端成員 | 選校介面、使用者互動、呼叫後端 API | `frontend/` |
| 後端成員 | API、推薦邏輯、資料讀取與後端測試 | `backend/` |
| 學校假資料成員 | 德國學校與科系假資料 | `data/schools/` |
| 成績單假資料成員 | 學生資料與成績單假資料 | `data/transcripts/` |

共同規格放在 `docs/`。任何會影響其他成員的欄位或 API 變更，先更新契約並取得共識，再修改自己的實作。

## 目錄結構

```text
UniCompass/
├─ frontend/
│  ├─ public/
│  ├─ src/
│  │  ├─ components/
│  │  ├─ pages/
│  │  ├─ services/
│  │  └─ styles/
│  └─ tests/
├─ backend/
│  ├─ src/
│  │  ├─ api/
│  │  ├─ models/
│  │  └─ services/
│  └─ tests/
├─ data/
│  ├─ schools/
│  │  └─ schools.json
│  └─ transcripts/
│     └─ transcripts.json
└─ docs/
   ├─ api-contract.md
   ├─ collaboration.md
   └─ data-contract.md
```

框架尚未決定，因此目前只建立不綁定語言的目錄與有效的空 JSON 資料集。選定前後端技術後，再由各目錄負責人補上套件設定與啟動入口。

