import tkinter as tk
from tkinter import messagebox, ttk

# --- 1. CẤU HÌNH THEME ---
THEME = {
    'bg': '#f8fafc',
    'sidebar': '#0f172a',
    'primary': '#2563eb',
    'success': '#059669',
    'danger': '#dc2626',
    'warning': '#d97706',
    'note_bg': '#fff7ed'
}

# --- 2. QUẢN LÝ DỮ LIỆU ---
class QuanLyDuLieu:
    def __init__(self):
        self.list_hdv = [{'maHDV':'HDV01','tenHDV':'Nguyễn Văn Anh','sdt':'0901234567','email':'anh@travel.com','kn':'5'}]
        self.list_tours = [{'ma':'T01','ten':'Đà Lạt Phố Hoa','ngay':'15/03/2026','khach':'20'}]

# --- 3. CÁC HÀM LOGIC (PHẢI ĐỂ TRÊN ĐẦU ĐỂ KHÔNG BỊ LỖI "NOT DEFINED") ---

def apply_zebra(tree):
    tree.tag_configure('odd', background='#ffffff')
    tree.tag_configure('even', background='#f1f5f9')
    for i, item in enumerate(tree.get_children()):
        tree.item(item, tags=('even' if i % 2 == 0 else 'odd',))

def refresh_hdv(app):
    for i in app['tv_hdv'].get_children(): app['tv_hdv'].delete(i)
    for h in app['ql'].list_hdv:
        app['tv_hdv'].insert('', 'end', values=(h['maHDV'], h['tenHDV'], h['sdt'], h['email'], h['kn']))
    apply_zebra(app['tv_hdv'])

def delete_hdv(app):
    sel = app['tv_hdv'].selection()
    if sel:
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa nhân sự này?"):
            ma = app['tv_hdv'].item(sel[0])['values'][0]
            app['ql'].list_hdv = [h for h in app['ql'].list_hdv if h['maHDV'] != ma]
            refresh_hdv(app)
    else:
        messagebox.showwarning("Thông báo", "Vui lòng chọn nhân sự cần xóa!")

def open_form_hdv(app, data=None):
    top = tk.Toplevel(app['root'])
    top.grab_set()
    top.title("Thông tin nhân sự")
    top.geometry("450x620")
    
    ents = {}
    fields = [('Mã HDV','maHDV'),('Tên HDV','tenHDV'),('SĐT','sdt'),('Email','email'),('Kinh nghiệm','kn')]
    
    for l, k in fields:
        f = tk.Frame(top)
        f.pack(fill='x', padx=30, pady=10) # Khoảng cách giữa các ô
        tk.Label(f, text=l, font=('Times New Roman', 14, 'bold')).pack(anchor='w')
        e = tk.Entry(f, font=('Times New Roman', 14), bd=2, relief='groove')
        e.pack(fill='x', ipady=8) # ipady giúp ô nhập liệu to và thoáng
        if data: e.insert(0, data[k])
        ents[k] = e

    def save():
        new_d = {k: v.get().strip() for k, v in ents.items()}
        if data:
            for i, h in enumerate(app['ql'].list_hdv):
                if h['maHDV'] == data['maHDV']: app['ql'].list_hdv[i] = new_d
        else:
            app['ql'].list_hdv.append(new_d)
        top.destroy()
        refresh_hdv(app)

    tk.Button(top, text="XÁC NHẬN LƯU", bg=THEME['success'], fg='white', 
              font=('Times New Roman', 14, 'bold'), pady=10, command=save).pack(pady=20, fill='x', padx=30)

def edit_hdv(app):
    sel = app['tv_hdv'].selection()
    if sel:
        ma = app['tv_hdv'].item(sel[0])['values'][0]
        hdv = next(h for h in app['ql'].list_hdv if h['maHDV'] == ma)
        open_form_hdv(app, hdv)
    else:
        messagebox.showwarning("Thông báo", "Vui lòng chọn nhân sự cần sửa!")

# --- 4. GIAO DIỆN CÁC TAB ---

