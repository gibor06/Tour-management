import json
import os
import re
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import copy

from core.security import prepare_password_for_storage
from core.system_rules import apply_system_rules

# =========================
# VALIDATION
# =========================
def is_valid_phone(phone):
    return bool(re.fullmatch(r"0\d{9}", str(phone or "").strip()))

def is_valid_email(email):
    return bool(re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", str(email or "").strip()))

def is_valid_password(pwd):
    return len(str(pwd or "").strip()) >= 3

def safe_int(value):
    try:
        return int(value)
    except:
        return 0


# =========================
# THEME
# =========================
THEME = {
    "bg": "#f1f5f9",
    "surface": "#ffffff",
    "sidebar": "#0b1220",
    "sidebar_hover": "#16233b",
    "sidebar_active": "#1e3a8a",
    "primary": "#2563eb",
    "success": "#059669",
    "danger": "#dc2626",
    "warning": "#d97706",
    "text": "#0f172a",
    "muted": "#64748b",
    "border": "#d2dae6",
    "header_bg": "#ffffff",
    "status_bg": "#e8eef8",
    "heading_bg": "#e2e8f0",
    "note_bg": "#fff7ed",
    "note_fg": "#9a3412",
    "zebra_even": "#f8fbff",
    "zebra_odd": "#ffffff",
}

HDV_STATUSES = ["Sẵn sàng", "Đã phân công", "Đang dẫn tour", "Tạm nghỉ"]
TOUR_FINISHED_STATUSES = ["Hoàn tất", "Đã hủy"]
BOOKING_CANCEL_STATUSES = ["Đã hủy", "Chờ hoàn tiền", "Hoàn tiền"]

# =========================
# PATH DỮ LIỆU
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "Admin", "data")
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
            "trangThai": "Sẵn sàng",
            "password": "123",
            "total_reviews": 0,
            "avg_rating": 0,
            "skill_score": 0,
            "attitude_score": 0,
            "problem_solving_score": 0,
        }
    ],
    "tours": [],
    "bookings": [],
    "users": [],
    "admin": {"username": "admin", "password": "123"},
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
                for key in ["hdv", "tours", "bookings", "users"]:
                    if key not in self.data:
                        self.data[key] = []
                if "admin" not in self.data:
                    self.data["admin"] = DEFAULT_DATA["admin"]
            except:
                self.data = copy.deepcopy(DEFAULT_DATA)

        for h in self.data["hdv"]:
            h.setdefault("password", "123")
            h.setdefault("trangThai", "Sẵn sàng")
            h.setdefault("total_reviews", 0)
            h.setdefault("avg_rating", 0)
            h.setdefault("skill_score", 0)
            h.setdefault("attitude_score", 0)
            h.setdefault("problem_solving_score", 0)

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
            b.setdefault("tongTien", 0)
            b.setdefault("tienCoc", 0)
            b.setdefault("daThanhToan", 0)
            b.setdefault("conNo", 0)
            b.setdefault("ghiChu", "")
            b.setdefault("danhSachKhach", [])

        self.data = apply_system_rules(self.data)

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

        self.data = apply_system_rules(self.data)
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
            if b.get("trangThai") in BOOKING_CANCEL_STATUSES:
                continue
            total += safe_int(b.get("soNguoi", 0))
        return total


# =========================
# UI HELPER
# =========================
def apply_zebra(tree):
    tree.tag_configure("odd", background=THEME["zebra_odd"])
    tree.tag_configure("even", background=THEME["zebra_even"])
    for i, item in enumerate(tree.get_children()):
        tree.item(item, tags=(("even" if i % 2 == 0 else "odd"),))

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
        font=("Times New Roman", 11, "bold"),
        padx=14,
        pady=9,
        highlightthickness=1,
        highlightbackground=bg,
        highlightcolor=bg,
        command=command,
    )

