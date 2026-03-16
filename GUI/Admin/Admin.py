import json
import os
import re
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import copy

from core.security import mask_password, prepare_password_for_storage

# =========================
# THEME
# =========================
THEME = {
    "bg": "#f8fafc",
    "surface": "#ffffff",
    "sidebar": "#0f172a",
    "primary": "#2563eb",
    "success": "#059669",
    "danger": "#dc2626",
    "warning": "#d97706",
    "text": "#0f172a",
    "muted": "#64748b",
    "border": "#cbd5e1",
    "note_bg": "#fff7ed",
    "note_fg": "#9a3412",
    "zebra_even": "#f8fafc",
    "zebra_odd": "#ffffff",
}

TOUR_STATUSES = ["Giữ chỗ", "Mở bán", "Đã chốt đoàn", "Chờ khởi hành", "Đang đi", "Hoàn tất", "Đã hủy", "Tạm hoãn"]
BOOKING_STATUSES = ["Mới tạo", "Đã cọc", "Đã thanh toán", "Đã hủy", "Chờ hoàn tiền", "Hoàn tiền"]
HDV_STATUSES = ["Sẵn sàng", "Đã phân công", "Đang dẫn tour", "Tạm nghỉ"]

# =========================
# PATH DỮ LIỆU
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "vietnam_travel_data.json")
REVIEWS_FILE = os.path.join(DATA_DIR, "vietnam_travel_reviews.json")
NOTIF_FILE = os.path.join(DATA_DIR, "vietnam_travel_notifications.json")

DEFAULT_DATA = {
    "hdv": [
        {
            "maHDV": "HDV01",
            "tenHDV": "Nguyễn Văn Anh",
            "sdt": "0901234567",
            "email": "anh@travel.com",
            "kn": "5",
            "gioiTinh": "Nam",
            "khuVuc": "Miền Bắc",
            "trangThai": "Đã phân công",
            "password": "123",
            "total_reviews": 0,
            "avg_rating": 0,
            "skill_score": 0,
            "attitude_score": 0,
            "problem_solving_score": 0
        },
        {
            "maHDV": "HDV02",
            "tenHDV": "Trần Minh Khoa",
            "sdt": "0912345678",
            "email": "khoa@travel.com",
            "kn": "3",
            "gioiTinh": "Nam",
            "khuVuc": "Miền Trung",
            "trangThai": "Sẵn sàng",
            "password": "123",
            "total_reviews": 0,
            "avg_rating": 0,
            "skill_score": 0,
            "attitude_score": 0,
            "problem_solving_score": 0
        }
    ],
    "tours": [
        {
            "ma": "T01",
            "ten": "Đà Lạt Phố Hoa",
            "ngay": "15/03/2026",
            "ngayKetThuc": "17/03/2026",
            "soNgay": "3N2D",
            "khach": "20",
            "gia": "2250000",
            "diemDi": "TP.HCM",
            "diemDen": "Đà Lạt",
            "trangThai": "Mở bán",
            "hdvPhuTrach": "HDV01",
            "chiPhiDuKien": 15000000,
            "chiPhiThucTe": 0,
            "ghiChuDieuHanh": "Tập trung tại cổng D1 lúc 05:30."
        },
        {
            "ma": "T02",
            "ten": "Sapa Mây Núi",
            "ngay": "20/03/2026",
            "ngayKetThuc": "22/03/2026",
            "soNgay": "3N2D",
            "khach": "15",
            "gia": "3450000",
            "diemDi": "Hà Nội",
            "diemDen": "Sapa",
            "trangThai": "Đã chốt đoàn",
            "hdvPhuTrach": "HDV02",
            "chiPhiDuKien": 25000000,
            "chiPhiThucTe": 0,
            "ghiChuDieuHanh": "Đã chốt danh sách khách."
        }
    ],
    "bookings": [
        {
            "maBooking": "BK01",
            "maTour": "T01",
            "tenKhach": "Khách hàng mẫu",
            "sdt": "0988111222",
            "soNguoi": "2",
            "trangThai": "Đã cọc",
            "ngayDat": "10/03/2026",
            "tongTien": 4500000,
            "tienCoc": 1000000,
            "daThanhToan": 1000000,
            "conNo": 3500000,
            "hinhThucThanhToan": "Chuyển khoản",
            "nguonKhach": "Khách lẻ",
            "ghiChu": "",
            "usernameDat": "Khach",
            "danhSachKhach": []
        }
    ],
    "users": [
        {
            "username": "Khach",
            "password": "123",
            "fullname": "Khách hàng mẫu",
            "sdt": "0988111222"
        }
    ],
    "admin": {"username": "admin", "password": "123"}
}


