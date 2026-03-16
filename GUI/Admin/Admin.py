import json
import os
import re
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import copy

from core.activity_log import write_activity_log
from core.security import mask_password, prepare_password_for_storage
from core.validation import is_valid_fullname, is_valid_password, is_valid_username

# CẤU HÌNH GIAO DIỆN
THEME = {
    "bg": "#f8fafc",        # Màu nền chính
    "surface": "#ffffff",   # Màu nền các thẻ/panel
    "sidebar": "#0f172a",   # Màu nền thanh menu bên trái
    "primary": "#2563eb",   # Màu chính
    "success": "#059669",   # Màu thành công/lưu
    "danger": "#dc2626",    # Màu cảnh báo/xóa
    "warning": "#d97706",   # Màu cảnh báo/chú ý
    "text": "#0f172a",      # Màu chữ chính
    "muted": "#64748b",     # Màu chữ phụ 
    "border": "#cbd5e1",    # Màu đường viền
    "note_bg": "#fff7ed",   # Màu nền ghi chú 
    "note_fg": "#9a3412",   # Màu chữ ghi chú
    "zebra_even": "#f8fafc", # Màu dòng chẵn bảng 
    "zebra_odd": "#ffffff",  # Màu dòng lẻ bảng
}

# Đường dẫn các tệp dữ liệu JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "vietnam_travel_data.json")
REVIEWS_FILE = os.path.join(DATA_DIR, "vietnam_travel_reviews.json")
NOTIF_FILE = os.path.join(DATA_DIR, "vietnam_travel_notifications.json")

# Dữ liệu mặc định nếu không tìm thấy tệp JSON
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
        },
        {
            "maHDV": "HDV02",
            "tenHDV": "Trần Minh Khoa",
            "sdt": "0912345678",
            "email": "khoa@travel.com",
            "kn": "3",
            "gioiTinh": "Nam",
            "khuVuc": "Miền Trung",
            "trangThai": "Đang dẫn tour",
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
            "khach": "20",
            "gia": "2250000",
            "diemDi": "TP.HCM",
            "diemDen": "Đà Lạt",
            "trangThai": "Mở bán",
            "hdvPhuTrach": "HDV01"
        },
        {
            "ma": "T02",
            "ten": "Sapa Mây Núi",
            "ngay": "20/03/2026",
            "khach": "15",
            "gia": "3450000",
            "diemDi": "Hà Nội",
            "diemDen": "Sapa",
            "trangThai": "Đã chốt",
            "hdvPhuTrach": "HDV02"
        }
    ],
    "bookings": [
        {
            "maBooking": "BK01",
            "maTour": "T01",
            "tenKhach": "Trần Thế Hệ",
            "sdt": "0988111222",
            "soNguoi": "2",
            "trangThai": "Đã cọc"
        }
    ],
    "users": [
        {"username": "Khach", "password": "123", "fullname": "Khách hàng mẫu", "sdt": "0988111222"}
    ],
    "admin": {"username": "admin", "password": "123"}
}


