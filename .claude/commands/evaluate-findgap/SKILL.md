---
name: evaluate-findgap
description: "Evaluate ket qua cua skill findgap: nhan log JSON + bang ket qua he thong, tinh TP/FP/FN, Precision/Recall/F1, va dien vao test_findgap_result_theflash.csv."
---

# Evaluate FindGap — Danh Gia Ket Qua Gap-Finding

> Output bang **tieng Viet**. Chi giu tieng Anh cho ten file, code block, ten metric.

## Muc dich

Skill nay nhan ket qua tu he thong gap-finding (log JSON + bang gap classifications), tinh cac metric danh gia (Precision, Recall, F1), va dien vao file CSV ket qua test.

---

## Arguments

```
<uc_id> <csv_path>
```

- `<uc_id>` = ID cua use case vua chay, vd `UC-06`
- `<csv_path>` = duong dan den file CSV ket qua, mac dinh `test_findgap_result_theflash.csv`

User se paste truc tiep vao chat:
1. **Log JSON** tu he thong (chua tokens, cost, duration) — neu khong co thi ghi `—` cho token/latency/cost
2. **Bang ket qua** (cac dong co cot Tag: match/mismatch/missing/surplus)
3. **Expected Output** = tong hop ky vong (vd: "2 match, 1 mismatch, 1 missing, 1 surplus")

---

## WORKFLOW

### Buoc 1: Parse Input

Tu **log JSON**, trich xuat:
| Field | JSON path |
|-------|-----------|
| UC ID | `uc_id` |
| PR title | `pr_title` |
| Duration | `total.duration_s` |
| Input tokens | `total.input_tokens` |
| Output tokens | `total.output_tokens` |
| Cost | `total.cost_usd` |

Tu **bang ket qua**, dem theo tag:
```
match_actual    = so dong tag "match"
mismatch_actual = so dong tag "mismatch"
missing_actual  = so dong tag "missing"
surplus_actual  = so dong tag "surplus"
```

Tu **Expected Output**, dem:
```
match_exp      = so match ky vong
mismatch_exp   = so mismatch ky vong
missing_exp    = so missing ky vong
surplus_exp    = so surplus ky vong
```

---

### Buoc 2: Tinh Metrics

**Dinh nghia "gaps"** = cac item khong phai match (mismatch + missing + surplus).

```
expected_gaps = mismatch_exp + missing_exp + surplus_exp
actual_gaps   = mismatch_actual + missing_actual + surplus_actual
```

**Tinh TP theo tung loai**:
```
TP_mismatch = min(mismatch_exp, mismatch_actual)
TP_missing  = min(missing_exp,  missing_actual)
TP_surplus  = min(surplus_exp,  surplus_actual)
TP          = TP_mismatch + TP_missing + TP_surplus

FP = actual_gaps - TP
FN = expected_gaps - TP
```

**Tinh ty le**:
```
Precision = TP / (TP + FP)
Recall    = TP / (TP + FN)
F1        = 2 x Precision x Recall / (Precision + Recall)
```

**Danh gia F1**:
| F1 | Muc |
|----|-----|
| < 0.5 | Kem |
| 0.5 – 0.7 | Chap nhan duoc |
| 0.7 – 0.85 | Tot |
| > 0.85 | Xuat sac (>0.95 check overfitting) |

---

### Buoc 3: Phan tich Gap Categories

Xac dinh nhan tong:
- `Match` — tat ca deu match, khong co gap nao
- `Missing` — chu yeu missing (AI bo sot nhieu buoc FE/BE)
- `Mismatch` — chu yeu mismatch (AI nham loai gap)
- `Surplus` — chu yeu surplus (AI tao ra nhieu gap khong co trong expected)
- `Mixed` — nhieu loai gap ket hop

---

### Buoc 4: Dien CSV

File CSV su dung cac cot sau (dung chinh xac ten cot nay):

```
STT, Use Case, Gap Categories, Expected Gap, Actual Gap,
Token (input / output), Recall, Precision, F1 Score, Latency (s),
Security, Stability, Cost (USD), Expected Output, Actual Output
```