# =========================
# DATA STORE
# =========================
class DataStore:
    def __init__(self, path=DATA_FILE, rev_path=REVIEWS_FILE, notif_path=NOTIF_FILE):
        self.path = path
        self.rev_path = rev_path
        self.notif_path = notif_path
        self.data = {"hdv": [], "tours": [], "bookings": [], "users": [], "admin": {}}
        self.reviews = []
        self.notifications = []
        self.load()

    def load(self):
        if not os.path.exists(self.path):
            self.data = copy.deepcopy(DEFAULT_DATA)
            self.save()
        else:
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except:
                self.data = copy.deepcopy(DEFAULT_DATA)

        for key in ["hdv", "tours", "bookings", "users"]:
            if key not in self.data or not isinstance(self.data[key], list):
                self.data[key] = []

        if "admin" not in self.data or not isinstance(self.data["admin"], dict):
            self.data["admin"] = DEFAULT_DATA["admin"]

        for h in self.data["hdv"]:
            h.setdefault("password", "123")
            h.setdefault("total_reviews", 0)
            h.setdefault("avg_rating", 0)
            h.setdefault("skill_score", 0)
            h.setdefault("attitude_score", 0)
            h.setdefault("problem_solving_score", 0)
            if h.get("trangThai") == "Đang dẫn tour" and h.get("trangThai") not in HDV_STATUSES:
                h["trangThai"] = "Đang dẫn tour"

        for t in self.data["tours"]:
            if t.get("trangThai") == "Đã chốt":
                t["trangThai"] = "Đã chốt đoàn"
            if t.get("trangThai") == "Hoàn thành":
                t["trangThai"] = "Hoàn tất"
            t.setdefault("ngayKetThuc", t.get("ngay", ""))
            t.setdefault("soNgay", "1N0D")
            t.setdefault("chiPhiDuKien", 0)
            t.setdefault("chiPhiThucTe", 0)
            t.setdefault("ghiChuDieuHanh", "")

        for b in self.data["bookings"]:
            b.setdefault("trangThai", "Mới tạo")
            b.setdefault("ngayDat", datetime.now().strftime("%d/%m/%Y"))
            b.setdefault("tongTien", 0)
            b.setdefault("tienCoc", 0)
            b.setdefault("daThanhToan", 0)
            b.setdefault("conNo", 0)
            b.setdefault("hinhThucThanhToan", "Tiền mặt")
            b.setdefault("nguonKhach", "Khách lẻ")
            b.setdefault("ghiChu", "")
            b.setdefault("usernameDat", "")
            b.setdefault("danhSachKhach", [])

        if os.path.exists(self.rev_path):
            try:
                with open(self.rev_path, "r", encoding="utf-8") as f:
                    self.reviews = json.load(f)
            except:
                self.reviews = []
        else:
            self.reviews = []

        if os.path.exists(self.notif_path):
            try:
                with open(self.notif_path, "r", encoding="utf-8") as f:
                    self.notifications = json.load(f)
            except:
                self.notifications = []
        else:
            self.notifications = []

    def save(self):
        folder = os.path.dirname(self.path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

        clean_data = copy.deepcopy(self.data)
        if "reviews" in clean_data:
            del clean_data["reviews"]
        if "notifications" in clean_data:
            del clean_data["notifications"]

        for hdv in clean_data.get("hdv", []):
            hdv["password"] = prepare_password_for_storage(hdv.get("password", ""))
        for user in clean_data.get("users", []):
            user["password"] = prepare_password_for_storage(user.get("password", ""))
        admin = clean_data.get("admin", {})
        if isinstance(admin, dict):
            admin["password"] = prepare_password_for_storage(admin.get("password", ""))

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(clean_data, f, ensure_ascii=False, indent=2)

        with open(self.rev_path, "w", encoding="utf-8") as f:
            json.dump(self.reviews, f, ensure_ascii=False, indent=2)

        with open(self.notif_path, "w", encoding="utf-8") as f:
            json.dump(self.notifications, f, ensure_ascii=False, indent=2)

    @property
    def list_hdv(self):
        return self.data["hdv"]

    @property
    def list_tours(self):
        return self.data["tours"]

    @property
    def list_bookings(self):
        return self.data["bookings"]

    @property
    def list_users(self):
        return self.data["users"]

    @property
    def list_reviews(self):
        return self.reviews

    @property
    def list_notifications(self):
        return self.notifications

    def find_user(self, username):
        return next((u for u in self.list_users if u.get("username") == username), None)

    def find_hdv(self, ma_hdv):
        return next((h for h in self.list_hdv if h.get("maHDV") == ma_hdv), None)

    def find_tour(self, ma_tour):
        return next((t for t in self.list_tours if t.get("ma") == ma_tour), None)

    def get_bookings_by_tour(self, ma_tour):
        return [b for b in self.list_bookings if b.get("maTour") == ma_tour]

    def get_occupied_seats(self, ma_tour):
        total = 0
        for b in self.get_bookings_by_tour(ma_tour):
            if b.get("trangThai") in ["Đã hủy", "Chờ hoàn tiền", "Hoàn tiền"]:
                continue
            total += safe_int(b.get("soNguoi", 0))
        return total


# =========================
# HELPERS
# =========================
def clear_container(app):
    for widget in app["container"].winfo_children():
        widget.destroy()

def set_status(app, text, color=None):
    app["status_var"].set(text)
    if color:
        app["status_label"].config(fg=color)

def style_button(parent, text, bg, command, fg="white"):
    return tk.Button(
        parent,
        text=text,
        bg=bg,
        fg=fg,
        activebackground=bg,
        activeforeground=fg,
        relief="flat",
        bd=0,
        cursor="hand2",
        font=("Times New Roman", 12, "bold"),
        padx=14,
        pady=8,
        command=command,
    )

def apply_zebra(tree):
    tree.tag_configure("odd", background=THEME["zebra_odd"])
    tree.tag_configure("even", background=THEME["zebra_even"])
    for i, item in enumerate(tree.get_children()):
        tree.item(item, tags=(("even" if i % 2 == 0 else "odd"),))

def is_valid_phone(phone):
    return bool(re.fullmatch(r"0\d{9}", str(phone or "").strip()))

def is_valid_email(email):
    return bool(re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", str(email or "").strip()))

def is_valid_date(date_text):
    try:
        datetime.strptime(date_text, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def create_scrollable_form(parent, bg):
    outer = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(outer, bg=bg, highlightthickness=0, bd=0)
    v_scroll = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=v_scroll.set)

    v_scroll.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    content = tk.Frame(canvas, bg=bg)
    win = canvas.create_window((0, 0), window=content, anchor="nw")

    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_canvas_configure(event):
        canvas.itemconfig(win, width=event.width)

    content.bind("<Configure>", on_configure)
    canvas.bind("<Configure>", on_canvas_configure)

    def _on_mousewheel(event):
        try:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except:
            pass

    parent.after(200, lambda: content.bind_all("<MouseWheel>", _on_mousewheel))
    return outer, content


# =========================
# DASHBOARD
# =========================
def dashboard_tab(app):
    clear_container(app)
    ql = app["ql"]

    tk.Label(
        app["container"],
        text="HỆ THỐNG VIETNAM TRAVEL",
        font=("Times New Roman", 22, "bold"),
        bg=THEME["bg"],
        fg=THEME["text"],
    ).pack(anchor="w", pady=(0, 20))

    stats = tk.Frame(app["container"], bg=THEME["bg"])
    stats.pack(fill="x", pady=(0, 18))

    revenue = sum(safe_int(t.get("gia", 0)) * ql.get_occupied_seats(t["ma"]) for t in ql.list_tours)
    stat_items = [
        ("Doanh thu tạm tính", f"{revenue:,}đ".replace(",", "."), THEME["primary"]),
        ("Tổng tour", str(len(ql.list_tours)), THEME["warning"]),
        ("Tổng HDV", str(len(ql.list_hdv)), THEME["success"]),
        ("Tổng booking", str(len(ql.list_bookings)), THEME["danger"]),
    ]

    for title, value, color in stat_items:
        card = tk.Frame(stats, bg=THEME["surface"], bd=1, relief="solid")
        card.pack(side="left", expand=True, fill="both", padx=8)
        tk.Label(card, text=title, bg=THEME["surface"], fg=THEME["muted"], font=("Times New Roman", 13, "bold")).pack(anchor="w", padx=16, pady=(16, 6))
        tk.Label(card, text=value, bg=THEME["surface"], fg=color, font=("Times New Roman", 22, "bold")).pack(anchor="w", padx=16, pady=(0, 16))

    lower = tk.Frame(app["container"], bg=THEME["bg"])
    lower.pack(fill="both", expand=True)

    left = tk.LabelFrame(lower, text="Tác vụ quản trị nhanh", font=("Times New Roman", 14, "bold"), bg=THEME["surface"], bd=1, relief="solid", padx=15, pady=15)
    left.pack(side="left", fill="both", expand=True, padx=(0, 8))
    style_button(left, "Thêm HDV mới", THEME["success"], lambda: open_hdv_form(app)).pack(fill="x", pady=5)
    style_button(left, "Tạo tour mới", THEME["primary"], lambda: open_tour_form(app)).pack(fill="x", pady=5)
    style_button(left, "Lưu dữ liệu JSON", THEME["warning"], lambda: manual_save(app)).pack(fill="x", pady=5)
    style_button(left, "Làm mới Dashboard", THEME["primary"], lambda: dashboard_tab(app)).pack(fill="x", pady=5)

    right = tk.LabelFrame(lower, text="Ghi chú điều hành", font=("Times New Roman", 14, "bold"), bg=THEME["note_bg"], fg=THEME["note_fg"], bd=1, relief="solid", padx=15, pady=15)
    right.pack(side="left", fill="both", expand=True, padx=(8, 0))

    dynamic_notes = []

    for t in ql.list_tours:
        occupied = ql.get_occupied_seats(t["ma"])
        total = safe_int(t["khach"])

        if t["trangThai"] == "Đã chốt đoàn":
            dynamic_notes.append(f"• Tour {t['ten']} đã chốt danh sách khách.")
        elif occupied >= total and total > 0:
            dynamic_notes.append(f"• Tour {t['ten']} đã đủ khách.")
        else:
            dynamic_notes.append(f"• Tour {t['ten']} còn {max(total - occupied, 0)} chỗ trống.")
            if total > 0 and occupied < total / 2 and t["trangThai"] in ["Mở bán", "Giữ chỗ"]:
                dynamic_notes.append(f"• Tour {t['ten']} có nguy cơ hủy nếu không đủ khách (mới có {occupied} khách).")

    for t in ql.list_tours:
        if t.get("hdvPhuTrach"):
            hdv = ql.find_hdv(t["hdvPhuTrach"])
            if hdv:
                dynamic_notes.append(f"• HDV {hdv['tenHDV']} phụ trách tour {t['ten']} từ {t['ngay']}.")
        else:
            dynamic_notes.append(f"• Cần phân công HDV cho tour {t['ten']} ({t['ngay']}).")

    for h in ql.list_hdv:
        if h["trangThai"] == "Tạm nghỉ":
            dynamic_notes.append(f"• HDV {h['tenHDV']} hiện đang tạm nghỉ.")

    note_text = "\n".join(dynamic_notes[:7]) if dynamic_notes else "• Hiện không có ghi chú điều hành mới."

    tk.Label(
        right,
        text=note_text,
        justify="left",
        anchor="nw",
        bg=THEME["note_bg"],
        fg=THEME["note_fg"],
        font=("Times New Roman", 13),
        wraplength=480
    ).pack(anchor="w", fill="both", expand=True)

    set_status(app, "Đang ở Dashboard", THEME["primary"])


# =========================
# HDV MANAGEMENT
# =========================
def validate_hdv(app, form_data, old_ma=None):
    required = ["maHDV", "tenHDV", "sdt", "email", "kn", "gioiTinh", "khuVuc", "trangThai"]
    if old_ma is None:
        required.append("password")

    if not all(form_data.get(k, "").strip() for k in required):
        return False, "Vui lòng nhập đầy đủ thông tin HDV."

    if not re.fullmatch(r"HDV\d{2,}", form_data["maHDV"]):
        return False, "Mã HDV phải theo dạng HDV01, HDV02..."

    if len(form_data["tenHDV"].strip()) < 3:
        return False, "Tên HDV quá ngắn."
    if form_data.get("password") and len(form_data["password"].strip()) < 3:
        return False, "Mật khẩu quá ngắn."

    if not is_valid_phone(form_data["sdt"]):
        return False, "Số điện thoại không hợp lệ."
    if not is_valid_email(form_data["email"]):
        return False, "Email không hợp lệ."

    if not form_data["kn"].isdigit() or not (0 <= int(form_data["kn"]) <= 50):
        return False, "Kinh nghiệm phải là số từ 0 đến 50."

    for h in app["ql"].list_hdv:
        if h["maHDV"] == form_data["maHDV"] and form_data["maHDV"] != old_ma:
            return False, "Mã HDV đã tồn tại."
        if h["sdt"] == form_data["sdt"] and h["maHDV"] != old_ma:
            return False, "Số điện thoại đã tồn tại."
        if str(h["email"]).lower() == form_data["email"].lower() and h["maHDV"] != old_ma:
            return False, "Email đã tồn tại."

    return True, ""


def refresh_hdv(app, keyword=""):
    tree = app.get("tv_hdv")
    if not tree:
        return

    for item in tree.get_children():
        tree.delete(item)

    rows = app["ql"].list_hdv
    if keyword:
        kw = keyword.lower().strip()
        rows = [h for h in rows if kw in h["maHDV"].lower() or kw in h["tenHDV"].lower() or kw in h["khuVuc"].lower() or kw in h["trangThai"].lower()]

    for h in rows:
        tree.insert("", "end", values=(h["maHDV"], h["tenHDV"], h["sdt"], h["email"], h["kn"], h["khuVuc"], h["trangThai"]))
    apply_zebra(tree)
    set_status(app, f"Hiển thị {len(rows)} HDV", THEME["primary"])


def open_hdv_form(app, data=None):
    top = tk.Toplevel(app["root"])
    top.title("Thông tin hướng dẫn viên")
    top.geometry("620x520")
    top.minsize(560, 420)
    top.configure(bg=THEME["bg"])
    top.transient(app["root"])
    top.grab_set()
    top.resizable(True, True)

    card = tk.Frame(top, bg=THEME["surface"], bd=1, relief="solid")
    card.pack(fill="both", expand=True, padx=16, pady=16)

    tk.Label(card, text="THÔNG TIN HƯỚNG DẪN VIÊN", bg=THEME["surface"], fg=THEME["text"], font=("Times New Roman", 18, "bold")).pack(pady=(14, 10))

    scroll_outer, form = create_scrollable_form(card, THEME["surface"])
    scroll_outer.pack(fill="both", expand=True, padx=20, pady=(0, 10))

    password_label = "Mật khẩu mới" if data else "Mật khẩu"
    fields = [
        ("Mã HDV", "maHDV", "entry"),
        ("Tên HDV", "tenHDV", "entry"),
        (password_label, "password", "entry"),
        ("Số điện thoại", "sdt", "entry"),
        ("Email", "email", "entry"),
        ("Kinh nghiệm (năm)", "kn", "entry"),
        ("Giới tính", "gioiTinh", "combo", ["Nam", "Nữ", "Khác"]),
        ("Khu vực", "khuVuc", "combo", ["Miền Bắc", "Miền Trung", "Miền Nam"]),
        ("Trạng thái", "trangThai", "combo", HDV_STATUSES),
    ]

    widgets = {}
    for label, key, kind, *extra in fields:
        row = tk.Frame(form, bg=THEME["surface"])
        row.pack(fill="x", pady=7)
        tk.Label(row, text=label, width=16, anchor="w", bg=THEME["surface"], font=("Times New Roman", 13, "bold")).pack(side="left")

        if kind == "entry":
            w = tk.Entry(row, font=("Times New Roman", 13), relief="solid", bd=1, show="*" if key == "password" else "")
            w.pack(side="left", fill="x", expand=True, ipady=5)
        else:
            w = ttk.Combobox(row, font=("Times New Roman", 12), values=extra[0], state="readonly")
            w.pack(side="left", fill="x", expand=True, ipady=5)

        widgets[key] = w
        if data:
            if kind == "entry" and key != "password":
                widgets[key].insert(0, data.get(key, ""))
            elif kind != "entry":
                widgets[key].set(data.get(key, ""))

    if data:
        widgets["maHDV"].config(state="disabled")

    def save_hdv():
        new_data = {}
        for _, key, kind, *extra in fields:
            if data and key == "maHDV":
                new_data[key] = data["maHDV"]
            else:
                new_data[key] = widgets[key].get().strip()

        raw_password = new_data.get("password", "")
        if data and not raw_password:
            new_data["password"] = data.get("password", "")

        ok, msg = validate_hdv(app, new_data, data["maHDV"] if data else None)
        if not ok:
            messagebox.showwarning("Thông báo", msg, parent=top)
            return

        if data and raw_password:
            new_data["password"] = prepare_password_for_storage(raw_password)
        if not data:
            new_data["password"] = prepare_password_for_storage(raw_password)

        if data:
            for field in ["total_reviews", "avg_rating", "skill_score", "attitude_score", "problem_solving_score"]:
                new_data[field] = data.get(field, 0)
            for i, h in enumerate(app["ql"].list_hdv):
                if h["maHDV"] == data["maHDV"]:
                    app["ql"].list_hdv[i] = new_data
                    break
        else:
            new_data.update({
                "total_reviews": 0,
                "avg_rating": 0,
                "skill_score": 0,
                "attitude_score": 0,
                "problem_solving_score": 0
            })
            app["ql"].list_hdv.append(new_data)

        app["ql"].save()
        top.destroy()
        refresh_hdv(app, app["search_hdv_var"].get())
        set_status(app, "Đã lưu HDV thành công", THEME["success"])

    btns = tk.Frame(card, bg=THEME["surface"])
    btns.pack(fill="x", padx=20, pady=(8, 16))
    style_button(btns, "Lưu thông tin", THEME["success"], save_hdv).pack(side="left", fill="x", expand=True, padx=(0, 8))
    style_button(btns, "Hủy bỏ", THEME["danger"], top.destroy).pack(side="left", fill="x", expand=True)


def edit_hdv(app):
    sel = app["tv_hdv"].selection()
    if not sel:
        messagebox.showwarning("Thông báo", "Vui lòng chọn hướng dẫn viên cần sửa.")
        return
    ma = app["tv_hdv"].item(sel[0])["values"][0]
    hdv = app["ql"].find_hdv(ma)
    if hdv:
        open_hdv_form(app, hdv)


def delete_hdv(app):
    sel = app["tv_hdv"].selection()
    if not sel:
        messagebox.showwarning("Thông báo", "Vui lòng chọn hướng dẫn viên cần xóa.")
        return
    ma = app["tv_hdv"].item(sel[0])["values"][0]

    if any(t.get("hdvPhuTrach") == ma for t in app["ql"].list_tours):
        messagebox.showwarning("Không thể xóa", "HDV này đang được phân công phụ trách tour. Hãy thay đổi HDV của tour đó trước.")
        return

    if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa HDV {ma}?"):
        app["ql"].data["hdv"] = [h for h in app["ql"].list_hdv if h["maHDV"] != ma]
        app["ql"].save()
        refresh_hdv(app, app["search_hdv_var"].get())
        set_status(app, f"Đã xóa HDV {ma}", THEME["danger"])


def admin_hdv_tab(app):
    clear_container(app)

    tk.Label(app["container"], text="QUẢN LÝ NHÂN SỰ HƯỚNG DẪN VIÊN", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 10))

    top = tk.Frame(app["container"], bg=THEME["bg"])
    top.pack(fill="x", pady=(0, 10))

    style_button(top, "Thêm HDV", THEME["success"], lambda: open_hdv_form(app)).pack(side="left", padx=(0, 8))
    style_button(top, "Cập nhật", THEME["primary"], lambda: edit_hdv(app)).pack(side="left", padx=(0, 8))
    style_button(top, "Xóa", THEME["danger"], lambda: delete_hdv(app)).pack(side="left", padx=(0, 20))

    tk.Label(top, text="Tìm kiếm:", bg=THEME["bg"], font=("Times New Roman", 12, "bold")).pack(side="left")
    search_entry = tk.Entry(top, textvariable=app["search_hdv_var"], font=("Times New Roman", 12), relief="solid", bd=1)
    search_entry.pack(side="left", fill="x", expand=True, ipady=4)
    search_entry.bind("<Return>", lambda e: refresh_hdv(app, app["search_hdv_var"].get()))
    style_button(top, "Lọc", THEME["primary"], lambda: refresh_hdv(app, app["search_hdv_var"].get())).pack(side="left", padx=(8, 0))

    wrapper = tk.Frame(app["container"], bg=THEME["surface"], bd=1, relief="solid")
    wrapper.pack(fill="both", expand=True)
    wrapper.pack_propagate(False)

    cols = ("ma", "ten", "sdt", "email", "kn", "kv", "tt")
    tv = ttk.Treeview(wrapper, columns=cols, show="headings", height=14)
    app["tv_hdv"] = tv

    config = [
        ("ma", "Mã HDV", 90),
        ("ten", "Họ tên", 180),
        ("sdt", "SĐT", 120),
        ("email", "Email", 180),
        ("kn", "KN (Năm)", 80),
        ("kv", "Khu vực", 110),
        ("tt", "Trạng thái", 130),
    ]
    for c, t, w in config:
        tv.heading(c, text=t)
        tv.column(c, anchor="center", width=w)

    sy = ttk.Scrollbar(wrapper, orient="vertical", command=tv.yview)
    tv.configure(yscrollcommand=sy.set)
    tv.pack(side="left", fill="both", expand=True)
    sy.pack(side="right", fill="y")

    refresh_hdv(app, app["search_hdv_var"].get())


# =========================
# USER MANAGEMENT
# =========================
def refresh_users(app, keyword=""):
    tree = app.get("tv_users")
    if not tree:
        return

    for item in tree.get_children():
        tree.delete(item)

    rows = app["ql"].list_users
    if keyword:
        kw = keyword.lower().strip()
        rows = [u for u in rows if kw in u["username"].lower() or kw in u["fullname"].lower()]

    for u in rows:
        tree.insert(
            "",
            "end",
            values=(u["username"], u["fullname"], u.get("sdt", ""), mask_password(u.get("password", ""))),
        )
    apply_zebra(tree)


def open_user_form(app, data=None):
    top = tk.Toplevel(app["root"])
    top.title("Thông tin Khách hàng")
    top.geometry("520x420")
    top.minsize(480, 360)
    top.configure(bg=THEME["bg"])
    top.transient(app["root"])
    top.grab_set()
    top.resizable(True, True)

    card = tk.Frame(top, bg=THEME["surface"], bd=1, relief="solid")
    card.pack(fill="both", expand=True, padx=16, pady=16)

    tk.Label(card, text="QUẢN LÝ KHÁCH HÀNG", bg=THEME["surface"], font=("Times New Roman", 16, "bold")).pack(pady=15)

    fields = [("Tên đăng nhập", "username"), ("Mật khẩu", "password"), ("Họ và tên", "fullname"), ("Số điện thoại", "sdt")]
    widgets = {}

    for label, key in fields:
        row = tk.Frame(card, bg=THEME["surface"])
        row.pack(fill="x", padx=20, pady=5)
        tk.Label(row, text=label, width=15, anchor="w", bg=THEME["surface"], font=("Times New Roman", 12)).pack(side="left")
        show_char = "*" if key == "password" else ""
        e = tk.Entry(row, font=("Times New Roman", 12), relief="solid", bd=1, show=show_char)
        e.pack(side="left", fill="x", expand=True, ipady=3)
        if data and key != "password":
            e.insert(0, data.get(key, ""))
        widgets[key] = e

    if data:
        widgets["username"].config(state="disabled")

    tk.Label(card, text="Để trống mật khẩu nếu không muốn thay đổi.", bg=THEME["surface"], fg=THEME["muted"], font=("Times New Roman", 11, "italic")).pack(anchor="w", padx=20, pady=(5, 0))

    def save():
        username = data["username"] if data else widgets["username"].get().strip()
        password = widgets["password"].get().strip()
        fullname = widgets["fullname"].get().strip()
        sdt = widgets["sdt"].get().strip()

        if not username or not fullname:
            return messagebox.showwarning("Lỗi", "Vui lòng nhập đủ các trường bắt buộc!", parent=top)

        if not is_valid_phone(sdt):
            return messagebox.showwarning("Lỗi", "Số điện thoại không hợp lệ.", parent=top)

        if data:
            for u in app["ql"].list_users:
                if u["username"] != username and u.get("sdt") == sdt:
                    return messagebox.showwarning("Lỗi", "Số điện thoại đã tồn tại!", parent=top)
            for i, u in enumerate(app["ql"].list_users):
                if u["username"] == username:
                    app["ql"].list_users[i]["fullname"] = fullname
                    app["ql"].list_users[i]["sdt"] = sdt
                    if password:
                        if len(password) < 3:
                            return messagebox.showwarning("Lỗi", "Mật khẩu phải có ít nhất 3 ký tự.", parent=top)
                        app["ql"].list_users[i]["password"] = prepare_password_for_storage(password)
                    break
        else:
            if not password or len(password) < 3:
                return messagebox.showwarning("Lỗi", "Mật khẩu phải có ít nhất 3 ký tự.", parent=top)
            if app["ql"].find_user(username):
                return messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại!", parent=top)
            if any(u.get("sdt") == sdt for u in app["ql"].list_users):
                return messagebox.showwarning("Lỗi", "Số điện thoại đã tồn tại!", parent=top)

            app["ql"].list_users.append({
                "username": username,
                "password": prepare_password_for_storage(password),
                "fullname": fullname,
                "sdt": sdt
            })

        app["ql"].save()
        refresh_users(app)
        top.destroy()
        set_status(app, "Đã lưu khách hàng thành công", THEME["success"])

    style_button(card, "Lưu thông tin", THEME["success"], save).pack(pady=20)


def delete_user(app):
    sel = app["tv_users"].selection()
    if not sel:
        return
    username = app["tv_users"].item(sel[0])["values"][0]
    if messagebox.askyesno("Xác nhận", f"Xóa khách hàng {username}?"):
        app["ql"].data["users"] = [u for u in app["ql"].list_users if u["username"] != username]
        app["ql"].save()
        refresh_users(app)
        set_status(app, f"Đã xóa khách hàng {username}", THEME["danger"])


def admin_user_tab(app):
    clear_container(app)
    tk.Label(app["container"], text="QUẢN LÝ DANH SÁCH KHÁCH HÀNG", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 10))

    toolbar = tk.Frame(app["container"], bg=THEME["bg"])
    toolbar.pack(fill="x", pady=10)
    style_button(toolbar, "Thêm khách mới", THEME["success"], lambda: open_user_form(app)).pack(side="left", padx=5)
    style_button(toolbar, "Sửa thông tin", THEME["primary"], lambda: open_user_form(app, app["ql"].find_user(app["tv_users"].item(app["tv_users"].selection()[0])["values"][0]) if app["tv_users"].selection() else None)).pack(side="left", padx=5)
    style_button(toolbar, "Xóa khách", THEME["danger"], lambda: delete_user(app)).pack(side="left", padx=5)

    wrapper = tk.Frame(app["container"], bg=THEME["surface"], bd=1, relief="solid")
    wrapper.pack(fill="both", expand=True)

    cols = ("user", "name", "sdt", "pass")
    tv = ttk.Treeview(wrapper, columns=cols, show="headings")
    app["tv_users"] = tv

    headers = [("user", "Tên đăng nhập"), ("name", "Họ và tên"), ("sdt", "Số điện thoại"), ("pass", "Mật khẩu")]
    for cid, txt in headers:
        tv.heading(cid, text=txt)
        tv.column(cid, anchor="center", width=150)

    tv.pack(side="left", fill="both", expand=True)
    sy = ttk.Scrollbar(wrapper, orient="vertical", command=tv.yview)
    tv.configure(yscrollcommand=sy.set)
    sy.pack(side="right", fill="y")
    refresh_users(app)


