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
        font=("Times New Roman", 12, "bold"),
        padx=14,
        pady=8,
        command=command
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
        "tv_tours": None,
        "detail_frame": None,
    }

    for widget in root.winfo_children():
        widget.destroy()

    root.title("VIETNAM TRAVEL - HƯỚNG DẪN VIÊN")
    root.geometry("1180x720")
    root.minsize(980, 620)
    root.configure(bg=THEME["bg"])

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", font=("Times New Roman", 12), rowheight=32, background=THEME["surface"], fieldbackground=THEME["surface"], foreground=THEME["text"])
    style.configure("Treeview.Heading", font=("Times New Roman", 12, "bold"), background="#e2e8f0", foreground=THEME["text"])
    style.map("Treeview", background=[("selected", "#bfdbfe")], foreground=[("selected", THEME["text"])])

    sidebar = tk.Frame(root, bg=THEME["sidebar"], width=260)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(sidebar, text="VIETNAM\nTRAVEL", justify="center", bg=THEME["sidebar"], fg="#10b981", font=("Times New Roman", 19, "bold"), pady=24).pack(fill="x")

    ten_hdv = user_data.get("tenHDV", "Hướng Dẫn Viên")
    tk.Label(sidebar, text=f"XIN CHÀO,\n{ten_hdv}", bg=THEME["sidebar"], fg="#cbd5e1", font=("Times New Roman", 11, "bold"), pady=10, wraplength=220, justify="center").pack(fill="x")

    menu = tk.Frame(sidebar, bg=THEME["sidebar"])
    menu.pack(fill="x", padx=10, pady=20)

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

    right_panel = tk.Frame(root, bg=THEME["bg"])
    right_panel.pack(side="left", fill="both", expand=True)

    content_area = tk.Frame(right_panel, bg=THEME["bg"], padx=24, pady=20)
    content_area.pack(fill="both", expand=True)
    app["container"] = content_area

    def clear_container():
        for widget in content_area.winfo_children():
            widget.destroy()

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

        tk.Label(app["detail_frame"], text="DANH SÁCH BOOKING / KHÁCH HÀNG", font=("Times New Roman", 15, "bold"), bg=THEME["bg"], fg=THEME["primary"]).pack(anchor="w", pady=(0, 8))

        wrapper = tk.Frame(app["detail_frame"], bg=THEME["surface"], bd=1, relief="solid")
        wrapper.pack(fill="both", expand=True)

        cols = ("stt", "ten", "sdt", "sl", "tt", "thanhtoan")
        tv = ttk.Treeview(wrapper, columns=cols, show="headings", height=8)

        tv.heading("stt", text="STT")
        tv.heading("ten", text="Tên khách hàng")
        tv.heading("sdt", text="Số điện thoại")
        tv.heading("sl", text="Số người")
        tv.heading("tt", text="Trạng thái")
        tv.heading("thanhtoan", text="Đã thanh toán")

        tv.column("stt", width=50, anchor="center")
        tv.column("ten", width=220, anchor="w")
        tv.column("sdt", width=120, anchor="center")
        tv.column("sl", width=90, anchor="center")
        tv.column("tt", width=150, anchor="center")
        tv.column("thanhtoan", width=140, anchor="center")

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

        apply_zebra(tv)
        tv.pack(side="left", fill="both", expand=True)

        sy = ttk.Scrollbar(wrapper, orient="vertical", command=tv.yview)
        sx = ttk.Scrollbar(wrapper, orient="horizontal", command=tv.xview)
        tv.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x")

    def tab_danh_sach_tour():
        clear_container()

        tk.Label(content_area, text="LỊCH TRÌNH TOUR ĐƯỢC PHÂN CÔNG", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 15))

        my_tours = get_my_tours()

        wrapper = tk.Frame(content_area, bg=THEME["surface"], bd=1, relief="solid")
        wrapper.pack(fill="x")

        cols = ("ma", "ten", "ngay", "khach", "tt")
        tv = ttk.Treeview(wrapper, columns=cols, show="headings", height=6)
        app["tv_tours"] = tv

        tv.heading("ma", text="Mã Tour")
        tv.heading("ten", text="Tên Tour")
        tv.heading("ngay", text="Ngày khởi hành")
        tv.heading("khach", text="Số khách")
        tv.heading("tt", text="Trạng thái")

        tv.column("ma", width=90, anchor="center")
        tv.column("ten", width=320, anchor="w")
        tv.column("ngay", width=130, anchor="center")
        tv.column("khach", width=100, anchor="center")
        tv.column("tt", width=150, anchor="center")

        for t in my_tours:
            occupied = app["ql"].get_occupied_seats(t["ma"])
            tv.insert("", "end", values=(t["ma"], t["ten"], t["ngay"], f"{occupied}/{t['khach']}", t["trangThai"]))

        apply_zebra(tv)
        tv.pack(side="left", fill="both", expand=True)

        sy = ttk.Scrollbar(wrapper, orient="vertical", command=tv.yview)
        sx = ttk.Scrollbar(wrapper, orient="horizontal", command=tv.xview)
        tv.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x")

        tv.bind("<<TreeviewSelect>>", hien_thi_chi_tiet)

        app["detail_frame"] = tk.Frame(content_area, bg=THEME["bg"])
        app["detail_frame"].pack(fill="both", expand=True, pady=12)

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

    menu_btn("Lịch Trình Tour", tab_danh_sach_tour).pack(fill="x", pady=4)
    menu_btn("Hiệu Suất & Đánh Giá", tab_thong_ke).pack(fill="x", pady=4)
    menu_btn("Gửi Thông Báo", tab_thong_bao).pack(fill="x", pady=4)
    menu_btn("Cài Đặt Tài Khoản", tab_cai_dat).pack(fill="x", pady=4)

    tk.Frame(sidebar, bg="#334155", height=1).pack(fill="x", padx=16, pady=16)

    tk.Button(
        sidebar,
        text="   Đăng Xuất",
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
        command=lambda: logout_system(root)
    ).pack(fill="x", side="bottom", padx=10, pady=20)

    tab_danh_sach_tour()


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
