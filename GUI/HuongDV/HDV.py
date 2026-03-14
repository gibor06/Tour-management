import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime

# --- CẤU HÌNH GIAO DIỆN ---
THEME = {
    'bg': '#f8fafc',
    'sidebar': '#1e293b',
    'active': '#334155',
    'primary': '#3b82f6',   # Blue (Sửa)
    'success': '#10b981',   # Green (Thêm/Lưu)
    'danger': '#ef4444',    # Red (Xóa)
    'warning': '#f59e0b',   # Orange (Xuất file)
    'info': '#06b6d4',      # Cyan (Nhập file)
    'border': '#cbd5e1',
    'text_light': '#ffffff',
    'text_dark': '#1e293b'
}

def apply_zebra(tree):
    tree.tag_configure('odd', background='#ffffff')
    tree.tag_configure('even', background='#f1f5f9')
    for i, item in enumerate(tree.get_children()):
        tree.item(item, tags=('even' if i % 2 == 0 else 'odd',))

# --- CÁC HÀM TIỆN ÍCH DỮ LIỆU ---

def export_data(app):
    messagebox.showinfo("Xuất dữ liệu", "Đã xuất danh sách thành file JSON thành công!")

def import_data(app):
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        messagebox.showinfo("Nhập dữ liệu", "Đã nạp dữ liệu từ file thành công!")

# --- CÁC HÀM XỬ LÝ HDV (THÊM, XÓA, SỬA) ---

def luu_hdv(app, entries, top, is_edit=False, old_ma=None):
    """Lấy dữ liệu từ ô nhập và lưu vào danh sách"""
    data = {k: v.get().strip() for k, v in entries.items()}

    if not data['maHDV'] or not data['tenHDV']:
        return messagebox.showwarning("Chú ý", "Vui lòng nhập Mã và Tên HDV!")

    if is_edit:
        # Cập nhật thông tin dựa trên mã cũ
        for i, h in enumerate(app['ql'].danh_sach_hdv):
            if h['maHDV'] == old_ma:
                app['ql'].danh_sach_hdv[i] = data
                break
    else:
        # Kiểm tra trùng mã khi thêm mới
        if any(h['maHDV'] == data['maHDV'] for h in app['ql'].danh_sach_hdv):
            return messagebox.showerror("Lỗi", "Mã HDV đã tồn tại!")
        app['ql'].danh_sach_hdv.append(data)

    top.destroy()
    mo_tab_hdv(app) # Làm mới bảng
    messagebox.showinfo("Thành công", "Đã cập nhật danh sách HDV!")

def xoa_hdv(app):
    sel = app['tv_hdv'].selection()
    if not sel: 
        return messagebox.showwarning("Chú ý", "Vui lòng chọn HDV cần xóa từ bảng!")
    
    item = app['tv_hdv'].item(sel[0])
    ma = item['values'][0]
    
    if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa HDV mã: {ma}?"):
        app['ql'].danh_sach_hdv = [h for h in app['ql'].danh_sach_hdv if h['maHDV'] != ma]
        mo_tab_hdv(app)