# =========================
# TOUR MANAGEMENT
# =========================
def validate_tour(app, form_data, old_ma=None):
    required = ["ma", "ten", "ngay", "ngayKetThuc", "soNgay", "khach", "gia", "diemDi", "diemDen", "trangThai", "hdvPhuTrach"]

    if not all(form_data.get(k, "").strip() for k in required):
        return False, "Vui lòng nhập đầy đủ thông tin tour."

    if not re.fullmatch(r"T\d{2,}", form_data["ma"]):
        return False, "Mã tour phải theo dạng T01, T02..."

    if len(form_data["ten"].strip()) < 5:
        return False, "Tên tour quá ngắn."

    if not is_valid_date(form_data["ngay"]) or not is_valid_date(form_data["ngayKetThuc"]):
        return False, "Ngày khởi hành / kết thúc không đúng định dạng dd/mm/yyyy."

    try:
        ngay_di = datetime.strptime(form_data["ngay"], "%d/%m/%Y")
        ngay_ve = datetime.strptime(form_data["ngayKetThuc"], "%d/%m/%Y")
        if ngay_ve < ngay_di:
            return False, "Ngày kết thúc không được nhỏ hơn ngày khởi hành."
    except:
        return False, "Ngày tour không hợp lệ."

    if not form_data["khach"].isdigit() or not (1 <= int(form_data["khach"]) <= 500):
        return False, "Sức chứa tối đa phải từ 1 đến 500 khách."

    if not form_data["gia"].isdigit() or int(form_data["gia"]) <= 0:
        return False, "Giá tour phải là số dương."

    if form_data["diemDi"].strip().lower() == form_data["diemDen"].strip().lower():
        return False, "Điểm đi và điểm đến không được trùng nhau."

    if form_data["chiPhiDuKien"] and (not form_data["chiPhiDuKien"].isdigit() or int(form_data["chiPhiDuKien"]) < 0):
        return False, "Chi phí dự kiến phải là số >= 0."

    if form_data["chiPhiThucTe"] and (not form_data["chiPhiThucTe"].isdigit() or int(form_data["chiPhiThucTe"]) < 0):
        return False, "Chi phí thực tế phải là số >= 0."

    hdv = app["ql"].find_hdv(form_data["hdvPhuTrach"])
    if not hdv:
        return False, "Hướng dẫn viên phụ trách không tồn tại."
    if hdv.get("trangThai") == "Tạm nghỉ":
        return False, "Không thể phân công HDV đang ở trạng thái tạm nghỉ."

    for t in app["ql"].list_tours:
        if t["ma"] == form_data["ma"] and t["ma"] != old_ma:
            return False, "Mã tour đã tồn tại."

    existing_booked = app["ql"].get_occupied_seats(old_ma or form_data["ma"])
    if int(form_data["khach"]) < existing_booked:
        return False, f"Không thể giảm sức chứa vì đã có {existing_booked} chỗ được đặt."

    return True, ""


