# 學生檔案命名範例

本資料夾中的學生申請者 JSON 檔案使用以下命名格式：

```text
profession_performance_rank_related_experience_rank.json
```

## 命名欄位說明

`profession` 代表學生主要申請背景或專業方向，例如：

- `computer_science`
- `finance`
- `mechanical_engineering`
- `business_administration`
- `hospitality_management`

`performance_rank` 代表學生大學成績表現：

- `high_performance`：高表現，GPA 通常較高，成績多為 A / A-。
- `medium_performance`：中等表現，GPA 通常中等，成績多為 B+ / B。
- `low_performance`：低表現，GPA 通常較低，成績多為 C+ / B- / C。

`related_experience_rank` 代表學生經歷與申請方向的相關程度：

- `high_related_experience`：有多項高度相關的實習、研究、專案或工作經驗。
- `medium_related_experience`：有部分相關經驗，但深度或數量較少。
- `low_related_experience`：相關經驗有限，或經驗與申請方向關聯較弱。

## 檔名範例

```text
computer_science_high_performance_high_related_experience.json
```

代表：電腦科學背景、高學業表現、且有高度相關經驗的學生。

```text
mechanical_engineering_high_performance_low_related_experience.json
```

代表：機械工程背景、高學業表現，但相關經驗較少或較弱的學生。

```text
electrical_engineering_medium_performance_high_related_experience.json
```

代表：電機工程背景、中等學業表現，但有高度相關實務經驗的學生。

```text
business_administration_low_performance_medium_related_experience.json
```

代表：企業管理背景、低學業表現，但有中等程度相關經驗的學生。

## 使用目的

這種命名方式可以讓資料在不打開 JSON 內容的情況下，快速辨識學生的三個核心特徵：

1. 申請背景或專業方向
2. 學業表現等級
3. 相關經驗等級

## 不同國家成績制的後綴

如果學生檔案使用非 4.0 GPA 的成績制，檔名最後會加上：

```text
_grade_scale_countryname
```

完整格式會變成：

```text
profession_performance_rank_related_experience_rank_grade_scale_countryname.json
```

例如：

```text
computer_science_high_performance_high_related_experience_grade_scale_india.json
```

代表：電腦科學背景、高學業表現、高相關經驗，且成績使用印度常見的 10 分制。

```text
finance_high_performance_medium_related_experience_grade_scale_united_kingdom.json
```

代表：金融背景、高學業表現、中等相關經驗，且成績使用英國百分制。

```text
electrical_engineering_medium_performance_high_related_experience_grade_scale_russia.json
```

代表：電機工程背景、中等學業表現、高相關經驗，且成績使用俄羅斯常見的 5 分制。
