import json
import os
import re
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import copy

from core.security import prepare_password_for_storage

# =========================
# VALIDATION
# =========================
def is_valid_phone(phone):
    return bool(re.fullmatch(r"0\d{9}", str(phone or "").strip()))

def is_valid_password(pwd):
    return len(str(pwd or "").strip()) >= 3

def is_valid_fullname(name):
    return len(str(name or "").strip()) >= 3

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

TOUR_BOOKABLE_STATUSES = ["Giữ chỗ", "Mở bán"]
TOUR_LOCK_CANCEL_STATUSES = ["Đã chốt đoàn", "Chờ khởi hành", "Đang đi", "Hoàn tất"]
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
            "problem_solving_score": 0
        }
    ],
    "tours": [],
    "bookings": [],
    "users": [],
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
                for key in ["hdv", "tours", "bookings", "users"]:
                    if key not in self.data:
                        self.data[key] = []
                if "admin" not in self.data:
                    self.data["admin"] = DEFAULT_DATA["admin"]
            except:
                self.data = copy.deepcopy(DEFAULT_DATA)

        for h in self.data["hdv"]:
            h.setdefault("password", "123")
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

    def find_tour(self, ma_tour):
        return next((t for t in self.list_tours if t.get("ma") == ma_tour), None)

    def find_hdv(self, ma_hdv):
        return next((h for h in self.list_hdv if h.get("maHDV") == ma_hdv), None)

    def get_occupied_seats(self, ma_tour):
        total = 0
        for b in self.list_bookings:
            if b.get("maTour") == ma_tour and b.get("trangThai") not in BOOKING_CANCEL_STATUSES:
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
        parent, text=text, bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
        relief="flat", bd=0, cursor="hand2", font=("Times New Roman", 12, "bold"),
        padx=14, pady=8, command=command
    )