def refresh_tours(app, keyword=""):
    tree = app.get("tv_tour")
    if not tree:
        return

    for item in tree.get_children():
        tree.delete(item)

    rows = app["ql"].list_tours
    if keyword:
        kw = keyword.lower().strip()
        rows = [t for t in rows if kw in t["ma"].lower() or kw in t["ten"].lower() or kw in t["diemDen"].lower() or kw in t["trangThai"].lower()]

    for t in rows:
        booked = app["ql"].get_occupied_seats(t["ma"])
        tree.insert("", "end", values=(
            t["ma"], t["ten"], t["ngay"], f"{booked}/{t['khach']}",
            f"{safe_int(t['gia']):,}".replace(",", "."),
            t.get("hdvPhuTrach", ""), t["trangThai"]
        ))
    apply_zebra(tree)
    set_status(app, f"Hiển thị {len(rows)} tour", THEME["primary"])


def open_tour_form(app, data=None):
    top = tk.Toplevel(app["root"])
    top.title("Thông tin tour du lịch")
    top.geometry("760x560")
    top.minsize(680, 460)
    top.configure(bg=THEME["bg"])
    top.transient(app["root"])
    top.grab_set()
    top.resizable(True, True)

    card = tk.Frame(top, bg=THEME["surface"], bd=1, relief="solid")
    card.pack(fill="both", expand=True, padx=16, pady=16)

    tk.Label(card, text="THÔNG TIN CHI TIẾT TOUR", bg=THEME["surface"], fg=THEME["text"], font=("Times New Roman", 18, "bold")).pack(pady=(14, 10))

    scroll_outer, form = create_scrollable_form(card, THEME["surface"])
    scroll_outer.pack(fill="both", expand=True, padx=20, pady=(0, 10))

    hdv_codes = [h["maHDV"] for h in app["ql"].list_hdv]

    fields = [
        ("Mã tour", "ma", "entry"),
        ("Tên tour", "ten", "entry"),
        ("Ngày khởi hành", "ngay", "entry"),
        ("Ngày kết thúc", "ngayKetThuc", "entry"),
        ("Số ngày", "soNgay", "entry"),
        ("Sức chứa tối đa", "khach", "entry"),
        ("Giá tour (VNĐ)", "gia", "entry"),
        ("Điểm xuất phát", "diemDi", "entry"),
        ("Điểm đến", "diemDen", "entry"),
        ("Chi phí dự kiến", "chiPhiDuKien", "entry"),
        ("Chi phí thực tế", "chiPhiThucTe", "entry"),
        ("Ghi chú điều hành", "ghiChuDieuHanh", "entry"),
        ("Trạng thái", "trangThai", "combo", TOUR_STATUSES),
        ("HDV phụ trách", "hdvPhuTrach", "combo", hdv_codes),
    ]

    widgets = {}
    for label, key, kind, *extra in fields:
        row = tk.Frame(form, bg=THEME["surface"])
        row.pack(fill="x", pady=7)
        tk.Label(row, text=label, width=16, anchor="w", bg=THEME["surface"], font=("Times New Roman", 13, "bold")).pack(side="left")

        if kind == "entry":
            w = tk.Entry(row, font=("Times New Roman", 13), relief="solid", bd=1)
            w.pack(side="left", fill="x", expand=True, ipady=5)
        else:
            w = ttk.Combobox(row, font=("Times New Roman", 12), values=extra[0], state="readonly")
            w.pack(side="left", fill="x", expand=True, ipady=5)

        widgets[key] = w
        if data:
            val = data.get(key, "")
            if kind == "entry":
                w.insert(0, str(val))
            else:
                w.set(val)

    if data:
        widgets["ma"].config(state="disabled")

    def save_tour():
        form_data = {}
        for _, key, kind, *extra in fields:
            if data and key == "ma":
                form_data[key] = data["ma"]
            else:
                form_data[key] = widgets[key].get().strip()

        if form_data["trangThai"] == "Đã hủy" and (not data or data["trangThai"] != "Đã hủy"):
            booked = app["ql"].get_occupied_seats(form_data["ma"])
            if booked > 0:
                if not messagebox.askyesno("Xác nhận hủy", f"Tour '{form_data['ten']}' hiện đang có {booked} khách đặt chỗ.\nBạn vẫn chắc chắn muốn hủy tour?"):
                    return

        ok, msg = validate_tour(app, form_data, data["ma"] if data else None)
        if not ok:
            messagebox.showwarning("Thông báo", msg, parent=top)
            return

        if data:
            for i, t in enumerate(app["ql"].list_tours):
                if t["ma"] == data["ma"]:
                    app["ql"].list_tours[i] = form_data
                    break
        else:
            app["ql"].list_tours.append(form_data)

        hdv = app["ql"].find_hdv(form_data["hdvPhuTrach"])
        if hdv:
            if form_data["trangThai"] in ["Giữ chỗ", "Mở bán", "Đã chốt đoàn", "Chờ khởi hành", "Đang đi"]:
                hdv["trangThai"] = "Đã phân công" if form_data["trangThai"] in ["Giữ chỗ", "Mở bán", "Đã chốt đoàn", "Chờ khởi hành"] else "Đang dẫn tour"

        app["ql"].save()
        top.destroy()
        refresh_tours(app, app["search_tour_var"].get())
        set_status(app, "Đã lưu thông tin tour thành công", THEME["success"])

    btns = tk.Frame(card, bg=THEME["surface"])
    btns.pack(fill="x", padx=20, pady=(8, 16))
    style_button(btns, "Lưu tour", THEME["success"], save_tour).pack(side="left", fill="x", expand=True, padx=(0, 8))
    style_button(btns, "Hủy", THEME["danger"], top.destroy).pack(side="left", fill="x", expand=True)


