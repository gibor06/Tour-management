from __future__ import annotations

from datetime import date, datetime


CANCEL_BOOKING_STATUSES = {"Đã hủy", "Chờ hoàn tiền", "Hoàn tiền"}
TERMINAL_TOUR_STATUSES = {"Hoàn tất", "Đã hủy", "Tạm hoãn"}


def _safe_int(value, default=0):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def _non_negative_int(value, default=0):
    return max(0, _safe_int(value, default))


def _parse_ddmmyyyy(value: str | None):
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.strptime(text, "%d/%m/%Y").date()
    except ValueError:
        return None


def _normalize_booking(booking: dict, tours_by_code: dict[str, dict], today: date) -> None:
    tour_code = str(booking.get("maTour", "")).strip()
    tour = tours_by_code.get(tour_code)

    so_nguoi = max(1, _safe_int(booking.get("soNguoi", 1), 1))
    booking["soNguoi"] = str(so_nguoi)

    price_per_person = _non_negative_int(tour.get("gia", 0)) if tour else _non_negative_int(booking.get("gia", 0))
    tong_tien = price_per_person * so_nguoi if price_per_person > 0 else _non_negative_int(booking.get("tongTien", 0))
    da_thanh_toan = _non_negative_int(booking.get("daThanhToan", booking.get("tienCoc", 0)))
    tien_coc = _non_negative_int(booking.get("tienCoc", 0))

    if tong_tien > 0 and da_thanh_toan > tong_tien:
        da_thanh_toan = tong_tien
    if tien_coc > da_thanh_toan:
        tien_coc = da_thanh_toan

    status = str(booking.get("trangThai", "")).strip()
    if status in CANCEL_BOOKING_STATUSES:
        if status == "Đã hủy" and da_thanh_toan > 0:
            status = "Chờ hoàn tiền"
        if status == "Hoàn tiền":
            da_thanh_toan = 0
            tien_coc = 0
        con_no = 0
    else:
        if da_thanh_toan <= 0:
            status = "Mới tạo"
        elif tong_tien > 0 and da_thanh_toan < tong_tien:
            status = "Đã cọc"
        else:
            status = "Đã thanh toán"
        con_no = max(tong_tien - da_thanh_toan, 0)

    ngay_dat = _parse_ddmmyyyy(booking.get("ngayDat"))
    if ngay_dat is None:
        booking["ngayDat"] = today.strftime("%d/%m/%Y")

    booking.setdefault("hinhThucThanhToan", "Tiền mặt")
    booking.setdefault("nguonKhach", "Khách lẻ")
    booking.setdefault("ghiChu", "")
    booking.setdefault("usernameDat", "")
    booking.setdefault("danhSachKhach", [])
    booking["tongTien"] = tong_tien
    booking["tienCoc"] = tien_coc
    booking["daThanhToan"] = da_thanh_toan
    booking["conNo"] = con_no
    booking["trangThai"] = status