class DataStore:
    """Lớp quản lý việc lưu trữ và truy xuất dữ liệu từ các file JSON."""

    def __init__(self, path=DATA_FILE, rev_path=REVIEWS_FILE, notif_path=NOTIF_FILE):
        self.path = path
        self.rev_path = rev_path
        self.notif_path = notif_path
        self.data = {"hdv": [], "tours": [], "bookings": [], "users": [], "admin": {}}
        self.reviews = []
        self.notifications = []
        self.load()

    def load(self):
        """Tải dữ liệu từ các tệp JSON."""
        # 1. Tải dữ liệu chính
        if not os.path.exists(self.path):
            self.data = copy.deepcopy(DEFAULT_DATA)
            self.save()
        else:
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                for key in ["hdv", "tours", "bookings", "users"]:
                    if key not in self.data: self.data[key] = []
                
                # Tự kiểm tra và bổ sung các trường dữ liệu còn thiếu cho HDV
                rating_fields = {
                    "total_reviews": 0, "avg_rating": 0, "skill_score": 0, 
                    "attitude_score": 0, "problem_solving_score": 0
                }
                for h in self.data["hdv"]:
                    if "password" not in h: h["password"] = "123"
                    for field, default_val in rating_fields.items():
                        if field not in h: h[field] = default_val

                if "admin" not in self.data: self.data["admin"] = DEFAULT_DATA["admin"]
            except:
                self.data = copy.deepcopy(DEFAULT_DATA)

        # 2. Tải đánh giá
        if os.path.exists(self.rev_path):
            try:
                with open(self.rev_path, "r", encoding="utf-8") as f:
                    self.reviews = json.load(f)
            except: self.reviews = []
        else: self.reviews = []

        # 3. Tải thông báo
        if os.path.exists(self.notif_path):
            try:
                with open(self.notif_path, "r", encoding="utf-8") as f:
                    self.notifications = json.load(f)
            except: self.notifications = []
        else: self.notifications = []

    def save(self):
        """Lưu trạng thái dữ liệu hiện tại vào các tệp JSON tương ứng."""
        folder = os.path.dirname(self.path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

        # Lưu dữ liệu chính (Bỏ reviews và notifications khỏi file này nếu có)
        clean_data = copy.deepcopy(self.data)
        if "reviews" in clean_data: del clean_data["reviews"]
        if "notifications" in clean_data: del clean_data["notifications"]
        for hdv in clean_data.get("hdv", []):
            hdv["password"] = prepare_password_for_storage(hdv.get("password", ""))
        for user in clean_data.get("users", []):
            user["password"] = prepare_password_for_storage(user.get("password", ""))
        admin = clean_data.get("admin", {})
        if isinstance(admin, dict):
            admin["password"] = prepare_password_for_storage(admin.get("password", ""))
        
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(clean_data, f, ensure_ascii=False, indent=2)

        # Lưu đánh giá riêng
        with open(self.rev_path, "w", encoding="utf-8") as f:
            json.dump(self.reviews, f, ensure_ascii=False, indent=2)

        # Lưu thông báo riêng
        with open(self.notif_path, "w", encoding="utf-8") as f:
            json.dump(self.notifications, f, ensure_ascii=False, indent=2)

    @property
    def list_hdv(self): return self.data["hdv"]
    @property
    def list_tours(self): return self.data["tours"]
    @property
    def list_bookings(self): return self.data["bookings"]
    @property
    def list_users(self): return self.data["users"]
    @property
    def list_reviews(self): return self.reviews
    @property
    def list_notifications(self): return self.notifications

    def find_user(self, username):
        """Tìm người dùng theo username."""
        return next((u for u in self.list_users if u["username"] == username), None)

    def find_hdv(self, ma_hdv):
        """Tìm hướng dẫn viên theo mã."""
        return next((h for h in self.list_hdv if h["maHDV"] == ma_hdv), None)

    def find_tour(self, ma_tour):
        """Tìm tour theo mã."""
        return next((t for t in self.list_tours if t["ma"] == ma_tour), None)

    def get_bookings_by_tour(self, ma_tour):
        """Lấy tất cả các booking thuộc về một tour cụ thể."""
        return [b for b in self.list_bookings if b["maTour"] == ma_tour]

    def get_occupied_seats(self, ma_tour):
        """Tính tổng số người đã đặt chỗ trong một tour."""
        total = 0
        for b in self.get_bookings_by_tour(ma_tour):
            try:
                total += int(b.get("soNguoi", 0))
            except (ValueError, TypeError):
                pass
        return total



# CÁC HÀM TIỆN ÍCH GIAO DIỆN
def clear_container(app):
    """Xóa tất cả các widget con trong container chính."""
    for widget in app["container"].winfo_children():
        widget.destroy()


def set_status(app, text, color=None):
    """Cập nhật nội dung và màu sắc của thanh trạng thái."""
    app["status_var"].set(text)
    if color:
        app["status_label"].config(fg=color)


def style_button(parent, text, bg, command, fg="white"):
    """Tạo một nút bấm được tùy chỉnh giao diện (Custom Styled Button)."""
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
    """Áp dụng hiệu ứng sọc vằn (Zebra stripe) cho bảng Treeview."""
    tree.tag_configure("odd", background=THEME["zebra_odd"])
    tree.tag_configure("even", background=THEME["zebra_even"])
    for i, item in enumerate(tree.get_children()):
        tree.item(item, tags=(("even" if i % 2 == 0 else "odd"),))


# CÁC HÀM KIỂM TRA DỮ LIỆU (VALIDATION)
def is_valid_phone(phone):
    """Kiểm tra số điện thoại (10 chữ số, bắt đầu bằng số 0)."""
    return bool(re.fullmatch(r"0\d{9}", phone))


def is_valid_email(email):
    """Kiểm tra định dạng email."""
    return bool(re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", email))


def is_valid_date(date_text):
    """Kiểm tra định dạng ngày tháng (dd/mm/yyyy)."""
    try:
        datetime.strptime(date_text, "%d/%m/%Y")
        return True
    except ValueError:
        return False


def safe_int(value):
    """Chuyển đổi giá trị sang kiểu int một cách an toàn."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0



# DASHBOARD TAB
def dashboard_tab(app):
    """Hiển thị giao diện trang chủ Dashboard."""
    clear_container(app)
    ql = app["ql"]

    # Tiêu đề trang
    tk.Label(
        app["container"],
        text="HỆ THỐNG VIETNAM TRAVEL",
        font=("Times New Roman", 22, "bold"),
        bg=THEME["bg"],
        fg=THEME["text"],
    ).pack(anchor="w", pady=(0, 20))

    # Khu vực thống kê (Thẻ thống kê)
    stats = tk.Frame(app["container"], bg=THEME["bg"])
    stats.pack(fill="x", pady=(0, 18))

    # Tính toán doanh thu và các chỉ số
    revenue = sum(safe_int(t.get("gia", 0)) * ql.get_occupied_seats(t["ma"]) for t in ql.list_tours)
    stat_items = [
        ("Doanh thu tạm tính", f"{revenue:,}đ".replace(",", "."), THEME["primary"]),
        ("Tổng tour", str(len(ql.list_tours)), THEME["warning"]),
        ("Tổng HDV", str(len(ql.list_hdv)), THEME["success"]),
        ("Tổng booking", str(len(ql.list_bookings)), THEME["danger"]),
    ]

    # Vẽ các thẻ thống kê
    for title, value, color in stat_items:
        card = tk.Frame(stats, bg=THEME["surface"], bd=1, relief="solid")
        card.pack(side="left", expand=True, fill="both", padx=8)
        tk.Label(card, text=title, bg=THEME["surface"], fg=THEME["muted"], font=("Times New Roman", 13, "bold")).pack(anchor="w", padx=16, pady=(16, 6))
        tk.Label(card, text=value, bg=THEME["surface"], fg=color, font=("Times New Roman", 22, "bold")).pack(anchor="w", padx=16, pady=(0, 16))

    # Khu vực bên dưới (Tác vụ nhanh & Ghi chú)
    lower = tk.Frame(app["container"], bg=THEME["bg"])
    lower.pack(fill="both", expand=True)

    # 1. Tác vụ quản trị nhanh (Cột bên trái)
    left = tk.LabelFrame(lower, text="Tác vụ quản trị nhanh", font=("Times New Roman", 14, "bold"), bg=THEME["surface"], bd=1, relief="solid", padx=15, pady=15)
    left.pack(side="left", fill="both", expand=True, padx=(0, 8))
    style_button(left, "Thêm HDV mới", THEME["success"], lambda: open_hdv_form(app)).pack(fill="x", pady=5)
    style_button(left, "Tạo tour mới", THEME["primary"], lambda: open_tour_form(app)).pack(fill="x", pady=5)
    style_button(left, "Lưu dữ liệu JSON", THEME["warning"], lambda: manual_save(app)).pack(fill="x", pady=5)
    style_button(left, "Làm mới Dashboard", THEME["primary"], lambda: dashboard_tab(app)).pack(fill="x", pady=5)

    # 2. Ghi chú điều hành động (Cột bên phải)
    right = tk.LabelFrame(lower, text="Ghi chú điều hành", font=("Times New Roman", 14, "bold"), bg=THEME["note_bg"], fg=THEME["note_fg"], bd=1, relief="solid", padx=15, pady=15)
    right.pack(side="left", fill="both", expand=True, padx=(8, 0))
    
    # Logic sinh ghi chú động
    dynamic_notes = []
    
    # --- Ghi chú về Tour ---
    for t in ql.list_tours:
        occupied = ql.get_occupied_seats(t["ma"])
        total = safe_int(t["khach"])
        
        if t["trangThai"] == "Đã chốt":
            dynamic_notes.append(f"• Tour {t['ten']} đã chốt danh sách khách.")
        elif occupied >= total:
            dynamic_notes.append(f"• Tour {t['ten']} đã đủ khách.")
        else:
            dynamic_notes.append(f"• Tour {t['ten']} còn {total - occupied} chỗ trống.")
            # Cảnh báo nếu sắp đi mà khách quá ít (giả định ít hơn 50%)
            if occupied < total / 2 and t["trangThai"] == "Mở bán":
                dynamic_notes.append(f"• Tour {t['ten']} có nguy cơ hủy nếu không đủ khách (mới có {occupied} khách).")

    # --- Ghi chú về HDV ---
    for t in ql.list_tours:
        if t.get("hdvPhuTrach"):
            hdv = ql.find_hdv(t["hdvPhuTrach"])
            if hdv:
                dynamic_notes.append(f"• HDV {hdv['tenHDV']} dẫn tour {t['ten']} từ {t['ngay']}.")
        else:
            dynamic_notes.append(f"• Cần phân công HDV cho tour {t['ten']} ({t['ngay']}).")
            
    for h in ql.list_hdv:
        if h["trangThai"] == "Tạm nghỉ":
            dynamic_notes.append(f"• HDV {h['tenHDV']} hiện đang tạm nghỉ.")

    # Giới hạn hiển thị 7 ghi chú quan trọng nhất
    note_text = "\n".join(dynamic_notes[:7]) if dynamic_notes else "• Hiện không có ghi chú điều hành mới."
    
    tk.Label(right, text=note_text, justify="left", bg=THEME["note_bg"], fg=THEME["note_fg"], font=("Times New Roman", 13)).pack(anchor="w")

    set_status(app, "Đang ở Dashboard", THEME["primary"])



# QUẢN LÝ HƯỚNG DẪN VIÊN (HDV MANAGEMENT)
def validate_hdv(app, form_data, old_ma=None):
    """Kiểm tra tính hợp lệ của dữ liệu hướng dẫn viên trước khi lưu."""
    required = ["maHDV", "tenHDV", "sdt", "email", "kn", "gioiTinh", "khuVuc", "trangThai"]
    if old_ma is None:
        required.append("password")
    
    # 1. Kiểm tra để trống
    if not all(form_data.get(k, "").strip() for k in required):
        return False, "Vui lòng nhập đầy đủ thông tin HDV."
    
    # 2. Kiểm tra định dạng mã HDV (HDVxx)
    if not re.fullmatch(r"HDV\d{2,}", form_data["maHDV"]):
        return False, "Mã HDV phải theo dạng HDV01, HDV02..."
    
    # 3. Kiểm tra độ dài tên và mật khẩu
    if len(form_data["tenHDV"].strip()) < 3:
        return False, "Tên HDV quá ngắn (tối thiểu 3 ký tự)."
    if form_data.get("password") and not is_valid_password(form_data["password"].strip()):
        return False, "Mật khẩu quá ngắn (tối thiểu 3 ký tự)."
    
    # 4. Kiểm tra số điện thoại và email
    if not is_valid_phone(form_data["sdt"]):
        return False, "Số điện thoại phải có 10 số và bắt đầu bằng 0."
    if not is_valid_email(form_data["email"]):
        return False, "Email không hợp lệ."
    
    # 5. Kiểm tra kinh nghiệm
    if not form_data["kn"].isdigit() or not (0 <= int(form_data["kn"]) <= 50):
        return False, "Kinh nghiệm phải là số từ 0 đến 50."

    # 6. Kiểm tra trùng lặp dữ liệu (Mã, SĐT, Email)
    for h in app["ql"].list_hdv:
        if h["maHDV"] == form_data["maHDV"] and form_data["maHDV"] != old_ma:
            return False, "Mã HDV đã tồn tại."
        if h["sdt"] == form_data["sdt"] and h["maHDV"] != old_ma:
            return False, "Số điện thoại đã tồn tại."
        if h["email"].lower() == form_data["email"].lower() and h["maHDV"] != old_ma:
            return False, "Email đã tồn tại."
            
    return True, ""


def refresh_hdv(app, keyword=""):
    """Làm mới danh sách hiển thị HDV trong Treeview, có hỗ trợ tìm kiếm."""
    tree = app.get("tv_hdv")
    if not tree:
        return

    # Xóa dữ liệu cũ trong bảng
    for item in tree.get_children():
        tree.delete(item)

    rows = app["ql"].list_hdv
    # Lọc dữ liệu theo từ khóa nếu có
    if keyword:
        kw = keyword.lower().strip()
        rows = [
            h for h in rows
            if kw in h["maHDV"].lower() or kw in h["tenHDV"].lower() or kw in h["khuVuc"].lower() or kw in h["trangThai"].lower()
        ]

    # Đưa dữ liệu vào bảng
    for h in rows:
        tree.insert(
            "",
            "end",
            values=(h["maHDV"], h["tenHDV"], h["sdt"], h["email"], h["kn"], h["khuVuc"], h["trangThai"]),
        )
    apply_zebra(tree)
    set_status(app, f"Hiển thị {len(rows)} HDV", THEME["primary"])


def open_hdv_form(app, data=None):
    """Mở cửa sổ nhập liệu/chỉnh sửa thông tin HDV."""
    top = tk.Toplevel(app["root"])
    top.title("Thông tin hướng dẫn viên")
    top.geometry("560x600")
    top.configure(bg=THEME["bg"])
    top.transient(app["root"])
    top.grab_set()

    # Thẻ chứa form
    card = tk.Frame(top, bg=THEME["surface"], bd=1, relief="solid")
    card.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(card, text="THÔNG TIN HƯỚNG DẪN VIÊN", bg=THEME["surface"], fg=THEME["text"], font=("Times New Roman", 18, "bold")).pack(pady=(18, 12))

    form = tk.Frame(card, bg=THEME["surface"])
    form.pack(fill="both", expand=True, padx=25)

    # Cấu hình các trường nhập liệu
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
        ("Trạng thái", "trangThai", "combo", ["Sẵn sàng", "Đang dẫn tour", "Tạm nghỉ"]),
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
        # Điền dữ liệu nếu là chế độ chỉnh sửa
        if data:
            if kind == "entry" and key != "password":
                widgets[key].insert(0, data[key])
            elif kind != "entry":
                widgets[key].set(data[key])

    # Không cho sửa mã HDV khi đang ở chế độ chỉnh sửa
    if data:
        widgets["maHDV"].config(state="disabled")

    def save_hdv():
        """Hàm nội bộ xử lý việc lưu dữ liệu từ form."""
        new_data = {}
        for _, key, kind, *extra in fields:
            if data and key == "maHDV":
                new_data[key] = data["maHDV"]
            else:
                new_data[key] = widgets[key].get().strip()

        if data and not new_data["password"]:
            new_data["password"] = data.get("password", "")
        elif new_data["password"]:
            new_data["password"] = prepare_password_for_storage(new_data["password"])
                
        # Kiểm tra tính hợp lệ
        ok, msg = validate_hdv(app, new_data, data["maHDV"] if data else None)
        if not ok:
            messagebox.showwarning("Thông báo", msg, parent=top)
            return

        # Cập nhật danh sách HDV
        if data:
            # Giữ nguyên các chỉ số đánh giá khi cập nhật
            for field in ["total_reviews", "avg_rating", "skill_score", "attitude_score", "problem_solving_score"]:
                if field in data:
                    new_data[field] = data[field]
            
            for i, h in enumerate(app["ql"].list_hdv):
                if h["maHDV"] == data["maHDV"]:
                    app["ql"].list_hdv[i] = new_data
                    break
        else:
            # Khởi tạo các trường đánh giá cho HDV mới
            new_data.update({
                "total_reviews": 0,
                "avg_rating": 0,
                "skill_score": 0,
                "attitude_score": 0,
                "problem_solving_score": 0
            })
            app["ql"].list_hdv.append(new_data)

        # Lưu vào JSON và cập nhật giao diện
        app["ql"].save()
        write_activity_log(
            action="SAVE_GUIDE",
            actor="admin",
            role="admin",
            status="SUCCESS",
            detail=f"Lưu hồ sơ hướng dẫn viên {new_data['maHDV']}.",
            datastore=app["ql"],
        )
        top.destroy()
        refresh_hdv(app, app["search_hdv_var"].get())
        set_status(app, "Đã lưu HDV thành công", THEME["success"])

    # Nút bấm
    btns = tk.Frame(card, bg=THEME["surface"])
    btns.pack(fill="x", padx=25, pady=20)
    style_button(btns, "Lưu thông tin", THEME["success"], save_hdv).pack(side="left", fill="x", expand=True, padx=(0, 8))
    style_button(btns, "Hủy bỏ", THEME["danger"], top.destroy).pack(side="left", fill="x", expand=True)


def edit_hdv(app):
    """Lấy HDV được chọn từ bảng và mở form chỉnh sửa."""
    sel = app["tv_hdv"].selection()
    if not sel:
        messagebox.showwarning("Thông báo", "Vui lòng chọn hướng dẫn viên cần sửa.")
        return
    ma = app["tv_hdv"].item(sel[0])["values"][0]
    hdv = app["ql"].find_hdv(ma)
    if hdv:
        open_hdv_form(app, hdv)


def delete_hdv(app):
    """Xóa HDV được chọn sau khi kiểm tra các ràng buộc."""
    sel = app["tv_hdv"].selection()
    if not sel:
        messagebox.showwarning("Thông báo", "Vui lòng chọn hướng dẫn viên cần xóa.")
        return
    ma = app["tv_hdv"].item(sel[0])["values"][0]
    
    # Kiểm tra xem HDV có đang phụ trách tour nào không
    if any(t.get("hdvPhuTrach") == ma for t in app["ql"].list_tours):
        messagebox.showwarning("Không thể xóa", "HDV này đang được phân công phụ trách tour. Hãy thay đổi HDV của tour đó trước.")
        return
        
    if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa HDV {ma}?"):
        app["ql"].data["hdv"] = [h for h in app["ql"].list_hdv if h["maHDV"] != ma]
        app["ql"].save()
        write_activity_log(
            action="DELETE_GUIDE",
            actor="admin",
            role="admin",
            status="SUCCESS",
            detail=f"Xóa hướng dẫn viên {ma}.",
            datastore=app["ql"],
        )
        refresh_hdv(app, app["search_hdv_var"].get())
        set_status(app, f"Đã xóa HDV {ma}", THEME["danger"])


def admin_hdv_tab(app):
    """Hiển thị tab quản lý hướng dẫn viên."""
    clear_container(app)

    tk.Label(app["container"], text="QUẢN LÝ NHÂN SỰ HƯỚNG DẪN VIÊN", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 10))

    # Thanh công cụ (Nút bấm & Tìm kiếm)
    top = tk.Frame(app["container"], bg=THEME["bg"])
    top.pack(fill="x", pady=(0, 10))

    style_button(top, "Thêm HDV", THEME["success"], lambda: open_hdv_form(app)).pack(side="left", padx=(0, 8))
    style_button(top, "Cập nhật", THEME["primary"], lambda: edit_hdv(app)).pack(side="left", padx=(0, 8))
    style_button(top, "Xóa", THEME["danger"], lambda: delete_hdv(app)).pack(side="left", padx=(0, 20))

    tk.Label(top, text="Tìm kiếm:", bg=THEME["bg"], font=("Times New Roman", 12, "bold")).pack(side="left")
    search_entry = tk.Entry(top, textvariable=app["search_hdv_var"], font=("Times New Roman", 12), relief="solid", bd=1)
    search_entry.pack(side="left", fill="x", expand=True, ipady=4)
    # Tự động lọc khi nhấn Enter
    search_entry.bind("<Return>", lambda e: refresh_hdv(app, app["search_hdv_var"].get()))
    style_button(top, "Lọc", THEME["primary"], lambda: refresh_hdv(app, app["search_hdv_var"].get())).pack(side="left", padx=(8, 0))

    # Khu vực bảng dữ liệu
    wrapper = tk.Frame(app["container"], bg=THEME["surface"], bd=1, relief="solid")
    wrapper.pack(fill="both", expand=True)

    cols = ("ma", "ten", "sdt", "email", "kn", "kv", "tt")
    tv = ttk.Treeview(wrapper, columns=cols, show="headings", height=14)
    app["tv_hdv"] = tv
    
    config = [
        ("ma", "Mã HDV", 90),
        ("ten", "Họ tên", 180),
        ("sdt", "SĐT", 120),
        ("email", "Email", 180),
        ("kn", "KN (Năm)", 70),
        ("kv", "Khu vực", 110),
        ("tt", "Trạng thái", 120),
    ]
    for c, t, w in config:
        tv.heading(c, text=t)
        tv.column(c, anchor="center", width=w)
        
    sy = ttk.Scrollbar(wrapper, orient="vertical", command=tv.yview)
    tv.configure(yscrollcommand=sy.set)
    tv.pack(side="left", fill="both", expand=True)
    sy.pack(side="right", fill="y")

    refresh_hdv(app, app["search_hdv_var"].get())



# QUẢN LÝ KHÁCH HÀNG (USER MANAGEMENT)

def refresh_users(app, keyword=""):
    """Làm mới danh sách khách hàng."""
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
            values=(u["username"], u["fullname"], u.get("sdt", "N/A"), mask_password(u.get("password", ""))),
        )
    apply_zebra(tree)

def open_user_form(app, data=None):
    """Mở form thêm/sửa khách hàng."""
    top = tk.Toplevel(app["root"])
    top.title("Thông tin Khách hàng")
    top.geometry("450x450")
    top.configure(bg=THEME["bg"])
    top.transient(app["root"])
    top.grab_set()

    card = tk.Frame(top, bg=THEME["surface"], bd=1, relief="solid")
    card.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(card, text="QUẢN LÝ KHÁCH HÀNG", bg=THEME["surface"], font=("Times New Roman", 16, "bold")).pack(pady=15)

    password_label = "Mật khẩu mới" if data else "Mật khẩu"
    fields = [("Tên đăng nhập", "username"), (password_label, "password"), ("Họ và tên", "fullname"), ("Số điện thoại", "sdt")]
    widgets = {}

    for label, key in fields:
        row = tk.Frame(card, bg=THEME["surface"])
        row.pack(fill="x", padx=20, pady=5)
        tk.Label(row, text=label, width=15, anchor="w", bg=THEME["surface"], font=("Times New Roman", 12)).pack(side="left")
        e = tk.Entry(row, font=("Times New Roman", 12), relief="solid", bd=1, show="*" if key == "password" else "")
        e.pack(side="left", fill="x", expand=True, ipady=3)
        if data and key != "password":
            e.insert(0, data.get(key, ""))
        widgets[key] = e

    if data: widgets["username"].config(state="disabled")

    def save():
        new_user = {k: v.get().strip() for k, v in widgets.items()}
        
        # Ràng buộc dữ liệu
        if not all([new_user["username"], new_user["fullname"]]):
            return messagebox.showwarning("Lỗi", "Vui lòng nhập đủ các trường bắt buộc!", parent=top)

        if not is_valid_username(new_user["username"]):
            return messagebox.showwarning("Lỗi", "Tên đăng nhập không hợp lệ.", parent=top)

        if not is_valid_fullname(new_user["fullname"]):
            return messagebox.showwarning("Lỗi", "Họ và tên phải có ít nhất 3 ký tự.", parent=top)
            
        if not is_valid_phone(new_user["sdt"]):
            return messagebox.showwarning("Lỗi", "Số điện thoại không hợp lệ (10 số, bắt đầu bằng 0).", parent=top)
            
        if not data and not new_user["password"]:
            return messagebox.showwarning("Lỗi", "Vui lòng nhập mật khẩu cho tài khoản mới.", parent=top)

        if new_user["password"] and not is_valid_password(new_user["password"]):
            return messagebox.showwarning("Lỗi", "Mật khẩu phải có ít nhất 3 ký tự.", parent=top)

        if data:
            new_user["password"] = data.get("password", "") if not new_user["password"] else prepare_password_for_storage(new_user["password"])
        else:
            new_user["password"] = prepare_password_for_storage(new_user["password"])

        if data:
            for i, u in enumerate(app["ql"].list_users):
                if u["username"] == data["username"]:
                    app["ql"].list_users[i].update(new_user)
                    break
        else:
            if app["ql"].find_user(new_user["username"]):
                return messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại!", parent=top)
            app["ql"].list_users.append(new_user)

        app["ql"].save()
        write_activity_log(
            action="SAVE_USER",
            actor="admin",
            role="admin",
            status="SUCCESS",
            detail=f"Lưu hồ sơ khách hàng {new_user['username']}.",
            datastore=app["ql"],
        )
        refresh_users(app)
        top.destroy()
        set_status(app, "Đã lưu khách hàng thành công", THEME["success"])

    style_button(card, "Lưu thông tin", THEME["success"], save).pack(pady=20)

def delete_user(app):
    sel = app["tv_users"].selection()
    if not sel: return
    username = app["tv_users"].item(sel[0])["values"][0]
    if messagebox.askyesno("Xác nhận", f"Xóa khách hàng {username}?"):
        app["ql"].data["users"] = [u for u in app["ql"].list_users if u["username"] != username]
        app["ql"].save()
        write_activity_log(
            action="DELETE_USER",
            actor="admin",
            role="admin",
            status="SUCCESS",
            detail=f"Xóa khách hàng {username}.",
            datastore=app["ql"],
        )
        refresh_users(app)
        set_status(app, f"Đã xóa khách hàng {username}", THEME["danger"])

def admin_user_tab(app):
    """Tab quản lý khách hàng."""
    clear_container(app)
    tk.Label(app["container"], text="QUẢN LÝ DANH SÁCH KHÁCH HÀNG", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 10))

    toolbar = tk.Frame(app["container"], bg=THEME["bg"])
    toolbar.pack(fill="x", pady=10)
    style_button(toolbar, "Thêm khách mới", THEME["success"], lambda: open_user_form(app)).pack(side="left", padx=5)
    style_button(toolbar, "Sửa thông tin", THEME["primary"], 
                 lambda: open_user_form(app, app["ql"].find_user(app["tv_users"].item(app["tv_users"].selection()[0])["values"][0]) if app["tv_users"].selection() else None)).pack(side="left", padx=5)
    style_button(toolbar, "Xóa khách", THEME["danger"], lambda: delete_user(app)).pack(side="left", padx=5)

    wrapper = tk.Frame(app["container"], bg=THEME["surface"], bd=1, relief="solid")
    wrapper.pack(fill="both", expand=True)

    cols = ("user", "name", "sdt", "pass")
    tv = ttk.Treeview(wrapper, columns=cols, show="headings")
    app["tv_users"] = tv
    
    headers = [("user", "Tên đăng nhập"), ("name", "Họ và tên"), ("sdt", "Số điện thoại"), ("pass", "Mật khẩu")]
    for id, txt in headers:
        tv.heading(id, text=txt)
        tv.column(id, anchor="center", width=150)

    tv.pack(side="left", fill="both", expand=True)
    sy = ttk.Scrollbar(wrapper, orient="vertical", command=tv.yview)
    tv.configure(yscrollcommand=sy.set)
    sy.pack(side="right", fill="y")
    refresh_users(app)


# QUẢN LÝ TOUR / CHUYẾN ĐI (TOUR MANAGEMENT)

def validate_tour(app, form_data, old_ma=None):
    """Kiểm tra tính hợp lệ của dữ liệu tour trước khi lưu."""
    required = ["ma", "ten", "ngay", "khach", "gia", "diemDi", "diemDen", "trangThai", "hdvPhuTrach"]
    
    # 1. Kiểm tra để trống
    if not all(form_data.get(k, "").strip() for k in required):
        return False, "Vui lòng nhập đầy đủ thông tin tour."
        
    # 2. Kiểm tra định dạng mã tour (Txx)
    if not re.fullmatch(r"T\d{2,}", form_data["ma"]):
        return False, "Mã tour phải theo dạng T01, T02..."
        
    # 3. Kiểm tra độ dài tên tour
    if len(form_data["ten"].strip()) < 5:
        return False, "Tên tour quá ngắn (tối thiểu 5 ký tự)."
        
    # 4. Kiểm tra định dạng ngày
    if not is_valid_date(form_data["ngay"]):
        return False, "Ngày khởi hành không đúng định dạng dd/mm/yyyy."
        
    # 5. Kiểm tra sức chứa và giá
    if not form_data["khach"].isdigit() or not (1 <= int(form_data["khach"]) <= 500):
        return False, "Sức chứa tối đa phải từ 1 đến 500 khách."
    if not form_data["gia"].isdigit() or int(form_data["gia"]) <= 0:
        return False, "Giá tour phải là một số dương."
        
    # 6. Kiểm tra điểm đi và điểm đến
    if form_data["diemDi"].strip().lower() == form_data["diemDen"].strip().lower():
        return False, "Điểm đi và điểm đến không được trùng nhau."
        
    # 7. Kiểm tra HDV phụ trách
    if not app["ql"].find_hdv(form_data["hdvPhuTrach"]):
        return False, "Hướng dẫn viên phụ trách không tồn tại trong hệ thống."

    # 8. Kiểm tra trùng mã tour
    for t in app["ql"].list_tours:
        if t["ma"] == form_data["ma"] and t["ma"] != old_ma:
            return False, "Mã tour đã tồn tại."

    # 9. Kiểm tra sức chứa mới so với số chỗ đã đặt
    existing_booked = app["ql"].get_occupied_seats(old_ma or form_data["ma"])
    if int(form_data["khach"]) < existing_booked:
        return False, f"Không thể giảm sức chứa xuống {form_data['khach']} vì đã có {existing_booked} chỗ được đặt."

    # 10. Kiểm tra trạng thái HDV
    hdv = app["ql"].find_hdv(form_data["hdvPhuTrach"])
    if hdv and hdv.get("trangThai") == "Tạm nghỉ":
        return False, "Không thể phân công HDV đang ở trạng thái 'Tạm nghỉ'."
        
    return True, ""


def refresh_tours(app, keyword=""):
    """Làm mới danh sách hiển thị Tour trong Treeview."""
    tree = app.get("tv_tour")
    if not tree:
        return
        
    for item in tree.get_children():
        tree.delete(item)

    rows = app["ql"].list_tours
    if keyword:
        kw = keyword.lower().strip()
        rows = [
            t for t in rows 
            if kw in t["ma"].lower() or kw in t["ten"].lower() or kw in t["diemDen"].lower() or kw in t["trangThai"].lower()
        ]

    for t in rows:
        booked = app["ql"].get_occupied_seats(t["ma"])
        tree.insert(
            "",
            "end",
            values=(t["ma"], t["ten"], t["ngay"], f"{booked}/{t['khach']}", f"{safe_int(t['gia']):,}".replace(",", "."), t["hdvPhuTrach"], t["trangThai"]),
        )
    apply_zebra(tree)
    set_status(app, f"Hiển thị {len(rows)} tour", THEME["primary"])


def open_tour_form(app, data=None):
    """Mở cửa sổ form nhập liệu hoặc chỉnh sửa tour."""
    top = tk.Toplevel(app["root"])
    top.title("Thông tin tour du lịch")
    top.geometry("620x620")
    top.configure(bg=THEME["bg"])
    top.transient(app["root"])
    top.grab_set()

    card = tk.Frame(top, bg=THEME["surface"], bd=1, relief="solid")
    card.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(card, text="THÔNG TIN CHI TIẾT TOUR", bg=THEME["surface"], fg=THEME["text"], font=("Times New Roman", 18, "bold")).pack(pady=(18, 12))

    form = tk.Frame(card, bg=THEME["surface"])
    form.pack(fill="both", expand=True, padx=25)

    # Lấy danh sách mã HDV hiện có để chọn
    hdv_codes = [h["maHDV"] for h in app["ql"].list_hdv]
    
    fields = [
        ("Mã tour", "ma", "entry"),
        ("Tên tour", "ten", "entry"),
        ("Ngày khởi hành", "ngay", "entry"),
        ("Sức chứa tối đa", "khach", "entry"),
        ("Giá tour (VNĐ)", "gia", "entry"),
        ("Điểm xuất phát", "diemDi", "entry"),
        ("Điểm đến", "diemDen", "entry"),
        ("Trạng thái", "trangThai", "combo", ["Mở bán", "Đã chốt", "Đang đi", "Hoàn tất", "Đã hủy", "Tạm hoãn"]),
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
            if kind == "entry":
                widgets[key].insert(0, data[key])
            else:
                widgets[key].set(data[key])

    if data:
        widgets["ma"].config(state="disabled")

    def save_tour():
        """Lưu dữ liệu tour."""
        form_data = {}
        for _, key, kind, *extra in fields:
            if data and key == "ma":
                form_data[key] = data["ma"]
            else:
                form_data[key] = widgets[key].get().strip()
                
        # Kiểm tra nếu đổi trạng thái sang "Đã hủy" mà có khách đặt chỗ
        if form_data["trangThai"] == "Đã hủy" and (not data or data["trangThai"] != "Đã hủy"):
            booked = app["ql"].get_occupied_seats(form_data["ma"])
            if booked > 0:
                if not messagebox.askyesno("Xác nhận hủy", 
                                           f"Tour '{form_data['ten']}' hiện đang có {booked} khách đặt chỗ.\n"
                                           "Nếu hủy tour, bạn sẽ phải thực hiện quy trình hoàn tiền cho khách.\n"
                                           "Bạn vẫn chắc chắn muốn đổi trạng thái sang 'Đã hủy'?"):
                    return

        ok, msg = validate_tour(app, form_data, data["ma"] if data else None)
        if not ok:
            messagebox.showwarning("Thông báo", msg, parent=top)
            return

        # Cập nhật dữ liệu vào list
        if data:
            for i, t in enumerate(app["ql"].list_tours):
                if t["ma"] == data["ma"]:
                    app["ql"].list_tours[i] = form_data
                    break
        else:
            app["ql"].list_tours.append(form_data)

        # Cập nhật trạng thái HDV tự động
        hdv = app["ql"].find_hdv(form_data["hdvPhuTrach"])
        if hdv and form_data["trangThai"] in ["Mở bán", "Đã chốt"]:
            hdv["trangThai"] = "Đang dẫn tour"

        app["ql"].save()
        top.destroy()
        refresh_tours(app, app["search_tour_var"].get())
        set_status(app, "Đã lưu thông tin tour thành công", THEME["success"])

    btns = tk.Frame(card, bg=THEME["surface"])
    btns.pack(fill="x", padx=25, pady=20)
    style_button(btns, "Lưu tour", THEME["success"], save_tour).pack(side="left", fill="x", expand=True, padx=(0, 8))
    style_button(btns, "Hủy", THEME["danger"], top.destroy).pack(side="left", fill="x", expand=True)


def edit_tour(app):
    """Mở form sửa tour đang được chọn."""
    sel = app["tv_tour"].selection()
    if not sel:
        messagebox.showwarning("Thông báo", "Vui lòng chọn tour cần sửa.")
        return
    ma = app["tv_tour"].item(sel[0])["values"][0]
    tour = app["ql"].find_tour(ma)
    if tour:
        open_tour_form(app, tour)


def delete_tour(app):
    """Xóa tour đang được chọn."""
    sel = app["tv_tour"].selection()
    if not sel:
        messagebox.showwarning("Thông báo", "Vui lòng chọn tour cần xóa.")
        return
    ma = app["tv_tour"].item(sel[0])["values"][0]
    
    # Tìm thông tin tour
    tour = app["ql"].find_tour(ma)
    if not tour:
        return

    # Ràng buộc 1: Không cho xóa nếu tour đang hoạt động hoặc đã chốt
    if tour.get("trangThai") in ["Đã chốt", "Đang đi"]:
        messagebox.showwarning("Không thể xóa", 
                               f"Tour '{tour['ten']}' hiện đang ở trạng thái '{tour['trangThai']}'.\n"
                               "Bạn phải chuyển trạng thái tour về 'Mở bán' hoặc 'Hủy' trước khi xóa.")
        return

    # Ràng buộc 2: Không cho xóa nếu đã có người đặt chỗ
    if app["ql"].get_bookings_by_tour(ma):
        messagebox.showwarning("Không thể xóa", "Tour này đã có khách đặt chỗ (booking). Vui lòng xử lý các booking trước.")
        return
        
    if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa tour {ma}?"):
        app["ql"].data["tours"] = [t for t in app["ql"].list_tours if t["ma"] != ma]
        app["ql"].save()
        refresh_tours(app, app["search_tour_var"].get())
        set_status(app, f"Đã xóa tour {ma}", THEME["danger"])


def admin_tour_tab(app):
    """Hiển thị giao diện quản lý Tour."""
    clear_container(app)

    tk.Label(app["container"], text="QUẢN LÝ DANH SÁCH TOUR DU LỊCH", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 10))

    # Thanh công cụ điều khiển
    toolbar = tk.Frame(app["container"], bg=THEME["bg"])
    toolbar.pack(fill="x", pady=(0, 10))
    style_button(toolbar, "Thêm tour mới", THEME["success"], lambda: open_tour_form(app)).pack(side="left", padx=(0, 8))
    style_button(toolbar, "Cập nhật", THEME["primary"], lambda: edit_tour(app)).pack(side="left", padx=(0, 8))
    style_button(toolbar, "Xóa tour", THEME["danger"], lambda: delete_tour(app)).pack(side="left", padx=(0, 20))

    # Tìm kiếm nhanh
    tk.Label(toolbar, text="Tìm kiếm:", bg=THEME["bg"], font=("Times New Roman", 12, "bold")).pack(side="left")
    search_entry = tk.Entry(toolbar, textvariable=app["search_tour_var"], font=("Times New Roman", 12), relief="solid", bd=1)
    search_entry.pack(side="left", fill="x", expand=True, ipady=4)
    search_entry.bind("<Return>", lambda e: refresh_tours(app, app["search_tour_var"].get()))
    style_button(toolbar, "Lọc", THEME["primary"], lambda: refresh_tours(app, app["search_tour_var"].get())).pack(side="left", padx=(8, 0))

    # Bảng danh sách tour
    wrapper = tk.Frame(app["container"], bg=THEME["surface"], bd=1, relief="solid")
    wrapper.pack(fill="both", expand=True)
    
    cols = ("ma", "ten", "ngay", "khach", "gia", "hdv", "tt")
    tv = ttk.Treeview(wrapper, columns=cols, show="headings", height=10)
    app["tv_tour"] = tv
    
    cfg = [
        ("ma", "Mã Tour", 80),
        ("ten", "Tên tour du lịch", 220),
        ("ngay", "Khởi hành", 110),
        ("khach", "Đã đặt/Tổng", 100),
        ("gia", "Giá tour", 110),
        ("hdv", "Mã HDV", 90),
        ("tt", "Trạng thái", 110),
    ]
    for c, t, w in cfg:
        tv.heading(c, text=t)
        tv.column(c, anchor="center", width=w)
        
    sy = ttk.Scrollbar(wrapper, orient="vertical", command=tv.yview)
    tv.configure(yscrollcommand=sy.set)
    tv.pack(side="left", fill="both", expand=True)
    sy.pack(side="right", fill="y")

    """Khu vực hiển thị chi tiết tour khi nhấn chọn"""
    # Tạo khung chứa chính
    details = tk.LabelFrame(app["container"], text="Chi tiết điều hành tour", 
                            font=("Times New Roman", 14, "bold"), bg=THEME["surface"], 
                            bd=1, relief="solid", padx=5, pady=5)
    details.pack(fill="both", expand=True, pady=(12, 0))

    # Tạo một khung phụ để chứa Text và Scrollbar cạnh nhau
    content_frame = tk.Frame(details, bg=THEME["surface"])
    content_frame.pack(fill="both", expand=True)

    # Tạo thanh cuộn (Scrollbar)
    scrollbar = tk.Scrollbar(content_frame)
    scrollbar.pack(side="right", fill="y")

    # Tạo ô văn bản (Text Widget)
    # state="disabled" để Admin không xóa sửa lung tung vào vùng hiển thị
    detail_text = tk.Text(content_frame, font=("Times New Roman", 13), 
                        bg=THEME["surface"], fg=THEME["text"],
                        height=6, bd=0, padx=10, pady=10,
                        yscrollcommand=scrollbar.set)
    detail_text.pack(side="left", fill="both", expand=True)

    # Kết nối thanh cuộn với ô văn bản
    scrollbar.config(command=detail_text.yview)

    # Thiết lập nội dung mặc định
    detail_text.insert("1.0", "Vui lòng chọn một tour trong danh sách để xem chi tiết và danh sách khách hàng.")
    detail_text.config(state="disabled") # Khóa lại sau khi chèn text

    # Cập nhật mô tả
    def update_detail(content):
        detail_text.config(state="normal")     # Mở khóa để ghi
        detail_text.delete("1.0", "end")       # Xóa nội dung cũ
        detail_text.insert("end", content)     # Chèn nội dung mới
        detail_text.config(state="disabled")   # Khóa lại để chỉ đọc

    def on_select(event):
        """Xử lý sự kiện khi người dùng chọn một tour trong bảng."""
        sel = tv.selection()
        if not sel:
            return
        item = tv.item(sel[0])
        values = item.get("values")

        if not values:
            return

        ma = values[0]
        tour = app["ql"].find_tour(ma)
        bookings = app["ql"].get_bookings_by_tour(ma)
        guest_count = app["ql"].get_occupied_seats(ma)
        
        lines = [
            f"TOUR: {tour['ten']} ({tour['ma']})",
            f"Lộ trình: {tour['diemDi']} → {tour['diemDen']} | Khởi hành: {tour['ngay']}",
            f"Giá: {safe_int(tour['gia']):,}đ | Sức chứa: {tour['khach']} | Hiện đã đặt: {guest_count}",
            f"Hướng dẫn viên: {tour['hdvPhuTrach']} | Trạng thái: {tour['trangThai']}",
            "",
            "DANH SÁCH BOOKING HIỆN TẠI:"
        ]
        
        if bookings:
            for i, b in enumerate(bookings, 1):
                lines.append(f"{i}. {b['maBooking']}: {b['tenKhach']} ({b['soNguoi']} người) - SĐT: {b['sdt']} [{b['trangThai']}]")
        else:
            lines.append("- (Chưa có booking nào cho tour này)")
            
        content = "\n".join(lines)
        update_detail(content)
        set_status(app, f"Đang xem chi tiết tour {ma}", THEME["primary"])

    tv.bind("<<TreeviewSelect>>", on_select)
    refresh_tours(app, app["search_tour_var"].get()) 



# QUẢN LÝ BOOKING / ĐẶT CHỖ (BOOKING MANAGEMENT)
def validate_booking(app, form_data, old_ma=None):
    """Kiểm tra tính hợp lệ của dữ liệu booking trước khi lưu."""
    required = ["maBooking", "maTour", "tenKhach", "sdt", "soNguoi", "trangThai"]
    
    # 1. Kiểm tra để trống
    if not all(form_data.get(k, "").strip() for k in required):
        return False, "Vui lòng nhập đầy đủ thông tin booking."
        
    # 2. Kiểm tra định dạng mã booking (BKxx)
    if not re.fullmatch(r"BK\d{2,}", form_data["maBooking"]):
        return False, "Mã booking phải theo dạng BK01, BK02..."
        
    # 3. Kiểm tra tên khách hàng
    if len(form_data["tenKhach"].strip()) < 3:
        return False, "Tên khách hàng quá ngắn."
        
    # 4. Kiểm tra số điện thoại
    if not is_valid_phone(form_data["sdt"]):
        return False, "Số điện thoại khách hàng không hợp lệ."
        
    # 5. Kiểm tra số người đi
    if not form_data["soNguoi"].isdigit() or int(form_data["soNguoi"]) <= 0:
        return False, "Số người đi phải là một số nguyên dương."
        
    # 6. Kiểm tra sự tồn tại của tour
    tour = app["ql"].find_tour(form_data["maTour"])
    if not tour:
        return False, "Tour được chọn không tồn tại."
        
    # 7. Kiểm tra trùng mã booking
    for b in app["ql"].list_bookings:
        if b["maBooking"] == form_data["maBooking"] and b["maBooking"] != old_ma:
            return False, "Mã booking này đã tồn tại."

    # 8. Kiểm tra sức chứa của tour (còn đủ chỗ không?)
    occupied = app["ql"].get_occupied_seats(form_data["maTour"])
    old_people = 0
    if old_ma:
        old_booking = next((b for b in app["ql"].list_bookings if b["maBooking"] == old_ma), None)
        if old_booking and old_booking["maTour"] == form_data["maTour"]:
            old_people = safe_int(old_booking["soNguoi"])
            
    if occupied - old_people + int(form_data["soNguoi"]) > int(tour["khach"]):
        return False, f"Tour này chỉ còn {int(tour['khach']) - (occupied - old_people)} chỗ trống. Không đủ cho {form_data['soNguoi']} người."
        
    # 9. Kiểm tra trạng thái tour
    if tour["trangThai"] in ["Hoàn tất", "Tạm hoãn"]:
        return False, f"Không thể đặt chỗ cho tour đang ở trạng thái '{tour['trangThai']}'."
        
    return True, ""


def refresh_bookings(app, keyword=""):
    """Làm mới danh sách hiển thị Booking trong Treeview."""
    tree = app.get("tv_booking")
    if not tree:
        return
        
    for item in tree.get_children():
        tree.delete(item)
        
    rows = app["ql"].list_bookings
    if keyword:
        kw = keyword.lower().strip()
        rows = [
            b for b in rows 
            if kw in b["maBooking"].lower() or kw in b["tenKhach"].lower() or kw in b["maTour"].lower()
        ]
        
    for b in rows:
        tree.insert("", "end", values=(b["maBooking"], b["maTour"], b["tenKhach"], b["sdt"], b["soNguoi"], b["trangThai"]))
        
    apply_zebra(tree)
    set_status(app, f"Hiển thị {len(rows)} booking", THEME["primary"])


def open_booking_form(app, data=None):
    """Mở cửa sổ form nhập liệu hoặc chỉnh sửa booking."""
    top = tk.Toplevel(app["root"])
    top.title("Thông tin đặt chỗ (Booking)")
    top.geometry("560x470")
    top.configure(bg=THEME["bg"])
    top.transient(app["root"])
    top.grab_set()

    card = tk.Frame(top, bg=THEME["surface"], bd=1, relief="solid")
    card.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(card, text="THÔNG TIN ĐẶT CHỖ", bg=THEME["surface"], font=("Times New Roman", 18, "bold")).pack(pady=(18, 12))
    
    form = tk.Frame(card, bg=THEME["surface"])
    form.pack(fill="both", expand=True, padx=25)

    # Danh sách mã tour hiện có để chọn
    tour_codes = [t["ma"] for t in app["ql"].list_tours]
    
    fields = [
        ("Mã booking", "maBooking", "entry"),
        ("Mã tour", "maTour", "combo", tour_codes),
        ("Tên khách hàng", "tenKhach", "entry"),
        ("Số điện thoại", "sdt", "entry"),
        ("Số người đi", "soNguoi", "entry"),
        ("Trạng thái", "trangThai", "combo", ["Đã cọc", "Đã thanh toán", "Đã hủy"]),
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
            if kind == "entry":
                widgets[key].insert(0, data[key])
            else:
                widgets[key].set(data[key])

    if data:
        widgets["maBooking"].config(state="disabled")

    def save_booking():
        """Lưu dữ liệu booking."""
        form_data = {}
        for _, key, kind, *extra in fields:
            if data and key == "maBooking":
                form_data[key] = data["maBooking"]
            else:
                form_data[key] = widgets[key].get().strip()
                
        ok, msg = validate_booking(app, form_data, data["maBooking"] if data else None)
        if not ok:
            messagebox.showwarning("Thông báo", msg, parent=top)
            return

        # Cập nhật vào danh sách
        if data:
            for i, b in enumerate(app["ql"].list_bookings):
                if b["maBooking"] == data["maBooking"]:
                    app["ql"].list_bookings[i] = form_data
                    break
        else:
            app["ql"].list_bookings.append(form_data)
            
        app["ql"].save()
        top.destroy()
        
        # Cập nhật lại các bảng liên quan
        refresh_bookings(app, app["search_booking_var"].get())
        if app.get("tv_tour"):
            refresh_tours(app, app["search_tour_var"].get())
            
        set_status(app, "Đã lưu booking thành công", THEME["success"])

    btns = tk.Frame(card, bg=THEME["surface"])
    btns.pack(fill="x", padx=25, pady=20)
    style_button(btns, "Lưu booking", THEME["success"], save_booking).pack(side="left", fill="x", expand=True, padx=(0, 8))
    style_button(btns, "Hủy bỏ", THEME["danger"], top.destroy).pack(side="left", fill="x", expand=True)


def edit_booking(app):
    """Mở form sửa cho booking được chọn."""
    sel = app["tv_booking"].selection()
    if not sel:
        messagebox.showwarning("Thông báo", "Vui lòng chọn booking cần sửa.")
        return
    ma = app["tv_booking"].item(sel[0])["values"][0]
    booking = next((b for b in app["ql"].list_bookings if b["maBooking"] == ma), None)
    if booking:
        open_booking_form(app, booking)


def delete_booking(app):
    """Xóa booking được chọn."""
    sel = app["tv_booking"].selection()
    if not sel:
        messagebox.showwarning("Thông báo", "Vui lòng chọn booking cần xóa.")
        return
    ma = app["tv_booking"].item(sel[0])["values"][0]
    
    # Kiểm tra trạng thái tour trước khi cho phép xóa booking
    booking = next((b for b in app["ql"].list_bookings if b["maBooking"] == ma), None)
    if booking:
        tour = app["ql"].find_tour(booking["maTour"])
        if tour and tour.get("trangThai") in ["Đã chốt", "Đang đi"]:
            if not messagebox.askyesno("Cảnh báo", 
                                       f"Tour '{tour['ten']}' hiện đang ở trạng thái '{tour['trangThai']}'.\n"
                                       "Việc xóa booking lúc này có thể ảnh hưởng đến việc điều hành tour.\n"
                                       "Bạn vẫn chắc chắn muốn xóa?"):
                return
    
    if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa booking {ma}?"):
        app["ql"].data["bookings"] = [b for b in app["ql"].list_bookings if b["maBooking"] != ma]
        app["ql"].save()
        
        refresh_bookings(app, app["search_booking_var"].get())
        if app.get("tv_tour"):
            refresh_tours(app, app["search_tour_var"].get())
            
        set_status(app, f"Đã xóa booking {ma}", THEME["danger"])


def admin_booking_tab(app):
    """Hiển thị giao diện quản lý Booking."""
    clear_container(app)

    tk.Label(app["container"], text="QUẢN LÝ ĐẶT CHỖ & KHÁCH HÀNG", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 10))
    
    # Thanh công cụ
    toolbar = tk.Frame(app["container"], bg=THEME["bg"])
    toolbar.pack(fill="x", pady=(0, 10))
    style_button(toolbar, "Thêm booking", THEME["success"], lambda: open_booking_form(app)).pack(side="left", padx=(0, 8))
    style_button(toolbar, "Cập nhật", THEME["primary"], lambda: edit_booking(app)).pack(side="left", padx=(0, 8))
    style_button(toolbar, "Xóa booking", THEME["danger"], lambda: delete_booking(app)).pack(side="left", padx=(0, 20))

    # Tìm kiếm
    tk.Label(toolbar, text="Tìm kiếm:", bg=THEME["bg"], font=("Times New Roman", 12, "bold")).pack(side="left")
    search_entry = tk.Entry(toolbar, textvariable=app["search_booking_var"], font=("Times New Roman", 12), relief="solid", bd=1)
    search_entry.pack(side="left", fill="x", expand=True, ipady=4)
    search_entry.bind("<Return>", lambda e: refresh_bookings(app, app["search_booking_var"].get()))
    style_button(toolbar, "Lọc", THEME["primary"], lambda: refresh_bookings(app, app["search_booking_var"].get())).pack(side="left", padx=(8, 0))

    # Bảng danh sách booking
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
        ("tt", "Trạng thái", 120),
    ]
    for c, t, w in cfg:
        tv.heading(c, text=t)
        tv.column(c, anchor="center", width=w)
        
    sy = ttk.Scrollbar(wrapper, orient="vertical", command=tv.yview)
    tv.configure(yscrollcommand=sy.set)
    tv.pack(side="left", fill="both", expand=True)
    sy.pack(side="right", fill="y")
    
    refresh_bookings(app, app["search_booking_var"].get())


def admin_feedback_tab(app):
    """Hiển thị tab quản lý Đánh giá & Thông báo."""
    clear_container(app)
    
    # 1. PHẦN ĐÁNH GIÁ TỪ KHÁCH HÀNG
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

    # 2. PHẦN THÔNG BÁO TỪ HDV
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
    notif_tv.column("tour", width=200, anchor="w")
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


# CÁC HÀM HỆ THỐNG (SYSTEM FUNCTIONS)
def manual_save(app):
    """Lưu dữ liệu vào file JSON một cách thủ công và hiển thị thông báo."""
    try:
        app["ql"].save()
        messagebox.showinfo("Thành công", f"Dữ liệu đã được lưu an toàn vào:\n{app['ql'].path}")
        set_status(app, "Đã lưu tệp JSON thành công", THEME["success"])
    except Exception as e:
        messagebox.showerror("Lỗi hệ thống", f"Không thể lưu tệp dữ liệu:\n{e}")
        set_status(app, "Lỗi khi lưu tệp dữ liệu", THEME["danger"])


def logout(app):
    """Xác nhận và đăng xuất, quay lại màn hình đăng nhập."""
    if messagebox.askyesno("Đăng xuất", "Bạn có chắc chắn muốn thoát khỏi hệ thống quản trị?"):
        # Import cục bộ để tránh vòng lặp import
        from main import TravelSystem
        for widget in app["root"].winfo_children():
            widget.destroy()
        TravelSystem(app["root"])


# CHƯƠNG TRÌNH CHÍNH (MAIN APPLICATION)
def main(root=None):
    """Khởi tạo và chạy ứng dụng chính."""
    if root is None:
        root = tk.Tk()

    # Cấu hình cửa sổ chính
    root.title("VIETNAM TRAVEL - HỆ THỐNG QUẢN TRỊ VIÊN")
    root.geometry("1280x800")
    root.minsize(1150, 700)
    root.configure(bg=THEME["bg"])

    # Cấu hình style cho các widget ttk (Treeview)
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Treeview", 
        font=("Times New Roman", 12), 
        rowheight=32, 
        background=THEME["surface"], 
        fieldbackground=THEME["surface"], 
        foreground=THEME["text"]
    )
    style.configure(
        "Treeview.Heading", 
        font=("Times New Roman", 12, "bold"), 
        background="#e2e8f0", 
        foreground=THEME["text"]
    )
    style.map("Treeview", background=[("selected", "#bfdbfe")], foreground=[("selected", THEME["text"])])

    # Khởi tạo đối tượng ứng dụng (App State)
    app = {
        "root": root,
        "ql": DataStore(),
        "container": None,
        "tv_hdv": None,
        "tv_tour": None,
        "tv_booking": None,
        "status_var": tk.StringVar(value="Hệ thống đã sẵn sàng"),
        "status_label": None,
        "search_hdv_var": tk.StringVar(),
        "search_tour_var": tk.StringVar(),
        "search_booking_var": tk.StringVar(),
    }

    # --- THANH MENU BÊN TRÁI (SIDEBAR) ---
    sidebar = tk.Frame(root, bg=THEME["sidebar"], width=250)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    # Logo/Tiêu đề Sidebar
    tk.Label(sidebar, text="VIETNAM\nTRAVEL", justify="center", bg=THEME["sidebar"], fg="#10b981", font=("Times New Roman", 19, "bold"), pady=24).pack(fill="x")

    # Danh sách nút menu
    menu = tk.Frame(sidebar, bg=THEME["sidebar"])
    menu.pack(fill="x", padx=10)

    def menu_btn(text, cmd):
        """Hàm tạo nút bấm menu nhanh."""
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

    # Thêm các nút điều hướng
    menu_btn("Tổng quan Dashboard", lambda: dashboard_tab(app)).pack(fill="x", pady=4)
    menu_btn("Quản lý HDV", lambda: admin_hdv_tab(app)).pack(fill="x", pady=4)
    menu_btn("Quản lý Khách hàng", lambda: admin_user_tab(app)).pack(fill="x", pady=4)
    menu_btn("Quản lý Tour", lambda: admin_tour_tab(app)).pack(fill="x", pady=4)
    menu_btn("Quản lý Booking", lambda: admin_booking_tab(app)).pack(fill="x", pady=4)
    menu_btn("Đánh giá & Thông báo", lambda: admin_feedback_tab(app)).pack(fill="x", pady=4)
    menu_btn("Lưu dữ liệu JSON", lambda: manual_save(app)).pack(fill="x", pady=4)
    
    # Đường kẻ ngăn cách
    tk.Frame(sidebar, bg="#334155", height=1).pack(fill="x", padx=16, pady=16)
    
    menu_btn("Đăng xuất hệ thống", lambda: logout(app)).pack(fill="x", pady=4)

    # --- KHU VỰC NỘI DUNG BÊN PHẢI (MAIN CONTENT) ---
    right_panel = tk.Frame(root, bg=THEME["bg"])
    right_panel.pack(side="right", fill="both", expand=True)
    
    # Container chứa nội dung thay đổi theo tab
    app["container"] = tk.Frame(right_panel, bg=THEME["bg"], padx=24, pady=20)
    app["container"].pack(fill="both", expand=True)

    # Thanh trạng thái dưới cùng (Status Bar)
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

    # Khởi động tab đầu tiên
    dashboard_tab(app)
    
    # Chạy vòng lặp ứng dụng
    root.mainloop()


if __name__ == "__main__":
    main()