def edit_tour(app):
    sel = app["tv_tour"].selection()
    if not sel:
        messagebox.showwarning("Thông báo", "Vui lòng chọn tour cần sửa.")
        return
    ma = app["tv_tour"].item(sel[0])["values"][0]
    tour = app["ql"].find_tour(ma)
    if tour:
        open_tour_form(app, tour)


def delete_tour(app):
    sel = app["tv_tour"].selection()
    if not sel:
        messagebox.showwarning("Thông báo", "Vui lòng chọn tour cần xóa.")
        return
    ma = app["tv_tour"].item(sel[0])["values"][0]

    tour = app["ql"].find_tour(ma)
    if not tour:
        return

    if tour.get("trangThai") in ["Đã chốt đoàn", "Chờ khởi hành", "Đang đi"]:
        messagebox.showwarning("Không thể xóa", f"Tour '{tour['ten']}' hiện đang ở trạng thái '{tour['trangThai']}'.")
        return

    active_bookings = [b for b in app["ql"].get_bookings_by_tour(ma) if b.get("trangThai") not in ["Đã hủy", "Chờ hoàn tiền", "Hoàn tiền"]]
    if active_bookings:
        messagebox.showwarning("Không thể xóa", "Tour này đã có booking đang hiệu lực. Vui lòng xử lý booking trước.")
        return

    if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa tour {ma}?"):
        app["ql"].data["tours"] = [t for t in app["ql"].list_tours if t["ma"] != ma]
        app["ql"].save()
        refresh_tours(app, app["search_tour_var"].get())
        set_status(app, f"Đã xóa tour {ma}", THEME["danger"])


