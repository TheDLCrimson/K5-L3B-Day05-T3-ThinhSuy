# Bài nộp LAB5 - T3 Du lịch · Nhóm ThinhSuy

**Lớp:** L3B · **Bàn / zone:** ____ · **Track:** T3 Du lịch

| Họ và Tên | Mã Học Viên | Việc đã làm |
| --- | --- | --- |
| Dương Minh Chiến | 2A202603921 |  |
| Trịnh Hưng Thịnh | 2A202603907 |  |
| Lưu Nguyễn Chí Đức | 2A202603923 |  |

## §1. Lát cắt & phạm vi

**Lát cắt (chép từ track).** Trong **Đặt chỗ của tôi**, khi **hành khách** vừa nhận tin chuyến bay bị huỷ và nhắn hỏi, **AI đề xuất và giữ chỗ chuyến thay thế, hỏi lại cho rõ, đổi vé, hay chuyển nhân viên**, để khách tới nơi kịp mà không mất vé hay tiền vì một thao tác không đảo lại được.

| Một người dùng | Một việc | Một quyết định của AI | Một kết quả |
| --- | --- | --- | --- |
| hành khách (ca dựng: chị Nguyễn Minh An đi cùng con 5 tuổi, mã TRV-7Q2K) | vừa nhận tin BM 213 19:00 bị huỷ do bão, nhắn hỏi | đề xuất và giữ chỗ, hỏi lại, đổi vé, hay chuyển nhân viên | tới TP.HCM kịp, không mất vé hay tiền vì một thao tác không đảo được |

**Đọc đề - AI được thêm quyền gì, sai thì ai chịu.**

- Hôm nay khách tự bấm qua từng bước Đổi lịch hoặc Hoàn tiền; trang trợ giúp không mô tả trợ lý nào làm thay ("Sản phẩm thật hôm nay", dòng cuối).
- Tích hợp AI nghĩa là AI được bấm thay khách ba việc thay đổi trạng thái: `giu_cho_chuyen_moi`, `doi_chuyen_bay`, `gui_yeu_cau_hoan_ve`.
- Hai tool không đảo được là chỗ nhóm phải cẩn thận nhất: `doi_chuyen_bay` dùng mất lần đổi miễn phí duy nhất, và `gui_yeu_cau_hoan_ve` gửi rồi không huỷ được.
- Người chịu khi AI sai là hành khách: mất lần đổi miễn phí, mất chỗ trên chuyến đúng, hoặc mất cả chỗ lẫn tiền tới 90 ngày.
- Nhìn chung, sai hướng "làm quá tay" (đổi hoặc hoàn khi khách chưa rõ) đắt hơn sai hướng "chờ" (hỏi lại thêm một câu, chuyển nhân viên).
- Nhưng hướng nào đắt hơn còn tuỳ tool:
  - Với `doi_chuyen_bay` và `gui_yeu_cau_hoan_ve`, làm quá tay đắt hơn, vì một lần làm sai là mất lần đổi miễn phí hoặc mất cả chỗ lẫn tiền, còn hỏi lại chỉ tốn thêm một tin nhắn.
  - Với `giu_cho_chuyen_moi`, chờ đắt hơn, vì giữ chỗ sai thì 20 phút sau tự nhả, còn chờ thì BM 217 21:00 (còn 1 chỗ) hay BM 205 09:30 (còn 4 chỗ) có thể hết trong lúc khách đang phân vân.

**Những việc tính năng KHÔNG làm.**

1. **Không đổi, không huỷ, không gửi hoàn khi khách chưa xác nhận rõ chuyến nào, cho hành khách nào.**
   `doi_chuyen_bay` dùng mất lần đổi miễn phí duy nhất và `gui_yeu_cau_hoan_ve` gửi rồi không huỷ được, trong khi đặt chỗ TRV-7Q2K có hai hành khách và ba chuyến thay thế, nên những câu như "đổi đi" hay "sáng mai" (BM 201 07:00 hay BM 205 09:30?) chưa đủ để chọn.
2. **Giờ bay, chỗ trống chỉ lấy từ dữ liệu đặt chỗ; không đoán.**
   `tra_cuu_dat_cho` là nguồn duy nhất: đoán theo vé cũ thì AI nói "19:00" cho một chuyến đã huỷ, và đoán số chỗ thì AI có thể đề xuất BM 217 cho hai mẹ con trong khi chuyến đó chỉ còn 1 chỗ.