def _normalize_tour(tour: dict, occupied: int, today: date) -> None:
    status = str(tour.get("trangThai", "")).strip()
    if status == "Đã chốt":
        status = "Đã chốt đoàn"
    if status == "Hoàn thành":
        status = "Hoàn tất"

    suc_chua = max(1, _safe_int(tour.get("khach", 1), 1))
    gia = _non_negative_int(tour.get("gia", 0))
    chi_phi_du_kien = _non_negative_int(tour.get("chiPhiDuKien", 0))
    chi_phi_thuc_te = _non_negative_int(tour.get("chiPhiThucTe", 0))

    ngay_di = _parse_ddmmyyyy(tour.get("ngay"))
    ngay_ve = _parse_ddmmyyyy(tour.get("ngayKetThuc")) or ngay_di
    if ngay_di and ngay_ve and ngay_ve < ngay_di:
        ngay_ve = ngay_di

    if ngay_di and ngay_ve:
        so_ngay = (ngay_ve - ngay_di).days + 1
        so_dem = max(so_ngay - 1, 0)
        tour["soNgay"] = f"{so_ngay}N{so_dem}D"
        tour["ngayKetThuc"] = ngay_ve.strftime("%d/%m/%Y")

    if status in {"Đã hủy", "Tạm hoãn"}:
        auto_status = status
    elif ngay_ve and today > ngay_ve:
        auto_status = "Hoàn tất"
    elif ngay_di and today >= ngay_di:
        auto_status = "Đang đi"
    elif occupied >= suc_chua:
        auto_status = "Đã chốt đoàn"
    elif occupied > 0:
        auto_status = "Giữ chỗ"
    else:
        auto_status = "Mở bán"

    ghi_chu = str(tour.get("ghiChuDieuHanh", "") or "").strip()
    if occupied > suc_chua:
        overbook_note = f"[AUTO] Quá tải {occupied - suc_chua} chỗ."
        if overbook_note not in ghi_chu:
            ghi_chu = f"{overbook_note} {ghi_chu}".strip()

    tour["trangThai"] = auto_status
    tour["khach"] = str(suc_chua)
    tour["gia"] = str(gia)
    tour["chiPhiDuKien"] = chi_phi_du_kien
    tour["chiPhiThucTe"] = chi_phi_thuc_te
    tour["ghiChuDieuHanh"] = ghi_chu
    tour.setdefault("hdvPhuTrach", "")


def _normalize_guide(guide: dict, assignments: dict[str, dict]) -> None:
    ma_hdv = str(guide.get("maHDV", "")).strip()
    current_status = str(guide.get("trangThai", "")).strip()
    assignment = assignments.get(ma_hdv, {"assigned": False, "in_progress": False})

    if assignment["in_progress"]:
        guide["trangThai"] = "Đang dẫn tour"
    elif assignment["assigned"]:
        guide["trangThai"] = "Đã phân công"
    elif current_status != "Tạm nghỉ":
        guide["trangThai"] = "Sẵn sàng"

    guide.setdefault("password", "123")
    guide.setdefault("total_reviews", 0)
    guide.setdefault("avg_rating", 0)
    guide.setdefault("skill_score", 0)
    guide.setdefault("attitude_score", 0)
    guide.setdefault("problem_solving_score", 0)


def apply_system_rules(data: dict, today: date | None = None) -> dict:
    if not isinstance(data, dict):
        return data

    today = today or date.today()
    data.setdefault("hdv", [])
    data.setdefault("tours", [])
    data.setdefault("bookings", [])
    data.setdefault("users", [])
    data.setdefault("admin", {})

    tours_by_code = {}
    for tour in data["tours"]:
        ma_tour = str(tour.get("ma", "")).strip()
        if ma_tour:
            tours_by_code[ma_tour] = tour

    occupied_by_tour = {}
    for booking in data["bookings"]:
        _normalize_booking(booking, tours_by_code, today)
        ma_tour = str(booking.get("maTour", "")).strip()
        if ma_tour and booking.get("trangThai") not in CANCEL_BOOKING_STATUSES:
            occupied_by_tour[ma_tour] = occupied_by_tour.get(ma_tour, 0) + _safe_int(booking.get("soNguoi", 0))

    for tour in data["tours"]:
        ma_tour = str(tour.get("ma", "")).strip()
        occupied = occupied_by_tour.get(ma_tour, 0)
        _normalize_tour(tour, occupied, today)

    assignments = {}
    for tour in data["tours"]:
        ma_hdv = str(tour.get("hdvPhuTrach", "")).strip()
        if not ma_hdv:
            continue
        status = str(tour.get("trangThai", "")).strip()
        if status in TERMINAL_TOUR_STATUSES:
            continue
        info = assignments.setdefault(ma_hdv, {"assigned": False, "in_progress": False})
        info["assigned"] = True
        if status == "Đang đi":
            info["in_progress"] = True

    for guide in data["hdv"]:
        _normalize_guide(guide, assignments)

    for user in data["users"]:
        user.setdefault("sdt", "")

    admin = data.get("admin", {})
    if isinstance(admin, dict):
        admin.setdefault("username", "admin")
        admin.setdefault("password", "123")

    return data