def mo_tab_dashboard(app):
    for w in app['container'].winfo_children(): w.destroy()
    tk.Label(app['container'], text="HỆ THỐNG VIETNAM TRAVEL", font=('Times New Roman', 22, 'bold'), bg=THEME['bg']).pack(pady=20)
    
    f_stat = tk.Frame(app['container'], bg=THEME['bg']); f_stat.pack(fill='x', pady=10)
    for t, v, c in [("Doanh Thu", "45,000,000đ", THEME['primary']), ("Mục Tiêu", "80%(1 tỷ)", THEME['warning'])]:
        card = tk.Frame(f_stat, bg='white', padx=20, pady=20, bd=1, relief='flat')
        card.pack(side='left', expand=True, fill='both', padx=10)
        tk.Label(card, text=t, font=('Times New Roman', 14), bg='white').pack()
        tk.Label(card, text=v, font=('Times New Roman', 24, 'bold'), bg='white', fg=c).pack()

    # PHẦN GHI CHÚ (NOTE)
    f_note = tk.LabelFrame(app['container'], text="Ghi chú quan trọng", font=('Times New Roman', 14, 'bold'), 
                           bg=THEME['note_bg'], padx=20, pady=20, fg='#c2410c')
    f_note.pack(fill='x', pady=30, padx=10)
    tk.Label(f_note, text="• Tour Sapa 15/03: Kiểm tra lại danh sách phòng.\n• Bảo trì hệ thống vào 23:00 tối nay.", 
             font=('Times New Roman', 14), bg=THEME['note_bg'], justify='left', fg='#92400e').pack(anchor='w')

def mo_tab_hdv(app):
    for w in app['container'].winfo_children(): w.destroy()
    tk.Label(app['container'], text="QUẢN LÝ NHÂN SỰ HDV", font=('Times New Roman', 18, 'bold'), bg=THEME['bg']).pack(pady=10)

    btn_f = tk.Frame(app['container'], bg=THEME['bg']); btn_f.pack(fill='x', pady=10)
    tk.Button(btn_f, text="Thêm HDV", bg=THEME['success'], fg='white', command=lambda: open_form_hdv(app)).pack(side='left', padx=5)
    tk.Button(btn_f, text="Cập nhật", bg=THEME['primary'], fg='white', command=lambda: edit_hdv(app)).pack(side='left', padx=5)
    tk.Button(btn_f, text="Xóa", bg=THEME['danger'], fg='white', command=lambda: delete_hdv(app)).pack(side='left', padx=5)

    app['tv_hdv'] = ttk.Treeview(app['container'], columns=('ma','ten','sdt','mail','kn'), show='headings', height=12)
    for c, t in [('ma','Mã'),('ten','Họ Tên'),('sdt','SĐT'),('mail','Email'),('kn','KN')]:
        app['tv_hdv'].heading(c, text=t); app['tv_hdv'].column(c, anchor='center')
    app['tv_hdv'].pack(fill='both', expand=True)
    refresh_hdv(app)

def refresh_tour(app):

    for i in app['tv_tour'].get_children():
        app['tv_tour'].delete(i)

    for t in app['ql'].list_tours:
        app['tv_tour'].insert(
            '',
            'end',
            values=(t['ma'], t['ten'], t['ngay'], t['khach'])
        )

    apply_zebra(app['tv_tour'])