def admin_tour_tab(app):
    clear_container(app)

    tk.Label(app["container"], text="QUẢN LÝ DANH SÁCH TOUR DU LỊCH", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 10))

    toolbar = tk.Frame(app["container"], bg=THEME["bg"])
    toolbar.pack(fill="x", pady=(0, 10))
    style_button(toolbar, "Thêm tour mới", THEME["success"], lambda: open_tour_form(app)).pack(side="left", padx=(0, 8))
    style_button(toolbar, "Cập nhật", THEME["primary"], lambda: edit_tour(app)).pack(side="left", padx=(0, 8))
    style_button(toolbar, "Xóa tour", THEME["danger"], lambda: delete_tour(app)).pack(side="left", padx=(0, 20))

    tk.Label(toolbar, text="Tìm kiếm:", bg=THEME["bg"], font=("Times New Roman", 12, "bold")).pack(side="left")
    search_entry = tk.Entry(toolbar, textvariable=app["search_tour_var"], font=("Times New Roman", 12), relief="solid", bd=1)
    search_entry.pack(side="left", fill="x", expand=True, ipady=4)
    search_entry.bind("<Return>", lambda e: refresh_tours(app, app["search_tour_var"].get()))
    style_button(toolbar, "Lọc", THEME["primary"], lambda: refresh_tours(app, app["search_tour_var"].get())).pack(side="left", padx=(8, 0))

    wrapper = tk.Frame(app["container"], bg=THEME["surface"], bd=1, relief="solid")
    wrapper.pack(fill="both", expand=True)

    cols = ("ma", "ten", "ngay", "khach", "gia", "hdv", "tt")
    tv = ttk.Treeview(wrapper, columns=cols, show="headings", height=10)
    app["tv_tour"] = tv

    cfg = [
        ("ma", "Mã Tour", 80),
        ("ten", "Tên tour du lịch", 240),
        ("ngay", "Khởi hành", 110),
        ("khach", "Đã đặt/Tổng", 100),
        ("gia", "Giá tour", 110),
        ("hdv", "Mã HDV", 90),
        ("tt", "Trạng thái", 130),
    ]
    for c, t, w in cfg:
        tv.heading(c, text=t)
        tv.column(c, anchor="center", width=w)

    sy = ttk.Scrollbar(wrapper, orient="vertical", command=tv.yview)
    tv.configure(yscrollcommand=sy.set)
    tv.pack(side="left", fill="both", expand=True)
    sy.pack(side="right", fill="y")

    details = tk.LabelFrame(app["container"], text="Chi tiết điều hành tour", font=("Times New Roman", 14, "bold"), bg=THEME["surface"], bd=1, relief="solid", padx=5, pady=5)
    details.pack(fill="both", expand=False, pady=(12, 0))

    content_frame = tk.Frame(details, bg=THEME["surface"])
    content_frame.pack(fill="both", expand=True)

    scrollbar = tk.Scrollbar(content_frame)
    scrollbar.pack(side="right", fill="y")

    detail_text = tk.Text(content_frame, font=("Times New Roman", 13), bg=THEME["surface"], fg=THEME["text"], height=10, bd=0, padx=10, pady=10, wrap="word", yscrollcommand=scrollbar.set)
    detail_text.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=detail_text.yview)

    detail_text.insert("1.0", "Vui lòng chọn một tour trong danh sách để xem chi tiết và danh sách khách hàng.")
    detail_text.config(state="disabled")

    def update_detail(content):
        detail_text.config(state="normal")
        detail_text.delete("1.0", "end")
        detail_text.insert("end", content)
        detail_text.config(state="disabled")

    def on_select(event):
        sel = tv.selection()
        if not sel:
            return

        ma = tv.item(sel[0])["values"][0]
        tour = app["ql"].find_tour(ma)
        bookings = app["ql"].get_bookings_by_tour(ma)
        guest_count = app["ql"].get_occupied_seats(ma)

        lines = [
            f"TOUR: {tour['ten']} ({tour['ma']})",
            f"Lộ trình: {tour.get('diemDi', '')} → {tour.get('diemDen', '')} | Khởi hành: {tour.get('ngay', '')}",
            f"Kết thúc: {tour.get('ngayKetThuc', '')} | Số ngày: {tour.get('soNgay', '')}",
            f"Giá: {safe_int(tour['gia']):,}đ | Sức chứa: {tour['khach']} | Hiện đã đặt: {guest_count}",
            f"Hướng dẫn viên: {tour.get('hdvPhuTrach', '')} | Trạng thái: {tour['trangThai']}",
            f"Chi phí dự kiến: {safe_int(tour.get('chiPhiDuKien', 0)):,}đ | Chi phí thực tế: {safe_int(tour.get('chiPhiThucTe', 0)):,}đ".replace(",", "."),
            f"Ghi chú điều hành: {tour.get('ghiChuDieuHanh', '') or 'Không có'}",
            "",
            "DANH SÁCH BOOKING HIỆN TẠI:"
        ]

        if bookings:
            for i, b in enumerate(bookings, 1):
                lines.append(
                    f"{i}. {b['maBooking']}: {b['tenKhach']} ({b['soNguoi']} người) - "
                    f"SĐT: {b['sdt']} [{b['trangThai']}] - Đã thanh toán: {safe_int(b.get('daThanhToan', 0)):,}đ".replace(",", ".")
                )
        else:
            lines.append("- (Chưa có booking nào cho tour này)")

        update_detail("\n".join(lines))
        set_status(app, f"Đang xem chi tiết tour {ma}", THEME["primary"])

    tv.bind("<<TreeviewSelect>>", on_select)
    refresh_tours(app, app["search_tour_var"].get())


# =========================
# BOOKING MANAGEMENT
# =========================
def validate_booking(app, form_data, old_ma=None):
    required = ["maBooking", "maTour", "tenKhach", "sdt", "soNguoi", "trangThai"]

    if not all(form_data.get(k, "").strip() for k in required):
        return False, "Vui lòng nhập đầy đủ thông tin booking."

    if not re.fullmatch(r"BK\d{2,}", form_data["maBooking"]):
        return False, "Mã booking phải theo dạng BK01, BK02..."

    if len(form_data["tenKhach"].strip()) < 3:
        return False, "Tên khách hàng quá ngắn."

    if not is_valid_phone(form_data["sdt"]):
        return False, "Số điện thoại khách hàng không hợp lệ."

    if not form_data["soNguoi"].isdigit() or int(form_data["soNguoi"]) <= 0:
        return False, "Số người đi phải là số nguyên dương."

    tour = app["ql"].find_tour(form_data["maTour"])
    if not tour:
        return False, "Tour được chọn không tồn tại."

    for b in app["ql"].list_bookings:
        if b["maBooking"] == form_data["maBooking"] and b["maBooking"] != old_ma:
            return False, "Mã booking này đã tồn tại."

    occupied = app["ql"].get_occupied_seats(form_data["maTour"])
    old_people = 0
    if old_ma:
        old_booking = next((b for b in app["ql"].list_bookings if b["maBooking"] == old_ma), None)
        if old_booking and old_booking["maTour"] == form_data["maTour"] and old_booking.get("trangThai") not in ["Đã hủy", "Chờ hoàn tiền", "Hoàn tiền"]:
            old_people = safe_int(old_booking["soNguoi"])

    if form_data["trangThai"] not in ["Đã hủy", "Chờ hoàn tiền", "Hoàn tiền"]:
        if occupied - old_people + int(form_data["soNguoi"]) > int(tour["khach"]):
            return False, f"Tour này không đủ chỗ cho {form_data['soNguoi']} người."

    if tour["trangThai"] in ["Hoàn tất", "Tạm hoãn", "Đã hủy"]:
        return False, f"Không thể đặt chỗ cho tour đang ở trạng thái '{tour['trangThai']}'."

    return True, ""


def refresh_bookings(app, keyword=""):
    tree = app.get("tv_booking")
    if not tree:
        return

    for item in tree.get_children():
        tree.delete(item)

    rows = app["ql"].list_bookings
    if keyword:
        kw = keyword.lower().strip()
        rows = [b for b in rows if kw in b["maBooking"].lower() or kw in b["tenKhach"].lower() or kw in b["maTour"].lower()]

    for b in rows:
        tree.insert("", "end", values=(b["maBooking"], b["maTour"], b["tenKhach"], b["sdt"], b["soNguoi"], b["trangThai"]))
    apply_zebra(tree)
    set_status(app, f"Hiển thị {len(rows)} booking", THEME["primary"])


