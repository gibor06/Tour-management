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
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
DATA_DIR = os.path.join(BASE_DIR, "Admin", "data")
DATA_FILE = os.path.join(DATA_DIR, "vietnam_travel_data.json")

class DataStore:
    """Lớp quản lý việc nạp và lưu dữ liệu JSON."""
    def __init__(self, path=DATA_FILE):
        self.path = path
        self.data = {"hdv": [], "tours": [], "bookings": []}
        self.load()

    def load(self):
        if not os.path.exists(self.path): return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            for key in ["hdv", "tours", "bookings"]:
                if key not in self.data or not isinstance(self.data[key], list):
                    self.data[key] = []
        except: pass

    def save(self):
        folder = os.path.dirname(self.path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    @property
    def list_hdv(self): return self.data["hdv"]

# --- CÁC HÀM TIỆN ÍCH ---
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

# --- QUẢN LÝ NHÂN SỰ HDV ---

def refresh_hdv(app):
    """Làm mới bảng danh sách HDV."""
    for item in app["tv_hdv"].get_children():
        app["tv_hdv"].delete(item)
    for h in app["ql"].list_hdv:
        app["tv_hdv"].insert("", "end", values=(
            h.get("maHDV", ""), h.get("tenHDV", ""), 
            h.get("sdt", ""), h.get("email", ""), 
            h.get("kn", ""), h.get("trangThai", "")
        ))
    apply_zebra(app["tv_hdv"])

def open_hdv_form(app, data=None):
    """Mở form thêm/sửa HDV."""
    top = tk.Toplevel(app["root"])
    top.title("Thông tin Hướng dẫn viên")
    top.geometry("500x550")
    top.configure(bg=THEME["bg"])
    top.transient(app["root"])
    top.grab_set()

    card = tk.Frame(top, bg=THEME["surface"], bd=1, relief="solid")
    card.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(card, text="CHI TIẾT NHÂN SỰ", font=("Times New Roman", 16, "bold"), 
             bg=THEME["surface"], fg=THEME["text"]).pack(pady=15)

    fields = [
        ("Mã HDV", "maHDV"), ("Họ Tên", "tenHDV"), 
        ("Số Điện Thoại", "sdt"), ("Email", "email"), 
        ("Kinh nghiệm", "kn")
    ]
    widgets = {}

    for label, key in fields:
        row = tk.Frame(card, bg=THEME["surface"])
        row.pack(fill="x", padx=25, pady=8)
        tk.Label(row, text=label, font=("Times New Roman", 12, "bold"), bg=THEME["surface"]).pack(anchor="w")
        e = tk.Entry(row, font=("Times New Roman", 12), relief="solid", bd=1)
        e.pack(fill="x", pady=5, ipady=3)
        if data: e.insert(0, data.get(key, ""))
        widgets[key] = e

    def save():
        new_hdv = {k: v.get().strip() for k, v in widgets.items()}
        if not new_hdv["maHDV"] or not new_hdv["tenHDV"]:
            return messagebox.showwarning("Lỗi", "Vui lòng nhập Mã và Tên HDV!")

        if data: # Sửa
            for i, h in enumerate(app["ql"].list_hdv):
                if h["maHDV"] == data["maHDV"]:
                    app["ql"].list_hdv[i].update(new_hdv)
                    break
        else: # Thêm
            if any(h["maHDV"] == new_hdv["maHDV"] for h in app["ql"].list_hdv):
                return messagebox.showerror("Lỗi", "Mã HDV đã tồn tại!")
            new_hdv["trangThai"] = "Sẵn sàng"
            app["ql"].list_hdv.append(new_hdv)

        app["ql"].save()
        refresh_hdv(app)
        top.destroy()
        messagebox.showinfo("Thành công", "Đã cập nhật dữ liệu nhân sự!")

    style_button(card, "LƯU THÔNG TIN", THEME["success"], save).pack(pady=20)

def delete_hdv(app):
    sel = app["tv_hdv"].selection()
    if not sel: return messagebox.showwarning("Chú ý", "Hãy chọn một nhân sự để xóa!")
    ma = app["tv_hdv"].item(sel[0])["values"][0]
    if messagebox.askyesno("Xác nhận", f"Xóa HDV {ma}?"):
        app["ql"].data["hdv"] = [h for h in app["ql"].list_hdv if h["maHDV"] != ma]
        app["ql"].save()
        refresh_hdv(app)

def tab_quan_ly_hdv(app):
    """Giao diện quản lý danh sách HDV."""
    for w in app["container"].winfo_children(): w.destroy()

    tk.Label(app["container"], text="QUẢN TRỊ NHÂN SỰ HƯỚNG DẪN VIÊN", 
             font=("Times New Roman", 20, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(anchor="w", pady=(0, 15))

    # Toolbar
    toolbar = tk.Frame(app["container"], bg=THEME["bg"])
    toolbar.pack(fill="x", pady=10)
    style_button(toolbar, "Thêm Nhân Sự", THEME["success"], lambda: open_hdv_form(app)).pack(side="left", padx=5)
    style_button(toolbar, "Sửa Thông Tin", THEME["primary"], 
                 lambda: open_hdv_form(app, app["ql"].list_hdv[app["tv_hdv"].index(app["tv_hdv"].selection()[0])] if app["tv_hdv"].selection() else None)).pack(side="left", padx=5)
    style_button(toolbar, "Xóa HDV", THEME["danger"], lambda: delete_hdv(app)).pack(side="left", padx=5)

    # Table
    wrapper = tk.Frame(app["container"], bg=THEME["surface"], bd=1, relief="solid")
    wrapper.pack(fill="both", expand=True)

    cols = ("ma", "ten", "sdt", "email", "kn", "tt")
    tv = ttk.Treeview(wrapper, columns=cols, show="headings", height=15)
    app["tv_hdv"] = tv

    headings = [("ma", "Mã HDV"), ("ten", "Họ và Tên"), ("sdt", "Số Điện Thoại"), 
                ("email", "Email"), ("kn", "Kinh Nghiệm"), ("tt", "Trạng Thái")]
    for id, txt in headings:
        tv.heading(id, text=txt)
        tv.column(id, anchor="center", width=120)
    
    tv.column("ten", width=200, anchor="w")
    tv.pack(side="left", fill="both", expand=True)
    
    sy = ttk.Scrollbar(wrapper, orient="vertical", command=tv.yview)
    tv.configure(yscrollcommand=sy.set)
    sy.pack(side="right", fill="y")

    refresh_hdv(app)

def khoi_tao_he_thong(root):
    """Khởi chạy giao diện chính."""
    app = {
        "root": root,
        "ql": DataStore(),
        "container": None,
        "tv_hdv": None
    }

    # Style Treeview
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", font=("Times New Roman", 12), rowheight=32, background=THEME["surface"], fieldbackground=THEME["surface"], foreground=THEME["text"])
    style.configure("Treeview.Heading", font=("Times New Roman", 12, "bold"), background="#e2e8f0", foreground=THEME["text"])
    style.map("Treeview", background=[("selected", "#bfdbfe")], foreground=[("selected", THEME["text"])])

    # Sidebar
    sidebar = tk.Frame(root, bg=THEME["sidebar"], width=250)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(sidebar, text="VIETNAM\nTRAVEL", justify="center", bg=THEME["sidebar"], 
             fg="#10b981", font=("Times New Roman", 19, "bold"), pady=24).pack(fill="x")

    menu_items = [
        ("Dashboard", lambda: messagebox.showinfo("Dashboard", "Chức năng đang phát triển")),
        ("Quản Lý Tour", lambda: messagebox.showinfo("Tour", "Chức năng đang phát triển")),
        ("Hướng Dẫn Viên", lambda: tab_quan_ly_hdv(app)),
        ("Booking/Khách", lambda: messagebox.showinfo("Booking", "Chức năng đang phát triển")),
        ("Cài Đặt", lambda: messagebox.showinfo("Settings", "Chức năng đang phát triển"))
    ]

    for txt, cmd in menu_items:
        tk.Button(sidebar, text=f"   {txt}", bg=THEME["sidebar"], fg="white", bd=0, 
                  font=("Times New Roman", 13, "bold"), pady=14, anchor="w", padx=20, 
                  cursor="hand2", activebackground="#1e293b", command=cmd).pack(fill="x")

    # Content
    app["container"] = tk.Frame(root, bg=THEME["bg"], padx=25, pady=20)
    app["container"].pack(side="right", fill="both", expand=True)

    tab_quan_ly_hdv(app) # Mặc định