def form_hdv(app, edit_data=None):
    """Cửa sổ Popup để nhập hoặc sửa thông tin"""
    top = tk.Toplevel(app['root'])
    top.title("Thông tin Hướng dẫn viên")
    top.geometry("400x550")
    top.configure(bg='white')
    top.resizable(False, False)
    top.grab_set() # Ngăn tương tác với cửa sổ chính

    fields = [
        ('Mã HDV', 'maHDV'), ('Tên HDV', 'tenHDV'), 
        ('Số Điện Thoại', 'sdt'), ('Email', 'email'), 
        ('Kinh nghiệm (năm)', 'kinhNghiem')
    ]
    entries = {}

    for label, key in fields:
        f = tk.Frame(top, bg='white')
        f.pack(fill='x', padx=30, pady=8)
        tk.Label(f, text=label, bg='white', font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        e = tk.Entry(f, font=('Segoe UI', 11), bd=1, relief='solid')
        e.pack(fill='x', pady=5)
        if edit_data: 
            e.insert(0, edit_data.get(key, ''))
        entries[key] = e

    btn_text = "LƯU THAY ĐỔI" if edit_data else "THÊM MỚI HDV"
    btn_color = THEME['primary'] if edit_data else THEME['success']
    
    btn_save = tk.Button(top, text=btn_text, bg=btn_color, fg='white', 
                         font=('Segoe UI', 10, 'bold'), bd=2, relief='raised',
                         padx=20, pady=10, cursor='hand2',
                         command=lambda: luu_hdv(app, entries, top, edit_data is not None, edit_data['maHDV'] if edit_data else None))
    btn_save.pack(pady=20)

def hien_thi_sua(app):
    """Hàm trung gian để mở form sửa cho dòng đang chọn"""
    sel = app['tv_hdv'].selection()
    if not sel: 
        return messagebox.showwarning("Chú ý", "Vui lòng chọn 1 HDV từ bảng để sửa!")
    
    ma = app['tv_hdv'].item(sel[0], 'values')[0]
    hdv = next((h for h in app['ql'].danh_sach_hdv if h['maHDV'] == ma), None)
    if hdv: 
        form_hdv(app, hdv)

# --- GIAO DIỆN CHÍNH ---

def mo_tab_hdv(app):
    for w in app['container'].winfo_children(): w.destroy()
    
    # 1. Header & Utility Bar
    header_frame = tk.Frame(app['container'], bg=THEME['bg'])
    header_frame.pack(fill='x', pady=(0, 10))
    
    tk.Label(header_frame, text="DANH SÁCH HƯỚNG DẪN VIÊN", 
             font=('Segoe UI', 16, 'bold'), bg=THEME['bg'], fg=THEME['text_dark']).pack(side='left')
    
    util_bar = tk.Frame(header_frame, bg=THEME['bg'])
    util_bar.pack(side='right')
    
    utils = [
        ("Nhập JSON", THEME['info'], lambda: import_data(app)),
        ("Xuất Excel", THEME['warning'], lambda: export_data(app)),
        ("In ấn", "#64748b", lambda: messagebox.showinfo("In", "Đang chuẩn bị..."))
    ]
    for txt, color, cmd in utils:
        btn = tk.Button(util_bar, text=txt, bg='white', fg=color, font=('Segoe UI', 8, 'bold'),
                        bd=1, relief='solid', padx=10, pady=5, cursor='hand2', command=cmd)
        btn.pack(side='left', padx=3)

    # 2. Action Bar
    btn_bar = tk.Frame(app['container'], bg=THEME['bg'])
    btn_bar.pack(fill='x', pady=10)

    actions = [
        ("THÊM MỚI", THEME['success'], lambda: form_hdv(app)),
        ("CẬP NHẬT", THEME['primary'], lambda: hien_thi_sua(app)),
        ("XÓA NHÂN VIÊN", THEME['danger'], lambda: xoa_hdv(app))
    ]

    for txt, color, cmd in actions:
        btn = tk.Button(btn_bar, text=txt, bg=color, fg='white', font=('Segoe UI', 9, 'bold'),
                        bd=2, relief='raised', padx=20, pady=10, cursor='hand2', command=cmd)
        btn.pack(side='left', padx=5)

    # 3. Bảng dữ liệu
    frame_table = tk.Frame(app['container'], bg='white', bd=1, relief='solid')
    frame_table.pack(fill='both', expand=True)

    columns = ('ma', 'ten', 'sdt', 'email', 'kn')
    tv = ttk.Treeview(frame_table, columns=columns, show='headings')
    tv.heading('ma', text='Mã HDV'); tv.heading('ten', text='Họ Tên')
    tv.heading('sdt', text='Số Điện Thoại'); tv.heading('email', text='Email')
    tv.heading('kn', text='Kinh Nghiệm (Năm)')
    
    tv.column('ma', width=100, anchor='center')
    tv.column('ten', width=200, anchor='w')
    tv.column('kn', width=150, anchor='center')
    
    tv.pack(side='left', fill='both', expand=True)
    
    # Nạp dữ liệu
    for h in app['ql'].danh_sach_hdv:
        tv.insert('', 'end', values=(h['maHDV'], h['tenHDV'], h.get('sdt',''), h.get('email',''), h.get('kinhNghiem','')))
    
    apply_zebra(tv)
    app['tv_hdv'] = tv

def khoi_tao_he_thong(root):
    class QL: 
        def __init__(self): self.danh_sach_hdv = [
            {'maHDV': 'HDV001', 'tenHDV': 'Nguyễn Văn Anh', 'sdt': '0901234567', 'email': 'anh.nv@travel.com', 'kinhNghiem': '5'},
            {'maHDV': 'HDV002', 'tenHDV': 'Lê Thị Bình', 'sdt': '0987654321', 'email': 'binh.lt@travel.com', 'kinhNghiem': '3'}
        ]
    
    app = {
        'root': root,
        'container': None,
        'tv_hdv': None,
        'ql': QL()
    }

    # Sidebar
    sidebar = tk.Frame(root, bg=THEME['sidebar'], width=240)
    sidebar.pack(side='left', fill='y')
    sidebar.pack_propagate(False)

    tk.Label(sidebar, text="VIETNAM TRAVEL", font=('Segoe UI', 16, 'bold'), 
             fg=THEME['success'], bg=THEME['sidebar'], pady=30).pack()

    menu_items = [
        ("Biểu Đồ Doanh Thu", lambda: messagebox.showinfo("Dashboard", "Giao diện Biểu đồ đang được xây dựng")),
        ("Quản Lý Tour", lambda: messagebox.showinfo("Tours", "Giao diện Quản lý Tour")),
        ("Hướng Dẫn Viên", lambda: mo_tab_hdv(app)),
        ("Khách Hàng", lambda: messagebox.showinfo("Customers", "Giao diện Khách hàng")),
        ("Lịch Trình", lambda: messagebox.showinfo("Flight", "Giao diện Lịch trình")),
        ("Cài Đặt Hệ Thống", lambda: messagebox.showinfo("Settings", "Giao diện Cài đặt"))
    ]

    for txt, cmd in menu_items:
        btn = tk.Button(sidebar, text=f"  {txt}", bg=THEME['sidebar'], fg='white', bd=0, 
                        font=('Segoe UI', 10), pady=12, anchor='w', padx=20, 
                        cursor='hand2', activebackground=THEME['active'], command=cmd)
        btn.pack(fill='x')

    # Status Bar
    status_bar = tk.Frame(root, bg='#e2e8f0', bd=1, relief='sunken')
    status_bar.pack(side='bottom', fill='x')
    time_str = datetime.now().strftime("%d/%m/%Y")
    tk.Label(status_bar, text=f" Phiên bản: 2.1.0 | Ngày: {time_str} | Quản trị viên: NHUNG & TUYỀN ", 
             font=('Segoe UI', 8), bg='#e2e8f0', fg='#64748b').pack(side='left', padx=10)

    # Content Area
    app['container'] = tk.Frame(root, bg=THEME['bg'], padx=30, pady=20)
    app['container'].pack(side='right', fill='both', expand=True)

    mo_tab_hdv(app)