def create_scrollable_frame(parent, bg):
    outer = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(outer, bg=bg, highlightthickness=0, bd=0)
    scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    content = tk.Frame(canvas, bg=bg)

    content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas_window = canvas.create_window((0, 0), window=content, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def resize_content(event):
        canvas.itemconfig(canvas_window, width=event.width)

    canvas.bind("<Configure>", resize_content)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    return outer, content

def responsive_wraplength(widget, offset=80, min_width=260, fallback=760):
    width = widget.winfo_width()
    if width <= 1:
        return fallback
    return max(min_width, width - offset)


# =========================
# GUIDE UI
# =========================
def khoi_tao_hdv(root, user_data=None):
    if not user_data:
        user_data = {"maHDV": "HDV01", "tenHDV": "Hướng Dẫn Viên"}

    app = {
        "root": root,
        "ql": DataStore(),
        "user": user_data,
        "container": None,
        "content_canvas": None,
        "tv_tours": None,
        "detail_frame": None,
        "active_menu_btn": None,
        "page_title_var": tk.StringVar(value="Lịch Trình Tour"),
        "page_subtitle_var": tk.StringVar(value="Theo dõi các tour được phân công và danh sách khách"),
        "status_var": tk.StringVar(value="Sẵn sàng làm việc"),
        "status_label": None,
    }

    for widget in root.winfo_children():
        widget.destroy()

    root.title("VIETNAM TRAVEL - HƯỚNG DẪN VIÊN")
    root.geometry("1240x760")
    root.minsize(1040, 660)
    root.configure(bg=THEME["bg"])

    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Treeview",
        font=("Times New Roman", 12),
        rowheight=34,
        background=THEME["surface"],
        fieldbackground=THEME["surface"],
        foreground=THEME["text"],
        bordercolor=THEME["border"],
        relief="flat",
    )
    style.configure(
        "Treeview.Heading",
        font=("Times New Roman", 12, "bold"),
        background=THEME["heading_bg"],
        foreground=THEME["text"],
        relief="flat",
    )
    style.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", THEME["text"])])
    style.configure(
        "TScrollbar",
        bordercolor=THEME["border"],
        troughcolor="#eef2ff",
        background="#94a3b8",
        darkcolor="#94a3b8",
        lightcolor="#94a3b8",
    )

    sidebar = tk.Frame(root, bg=THEME["sidebar"], width=270)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    brand = tk.Frame(sidebar, bg=THEME["sidebar"])
    brand.pack(fill="x", padx=16, pady=(20, 12))
    tk.Label(
        brand,
        text="VIETNAM TRAVEL",
        justify="left",
        anchor="w",
        bg=THEME["sidebar"],
        fg="#34d399",
        font=("Times New Roman", 18, "bold"),
    ).pack(fill="x")
    tk.Label(
        brand,
        text="Guide Control Center",
        justify="left",
        anchor="w",
        bg=THEME["sidebar"],
        fg="#93c5fd",
        font=("Times New Roman", 10, "italic"),
    ).pack(fill="x", pady=(2, 0))

    ten_hdv = user_data.get("tenHDV", "Hướng Dẫn Viên")
    hello = tk.Frame(sidebar, bg="#111b30", highlightbackground="#243450", highlightthickness=1)
    hello.pack(fill="x", padx=16, pady=(0, 8))
    tk.Label(
        hello,
        text=f"XIN CHÀO,\n{ten_hdv}",
        bg="#111b30",
        fg="#dbeafe",
        font=("Times New Roman", 11, "bold"),
        pady=10,
        wraplength=220,
        justify="center",
    ).pack(fill="x")

    menu = tk.Frame(sidebar, bg=THEME["sidebar"])
    menu.pack(fill="x", padx=10, pady=(10, 0))

    def set_status(text, color=THEME["primary"]):
        app["status_var"].set(text)
        if app.get("status_label"):
            app["status_label"].config(fg=color)

    def set_active_menu(button):
        prev = app.get("active_menu_btn")
        if prev and prev.winfo_exists() and prev is not button:
            prev.configure(bg=THEME["sidebar"], fg="#dbe4f5")
        app["active_menu_btn"] = button
        button.configure(bg=THEME["sidebar_active"], fg="white")

    def menu_btn(text, cmd, icon=""):
        label = f"  {icon}  {text}" if icon else f"  {text}"
        btn = tk.Button(
            menu,
            text=label,
            bg=THEME["sidebar"],
            fg="#dbe4f5",
            activebackground=THEME["sidebar_active"],
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            anchor="w",
            font=("Times New Roman", 13, "bold"),
            padx=12,
            pady=12,
            command=cmd,
        )
        btn.bind("<Enter>", lambda _e, b=btn: b.configure(bg=THEME["sidebar_hover"]) if app.get("active_menu_btn") is not b else None)
        btn.bind("<Leave>", lambda _e, b=btn: b.configure(bg=THEME["sidebar"]) if app.get("active_menu_btn") is not b else None)
        return btn

    right_panel = tk.Frame(root, bg=THEME["bg"])
    right_panel.pack(side="left", fill="both", expand=True)

    header = tk.Frame(
        right_panel,
        bg=THEME["header_bg"],
        height=82,
        highlightbackground=THEME["border"],
        highlightthickness=1,
    )
    header.pack(side="top", fill="x", padx=16, pady=(16, 10))
    header.pack_propagate(False)

    head_left = tk.Frame(header, bg=THEME["header_bg"])
    head_left.pack(side="left", fill="both", expand=True, padx=14, pady=10)
    tk.Label(
        head_left,
        textvariable=app["page_title_var"],
        bg=THEME["header_bg"],
        fg=THEME["text"],
        font=("Times New Roman", 18, "bold"),
        anchor="w",
    ).pack(anchor="w")
    tk.Label(
        head_left,
        textvariable=app["page_subtitle_var"],
        bg=THEME["header_bg"],
        fg=THEME["muted"],
        font=("Times New Roman", 11, "italic"),
        anchor="w",
    ).pack(anchor="w", pady=(2, 0))

    content_shell = tk.Frame(right_panel, bg=THEME["bg"])
    content_shell.pack(fill="both", expand=True, padx=16)

    content_canvas = tk.Canvas(content_shell, bg=THEME["bg"], highlightthickness=0, bd=0)
    outer_sy = ttk.Scrollbar(content_shell, orient="vertical", command=content_canvas.yview)
    content_canvas.configure(yscrollcommand=outer_sy.set)

    outer_sy.pack(side="right", fill="y")
    content_canvas.pack(side="left", fill="both", expand=True)

    content_area = tk.Frame(content_canvas, bg=THEME["bg"], padx=8, pady=8)
    canvas_window = content_canvas.create_window((0, 0), window=content_area, anchor="nw")

    def on_content_configure(_event):
        content_canvas.configure(scrollregion=content_canvas.bbox("all"))

    def on_canvas_resize(event):
        content_canvas.itemconfigure(canvas_window, width=max(event.width - 2, 1))

    def on_outer_mousewheel(event):
        try:
            content_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    content_area.bind("<Configure>", on_content_configure)
    content_canvas.bind("<Configure>", on_canvas_resize)
    content_canvas.bind("<Enter>", lambda _e: content_canvas.bind_all("<MouseWheel>", on_outer_mousewheel))
    content_canvas.bind("<Leave>", lambda _e: content_canvas.unbind_all("<MouseWheel>"))

    app["container"] = content_area
    app["content_canvas"] = content_canvas

    status_bar = tk.Frame(
        right_panel,
        bg=THEME["status_bg"],
        height=34,
        highlightbackground=THEME["border"],
        highlightthickness=1,
    )
    status_bar.pack(side="bottom", fill="x", padx=16, pady=(0, 14))
    status_bar.pack_propagate(False)
    app["status_label"] = tk.Label(
        status_bar,
        textvariable=app["status_var"],
        bg=THEME["status_bg"],
        fg=THEME["primary"],
        anchor="w",
        padx=12,
        font=("Times New Roman", 11, "italic"),
    )
    app["status_label"].pack(fill="both", expand=True)

    def clear_container():
        for widget in content_area.winfo_children():
            widget.destroy()
        if app.get("content_canvas"):
            app["content_canvas"].yview_moveto(0)

    def get_my_tours():
        ma_hdv = user_data.get("maHDV", "")
        return [t for t in app["ql"].list_tours if t.get("hdvPhuTrach") == ma_hdv]

    def hien_thi_chi_tiet(event=None):
        sel = app["tv_tours"].selection()
        if not sel:
            return

        ma_tour = app["tv_tours"].item(sel[0])["values"][0]
        tour = app["ql"].find_tour(ma_tour)
        bookings = app["ql"].get_bookings_by_tour(ma_tour)

        for w in app["detail_frame"].winfo_children():
            w.destroy()

        if not tour:
            tk.Label(app["detail_frame"], text="Không tìm thấy dữ liệu tour.", font=("Times New Roman", 13), bg=THEME["bg"], fg=THEME["danger"]).pack(pady=20)
            return

        info_card = tk.Frame(app["detail_frame"], bg=THEME["surface"], bd=1, relief="solid", padx=16, pady=12)
        info_card.pack(fill="x", pady=(0, 12))

        lines = [
            f"TOUR: {tour.get('ten', '')} ({tour.get('ma', '')})",
            f"Khởi hành: {tour.get('ngay', '')} | Kết thúc: {tour.get('ngayKetThuc', '')} | Số ngày: {tour.get('soNgay', '')}",
            f"Lộ trình: {tour.get('diemDi', '')} → {tour.get('diemDen', '')}",
            f"Trạng thái: {tour.get('trangThai', '')} | Sức chứa: {tour.get('khach', '')} | Đã đặt: {app['ql'].get_occupied_seats(ma_tour)}",
            f"Ghi chú điều hành: {tour.get('ghiChuDieuHanh', '') or 'Không có'}"
        ]

        info_label = tk.Label(
            info_card,
            text="\n".join(lines),
            font=("Times New Roman", 13),
            bg=THEME["surface"],
            fg=THEME["text"],
            justify="left",
            anchor="w",
            wraplength=responsive_wraplength(info_card, offset=36, min_width=280, fallback=760),
        )
        info_label.pack(fill="x")

        def on_info_resize(event):
            info_label.configure(
                wraplength=responsive_wraplength(info_card, offset=36, min_width=280, fallback=760)
            )

        info_card.bind("<Configure>", on_info_resize)

        tk.Label(
            app["detail_frame"],
            text="DANH SÁCH BOOKING / KHÁCH HÀNG",
            font=("Times New Roman", 15, "bold"),
            bg=THEME["bg"],
            fg=THEME["primary"],
        ).pack(anchor="w", pady=(0, 8))

        wrapper = tk.Frame(app["detail_frame"], bg=THEME["surface"], bd=1, relief="solid")
        wrapper.pack(fill="both", expand=True)
        wrapper.pack_propagate(False)
        wrapper.configure(height=230)

        cols = ("stt", "ten", "sdt", "sl", "tt", "thanhtoan")
        tv = ttk.Treeview(wrapper, columns=cols, show="headings", height=7)

        tv.heading("stt", text="STT")
        tv.heading("ten", text="Tên khách hàng")
        tv.heading("sdt", text="Số điện thoại")
        tv.heading("sl", text="Số người")
        tv.heading("tt", text="Trạng thái")
        tv.heading("thanhtoan", text="Đã thanh toán")

        tv.column("stt", width=60, minwidth=50, anchor="center", stretch=False)
        tv.column("ten", width=260, minwidth=200, anchor="w", stretch=False)
        tv.column("sdt", width=130, minwidth=110, anchor="center", stretch=False)
        tv.column("sl", width=90, minwidth=80, anchor="center", stretch=False)
        tv.column("tt", width=170, minwidth=130, anchor="center", stretch=False)
        tv.column("thanhtoan", width=150, minwidth=120, anchor="center", stretch=False)

        for i, b in enumerate(bookings, 1):
            tv.insert(
                "",
                "end",
                values=(
                    i,
                    b.get("tenKhach", ""),
                    b.get("sdt", ""),
                    b.get("soNguoi", ""),
                    b.get("trangThai", ""),
                    f"{safe_int(b.get('daThanhToan', 0)):,}".replace(",", ".")
                )
            )

        if not bookings:
            tv.insert("", "end", values=("", "Chưa có booking nào cho tour này", "", "", "", ""))

        apply_zebra(tv)
        sy = ttk.Scrollbar(wrapper, orient="vertical", command=tv.yview)
        sx = ttk.Scrollbar(wrapper, orient="horizontal", command=tv.xview)
        tv.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x")
        tv.pack(side="left", fill="both", expand=True)

        def fit_booking_columns(event=None):
            width = max(760, wrapper.winfo_width() - 24)
            ratios = {"stt": 0.08, "ten": 0.32, "sdt": 0.16, "sl": 0.10, "tt": 0.20, "thanhtoan": 0.14}
            mins = {"stt": 50, "ten": 200, "sdt": 110, "sl": 80, "tt": 130, "thanhtoan": 120}
            for col in cols:
                tv.column(col, width=max(mins[col], int(width * ratios[col])))

        wrapper.bind("<Configure>", fit_booking_columns)
        fit_booking_columns()

    def tab_danh_sach_tour():
        clear_container()

        tk.Label(content_area, text="LỊCH TRÌNH TOUR ĐƯỢC PHÂN CÔNG", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 15))

        my_tours = get_my_tours()

        wrapper = tk.Frame(content_area, bg=THEME["surface"], bd=1, relief="solid")
        wrapper.pack(fill="x")
        wrapper.pack_propagate(False)
        wrapper.configure(height=290)

        cols = ("ma", "ten", "ngay", "khach", "tt")
        tv = ttk.Treeview(wrapper, columns=cols, show="headings", height=6)
        app["tv_tours"] = tv

        tv.heading("ma", text="Mã Tour")
        tv.heading("ten", text="Tên Tour")
        tv.heading("ngay", text="Ngày khởi hành")
        tv.heading("khach", text="Số khách")
        tv.heading("tt", text="Trạng thái")

        tv.column("ma", width=90, minwidth=80, anchor="center", stretch=False)
        tv.column("ten", width=360, minwidth=260, anchor="w", stretch=False)
        tv.column("ngay", width=150, minwidth=120, anchor="center", stretch=False)
        tv.column("khach", width=110, minwidth=90, anchor="center", stretch=False)
        tv.column("tt", width=150, minwidth=130, anchor="center", stretch=False)

        for t in my_tours:
            occupied = app["ql"].get_occupied_seats(t["ma"])
            tv.insert("", "end", values=(t["ma"], t["ten"], t["ngay"], f"{occupied}/{t['khach']}", t["trangThai"]))

        apply_zebra(tv)
        sy = ttk.Scrollbar(wrapper, orient="vertical", command=tv.yview)
        sx = ttk.Scrollbar(wrapper, orient="horizontal", command=tv.xview)
        tv.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x")
        tv.pack(side="left", fill="both", expand=True)

        def fit_tour_columns(event=None):
            width = max(760, wrapper.winfo_width() - 24)
            ratios = {"ma": 0.11, "ten": 0.42, "ngay": 0.18, "khach": 0.13, "tt": 0.16}
            mins = {"ma": 80, "ten": 260, "ngay": 120, "khach": 90, "tt": 130}
            for col in cols:
                tv.column(col, width=max(mins[col], int(width * ratios[col])))

        wrapper.bind("<Configure>", fit_tour_columns)
        fit_tour_columns()

        tv.bind("<<TreeviewSelect>>", hien_thi_chi_tiet)

        app["detail_frame"] = tk.Frame(content_area, bg=THEME["bg"])
        app["detail_frame"].pack(fill="both", expand=True, pady=(12, 0))

        if not my_tours:
            tk.Label(app["detail_frame"], text="Hiện tại bạn chưa có tour nào được phân công.", font=("Times New Roman", 13), bg=THEME["bg"], fg=THEME["muted"]).pack(pady=20)

    def tab_thong_ke():
        clear_container()

        tk.Label(content_area, text="HIỆU SUẤT & ĐÁNH GIÁ CỦA KHÁCH HÀNG", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 20))

        card_frame = tk.Frame(content_area, bg=THEME["bg"])
        card_frame.pack(fill="x", pady=10)

        ma_hdv = user_data.get("maHDV", "")
        h = app["ql"].find_hdv(ma_hdv)

        if not h:
            h = {
                "avg_rating": 0,
                "skill_score": 0,
                "attitude_score": 0,
                "problem_solving_score": 0,
                "total_reviews": 0
            }

        stats = [
            ("Điểm trung bình", f"{h.get('avg_rating', 0) / 20:.1f} / 5.0", THEME["warning"]),
            ("Tỷ lệ hài lòng", f"{h.get('avg_rating', 0):.1f}%", THEME["success"]),
            ("Số lượt đánh giá", str(h.get("total_reviews", 0)), THEME["primary"])
        ]

        for t, v, c in stats:
            f = tk.Frame(card_frame, bg=THEME["surface"], bd=1, relief="solid", padx=15, pady=15)
            f.pack(side="left", expand=True, fill="both", padx=8)
            tk.Label(f, text=t, font=("Times New Roman", 13, "bold"), bg=THEME["surface"], fg=THEME["muted"]).pack()
            tk.Label(f, text=v, font=("Times New Roman", 22, "bold"), fg=c, bg=THEME["surface"]).pack()

        tk.Label(content_area, text="Chỉ số đánh giá chuyên môn (%)", font=("Times New Roman", 15, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(pady=(25, 10), anchor="w")

        chart_frame = tk.Frame(content_area, bg=THEME["surface"], bd=1, relief="solid", padx=20, pady=20)
        chart_frame.pack(fill="x")

        criteria = [
            ("Kiến thức chuyên môn", h.get("skill_score", 0), THEME["primary"]),
            ("Thái độ phục vụ", h.get("attitude_score", 0), THEME["success"]),
            ("Xử lý tình huống", h.get("problem_solving_score", 0), THEME["warning"])
        ]

        for name, val, color in criteria:
            row = tk.Frame(chart_frame, bg=THEME["surface"])
            row.pack(fill="x", pady=8)

            tk.Label(row, text=name, font=("Times New Roman", 12), width=20, anchor="w", bg=THEME["surface"]).pack(side="left")

            p_bg = tk.Frame(row, bg="#e2e8f0", width=420, height=18)
            p_bg.pack(side="left", padx=15)
            p_bg.pack_propagate(False)

            fill_width = max(1, int(float(val) * 4.2)) if float(val) > 0 else 1
            tk.Frame(p_bg, bg=color, width=fill_width, height=18).pack(side="left")

            tk.Label(row, text=f"{float(val):.1f}%", font=("Times New Roman", 12, "bold"), bg=THEME["surface"]).pack(side="left")

    def tab_thong_bao():
        clear_container()

        tk.Label(content_area, text="GỬI THÔNG BÁO KHẨN CẤP", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["danger"]).pack(anchor="w", pady=(0, 10))

        card = tk.Frame(content_area, bg=THEME["surface"], bd=1, relief="solid", padx=20, pady=20)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Gửi thông báo đến đoàn (Tour):", font=("Times New Roman", 13, "bold"), bg=THEME["surface"]).pack(anchor="w", pady=(0, 5))

        my_tours = get_my_tours()
        active_tours = [t for t in my_tours if t.get("trangThai") not in TOUR_FINISHED_STATUSES]
        tour_options = [f"{t['ma']} - {t['ten']}" for t in active_tours]

        tour_var = tk.StringVar()
        tour_cb = ttk.Combobox(card, textvariable=tour_var, values=tour_options, state="readonly", font=("Times New Roman", 12), width=50)
        tour_cb.pack(anchor="w", pady=(0, 20))
        if tour_options:
            tour_cb.current(0)

        tk.Label(card, text="Nội dung thông báo:", font=("Times New Roman", 13, "bold"), bg=THEME["surface"], fg=THEME["text"]).pack(anchor="w", pady=(0, 10))

        txt = tk.Text(card, height=10, font=("Times New Roman", 13), relief="solid", bd=1, wrap="word")
        txt.pack(fill="both", expand=True, pady=(0, 20))

        def gui_thong_bao():
            content = txt.get("1.0", "end").strip()

            if not tour_var.get():
                return messagebox.showwarning("Lỗi", "Vui lòng chọn đoàn khách muốn gửi thông báo!")
            if not content:
                return messagebox.showwarning("Lỗi", "Vui lòng nhập nội dung thông báo!")

            selected = tour_var.get().split(" - ", 1)
            selected_tour_ma = selected[0]
            selected_tour_ten = selected[1] if len(selected) > 1 else ""

            new_notif = {
                "maHDV": user_data.get("maHDV", "N/A"),
                "tenHDV": user_data.get("tenHDV", "Hướng Dẫn Viên"),
                "maTour": selected_tour_ma,
                "tenTour": selected_tour_ten,
                "content": content,
                "date": datetime.now().strftime("%d/%m/%Y %H:%M")
            }

            app["ql"].notifications.append(new_notif)
            app["ql"].save()

            messagebox.showinfo("Thành công", f"Đã gửi thông báo đến đoàn '{selected_tour_ten}'!")
            tab_danh_sach_tour()

        style_button(card, "XÁC NHẬN GỬI THÔNG BÁO", THEME["danger"], gui_thong_bao).pack()

    def tab_cai_dat():
        clear_container()

        tk.Label(content_area, text="CÀI ĐẶT TÀI KHOẢN CÁ NHÂN", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 20))

        outer, scroll_content = create_scrollable_frame(content_area, THEME["bg"])
        outer.pack(fill="both", expand=True)

        card = tk.Frame(scroll_content, bg=THEME["surface"], bd=1, relief="solid", padx=30, pady=30)
        card.pack(pady=10, fill="x")

        ma_hdv = user_data.get("maHDV", "")
        hdv_data = app["ql"].find_hdv(ma_hdv)

        if not hdv_data:
            tk.Label(card, text="Lỗi: Không tìm thấy thông tin tài khoản!", fg=THEME["danger"], bg=THEME["surface"]).pack()
            return

        fields = [
            ("Họ và tên", "tenHDV"),
            ("Số điện thoại", "sdt"),
            ("Email", "email"),
            ("Mật khẩu mới", "password")
        ]
        widgets = {}

        for label, key in fields:
            row = tk.Frame(card, bg=THEME["surface"])
            row.pack(fill="x", pady=8)
            tk.Label(row, text=label, width=15, anchor="w", bg=THEME["surface"], font=("Times New Roman", 12, "bold")).pack(side="left")

            show_char = "*" if key == "password" else ""
            e = tk.Entry(row, font=("Times New Roman", 12), relief="solid", bd=1, width=34, show=show_char)
            e.pack(side="left", ipady=3)

            if key != "password":
                e.insert(0, hdv_data.get(key, ""))
            widgets[key] = e

        tk.Label(card, text="Để trống mật khẩu nếu không muốn thay đổi.", bg=THEME["surface"], fg=THEME["muted"], font=("Times New Roman", 11, "italic")).pack(anchor="w", pady=(4, 10))

        def save_profile():
            new_name = widgets["tenHDV"].get().strip()
            new_phone = widgets["sdt"].get().strip()
            new_email = widgets["email"].get().strip()
            new_pass = widgets["password"].get().strip()

            if len(new_name) < 3:
                return messagebox.showwarning("Lỗi", "Họ tên quá ngắn (tối thiểu 3 ký tự).")
            if not is_valid_phone(new_phone):
                return messagebox.showwarning("Lỗi", "Số điện thoại không hợp lệ.")
            if not is_valid_email(new_email):
                return messagebox.showwarning("Lỗi", "Định dạng email không hợp lệ.")
            if new_pass and not is_valid_password(new_pass):
                return messagebox.showwarning("Lỗi", "Mật khẩu quá ngắn (tối thiểu 3 ký tự).")

            for h in app["ql"].list_hdv:
                if h.get("maHDV") == ma_hdv:
                    continue
                if h.get("sdt") == new_phone:
                    return messagebox.showwarning("Lỗi", "Số điện thoại đã tồn tại ở HDV khác.")
                if str(h.get("email", "")).lower() == new_email.lower():
                    return messagebox.showwarning("Lỗi", "Email đã tồn tại ở HDV khác.")

            hdv_data["tenHDV"] = new_name
            hdv_data["sdt"] = new_phone
            hdv_data["email"] = new_email
            if new_pass:
                hdv_data["password"] = prepare_password_for_storage(new_pass)

            user_data["tenHDV"] = new_name
            app["ql"].save()
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin cá nhân thành công!")
            tab_cai_dat()

        style_button(card, "CẬP NHẬT THÔNG TIN", THEME["success"], save_profile).pack(pady=20)

    def open_view(title, subtitle, view_fn, button):
        set_active_menu(button)
        app["page_title_var"].set(title)
        app["page_subtitle_var"].set(subtitle)
        view_fn()
        set_status(f"Đang ở {title}", THEME["primary"])

    nav_items = [
        ("Lịch Trình Tour", "Theo dõi các tour được phân công và danh sách khách", tab_danh_sach_tour, "▣"),
        ("Hiệu Suất & Đánh Giá", "Tổng hợp hiệu suất và phản hồi từ khách hàng", tab_thong_ke, "◈"),
        ("Gửi Thông Báo", "Gửi thông báo khẩn cấp đến từng đoàn tour", tab_thong_bao, "✦"),
        ("Cài Đặt Tài Khoản", "Quản lý thông tin cá nhân của hướng dẫn viên", tab_cai_dat, "⚙"),
    ]

    nav_buttons = []
    for idx, (title, subtitle, view_fn, icon) in enumerate(nav_items):
        btn = menu_btn(
            title,
            lambda t=title, s=subtitle, f=view_fn, b_idx=idx: open_view(t, s, f, nav_buttons[b_idx]),
            icon=icon,
        )
        btn.pack(fill="x", pady=3)
        nav_buttons.append(btn)

    util = tk.Frame(sidebar, bg=THEME["sidebar"])
    util.pack(side="bottom", fill="x", padx=10, pady=14)

    tk.Frame(util, bg="#2e3b56", height=1).pack(fill="x", pady=(0, 10))
    tk.Button(
        util,
        text="  ⏻  Đăng xuất hệ thống",
        bg="#7f1d1d",
        fg="white",
        activebackground="#991b1b",
        activeforeground="white",
        relief="flat",
        bd=0,
        cursor="hand2",
        anchor="w",
        font=("Times New Roman", 12, "bold"),
        padx=12,
        pady=10,
        command=lambda: logout_system(root),
    ).pack(fill="x")

    open_view(
        "Lịch Trình Tour",
        "Theo dõi các tour được phân công và danh sách khách",
        tab_danh_sach_tour,
        nav_buttons[0],
    )


def logout_system(root):
    if messagebox.askyesno("Xác nhận", "Bạn có muốn đăng xuất khỏi hệ thống?"):
        for widget in root.winfo_children():
            widget.destroy()
        try:
            from GUI.Login.login import set_root, show_role_selection
            set_root(root)
            root.configure(bg=THEME["bg"])
            show_role_selection()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể quay lại màn hình đăng nhập.\n{e}")