def open_booking_form(app, data=None):
    top = tk.Toplevel(app["root"])
    top.title("Thông tin đặt chỗ (Booking)")
    top.geometry("720x560")
    top.minsize(640, 440)
    top.configure(bg=THEME["bg"])
    top.transient(app["root"])
    top.grab_set()
    top.resizable(True, True)

    card = tk.Frame(top, bg=THEME["surface"], bd=1, relief="solid")
    card.pack(fill="both", expand=True, padx=16, pady=16)

    tk.Label(card, text="THÔNG TIN ĐẶT CHỖ", bg=THEME["surface"], font=("Times New Roman", 18, "bold")).pack(pady=(14, 10))

    scroll_outer, form = create_scrollable_form(card, THEME["surface"])
    scroll_outer.pack(fill="both", expand=True, padx=20, pady=(0, 10))

    tour_codes = [t["ma"] for t in app["ql"].list_tours]

    fields = [
        ("Mã booking", "maBooking", "entry"),
        ("Mã tour", "maTour", "combo", tour_codes),
        ("Tên khách hàng", "tenKhach", "entry"),
        ("Số điện thoại", "sdt", "entry"),
        ("Số người đi", "soNguoi", "entry"),
        ("Tổng tiền", "tongTien", "entry"),
        ("Tiền cọc", "tienCoc", "entry"),
        ("Đã thanh toán", "daThanhToan", "entry"),
        ("Còn nợ", "conNo", "entry"),
        ("Hình thức thanh toán", "hinhThucThanhToan", "combo", ["Tiền mặt", "Chuyển khoản", "Thẻ"]),
        ("Nguồn khách", "nguonKhach", "combo", ["Khách lẻ", "Facebook", "Zalo", "Website", "Đại lý"]),
        ("Username đặt", "usernameDat", "entry"),
        ("Ghi chú", "ghiChu", "entry"),
        ("Trạng thái", "trangThai", "combo", BOOKING_STATUSES),
    ]

    widgets = {}
    for label, key, kind, *extra in fields:
        row = tk.Frame(form, bg=THEME["surface"])
        row.pack(fill="x", pady=7)
        tk.Label(row, text=label, width=18, anchor="w", bg=THEME["surface"], font=("Times New Roman", 13, "bold")).pack(side="left")

        if kind == "entry":
            w = tk.Entry(row, font=("Times New Roman", 13), relief="solid", bd=1)
            w.pack(side="left", fill="x", expand=True, ipady=5)
        else:
            w = ttk.Combobox(row, font=("Times New Roman", 12), values=extra[0], state="readonly")
            w.pack(side="left", fill="x", expand=True, ipady=5)

        widgets[key] = w
        if data:
            val = data.get(key, "")
            if kind == "entry":
                w.insert(0, str(val))
            else:
                w.set(val)

    if data:
        widgets["maBooking"].config(state="disabled")

    def save_booking():
        form_data = {}
        for _, key, kind, *extra in fields:
            if data and key == "maBooking":
                form_data[key] = data["maBooking"]
            else:
                form_data[key] = widgets[key].get().strip()

        for key in ["tongTien", "tienCoc", "daThanhToan", "conNo"]:
            if not form_data[key]:
                form_data[key] = "0"

        if not form_data["tongTien"].isdigit() or not form_data["tienCoc"].isdigit() or not form_data["daThanhToan"].isdigit() or not form_data["conNo"].isdigit():
            messagebox.showwarning("Thông báo", "Tiền phải là số nguyên không âm.", parent=top)
            return

        form_data["ngayDat"] = data.get("ngayDat", datetime.now().strftime("%d/%m/%Y")) if data else datetime.now().strftime("%d/%m/%Y")
        form_data["danhSachKhach"] = data.get("danhSachKhach", []) if data else []

        ok, msg = validate_booking(app, form_data, data["maBooking"] if data else None)
        if not ok:
            messagebox.showwarning("Thông báo", msg, parent=top)
            return

        if data:
            for i, b in enumerate(app["ql"].list_bookings):
                if b["maBooking"] == data["maBooking"]:
                    app["ql"].list_bookings[i] = form_data
                    break
        else:
            app["ql"].list_bookings.append(form_data)

        app["ql"].save()
        top.destroy()

        refresh_bookings(app, app["search_booking_var"].get())
        if app.get("tv_tour"):
            refresh_tours(app, app["search_tour_var"].get())

        set_status(app, "Đã lưu booking thành công", THEME["success"])

    btns = tk.Frame(card, bg=THEME["surface"])
    btns.pack(fill="x", padx=20, pady=(8, 16))
    style_button(btns, "Lưu booking", THEME["success"], save_booking).pack(side="left", fill="x", expand=True, padx=(0, 8))
    style_button(btns, "Hủy bỏ", THEME["danger"], top.destroy).pack(side="left", fill="x", expand=True)


def edit_booking(app):
    sel = app["tv_booking"].selection()
    if not sel:
        messagebox.showwarning("Thông báo", "Vui lòng chọn booking cần sửa.")
        return
    ma = app["tv_booking"].item(sel[0])["values"][0]
    booking = next((b for b in app["ql"].list_bookings if b["maBooking"] == ma), None)
    if booking:
        open_booking_form(app, booking)


def delete_booking(app):
    sel = app["tv_booking"].selection()
    if not sel:
        messagebox.showwarning("Thông báo", "Vui lòng chọn booking cần xóa.")
        return
    ma = app["tv_booking"].item(sel[0])["values"][0]

    booking = next((b for b in app["ql"].list_bookings if b["maBooking"] == ma), None)
    if booking:
        tour = app["ql"].find_tour(booking["maTour"])
        if tour and tour.get("trangThai") in ["Đã chốt đoàn", "Chờ khởi hành", "Đang đi"]:
            if not messagebox.askyesno("Cảnh báo", f"Tour '{tour['ten']}' hiện đang ở trạng thái '{tour['trangThai']}'.\nBạn vẫn chắc chắn muốn xóa?"):
                return

    if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa booking {ma}?"):
        app["ql"].data["bookings"] = [b for b in app["ql"].list_bookings if b["maBooking"] != ma]
        app["ql"].save()

        refresh_bookings(app, app["search_booking_var"].get())
        if app.get("tv_tour"):
            refresh_tours(app, app["search_tour_var"].get())

        set_status(app, f"Đã xóa booking {ma}", THEME["danger"])


def admin_booking_tab(app):
    clear_container(app)

    tk.Label(app["container"], text="QUẢN LÝ ĐẶT CHỖ & KHÁCH HÀNG", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 10))

    toolbar = tk.Frame(app["container"], bg=THEME["bg"])
    toolbar.pack(fill="x", pady=(0, 10))
    style_button(toolbar, "Thêm booking", THEME["success"], lambda: open_booking_form(app)).pack(side="left", padx=(0, 8))
    style_button(toolbar, "Cập nhật", THEME["primary"], lambda: edit_booking(app)).pack(side="left", padx=(0, 8))
    style_button(toolbar, "Xóa booking", THEME["danger"], lambda: delete_booking(app)).pack(side="left", padx=(0, 20))

    tk.Label(toolbar, text="Tìm kiếm:", bg=THEME["bg"], font=("Times New Roman", 12, "bold")).pack(side="left")
    search_entry = tk.Entry(toolbar, textvariable=app["search_booking_var"], font=("Times New Roman", 12), relief="solid", bd=1)
    search_entry.pack(side="left", fill="x", expand=True, ipady=4)
    search_entry.bind("<Return>", lambda e: refresh_bookings(app, app["search_booking_var"].get()))
    style_button(toolbar, "Lọc", THEME["primary"], lambda: refresh_bookings(app, app["search_booking_var"].get())).pack(side="left", padx=(8, 0))

    wrapper = tk.Frame(app["container"], bg=THEME["surface"], bd=1, relief="solid")
    wrapper.pack(fill="both", expand=True)

    cols = ("ma", "tour", "ten", "sdt", "songuoi", "tt")
    tv = ttk.Treeview(wrapper, columns=cols, show="headings", height=13)
    app["tv_booking"] = tv

    cfg = [
        ("ma", "Mã Booking", 100),
        ("tour", "Mã Tour", 90),
        ("ten", "Tên khách hàng", 190),
        ("sdt", "Số điện thoại", 120),
        ("songuoi", "Số người", 90),
        ("tt", "Trạng thái", 130),
    ]
    for c, t, w in cfg:
        tv.heading(c, text=t)
        tv.column(c, anchor="center", width=w)

    sy = ttk.Scrollbar(wrapper, orient="vertical", command=tv.yview)
    tv.configure(yscrollcommand=sy.set)
    tv.pack(side="left", fill="both", expand=True)
    sy.pack(side="right", fill="y")

    refresh_bookings(app, app["search_booking_var"].get())


