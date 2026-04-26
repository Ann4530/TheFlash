---
name: findgap
description: "Tạo test data cho hệ thống gap-finding: (1) thiết kế gaps theo loại user yêu cầu, (2) ưu tiên sửa CODE để tạo gaps, nếu cần sửa SRS thì tạo file findgap.md mới, (3) output sẵn sàng để pull request, gap-finding check xem có hiện đúng các loại gap hay không."
---

# Find Gap — Tạo Test Data cho Gap-Finding System

> Output cho user bằng **tiếng Việt**. Chỉ giữ tiếng Anh cho tên file, tên class, code block, error code.

## Mục đích

Skill này tạo **test data có kiểm soát** cho hệ thống gap-finding tự động. Workflow tập trung vào việc thiết kế và inject gaps để kiểm chứng hệ thống gap-finding có phát hiện đúng các loại gap khi chạy trên PR.

---

## Arguments

```
<target> <gap_spec>
```

- `<target>` = UC cần xử lý, vd `uc1`, `UC01`
- `<gap_spec>` = số lượng và loại gap cần tạo, vd:
  - `5 gap gồm 2 mismatch, 1 surplus, 1 missing, 1 match`
  - `3 gap gồm 1 mismatch, 1 missing, 1 match`

---

## WORKFLOW — Inject Gaps

### Bước 1: Thiết kế gaps

Từ `<gap_spec>`, lên kế hoạch cụ thể cho từng gap:

| STT | Loại | Mô tả | Cách tạo | File sửa |
|-----|------|-------|---------|----------|
| 1 | ✅ MATCH | Requirement đúng, code cũng đúng | Giữ nguyên hiện trạng | — |
| 2 | ⚠️ MISMATCH | SRS nói 1 cách, code làm cách khác | **Sửa CODE** để mismatch với SRS | Code file (ưu tiên) |
| 3 | ❌ MISSING | Chức năng/yêu cầu trong SRS nhưng code không implement | **Sửa CODE** để thêm behavior/feature mới mà SRS không đề cập | Code file (ưu tiên) |
| 4 | ➕ SURPLUS | Code có behavior mà SRS không đề cập | **Sửa CODE** để thêm logic mới hoặc giữ behavior đã có | Code file (ưu tiên) |

**Nguyên tắc tạo gap:**
- **MATCH**: giữ nguyên một requirement đang đúng
- **MISMATCH**: **ưu tiên sửa CODE** để làm khác so với SRS
- **MISSING**: **sửa CODE** để thêm tính năng/behavior/handler mới mà SRS không đề cập (hoặc validate mới, exception mới, etc.)
- **SURPLUS**: **sửa CODE** để thêm behavior mà SRS không đề cập
- Mỗi gap phải **độc lập, rõ ràng, testable**
- **KHÔNG sửa file dùng chung** (ErrorCode.java, shared service) — chỉ sửa code liên quan UC

**Xác nhận kế hoạch với user** trước khi thực hiện.

### Bước 2: Thực hiện inject

Sau khi user xác nhận:

1. **Sửa CODE** (`src/main/java/...`):
   - Thêm/sửa controller logic, service logic, validation, exception handling, DTO field
   - Sửa tối thiểu, không phá vỡ logic không liên quan
   - Mỗi sửa phải **có comment** ghi rõ loại gap (vd: `// MISMATCH-GAP-01: ...`)

2. **Nếu cần sửa SRS**:
   - **KHÔNG sửa** `uc_specs/<target>.md` gốc
   - **Tạo file mới**: `uc_specs/<target>.findgap.md`
   - File này ghi chú rõ:
     - Loại gaps được tạo
     - Thay đổi nào trong code
     - Lý do thay đổi
     - Kỳ vọng gap-finding sẽ phát hiện những gì

### Bước 3: Báo cáo kết quả

```
## Gaps đã tạo cho <UCxx>

| STT | Loại | Mô tả gap | Code sửa tại | File đã sửa |
|-----|------|-----------|--------------|------------|
| 1 | ✅ MATCH    | BRL-01-01: Login thành công | không sửa | — |
| 2 | ⚠️ MISMATCH | BRL-01-02: Error message khác | LoginController:45 | src/.../LoginController.java |
| 3 | ❌ MISSING  | Tính năng: Log login attempt | LoginService:67 | src/.../LoginService.java |
| 4 | ➕ SURPLUS  | Behavior: Increment failed count | LoginService:72 | src/.../LoginService.java |
| 5 | ⚠️ MISMATCH | Validation: Email format | LoginRequest.java:34 | src/.../LoginRequest.java |

## Files đã thay đổi
- src/main/java/com/mp/karental/controller/LoginController.java:45 — error message mismatch
- src/main/java/com/mp/karental/service/LoginService.java:67,72 — thêm logging + failed attempt counter
- src/main/java/com/mp/karental/dto/request/LoginRequest.java:34 — validation khác

## File ghi chú (nếu cần)
- uc_specs/UC01_Log_in.findgap.md — mô tả chi tiết gaps và kỳ vọng gap-finding

## Bước tiếp theo
Push các file này lên branch, tạo PR để gap-finding check xem có phát hiện đúng 5 gaps trên không.
```

---

## Lưu ý quan trọng

✅ **Làm:**
- **Ưu tiên sửa CODE** để tạo gaps (không sửa SRS gốc)
- Nếu sửa SRS, tạo file mới `UC<xx>.findgap.md`
- **Xác nhận kế hoạch** với user trước khi thực hiện
- Thêm **comment** trong code để ghi rõ loại gap
- Sửa **tối thiểu**, không refactor hay cleanup thêm
- MATCH có thể là giữ nguyên hiện trạng

❌ **Không:**
- Sửa SRS gốc (`uc_specs/<target>.md`)
- Sửa file dùng chung (ErrorCode.java, shared service, util)
- Mở rộng scope ngoài UC được chỉ định
- Tạo gaps mơ hồ, khó testable

---

## Mục tiêu

Khi PR được tạo, hệ thống gap-finding sẽ:
1. So sánh SRS (`uc_specs/UC<xx>.md`) vs Code
2. Phát hiện đúng các loại gaps đã được tạo
3. Report kết quả: ✅ pass nếu tìm thấy đúng số lượng gaps, ❌ fail nếu thiếu hoặc sai loại