**Format tung cot:**

| Cot | Format | Vi du |
|-----|--------|-------|
| STT | so thu tu | `2` |
| Use Case | `{uc_id}: {pr_title}` | `UC-06: Homepage...` |
| Gap Categories | nhan tu Buoc 3 | `Mixed` |
| Expected Gap | **bullet list** (xem ben duoi) | |
| Actual Gap | mo ta chi tiet co so thu tu (1)(2)(3)... | |
| Token (input / output) | `{input} / {output}` — ghi `—` neu khong co JSON log | `25,888 / 9,009` |
| Recall | `{decimal} ({percent}%)` | `0.667 (67%)` |
| Precision | `{decimal} ({percent}%)` | `0.400 (40%)` |
| F1 Score | chi so thap phan (KHONG phan tram) | `0.53` |
| Latency (s) | so giay thap phan — `—` neu khong co | `110.84` |
| Security | `—` neu khong phat hien / `Warning: {mo ta}` / `Fail: {mo ta}` | `—` |
| Stability | `—` neu chi 1 lan chay; `{0.0-1.0}` neu co 2 lan | `—` |
| Cost (USD) | `$X.XX` — `—` neu khong co | `$0.29` |
| Expected Output | multi-line list (xem ben duoi) | |
| Actual Output | multi-line list (xem ben duoi) | |

**Format Expected Gap** (bullet points, wrap trong dau ngoac kep trong CSV):
```
"N gaps
• TYPE-01: [mo ta gap thu 1]
• TYPE-02: [mo ta gap thu 2]
..."
```

Vi du:
```
"6 gaps
• MATCH-01: BE city query — top 6 cities (BRL-06-02)
• MISMATCH-01: FE flow SRS vs code tach 2 endpoint
• MISSING-01: Guest FE navigation step
• SURPLUS-01: separate endpoints thay 1 unified flow"
```

**Format Expected Output / Actual Output** (multi-line, wrap trong dau ngoac kep):
```
"Mismatch: X
Missing: X
Surplus: X"
```

Chi liet ke cac loai co xuat hien (bo qua loai = 0). Neu tat ca Match thi ghi `"Match: X"`.

**Luu y CSV:** Moi field chua dau phay hoac xuat dong PHAI duoc boc trong dau ngoac kep `"..."`.
Neu khong co du lieu (JSON log khong duoc cung cap) thi ghi `—`.

---

### Buoc 5: Bao cao

In ra tom tat ket qua:

```
## Ket qua danh gia {uc_id}

| Metric | Gia tri |
|--------|---------|
| TP | X |
| FP | X |
| FN | X |
| Precision | X.XXX (XX%) |
| Recall | X.XXX (XX%) |
| F1 Score | X.XX — [Danh gia] |
| Token | X (input) / X (output) |
| Latency | X.XX giay |
| Cost | $X.XX |

**Nhan xet:** [2-3 cau ve diem manh/yeu cua findgap trong test case nay]

→ Da dien vao `{csv_path}` dong STT={n}.
```

---

## Vi du tinh toan

**Expected:** "2 matching, 1 mismatch, 1 missing, 1 surplus"
**Actual (tu bang):** 4 match, 0 mismatch, 4 missing, 1 surplus

```
expected_gaps = 1 + 1 + 1 = 3
actual_gaps   = 0 + 4 + 1 = 5

TP = min(1,0) + min(1,4) + min(1,1) = 0 + 1 + 1 = 2
FP = 5 - 2 = 3
FN = 3 - 2 = 1

Precision = 2/5 = 0.400 (40%)
Recall    = 2/3 = 0.667 (67%)
F1        = 0.53 — Chap nhan duoc
```

**CSV row tuong ung:**
```
Token:           25,888 / 9,009
Recall:          0.667 (67%)
Precision:       0.400 (40%)
F1 Score:        0.53
Expected Output: "Mismatch: 1
Missing: 1
Surplus: 1"
Actual Output:   "Missing: 4
Surplus: 1"
```