# =========================
# USER UI
# =========================
def khoi_tao_khach(root, user_data=None):
    if not user_data:
        user_data = {"username": "Khach", "name": "Khách hàng", "fullname": "Khách hàng", "sdt": ""}

    app = {
        "root": root,
        "ql": DataStore(),
        "user": user_data,
        "container": None,
        "tv_tours": None,
        "detail_var": tk.StringVar(value="Chọn một tour để xem chi tiết và đăng ký.")
    }

    for widget in root.winfo_children():
        widget.destroy()

    root.title("VIETNAM TRAVEL - KHÁCH HÀNG")
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

    hello_name = user_data.get("fullname") or user_data.get("name", "Khách hàng")
    tk.Label(sidebar, text=f"XIN CHÀO,\n{hello_name}", bg=THEME["sidebar"], fg="#cbd5e1", font=("Times New Roman", 11, "bold"), pady=10, wraplength=220, justify="center").pack(fill="x")

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

    def get_current_user():
        username = user_data.get("username", "")
        return app["ql"].find_user(username)

    def my_bookings():
        username = user_data.get("username", "")
        return [b for b in app["ql"].list_bookings if b.get("usernameDat") == username]

    def tab_danh_sach_tour():
        clear_container()

        tk.Label(content_area, text="KHÁM PHÁ CÁC TOUR DU LỊCH", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 15))

        wrapper = tk.Frame(content_area, bg=THEME["surface"], bd=1, relief="solid")
        wrapper.pack(fill="x")

        cols = ("ma", "ten", "ngay", "gia", "khach", "tt")
        tv = ttk.Treeview(wrapper, columns=cols, show="headings", height=8)
        app["tv_tours"] = tv

        tv.heading("ma", text="Mã")
        tv.heading("ten", text="Tên Tour Du Lịch")
        tv.heading("ngay", text="Khởi hành")
        tv.heading("gia", text="Giá vé")
        tv.heading("khach", text="Chỗ trống")
        tv.heading("tt", text="Trạng thái")

        tv.column("ma", width=60, anchor="center")
        tv.column("ten", width=300, anchor="w")
        tv.column("ngay", width=120, anchor="center")
        tv.column("gia", width=120, anchor="center")
        tv.column("khach", width=100, anchor="center")
        tv.column("tt", width=120, anchor="center")

        for t in app["ql"].list_tours:
            if t.get("trangThai") in TOUR_BOOKABLE_STATUSES:
                occupied = app["ql"].get_occupied_seats(t["ma"])
                available = max(safe_int(t["khach"]) - occupied, 0)
                tv.insert("", "end", values=(
                    t["ma"],
                    t["ten"],
                    t["ngay"],
                    f"{safe_int(t['gia']):,}đ".replace(",", "."),
                    f"{available} chỗ",
                    t["trangThai"]
                ))

        apply_zebra(tv)
        tv.pack(fill="x")

        detail_fr = tk.LabelFrame(content_area, text="Chi tiết tour & Đăng ký", font=("Times New Roman", 14, "bold"), bg=THEME["surface"], bd=1, relief="solid", padx=15, pady=15)
        detail_fr.pack(fill="both", expand=True, pady=15)

        lbl_detail = tk.Label(detail_fr, textvariable=app["detail_var"], justify="left", font=("Times New Roman", 13), bg=THEME["surface"], anchor="w", wraplength=720)
        lbl_detail.pack(side="left", fill="both", expand=True)

        action_fr = tk.Frame(detail_fr, bg=THEME["surface"])
        action_fr.pack(side="right", padx=10)

        tk.Label(action_fr, text="Số người đi:", font=("Times New Roman", 12, "bold"), bg=THEME["surface"]).pack(pady=(0, 5))

        spn_people = tk.Spinbox(action_fr, from_=1, to=50, width=10, font=("Times New Roman", 12), relief="solid", bd=1, justify="center")
        spn_people.pack(pady=(0, 15))

        def on_select(event):
            sel = tv.selection()
            if not sel:
                return
            ma = tv.item(sel[0])["values"][0]
            t = app["ql"].find_tour(ma)
            hdv = app["ql"].find_hdv(t.get("hdvPhuTrach"))
            occupied = app["ql"].get_occupied_seats(ma)
            available = max(safe_int(t["khach"]) - occupied, 0)
            spn_people.config(to=max(1, available))

            info = [
                f"TOUR: {t['ten']} ({t['ma']})",
                f"Lộ trình: {t.get('diemDi', '')} → {t.get('diemDen', '')}",
                f"Khởi hành: {t['ngay']} | Kết thúc: {t.get('ngayKetThuc', '')} | Số ngày: {t.get('soNgay', '')}",
                f"Giá: {safe_int(t['gia']):,}đ".replace(",", "."),
                f"Hướng dẫn viên: {hdv['tenHDV'] if hdv else 'Chưa phân công'} - SĐT: {hdv['sdt'] if hdv else 'N/A'}",
                f"Trạng thái: {t['trangThai']} | Còn trống: {available} chỗ",
                f"Ghi chú điều hành: {t.get('ghiChuDieuHanh', '') or 'Không có'}"
            ]
            app["detail_var"].set("\n".join(info))

        tv.bind("<<TreeviewSelect>>", on_select)

        def dang_ky_tour():
            sel = tv.selection()
            if not sel:
                return messagebox.showwarning("Chú ý", "Vui lòng chọn một tour để đăng ký!")

            num_people = safe_int(spn_people.get())
            if num_people <= 0:
                return messagebox.showwarning("Lỗi", "Số người đi không hợp lệ!")

            ma = tv.item(sel[0])["values"][0]
            t = app["ql"].find_tour(ma)
            if not t:
                return

            if t.get("trangThai") not in TOUR_BOOKABLE_STATUSES:
                return messagebox.showwarning("Không thể đăng ký", f"Tour đang ở trạng thái '{t.get('trangThai', '')}'.")

            occupied = app["ql"].get_occupied_seats(ma)
            available = max(safe_int(t["khach"]) - occupied, 0)

            if num_people > available:
                return messagebox.showerror("Hết chỗ", f"Rất tiếc, tour này chỉ còn {available} chỗ trống!")

            existing_ids = []
            for b in app["ql"].list_bookings:
                ma_bk = str(b.get("maBooking", ""))
                if ma_bk.startswith("BK"):
                    try:
                        existing_ids.append(int(ma_bk[2:]))
                    except:
                        pass
            next_id = max(existing_ids, default=0) + 1
            new_id = f"BK{next_id:02d}"

            user_info = get_current_user()
            fullname = user_info.get("fullname", user_data.get("fullname", user_data.get("name", "Khách hàng"))) if user_info else user_data.get("fullname", "Khách hàng")
            sdt_khach = user_info.get("sdt", "Chưa cập nhật") if user_info else user_data.get("sdt", "Chưa cập nhật")

            tong_tien = safe_int(t.get("gia", 0)) * num_people

            new_booking = {
                "maBooking": new_id,
                "maTour": ma,
                "tenKhach": fullname,
                "sdt": sdt_khach,
                "soNguoi": str(num_people),
                "trangThai": "Mới tạo",
                "ngayDat": datetime.now().strftime("%d/%m/%Y"),
                "tongTien": tong_tien,
                "tienCoc": 0,
                "daThanhToan": 0,
                "conNo": tong_tien,
                "hinhThucThanhToan": "Tiền mặt",
                "nguonKhach": "Khách lẻ",
                "ghiChu": "",
                "usernameDat": user_data.get("username", ""),
                "danhSachKhach": []
            }

            app["ql"].list_bookings.append(new_booking)
            app["ql"].save()

            messagebox.showinfo("Thành công", f"Bạn đã đăng ký tour {t['ten']} cho {num_people} người thành công!\nMã đặt chỗ: {new_id}")
            tab_danh_sach_tour()

        style_button(action_fr, "ĐĂNG KÝ NGAY", THEME["success"], dang_ky_tour).pack(fill="x")

    def tab_tour_da_dat():
        clear_container()

        tk.Label(content_area, text="LỊCH SỬ ĐẶT TOUR CỦA BẠN", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 20))

        bookings = my_bookings()

        if not bookings:
            tk.Label(content_area, text="Bạn chưa tham gia tour nào.", font=("Times New Roman", 13), bg=THEME["bg"], fg=THEME["muted"]).pack(pady=50)
            return

        for b in bookings:
            t = app["ql"].find_tour(b["maTour"])
            if not t:
                continue

            card = tk.Frame(content_area, bg=THEME["surface"], bd=1, relief="solid", padx=15, pady=10)
            card.pack(fill="x", pady=5)

            left = tk.Frame(card, bg=THEME["surface"])
            left.pack(side="left", fill="both", expand=True)

            tk.Label(left, text=f"✅ {t['ten']}", font=("Times New Roman", 14, "bold"), bg=THEME["surface"], fg=THEME["primary"]).pack(anchor="w")

            tk.Label(
                left,
                text=(
                    f"Mã: {b['maBooking']} | Ngày: {t['ngay']} | Số người: {b['soNguoi']} | "
                    f"Trạng thái: {b['trangThai']} | Đã thanh toán: {safe_int(b.get('daThanhToan', 0)):,}đ".replace(",", ".")
                ),
                font=("Times New Roman", 12),
                bg=THEME["surface"],
                wraplength=760,
                justify="left"
            ).pack(anchor="w", pady=(4, 0))

            style_button(card, "Hủy", THEME["danger"], lambda m=b["maBooking"]: huy_tour(m)).pack(side="right")

    def huy_tour(ma_booking):
        booking = next((b for b in app["ql"].list_bookings if b["maBooking"] == ma_booking), None)
        if not booking:
            return

        t = app["ql"].find_tour(booking["maTour"])
        if t and t.get("trangThai") in TOUR_LOCK_CANCEL_STATUSES:
            messagebox.showwarning(
                "Không thể hủy",
                f"Tour '{t['ten']}' hiện đang ở trạng thái '{t['trangThai']}'.\n"
                "Bạn không thể tự hủy booking này. Vui lòng liên hệ quản trị viên để được hỗ trợ."
            )
            return

        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn hủy đặt chỗ {ma_booking}?"):
            if safe_int(booking.get("daThanhToan", 0)) > 0:
                booking["trangThai"] = "Chờ hoàn tiền"
            else:
                booking["trangThai"] = "Đã hủy"
            app["ql"].save()
            messagebox.showinfo("Thành công", f"Đã cập nhật trạng thái booking {ma_booking} thành '{booking['trangThai']}'.")
            tab_tour_da_dat()

    def tab_gui_danh_gia():
        clear_container()

        tk.Label(content_area, text="GỬI Ý KIẾN PHẢN HỒI", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 20))

        card = tk.Frame(content_area, bg=THEME["surface"], bd=1, relief="solid", padx=25, pady=25)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Bạn muốn đánh giá cho đối tượng nào?", font=("Times New Roman", 13, "bold"), bg=THEME["surface"]).pack(anchor="w")

        target_var = tk.StringVar(value="Công ty")
        target_fr = tk.Frame(card, bg=THEME["surface"])
        target_fr.pack(fill="x", pady=(5, 15))

        tk.Radiobutton(target_fr, text="Công ty Vietnam Travel", variable=target_var, value="Công ty", bg=THEME["surface"], font=("Times New Roman", 12)).pack(side="left", padx=(0, 20))
        tk.Radiobutton(target_fr, text="Hướng dẫn viên", variable=target_var, value="HDV", bg=THEME["surface"], font=("Times New Roman", 12)).pack(side="left")

        my_hdvs = []
        for b in my_bookings():
            t = app["ql"].find_tour(b["maTour"])
            if t and t.get("hdvPhuTrach"):
                h = app["ql"].find_hdv(t["hdvPhuTrach"])
                if h and h not in my_hdvs:
                    my_hdvs.append(h)

        hdv_options = [f"{h['maHDV']} - {h['tenHDV']}" for h in my_hdvs]
        hdv_var = tk.StringVar()

        hdv_sel_fr = tk.Frame(card, bg=THEME["surface"])
        tk.Label(hdv_sel_fr, text="Chọn Hướng dẫn viên:", font=("Times New Roman", 12), bg=THEME["surface"]).pack(side="left", padx=(0, 10))
        hdv_cb = ttk.Combobox(hdv_sel_fr, textvariable=hdv_var, values=hdv_options, state="readonly", width=30, font=("Times New Roman", 11))
        hdv_cb.pack(side="left")

        score_fr = tk.Frame(card, bg=THEME["surface"])
        scores = {}

        criteria = [
            ("Kiến thức chuyên môn", "skill"),
            ("Thái độ phục vụ", "attitude"),
            ("Xử lý tình huống", "problem")
        ]

        for label, key in criteria:
            row = tk.Frame(score_fr, bg=THEME["surface"])
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label, width=20, anchor="w", bg=THEME["surface"], font=("Times New Roman", 12)).pack(side="left")
            s = tk.Scale(row, from_=0, to=100, orient="horizontal", bg=THEME["surface"], length=300, showvalue=True, highlightthickness=0)
            s.set(80)
            s.pack(side="left")
            scores[key] = s

        def update_ui(*args):
            if target_var.get() == "HDV":
                hdv_sel_fr.pack(fill="x", pady=(0, 15), before=txt_label)
                score_fr.pack(fill="x", pady=(0, 15), before=txt_label)
            else:
                hdv_sel_fr.pack_forget()
                score_fr.pack_forget()

        target_var.trace_add("write", update_ui)

        txt_label = tk.Label(card, text="Nội dung nhận xét chi tiết:", font=("Times New Roman", 12, "bold"), bg=THEME["surface"])
        txt_label.pack(anchor="w")

        txt = tk.Text(card, height=6, font=("Times New Roman", 13), relief="solid", bd=1, wrap="word")
        txt.pack(fill="both", expand=True, pady=(5, 20))

        def update_hdv_metrics(ma_hdv, review_data):
            h = app["ql"].find_hdv(ma_hdv)
            if not h:
                return

            for f in ["total_reviews", "skill_score", "attitude_score", "problem_solving_score", "avg_rating"]:
                if f not in h:
                    h[f] = 0

            n = h["total_reviews"]
            h["skill_score"] = round((h["skill_score"] * n + review_data["skill"]) / (n + 1), 1)
            h["attitude_score"] = round((h["attitude_score"] * n + review_data["attitude"]) / (n + 1), 1)
            h["problem_solving_score"] = round((h["problem_solving_score"] * n + review_data["problem"]) / (n + 1), 1)
            h["total_reviews"] += 1
            h["avg_rating"] = round((h["skill_score"] + h["attitude_score"] + h["problem_solving_score"]) / 3, 1)

        def gui_review():
            content = txt.get("1.0", "end").strip()
            if not content:
                return messagebox.showwarning("Lỗi", "Vui lòng nhập nội dung đánh giá!")

            target = target_var.get()
            selected_hdv_code = ""

            if target == "HDV":
                if not hdv_var.get():
                    return messagebox.showwarning("Lỗi", "Vui lòng chọn Hướng dẫn viên muốn đánh giá!")
                selected_hdv_code = hdv_var.get().split(" - ")[0]

            fullname = user_data.get("fullname") or user_data.get("name", "Khách hàng")

            new_review = {
                "username": user_data.get("username", "N/A"),
                "fullname": fullname,
                "target": target,
                "target_id": selected_hdv_code,
                "content": content,
                "date": datetime.now().strftime("%d/%m/%Y %H:%M")
            }

            if target == "HDV":
                new_review.update({
                    "skill": scores["skill"].get(),
                    "attitude": scores["attitude"].get(),
                    "problem": scores["problem"].get()
                })
                update_hdv_metrics(selected_hdv_code, new_review)

            app["ql"].reviews.append(new_review)
            app["ql"].save()

            messagebox.showinfo("Cảm ơn", "Cảm ơn bạn đã gửi phản hồi cho chúng tôi!")
            tab_danh_sach_tour()

        style_button(card, "GỬI NHẬN XÉT", THEME["primary"], gui_review).pack()
        update_ui()

    def tab_ho_so():
        clear_container()

        tk.Label(content_area, text="THÔNG TIN HỒ SƠ CÁ NHÂN", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 20))

        card = tk.Frame(content_area, bg=THEME["surface"], bd=1, relief="solid", padx=30, pady=30)
        card.pack(pady=10)

        user_info = get_current_user()
        if not user_info:
            tk.Label(card, text="Lỗi: Không tìm thấy thông tin tài khoản!", fg=THEME["danger"], bg=THEME["surface"]).pack()
            return

        fields = [("Họ và tên", "fullname"), ("Số điện thoại", "sdt"), ("Mật khẩu mới", "password")]
        widgets = {}

        for label, key in fields:
            row = tk.Frame(card, bg=THEME["surface"])
            row.pack(fill="x", pady=8)
            tk.Label(row, text=label, width=15, anchor="w", bg=THEME["surface"], font=("Times New Roman", 12, "bold")).pack(side="left")

            show_char = "*" if key == "password" else ""
            e = tk.Entry(row, font=("Times New Roman", 12), relief="solid", bd=1, width=30, show=show_char)
            e.pack(side="left", ipady=3)
            if key != "password":
                e.insert(0, user_info.get(key, ""))
            widgets[key] = e

        tk.Label(card, text="Để trống mật khẩu nếu không muốn thay đổi.", bg=THEME["surface"], fg=THEME["muted"], font=("Times New Roman", 11, "italic")).pack(anchor="w", pady=(4, 10))

        def save_profile():
            new_fullname = widgets["fullname"].get().strip()
            new_phone = widgets["sdt"].get().strip()
            new_pass = widgets["password"].get().strip()

            if not is_valid_fullname(new_fullname):
                return messagebox.showwarning("Lỗi", "Họ tên quá ngắn (tối thiểu 3 ký tự).")
            if not is_valid_phone(new_phone):
                return messagebox.showwarning("Lỗi", "Số điện thoại không hợp lệ (10 số, bắt đầu bằng 0).")
            if new_pass and not is_valid_password(new_pass):
                return messagebox.showwarning("Lỗi", "Mật khẩu quá ngắn (tối thiểu 3 ký tự).")

            for u in app["ql"].list_users:
                if u.get("username") == user_info.get("username"):
                    continue
                if u.get("sdt") == new_phone:
                    return messagebox.showwarning("Lỗi", "Số điện thoại đã tồn tại ở tài khoản khác.")

            user_info["fullname"] = new_fullname
            user_info["sdt"] = new_phone
            if new_pass:
                user_info["password"] = prepare_password_for_storage(new_pass)

            user_data["fullname"] = new_fullname
            user_data["name"] = new_fullname
            user_data["sdt"] = new_phone

            app["ql"].save()
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin cá nhân thành công!")
            khoi_tao_khach(root, user_data)

        style_button(card, "LƯU THÔNG TIN", THEME["success"], save_profile).pack(pady=20)

    def tab_thong_bao():
        clear_container()

        tk.Label(content_area, text="THÔNG BÁO TỪ ĐOÀN DU LỊCH", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["danger"]).pack(anchor="w", pady=(0, 20))

        my_tour_ids = [b["maTour"] for b in my_bookings()]
        relevant_notifs = [n for n in app["ql"].list_notifications if n.get("maTour") in my_tour_ids]
        relevant_notifs.sort(key=lambda x: x.get("date", ""), reverse=True)

        if not relevant_notifs:
            tk.Label(content_area, text="Hiện chưa có thông báo nào từ đoàn của bạn.", font=("Times New Roman", 13), bg=THEME["bg"], fg=THEME["muted"]).pack(pady=50)
            return

        canvas = tk.Canvas(content_area, bg=THEME["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_area, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=THEME["bg"])

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for n in relevant_notifs:
            card = tk.Frame(scrollable_frame, bg=THEME["surface"], bd=1, relief="solid", padx=20, pady=15)
            card.pack(fill="x", pady=8)

            header_fr = tk.Frame(card, bg=THEME["surface"])
            header_fr.pack(fill="x")

            tk.Label(header_fr, text=f"📢 {n.get('tenTour', 'Thông báo')}", font=("Times New Roman", 14, "bold"), bg=THEME["surface"], fg=THEME["danger"]).pack(side="left")
            tk.Label(header_fr, text=n.get("date", ""), font=("Times New Roman", 11), bg=THEME["surface"], fg=THEME["muted"]).pack(side="right")

            tk.Label(card, text=f"HDV: {n.get('tenHDV', 'N/A')}", font=("Times New Roman", 12, "italic"), bg=THEME["surface"], fg=THEME["primary"]).pack(anchor="w", pady=(5, 10))

            msg = tk.Label(card, text=n.get("content", ""), font=("Times New Roman", 13), bg=THEME["surface"], justify="left", wraplength=800)
            msg.pack(anchor="w")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    menu_btn("Khám phá Tour", tab_danh_sach_tour).pack(fill="x", pady=4)
    menu_btn("Tour đã đặt", tab_tour_da_dat).pack(fill="x", pady=4)
    menu_btn("Thông báo", tab_thong_bao).pack(fill="x", pady=4)
    menu_btn("Gửi đánh giá", tab_gui_danh_gia).pack(fill="x", pady=4)
    menu_btn("Hồ sơ cá nhân", tab_ho_so).pack(fill="x", pady=4)

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
        command=lambda: logout_user(root)
    ).pack(fill="x", side="bottom", padx=10, pady=20)

    tab_danh_sach_tour()


def logout_user(root):
    if messagebox.askyesno("Xác nhận", "Bạn có muốn đăng xuất?"):
        for widget in root.winfo_children():
            widget.destroy()
        try:
            from GUI.Login.login import set_root, show_role_selection
            set_root(root)
            root.configure(bg=THEME["bg"])
            show_role_selection()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể quay lại màn hình đăng nhập.\n{e}")


if __name__ == "__main__":
    win = tk.Tk()
    win.title("Vietnam Travel 2026")
    win.geometry("1180x720")
    win.minsize(980, 620)
    khoi_tao_khach(win, {"username": "Khach", "name": "Khách hàng", "fullname": "Khách hàng mẫu", "sdt": "0988111222"})
    win.mainloop()
