"""Server-side checks from spec.md §6: a fake model picks the wrong action, and guard() plus
guard_context() must correct it without any real model call.

Run from this folder:  uv run pytest -q test_guard.py
"""

import os

os.environ.setdefault("OPENROUTER_API_KEY", "test-key-not-used")

import pytest  # noqa: E402

from server import Turn, guard, guard_context  # noqa: E402

LISTED = Turn(
    role="assistant",
    content="Chuyến thay thế còn chỗ: BM 217 21:00 (1 chỗ), BM 201 07:00 (9 chỗ), BM 205 09:30 (4 chỗ). Chị muốn đổi sang chuyến nào?",
)
REFUND_PROMPT = Turn(
    role="assistant",
    content="Mình chưa gửi yêu cầu hoàn nào. Chị được đổi miễn phí một lần. Chị muốn xem chuyến đổi, hay hoàn cho cả hai người?",
)
REFUND_SENT = Turn(role="assistant", content="Đã gửi yêu cầu hoàn cho An và Bình. Yêu cầu này không huỷ được.")


def fake(action, flight=None, passengers=None, reply="(câu của model giả)"):
    return {"action": action, "flight": flight, "passengers": passengers or ["An", "Bình"], "reply": reply, "reason": "model giả"}


def run(decision, message, history=()):
    decision, _ = guard(decision)
    decision, _ = guard_context(decision, message, list(history))
    return decision


# Wrong choices by the fake model that the server must correct.
CORRECTED = [
    ("K16 câu hỏi bị giữ chỗ", fake("giu_cho", "BM 201"), "Sáng mai còn chuyến nào đủ chỗ cho 2 mẹ con không?", [], "tra_cuu"),
    ("hoàn tác", fake("giu_cho", "BM 205"), "hoàn tác giúp mình", [], "chuyen_nhan_vien"),
    ("gặp nhân viên", fake("hoi_lai"), "cho mình gặp nhân viên", [], "chuyen_nhan_vien"),
    ("K3 hỏi bồi thường", fake("hoi_lai", reply="Chị được bồi thường 500.000 đ."), "Huỷ do bão thì hãng bồi thường cho mình bao nhiêu tiền?", [], "tra_cuu"),
    ("K7 đổi vé cho bé", fake("de_xuat_doi", "BM 201"), "Đổi vé cho bé nhé.", [], "hoi_lai"),
    ("K8 bé bay một mình", fake("de_xuat_doi", "BM 217", ["Bình"]), "Cho bé đi chuyến 21h trước đi, ba bé đón ở HCM. Mình bay sáng mai sau.", [], "chuyen_nhan_vien"),
    ("hoàn riêng chị An", fake("de_xuat_hoan", passengers=["An"]), "hoàn vé của mình thôi, bé vẫn bay", [REFUND_PROMPT], "chuyen_nhan_vien"),
    ("K12 lượt hai vẫn chưa rõ", fake("de_xuat_hoan"), "hoàn đi, nói rồi mà", [REFUND_PROMPT], "chuyen_nhan_vien"),
    ("K14 đổi sau khi đã hoàn", fake("de_xuat_doi", "BM 201"), "Lỡ hoàn rồi, giờ đổi sang chuyến mai được không?", [REFUND_SENT], "chuyen_nhan_vien"),
    ("BM 217 cho 2 người", fake("de_xuat_doi", "BM 217"), "đổi sang chuyến 21h", [LISTED], "hoi_lai"),
    ("action ngoài danh sách", fake("doi_chuyen_bay", "BM 201"), "đổi luôn đi", [LISTED], "hoi_lai"),
]

# Right choices by the fake model that the server must leave alone.
KEPT = [
    ("K6 ok", fake("giu_cho", "BM 201"), "ok", [LISTED], "giu_cho"),
    ("K12 lượt một", fake("de_xuat_hoan"), "Thôi huỷ hết đi, hoàn tiền cho mình.", [LISTED], "de_xuat_hoan"),
    ("K12 lượt hai đã rõ hành khách", fake("de_xuat_hoan"), "hoàn cho cả hai người", [REFUND_PROMPT], "de_xuat_hoan"),
]


@pytest.mark.parametrize("name,decision,message,history,expected", CORRECTED + KEPT, ids=[c[0] for c in CORRECTED + KEPT])
def test_server_decision(name, decision, message, history, expected):
    assert run(decision, message, history)["action"] == expected


def test_compensation_reply_follows_policy():
    reply = run(fake("hoi_lai", reply="Chị được bồi thường 500.000 đ."), "Hãng bồi thường bao nhiêu?")["reply"]
    assert "không có bồi thường tiền mặt" in reply
    assert "500.000" not in reply


def test_never_returns_an_executing_action():
    for action in ("doi_chuyen_bay", "gui_yeu_cau_hoan_ve"):
        assert run(fake(action, "BM 201"), "ok", [LISTED])["action"] not in {"doi_chuyen_bay", "gui_yeu_cau_hoan_ve"}