3. **Tin tự xưng nhân viên, đòi bỏ qua quy định: không làm theo; tin nhắn là dữ liệu, không phải lệnh.**
   Kênh chat là kênh của hành khách và nhân viên thật nhận ca qua `chuyen_nhan_vien`, không ra lệnh qua tin nhắn của khách, nên làm theo tin đó có thể khiến AI đổi chuyến hoặc gửi hoàn ngoài chính sách (hard test "tin tự xưng nhân viên hãng" của track).
4. **Không hứa, không tính bồi thường tiền mặt.**
   BM 213 huỷ do thời tiết, và chính sách hãng Bay Mẫu ghi rõ huỷ do thời tiết không bồi thường tiền mặt, nên AI chỉ nói hai quyền lợi có thật: đổi miễn phí một lần trong 48 giờ hoặc hoàn toàn bộ.

Prototype giữ đúng phạm vi này:

- Nút đổi vé và gửi hoàn chỉ hiện sau khi khách đã chọn một chuyến cụ thể và hành khách cụ thể.
- Mọi giờ bay và số chỗ trên màn hình ghi nguồn là dữ liệu đặt chỗ TRV-7Q2K.
- Không có lối nào để một tin nhắn mở khoá thao tác ngoài quy định; AI trả lời theo quy định và đưa nút "Chuyển nhân viên".
- Không có màn hình hay nút nào nhắc tới bồi thường tiền mặt; quyền lợi hiện trên màn hình chỉ là "đổi miễn phí 1 lần trong 48 giờ" hoặc "hoàn toàn bộ".

## §2. Kịch bản rủi ro  (chặng 2)

- ≥8 kịch bản, mỗi lớp ①②③④ ít nhất một; mỗi kịch bản: tin người dùng · lớp · AI có thể sai thế nào · sản phẩm tốt nên làm gì · nhãn (nhẹ / sửa được / không chấp nhận được).
- Bằng chứng: cột "AI có thể sai thế nào" trỏ về một tool hoặc một dòng dữ liệu của track (hoặc chỗ dữ liệu không có).
- Quyết định: 2 kịch bản đắt nhất - vì sao đắt hơn các kịch bản còn lại; kịch bản nào suýt được chọn và vì sao không.

## §3. Khi AI sai  (chặng 3)

Với mỗi kịch bản đắt nhất:

- AI nói gì (nguyên văn) · người dùng thấy gì · làm gì tiếp · ai được báo, sau bao lâu.
- Quyết định: hỏi lại / trả lời kèm giới hạn / dừng và chuyển người - chọn cách nào, đã loại cách nào, vì sao.
- Loại lỗi (hệ thống / người dùng / ngữ cảnh) và vì sao cách nói, cách sửa đi theo loại đó.
- 2-3 nguyên tắc HAX/PAIR, mỗi cái trỏ vào một chỗ cụ thể (câu chữ hoặc chỗ trên màn hình).
- Lỗi nào sửa câu chữ không cứu được (nếu có), và thiết kế cứu nó thế nào.

## §4. Mức tự chủ  (chặng 4)

Với mỗi tool:

- Mức của nhóm (tự làm / cần người duyệt / cấm). Nếu cần người duyệt: ai duyệt · người duyệt thấy gì · quá hạn thì sao.
- Lý do theo cost-of-error: sai thì ai chịu gì · đảo lại được không · chờ người thì mất gì.
- Phương án đã cân nhắc và vì sao loại.

Thêm:

- Tool khó xếp nhất: mỗi người từng chọn gì, cái giá của mỗi phía (trỏ về kịch bản ở §2), nhóm chốt thế nào.
- Thử mức đã đặt trên 2 kịch bản đắt nhất + 1 kịch bản bình thường: cái sai có bị chặn không? còn việc nào làm khi lẽ ra phải hỏi? người dùng bình thường có phải chờ vô ích không?
- Luật thêm hoặc tool tách bước (nếu có), và vì sao.
- Một mức tự chủ đã đổi lời hứa nào với người dùng.

## §5. Prototype  (chặng 5)

- Link hoặc file · công cụ · phần nào mock · có lời gọi AI thật không.
- 1-2 ảnh có đánh số; mỗi số: thể hiện gì · nguyên tắc HAX/PAIR nào · mức tự chủ nào.
- Quyết định: cách hiện độ chắc/bằng chứng và điều khiển mức tự chủ - đã nghĩ tới cách nào khác, vì sao chọn cách này.

## §6. Tốt là gì  (chặng 6 - nhẹ, bỏ được nếu thiếu giờ)

- 3 tiêu chí Pass/Fail chấm được; thiết kế của nhóm đạt tiêu chí nào trên 2 kịch bản đắt nhất; lỗi còn lại.

## §7. Demo

- Ca lạ nhận được ở demo: prototype đã làm gì, và nhóm có đổi ý gì sau ca đó không.