def mo_tab_tuyen_di(app):
    for w in app['container'].winfo_children(): w.destroy()
    tk.Label(app['container'], text="ĐIỀU HÀNH CHUYẾN ĐI", font=('Times New Roman', 18, 'bold'), bg=THEME['bg']).pack(pady=10)

    app['tv_tour'] = ttk.Treeview(app['container'], columns=('ma','ten','ngay','khach'), show='headings', height=6)
    for c, t in [('ma','Mã Tour'),('ten','Tên Tuyến'),('ngay','Khởi Hành'),('khach','Khách')]:
        app['tv_tour'].heading(c, text=t); app['tv_tour'].column(c, anchor='center')
    app['tv_tour'].pack(fill='x', pady=5); refresh_tour(app)

    # Vùng hiện thông tin chi tiết (Chỉ hiện khi Click)
    split_f = tk.Frame(app['container'], bg=THEME['bg']); split_f.pack(fill='both', expand=True, pady=15)
    f_left = tk.Frame(split_f, bg=THEME['bg']); f_left.pack(side='left', fill='both', expand=True, padx=(0, 10))
    f_right = tk.Frame(split_f, bg=THEME['bg']); f_right.pack(side='left', fill='both', expand=True)

    def on_tour_select(e):
        for w in f_left.winfo_children(): w.destroy()
        for w in f_right.winfo_children(): w.destroy()
        if app['tv_tour'].selection():
            # Khung HDV
            lf_hdv = tk.LabelFrame(f_left, text="Thông tin HDV", font=('Times New Roman', 14, 'bold'), bg='white', padx=15, pady=15)
            lf_hdv.pack(fill='both', expand=True)
            tk.Label(lf_hdv, text="Họ tên: Nguyễn Văn Anh\nSĐT: 0901234567\nKinh nghiệm: 5 năm", 
                     font=('Times New Roman', 14), bg='white', justify='left').pack(anchor='w')
            # Khung Khách hàng
            lf_kh = tk.LabelFrame(f_right, text="Thông tin Khách hàng", font=('Times New Roman', 14, 'bold'), bg='white', padx=15, pady=15)
            lf_kh.pack(fill='both', expand=True)
            tk.Label(lf_kh, text="1. Trần Thế Hệ - 012xxx\n2. Phạm Hải Yến - 098xxx", 
                     font=('Times New Roman', 14), bg='white', justify='left').pack(anchor='w')

    app['tv_tour'].bind("<<TreeviewSelect>>", on_tour_select)

def thuc_hien_dang_xuat(app):
    if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất khỏi hệ thống?"):
        app['root'].destroy()



# --- 5. HÀM CHÍNH (QUAN TRỌNG: CÓ NHẬN ROOT) ---
def main(root):
    root = tk.Tk()
    root.title("Vietnam Travel Admin - Hệ Thống Quản Lý")
    root.geometry("1150x780")
    
    app = {
        'root': root,
        'container': None,
        'ql': QuanLyDuLieu(),
        'tv_hdv': None,
        'tv_tour': None
    }
    
    # Style cho bảng
    style = ttk.Style()
    style.configure("Treeview.Heading", font=('Times New Roman', 13, 'bold'))
    style.configure("Treeview", font=('Times New Roman', 13), rowheight=35)

    # Sidebar
    sidebar = tk.Frame(root, bg=THEME['sidebar'], width=240)
    sidebar.pack(side='left', fill='y'); sidebar.pack_propagate(False)
    
    tk.Label(sidebar, text="VIETNAM TRAVEL", font=('Times New Roman', 16, 'bold'), fg='#10b981', bg=THEME['sidebar'], pady=30).pack()
    
    menu = [("Dashboard", lambda: mo_tab_dashboard(app)), 
            ("Nhân Sự HDV", lambda: mo_tab_hdv(app)), 
            ("Chuyến Đi", lambda: mo_tab_tuyen_di(app))]
               
    for text, cmd in menu:
        tk.Button(sidebar, text=f"  {text}", bg=THEME['sidebar'], fg='white', bd=0, 
                  font=('Times New Roman', 14, 'bold'), pady=15, anchor='w', padx=20, command=cmd).pack(fill='x')

    # Nút Đăng xuất ở dưới cùng Sidebar
    tk.Button(sidebar, text="Đăng xuất", bg=THEME['sidebar'], fg=THEME['danger'], bd=0, 
              font=('Times New Roman', 14, 'bold'), pady=15, anchor='w', padx=20, 
              command=lambda: thuc_hien_dang_xuat(app)).pack(side='bottom', fill='x', pady=20)

    # Vùng chính
    app['container'] = tk.Frame(root, bg=THEME['bg'], padx=30, pady=20)
    app['container'].pack(side='right', fill='both', expand=True)
    
    # Mở mặc định Dashboard
    mo_tab_dashboard(app)
    
    root.mainloop()

if __name__ == "__main__":
    main()