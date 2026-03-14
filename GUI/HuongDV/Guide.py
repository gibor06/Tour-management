import json
import os
import re
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import copy


# CẤU HÌNH GIAO DIỆN (THEME)
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

# Đường dẫn tệp dữ liệu JSON (Dùng chung với Admin)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Lùi 1 cấp để ra QL_DL
DATA_DIR = os.path.join(BASE_DIR, "Admin", "data")
DATA_FILE = os.path.join(DATA_DIR, "vietnam_travel_data.json")

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
            "password": "123"
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
            "password": "123"
        }
    ],
    "tours": [],
    "bookings": [],
    "users": [],
    "admin": {"username": "admin", "password": "123"}
}

class DataStore:
    """Lớp quản lý việc lưu trữ và truy xuất dữ liệu từ file JSON."""
    def __init__(self, path=DATA_FILE):
        self.path = path
        self.data = {"hdv": [], "tours": [], "bookings": [], "users": [], "admin": {}}
        self.load()

    def load(self):
        """Tải dữ liệu từ tệp JSON. Nếu tệp lỗi hoặc không tồn tại, sử dụng dữ liệu mặc định."""
        if not os.path.exists(self.path):
            self.data = copy.deepcopy(DEFAULT_DATA)
            self.save()
            return

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)

            # Đảm bảo các khóa cần thiết luôn tồn tại
            for key in ["hdv", "tours", "bookings", "users"]:
                if key not in self.data or not isinstance(self.data[key], list):
                    self.data[key] = []
            
            # Cập nhật mật khẩu mặc định cho các tài khoản HDV nếu thiếu
            for default_h in DEFAULT_DATA["hdv"]:
                h = self.find_hdv(default_h["maHDV"])
                if h and "password" not in h:
                    h["password"] = default_h["password"]
            
            # Đảm bảo có tài khoản khách hàng mặc định nếu danh sách trống
            if not self.data["users"] and DEFAULT_DATA["users"]:
                self.data["users"] = copy.deepcopy(DEFAULT_DATA["users"])

            if "admin" not in self.data or not self.data["admin"]:
                self.data["admin"] = DEFAULT_DATA["admin"]

        except Exception:
            self.data = copy.deepcopy(DEFAULT_DATA)
            self.save()

    def save(self):
        """Lưu trạng thái dữ liệu hiện tại vào tệp JSON."""
        folder = os.path.dirname(self.path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    @property
    def list_hdv(self): return self.data["hdv"]
    @property
    def list_tours(self): return self.data["tours"]
    @property
    def list_bookings(self): return self.data["bookings"]
    @property
    def list_users(self): return self.data["users"]

    def find_user(self, username):
        return next((u for u in self.list_users if u["username"] == username), None)

    def find_hdv(self, ma_hdv):
        return next((h for h in self.list_hdv if h["maHDV"] == ma_hdv), None)

    def find_tour(self, ma_tour):
        return next((t for t in self.list_tours if t["ma"] == ma_tour), None)

    def get_bookings_by_tour(self, ma_tour):
        return [b for b in self.list_bookings if b["maTour"] == ma_tour]

    def get_occupied_seats(self, ma_tour):
        total = 0
        for b in self.get_bookings_by_tour(ma_tour):
            try: total += int(b.get("soNguoi", 0))
            except: pass
        return total

# CÁC HÀM TIỆN ÍCH
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

def safe_int(value):
    try: return int(value)
    except: return 0

def khoi_tao_hdv(root, user_data=None):
    """Hàm chính khởi tạo giao diện cho Hướng dẫn viên."""
    
    # Nếu không có user_data, giả định là HDV01 để test
    if not user_data:
        user_data = {"maHDV": "HDV01", "tenHDV": "Hướng Dẫn Viên"}

    app = {
        "root": root,
        "ql": DataStore(),
        "user": user_data,
        "container": None,
        "tv_tours": None,
        "detail_frame": None
    }

    # Cấu hình Style Treeview
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", font=("Times New Roman", 12), rowheight=32, background=THEME["surface"], fieldbackground=THEME["surface"], foreground=THEME["text"])
    style.configure("Treeview.Heading", font=("Times New Roman", 12, "bold"), background="#e2e8f0", foreground=THEME["text"])
    style.map("Treeview", background=[("selected", "#bfdbfe")], foreground=[("selected", THEME["text"])])

    # --- SIDEBAR ---
    sidebar = tk.Frame(root, bg=THEME["sidebar"], width=260)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(sidebar, text="VIETNAM\nTRAVEL", justify="center", bg=THEME["sidebar"], fg="#10b981", font=("Times New Roman", 19, "bold"), pady=24).pack(fill="x")
    
    # Sử dụng .get() để tránh lỗi KeyError nếu thiếu dữ liệu
    ten_hdv = user_data.get("tenHDV", "Hướng Dẫn Viên") if user_data else "Hướng Dẫn Viên"
    tk.Label(sidebar, text=f"XIN CHÀO,\n{ten_hdv}", bg=THEME["sidebar"], fg="#cbd5e1", font=("Times New Roman", 11, "bold"), pady=10).pack(fill="x")

    menu = tk.Frame(sidebar, bg=THEME["sidebar"])
    menu.pack(fill="x", padx=10, pady=20)

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
    # (Di chuyển xuống sau khi định nghĩa các hàm tab để tránh lỗi NameError)
    
    # --- NỘI DUNG CHÍNH (Right Panel) ---
    right_panel = tk.Frame(root, bg=THEME["bg"])
    right_panel.pack(side="left", fill="both", expand=True)
    
    content_area = tk.Frame(right_panel, bg=THEME["bg"], padx=24, pady=20)
    content_area.pack(fill="both", expand=True)
    app["container"] = content_area

    def clear_container():
        for widget in content_area.winfo_children():
            widget.destroy()

    # --- TAB: DANH SÁCH TOUR ---
    def hien_thi_chi_tiet(event):
        sel = app["tv_tours"].selection()
        if not sel: return
        ma_tour = app["tv_tours"].item(sel[0])["values"][0]
        tour = app["ql"].find_tour(ma_tour)
        bookings = app["ql"].get_bookings_by_tour(ma_tour)
        
        for w in app["detail_frame"].winfo_children(): w.destroy()
        
        # Tiêu đề chi tiết - Sử dụng wraplength để tránh tràn chiều ngang
        tk.Label(app["detail_frame"], text=f"CHI TIẾT ĐOÀN KHÁCH - {tour['ten']}", 
                 font=("Times New Roman", 15, "bold"), bg=THEME["bg"], fg=THEME["primary"],
                 wraplength=700, justify="center").pack(pady=(10, 5))
        
        # Bảng khách hàng - Giảm height xuống để tránh tràn chiều dọc
        wrapper = tk.Frame(app["detail_frame"], bg=THEME["surface"], bd=1, relief="solid")
        wrapper.pack(fill="both", expand=True)
        
        cols = ("stt", "ten", "sdt", "sl", "tt")
        tv = ttk.Treeview(wrapper, columns=cols, show="headings", height=6) # Giảm từ 8 xuống 6
        tv.heading("stt", text="STT"); tv.heading("ten", text="Tên khách hàng")
        tv.heading("sdt", text="Số điện thoại"); tv.heading("sl", text="Số người"); tv.heading("tt", text="Trạng thái")
        
        # Tối ưu hóa chiều rộng các cột
        tv.column("stt", width=40, anchor="center")
        tv.column("ten", width=180, anchor="w")
        tv.column("sdt", width=110, anchor="center")
        tv.column("sl", width=70, anchor="center")
        tv.column("tt", width=110, anchor="center")
        
        for i, b in enumerate(bookings, 1):
            tv.insert("", "end", values=(i, b["tenKhach"], b["sdt"], b["soNguoi"], b["trangThai"]))
        
        apply_zebra(tv)
        tv.pack(side="left", fill="both", expand=True)
        
        # Thanh cuộn
        sy = ttk.Scrollbar(wrapper, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sy.set)
        sy.pack(side="right", fill="y")

    def tab_danh_sach_tour():
        clear_container()
        tk.Label(content_area, text="LỊCH TRÌNH TOUR ĐƯỢC PHÂN CÔNG", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 15))
        
        # Lấy mã HDV an toàn
        ma_hdv = user_data.get("maHDV", "") if user_data else ""
        
        # Lọc tour của HDV này
        my_tours = [t for t in app["ql"].list_tours if t.get("hdvPhuTrach") == ma_hdv]
        
        # Khung bao bảng danh sách tour - Giảm height xuống
        wrapper = tk.Frame(content_area, bg=THEME["surface"], bd=1, relief="solid")
        wrapper.pack(fill="x")
        
        cols = ("ma", "ten", "ngay", "khach", "tt")
        tv = ttk.Treeview(wrapper, columns=cols, show="headings", height=5) # Giảm từ 6 xuống 5
        app["tv_tours"] = tv
        
        tv.heading("ma", text="Mã Tour"); tv.heading("ten", text="Tên Tour")
        tv.heading("ngay", text="Ngày khởi hành"); tv.heading("khach", text="Số khách"); tv.heading("tt", text="Trạng thái")
        
        for c in cols: tv.column(c, anchor="center")
        tv.column("ten", width=220, anchor="w") # Giảm từ 250 xuống 220
        
        for t in my_tours:
            occupied = app["ql"].get_occupied_seats(t["ma"])
            tv.insert("", "end", values=(t["ma"], t["ten"], t["ngay"], f"{occupied}/{t['khach']}", t["trangThai"]))
            
        apply_zebra(tv)
        tv.pack(fill="x")
        tv.bind("<<TreeviewSelect>>", hien_thi_chi_tiet)
        
        # Vùng hiển thị chi tiết bên dưới
        app["detail_frame"] = tk.Frame(content_area, bg=THEME["bg"])
        app["detail_frame"].pack(fill="both", expand=True, pady=10)
        
        if not my_tours:
            tk.Label(app["detail_frame"], text="Hiện tại bạn chưa có tour nào được phân công.", 
                     font=("Times New Roman", 13), bg=THEME["bg"], fg=THEME["muted"]).pack(pady=20)

    # --- TAB: THỐNG KÊ & PHẢN HỒI (GIỮ NGUYÊN LOGIC CŨ NHƯNG ĐỔI STYLE) ---
    def tab_thong_ke():
        clear_container()
        tk.Label(content_area, text="HIỆU SUẤT & ĐÁNH GIÁ CỦA KHÁCH HÀNG", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 20))
        
        card_frame = tk.Frame(content_area, bg=THEME["bg"])
        card_frame.pack(fill="x", pady=10)
    
        # Lấy mã HDV an toàn
        ma_hdv = user_data.get("maHDV", "") if user_data else ""
        
        # Đếm số tour đã dẫn hoàn tất
        completed_tours = [t for t in app["ql"].list_tours if t.get("hdvPhuTrach") == ma_hdv and t.get("trangThai") == "Hoàn tất"]
        
        stats = [
            ("Điểm trung bình", "4.9 / 5.0", THEME["warning"]), 
            ("Tỷ lệ hài lòng", "98%", THEME["success"]), 
            ("Số tour đã dẫn", str(len(completed_tours)), THEME["primary"])
        ]
    
        for t, v, c in stats:
            f = tk.Frame(card_frame, bg=THEME["surface"], bd=1, relief="solid", padx=15, pady=15)
            f.pack(side="left", expand=True, fill="both", padx=8)
            tk.Label(f, text=t, font=("Times New Roman", 13, "bold"), bg=THEME["surface"], fg=THEME["muted"]).pack()
            tk.Label(f, text=v, font=("Times New Roman", 22, "bold"), fg=c, bg=THEME["surface"]).pack()

        # Biểu đồ tiêu chí
        tk.Label(content_area, text="Chỉ số đánh giá chuyên môn (%)", font=("Times New Roman", 15, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(pady=(25, 10), anchor="w")
        
        chart_frame = tk.Frame(content_area, bg=THEME["surface"], bd=1, relief="solid", padx=20, pady=20)
        chart_frame.pack(fill="x")

        criteria = [("Kiến thức chuyên môn", 95, THEME["primary"]), 
                    ("Thái độ phục vụ", 98, THEME["success"]), 
                    ("Xử lý tình huống", 85, THEME["warning"])]

        for name, val, color in criteria:
            row = tk.Frame(chart_frame, bg=THEME["surface"])
            row.pack(fill="x", pady=8)
            tk.Label(row, text=name, font=("Times New Roman", 12), width=20, anchor="w", bg=THEME["surface"]).pack(side="left")
            
            p_bg = tk.Frame(row, bg="#e2e8f0", width=400, height=18)
            p_bg.pack(side="left", padx=15)
            p_bg.pack_propagate(False)
            tk.Frame(p_bg, bg=color, width=int(val * 4), height=18).pack(side="left")
            tk.Label(row, text=f"{val}%", font=("Times New Roman", 12, "bold"), bg=THEME["surface"]).pack(side="left")

    def tab_thong_bao():
        clear_container()
        tk.Label(content_area, text="GỬI THÔNG BÁO KHẨN CẤP", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["danger"]).pack(anchor="w", pady=(0, 10))
        
        card = tk.Frame(content_area, bg=THEME["surface"], bd=1, relief="solid", padx=20, pady=20)
        card.pack(fill="both", expand=True)
        
        tk.Label(card, text="Nội dung thông báo (Sẽ gửi đến tất cả khách hàng trong đoàn):", 
                 font=("Times New Roman", 13), bg=THEME["surface"], fg=THEME["text"]).pack(anchor="w", pady=(0, 10))
        
        txt = tk.Text(card, height=10, font=("Times New Roman", 13), relief="solid", bd=1)
        txt.pack(fill="both", expand=True, pady=(0, 20))
        
        style_button(card, "XÁC NHẬN GỬI THÔNG BÁO", THEME["danger"], 
                     lambda: messagebox.showinfo("Thành công", "Đã gửi thông báo đến toàn bộ khách hàng!")).pack()

    # --- TAB: CÀI ĐẶT TÀI KHOẢN ---
    def tab_cai_dat():
        clear_container()
        tk.Label(content_area, text="CÀI ĐẶT TÀI KHOẢN CÁ NHÂN", font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 20))
        
        card = tk.Frame(content_area, bg=THEME["surface"], bd=1, relief="solid", padx=30, pady=30)
        card.pack(pady=10)

        # Tìm dữ liệu HDV hiện tại
        ma_hdv = user_data.get("maHDV", "")
        hdv_data = app["ql"].find_hdv(ma_hdv)
        
        if not hdv_data:
            tk.Label(card, text="Lỗi: Không tìm thấy thông tin tài khoản!", fg=THEME["danger"], bg=THEME["surface"]).pack()
            return

        fields = [("Họ và tên", "tenHDV"), ("Số điện thoại", "sdt"), ("Email", "email"), ("Mật khẩu mới", "password")]
        widgets = {}

        for label, key in fields:
            row = tk.Frame(card, bg=THEME["surface"])
            row.pack(fill="x", pady=8)
            tk.Label(row, text=label, width=15, anchor="w", bg=THEME["surface"], font=("Times New Roman", 12, "bold")).pack(side="left")
            e = tk.Entry(row, font=("Times New Roman", 12), relief="solid", bd=1, width=30)
            e.pack(side="left", ipady=3)
            e.insert(0, hdv_data.get(key, ""))
            widgets[key] = e

        def save_profile():
            for key, entry in widgets.items():
                hdv_data[key] = entry.get().strip()
            
            app["ql"].save()
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin cá nhân thành công!")
            tab_cai_dat()

        style_button(card, "CẬP NHẬT THÔNG TIN", THEME["success"], save_profile).pack(pady=20)

    # --- ĐĂNG KÝ NÚT MENU ---
    menu_btn("Lịch Trình Tour", tab_danh_sach_tour).pack(fill="x", pady=4)
    menu_btn("Hiệu Suất & Đánh Giá", tab_thong_ke).pack(fill="x", pady=4)
    menu_btn("Gửi Thông Báo", tab_thong_bao).pack(fill="x", pady=4)
    menu_btn("Cài Đặt Tài Khoản", tab_cai_dat).pack(fill="x", pady=4)
    
    # Đường kẻ ngăn cách
    tk.Frame(sidebar, bg="#334155", height=1).pack(fill="x", padx=16, pady=16)
    
    tk.Button(sidebar, text="   Đăng Xuất", bg=THEME["sidebar"], fg="white", activebackground="#1e293b", activeforeground="white",
              relief="flat", bd=0, cursor="hand2", anchor="w", font=("Times New Roman", 14, "bold"),
              padx=16, pady=14, command=lambda: logout_system(root)).pack(fill="x", side="bottom", padx=10, pady=20)

    tab_danh_sach_tour() # Mở mặc định

def logout_system(root):
    if messagebox.askyesno("Xác nhận", "Bạn có muốn đăng xuất khỏi hệ thống?"):
        from ChayUD import TravelSystem
        for widget in root.winfo_children():
            widget.destroy()
        TravelSystem(root)
