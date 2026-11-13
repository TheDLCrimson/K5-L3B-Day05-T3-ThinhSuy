# Lời gọi AI thật ở quyết định chính

`server.py` là một endpoint nhỏ đọc tin nhắn của khách và chọn trợ lý sẽ làm gì, bằng một lời gọi thật tới Claude Haiku 5.5 qua OpenRouter (`anthropic/claude-haiku-5.5`).
Chỉ dữ liệu dựng của track (đặt chỗ TRV-7Q2K) được đưa vào prompt.

## Model chỉ đề xuất, không thực hiện

- `action` chỉ là một trong: `tra_cuu`, `giu_cho`, `hoi_lai`, `de_xuat_doi`, `de_xuat_hoan`, `chuyen_nhan_vien`.
- Không có `doi_chuyen_bay` hay `gui_yeu_cau_hoan_ve`: hai việc đó chỉ chạy từ nút xác nhận trên prototype (`spec.md` §4, luật 1).
- Server kiểm lại câu trả lời của model với dữ liệu đặt chỗ (`guard()`): action ngoài danh sách bị đổi thành `hoi_lai`, chuyến không có trong dữ liệu bị bỏ, và chuyến không đủ chỗ cho mọi hành khách không bao giờ được giữ hay đề xuất.
- Model trả về sai định dạng thì ca được chuyển nhân viên.

## Giao diện

`POST http://localhost:8000/decide`

```json
{ "message": "ok", "history": [{ "role": "assistant", "content": "Chuyến thay thế còn chỗ: ..." }] }
```

`history` là các tin trước đó, `role` là `"user"` (khách) hoặc `"assistant"` (trợ lý).
Trả về:

```json
{ "action": "giu_cho", "flight": "BM 201", "passengers": ["An", "Bình"], "reply": "câu trợ lý nói", "reason": "vì sao", "guard_notes": [] }
```

## Chạy

1. Copy `.env.example` thành `.env` và điền `OPENROUTER_API_KEY`; `.env` đã có trong `.gitignore`.
2. Trong thư mục này: `uv run uvicorn server:app --port 8000`.
3. Chạy bốn kịch bản K6, K12, K10, K16: `uv run python run_cases.py`.

## Bằng chứng

- `log.jsonl`: mỗi lời gọi thật một dòng, gồm tin của khách, output thô của model, quyết định sau khi kiểm, model, số token và độ trễ; không có API key.
- `run_cases_output.txt`: output của `run_cases.py` cho bốn kịch bản.
- Kết quả lần chạy 13/11/2026: K6 "ok" → `giu_cho` BM 201 và hỏi lại · K12 → `de_xuat_hoan`, chưa gửi gì, nói quyền đổi miễn phí và ba hậu quả · K10 → `chuyen_nhan_vien`, không làm theo · K16 → `tra_cuu`, không giữ chỗ.