# =========================
# FEEDBACK / NOTIFICATION
# =========================
def admin_feedback_tab(app):
    clear_container(app)

    tk.Label(app["container"], text="ĐÁNH GIÁ TỪ KHÁCH HÀNG", font=("Times New Roman", 18, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 10))

    rev_wrapper = tk.Frame(app["container"], bg=THEME["surface"], bd=1, relief="solid")
    rev_wrapper.pack(fill="both", expand=True, pady=(0, 20))

    rev_tv = ttk.Treeview(rev_wrapper, columns=("user", "target", "content", "date"), show="headings", height=8)
    rev_tv.heading("user", text="Khách hàng")
    rev_tv.heading("target", text="Đối tượng")
    rev_tv.heading("content", text="Nội dung đánh giá")
    rev_tv.heading("date", text="Ngày gửi")

    rev_tv.column("user", width=150, anchor="w")
    rev_tv.column("target", width=150, anchor="center")
    rev_tv.column("content", width=500, anchor="w")
    rev_tv.column("date", width=150, anchor="center")

    rev_tv.pack(side="left", fill="both", expand=True)
    ttk.Scrollbar(rev_wrapper, orient="vertical", command=rev_tv.yview).pack(side="right", fill="y")

    for r in app["ql"].list_reviews:
        target_display = r.get("target", "Công ty")
        if target_display == "HDV":
            target_display = f"HDV: {r.get('target_id', '')}"

        rev_tv.insert("", "end", values=(
            f"{r.get('fullname')} ({r.get('username')})",
            target_display,
            r.get("content"),
            r.get("date")
        ))
    apply_zebra(rev_tv)

    tk.Label(app["container"], text="THÔNG BÁO TỪ HƯỚNG DẪN VIÊN", font=("Times New Roman", 18, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 10))

    notif_wrapper = tk.Frame(app["container"], bg=THEME["surface"], bd=1, relief="solid")
    notif_wrapper.pack(fill="both", expand=True)

    notif_tv = ttk.Treeview(notif_wrapper, columns=("ma", "ten", "tour", "content", "date"), show="headings", height=8)
    notif_tv.heading("ma", text="Mã HDV")
    notif_tv.heading("ten", text="Tên HDV")
    notif_tv.heading("tour", text="Đoàn (Tour)")
    notif_tv.heading("content", text="Nội dung thông báo")
    notif_tv.heading("date", text="Ngày gửi")

    notif_tv.column("ma", width=100, anchor="center")
    notif_tv.column("ten", width=150, anchor="w")
    notif_tv.column("tour", width=220, anchor="w")
    notif_tv.column("content", width=400, anchor="w")
    notif_tv.column("date", width=150, anchor="center")

    notif_tv.pack(side="left", fill="both", expand=True)
    ttk.Scrollbar(notif_wrapper, orient="vertical", command=notif_tv.yview).pack(side="right", fill="y")

    for n in app["ql"].list_notifications:
        tour_info = f"{n.get('maTour', 'N/A')} - {n.get('tenTour', '')}"
        notif_tv.insert("", "end", values=(
            n.get("maHDV"),
            n.get("tenHDV"),
            tour_info,
            n.get("content"),
            n.get("date")
        ))
    apply_zebra(notif_tv)

    set_status(app, "Đang xem Đánh giá & Thông báo", THEME["primary"])


# =========================
# SYSTEM
# =========================
def manual_save(app):
    try:
        app["ql"].save()
        messagebox.showinfo("Thành công", f"Dữ liệu đã được lưu an toàn vào:\n{app['ql'].path}")
        set_status(app, "Đã lưu tệp JSON thành công", THEME["success"])
    except Exception as e:
        messagebox.showerror("Lỗi hệ thống", f"Không thể lưu tệp dữ liệu:\n{e}")
        set_status(app, "Lỗi khi lưu tệp dữ liệu", THEME["danger"])


def logout(app):
    if messagebox.askyesno("Đăng xuất", "Bạn có chắc chắn muốn thoát khỏi hệ thống quản trị?"):
        for widget in app["root"].winfo_children():
            widget.destroy()
        try:
            from GUI.Login.login import set_root, show_role_selection
            set_root(app["root"])
            app["root"].configure(bg=THEME["bg"])
            show_role_selection()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể quay lại màn hình đăng nhập.\n{e}")


# =========================
# MAIN
# =========================
def main(root=None):
    if root is None:
        root = tk.Tk()

    root.title("VIETNAM TRAVEL - HỆ THỐNG QUẢN TRỊ VIÊN")
    root.geometry("1180x720")
    root.minsize(980, 620)
    root.configure(bg=THEME["bg"])

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", font=("Times New Roman", 12), rowheight=32, background=THEME["surface"], fieldbackground=THEME["surface"], foreground=THEME["text"])
    style.configure("Treeview.Heading", font=("Times New Roman", 12, "bold"), background="#e2e8f0", foreground=THEME["text"])
    style.map("Treeview", background=[("selected", "#bfdbfe")], foreground=[("selected", THEME["text"])])

    app = {
        "root": root,
        "ql": DataStore(),
        "container": None,
        "tv_hdv": None,
        "tv_tour": None,
        "tv_booking": None,
        "tv_users": None,
        "status_var": tk.StringVar(value="Hệ thống đã sẵn sàng"),
        "status_label": None,
        "search_hdv_var": tk.StringVar(),
        "search_tour_var": tk.StringVar(),
        "search_booking_var": tk.StringVar(),
    }

    sidebar = tk.Frame(root, bg=THEME["sidebar"], width=250)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(sidebar, text="VIETNAM\nTRAVEL", justify="center", bg=THEME["sidebar"], fg="#10b981", font=("Times New Roman", 19, "bold"), pady=24).pack(fill="x")

    menu = tk.Frame(sidebar, bg=THEME["sidebar"])
    menu.pack(fill="x", padx=10)

    def menu_btn(text, cmd):
        return tk.Button(
            menu,
            text=f"   {text}",
            bg=THEME["sidebar"],
            fg="white",
            activebackground="#1e293b",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            anchor="w",
            font=("Times New Roman", 14, "bold"),
            padx=16,
            pady=14,
            command=cmd,
        )

    menu_btn("Tổng quan Dashboard", lambda: dashboard_tab(app)).pack(fill="x", pady=4)
    menu_btn("Quản lý HDV", lambda: admin_hdv_tab(app)).pack(fill="x", pady=4)
    menu_btn("Quản lý Khách hàng", lambda: admin_user_tab(app)).pack(fill="x", pady=4)
    menu_btn("Quản lý Tour", lambda: admin_tour_tab(app)).pack(fill="x", pady=4)
    menu_btn("Quản lý Booking", lambda: admin_booking_tab(app)).pack(fill="x", pady=4)
    menu_btn("Đánh giá & Thông báo", lambda: admin_feedback_tab(app)).pack(fill="x", pady=4)
    menu_btn("Lưu dữ liệu JSON", lambda: manual_save(app)).pack(fill="x", pady=4)

    tk.Frame(sidebar, bg="#334155", height=1).pack(fill="x", padx=16, pady=16)
    menu_btn("Đăng xuất hệ thống", lambda: logout(app)).pack(fill="x", pady=4)

    right_panel = tk.Frame(root, bg=THEME["bg"])
    right_panel.pack(side="right", fill="both", expand=True)

    app["container"] = tk.Frame(right_panel, bg=THEME["bg"], padx=24, pady=20)
    app["container"].pack(fill="both", expand=True)

    status_bar = tk.Frame(right_panel, bg="#e2e8f0", height=30)
    status_bar.pack(side="bottom", fill="x")
    status_bar.pack_propagate(False)

    app["status_label"] = tk.Label(
        status_bar,
        textvariable=app["status_var"],
        bg="#e2e8f0",
        fg=THEME["primary"],
        anchor="w",
        padx=10,
        font=("Times New Roman", 11, "italic")
    )
    app["status_label"].pack(fill="both", expand=True)

    dashboard_tab(app)

    if root is not None and not isinstance(root, tk.Tk):
        return
    root.mainloop()


if __name__ == "__main__":
    main()
