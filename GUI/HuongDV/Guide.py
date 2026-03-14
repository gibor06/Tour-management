import tkinter as tk
from tkinter import messagebox, ttk

def khoi_tao_hdv(root, user_data=None):
    # --- CẤU HÌNH STYLE ---
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview.Heading", font=('Times New Roman', 14, 'bold'), foreground="#ffffff", background="#1e3a8a")
    style.configure("Treeview", font=('Times New Roman', 13), rowheight=35)

    # --- DỮ LIỆU GIẢ LẬP (DATABASE) ---
    db_tours = {
        "T001": {
            "name": "Khám phá Sài Gòn",
            "diem_den": [("08:00", "Dinh Độc Lập", "Quận 1"), ("10:00", "Bưu Điện TP", "Quận 1")],
            "khach_hang": [("Nguyễn Văn An", "0901xxx", "Đã thanh toán"), ("Lê Thị Bình", "0912xxx", "Chưa thanh toán")]
        },
        "T002": {
            "name": "Ẩm thực đường phố",
            "diem_den": [("09:00", "Chợ Bến Thành", "Quận 1"), ("11:00", "Bitexco", "Quận 1")],
            "khach_hang": [("Trần Văn Cường", "0988xxx", "Đã thanh toán")]
        }
    }

    # --- GIAO DIỆN CHÍNH ---
    sidebar = tk.Frame(root, bg='#0f172a', width=280)
    sidebar.pack(side='left', fill='y')
    sidebar.pack_propagate(False)

    tk.Label(sidebar, text="VIETNAM TRAVEL", font=('Times New Roman', 18, 'bold'), fg='#10b981', bg='#0f172a', pady=30).pack()

    content_area = tk.Frame(root, bg='#f1f5f9', padx=30, pady=20)
    content_area.pack(side='right', fill='both', expand=True)

    # --- HÀM XỬ LÝ CLICK CHỌN TOUR (TỪ CODE CŨ) ---
    def hien_thi_chi_tiet(event):
        selected_item = tv_tours.selection()
        if not selected_item: return
        tour_id = tv_tours.item(selected_item)['values'][0]
        
        for w in detail_frame.winfo_children(): w.destroy()
        
        if tour_id in db_tours:
            data = db_tours[tour_id]
            # Bảng Địa Điểm
            tk.Label(detail_frame, text=f"CHI TIẾT ĐỊA ĐIỂM - {tour_id}", font=('Times New Roman', 14, 'bold'), fg='#1e3a8a', bg='#f1f5f9').pack(pady=5)
            tv_loc = ttk.Treeview(detail_frame, columns=('t','n','a'), show='headings', height=3)
            tv_loc.heading('t', text='Giờ'); tv_loc.heading('n', text='Địa điểm'); tv_loc.heading('a', text='Khu vực')
            for c in ('t','n','a'): tv_loc.column(c, anchor='center')
            for loc in data['diem_den']: tv_loc.insert('', 'end', values=loc)
            tv_loc.pack(fill='x', pady=5)
            # Bảng Khách Hàng
            tk.Label(detail_frame, text="DANH SÁCH KHÁCH TRONG ĐOÀN", font=('Times New Roman', 14, 'bold'), fg='#b91c1c', bg='#f1f5f9').pack(pady=5)
            tv_cus = ttk.Treeview(detail_frame, columns=('n','p','s'), show='headings', height=3)
            tv_cus.heading('n', text='Tên khách'); tv_cus.heading('p', text='SĐT'); tv_cus.heading('s', text='Trạng thái')
            for c in ('n','p','s'): tv_cus.column(c, anchor='center')
            for cus in data['khach_hang']: tv_cus.insert('', 'end', values=cus)
            tv_cus.pack(fill='x')

    # --- CÁC TAB CHỨC NĂNG ---

    def mo_tab_danh_sach_tour():
        for w in content_area.winfo_children(): w.destroy()
        tk.Label(content_area, text="QUẢN LÝ TOUR ĐƯỢC GIAO", font=('Times New Roman', 18, 'bold'), fg='#1e3a8a', bg='#f1f5f9').pack(pady=(0, 10))
        
        global tv_tours, detail_frame
        tv_tours = ttk.Treeview(content_area, columns=('id','name','date'), show='headings', height=5)
        tv_tours.heading('id', text='Mã Tour'); tv_tours.heading('name', text='Tên Tour'); tv_tours.heading('date', text='Khởi hành')
        for c in ('id','name','date'): tv_tours.column(c, anchor='center')
        
        for tid, tinfo in db_tours.items():
            tv_tours.insert('', 'end', values=(tid, tinfo['name'], "12/03/2026"))
        
        tv_tours.pack(fill='x', pady=10)
        tv_tours.bind("<<TreeviewSelect>>", hien_thi_chi_tiet)
        detail_frame = tk.Frame(content_area, bg='#f1f5f9')
        detail_frame.pack(fill='both', expand=True)

    def mo_tab_thong_ke():
        for w in content_area.winfo_children(): w.destroy()
    
        # --- TIÊU ĐỀ CHÍNH ---
        tk.Label(content_area, text="TRUNG TÂM PHÂN TÍCH & ĐÁNH GIÁ HIỆU SUẤT", 
                 font=('Times New Roman', 18, 'bold'), fg='#1e3a8a', bg='#f1f5f9').pack(pady=(0, 20))
    
        # --- 1. THẺ THÔNG SỐ NHANH (CARDS) ---
        card_frame = tk.Frame(content_area, bg='#f1f5f9')
        card_frame.pack(fill='x', pady=10)
    
        stats = [
            ("Điểm Đánh Giá", "4.9 / 5.0", "#f59e0b"), 
            ("Tỷ Lệ Hoàn Thành", "95%", "#10b981"), 
            ("Phản Hồi Tích Cực", "98.5%", "#ec4899")
        ]
    
        for t, v, c in stats:
            f = tk.Frame(card_frame, bg='white', bd=1, relief='solid', padx=15, pady=15)
            f.pack(side='left', expand=True, fill='both', padx=10)
            tk.Label(f, text=t, font=('Times New Roman', 14, 'bold'), bg='white').pack()
            tk.Label(f, text=v, font=('Times New Roman', 22, 'bold'), fg=c, bg='white').pack()

        # --- 2. BIỂU ĐỒ GIẢ LẬP (SÁNG TẠO) ---
        tk.Label(content_area, text="Mức độ hài lòng theo tiêu chí (%)", 
                 font=('Times New Roman', 15, 'bold'), bg='#f1f5f9', fg='#1e293b').pack(pady=(20, 10))
    
        chart_frame = tk.Frame(content_area, bg='white', bd=1, relief='flat', padx=20, pady=20)
        chart_frame.pack(fill='x', padx=10)

        criteria = [("Kiến thức chuyên môn", 95, "#3b82f6"), 
                    ("Thái độ phục vụ", 98, "#10b981"), 
                    ("Xử lý tình huống", 85, "#f59e0b")]

        for name, val, color in criteria:
            row = tk.Frame(chart_frame, bg='white')
            row.pack(fill='x', pady=5)
            tk.Label(row, text=name, font=('Times New Roman', 13), width=20, anchor='w', bg='white').pack(side='left')
        
            # Thanh tiến trình giả lập biểu đồ
            progress_bg = tk.Frame(row, bg='#e2e8f0', width=400, height=20)
            progress_bg.pack(side='left', padx=10)
            progress_bg.pack_propagate(False)
        
            tk.Frame(progress_bg, bg=color, width=int(val * 4), height=20).pack(side='left') # Độ dài dựa trên %
            tk.Label(row, text=f"{val}%", font=('Times New Roman', 13, 'bold'), bg='white').pack(side='left')

        # --- 3. BẢNG ĐÁNH GIÁ CHI TIẾT TỪ KHÁCH ---
        tk.Label(content_area, text="Chi tiết đánh giá gần nhất", 
                 font=('Times New Roman', 15, 'bold'), bg='#f1f5f9', fg='#1e293b').pack(pady=(20, 10))

        cols = ('id', 'guest', 'star', 'comment')
        tv_feedback = ttk.Treeview(content_area, columns=cols, show='headings', height=4)
        tv_feedback.heading('id', text='Mã Tour'); tv_feedback.heading('guest', text='Khách Hàng')
        tv_feedback.heading('star', text='Số Sao'); tv_feedback.heading('comment', text='Nội Dung Phản Hồi')
    
        for c in cols: tv_feedback.column(c, anchor='center')
        tv_feedback.column('comment', width=400) # Cột nhận xét rộng hơn

        # Dữ liệu đánh giá mẫu
        feedbacks = [
            ("T001", "Nguyễn An", "⭐⭐⭐⭐⭐", "HDV rất am hiểu lịch sử, nói chuyện lôi cuốn."),
            ("T001", "Trần Bình", "⭐⭐⭐⭐", "Chuyến đi tuyệt vời, nhưng thời gian hơi gấp."),
            ("T002", "Lê Cường", "⭐⭐⭐⭐⭐", "Món ăn ngon, HDV hỗ trợ nhiệt tình lúc mình bị lạc.")
        ]
        for fb in feedbacks: tv_feedback.insert('', 'end', values=fb)
        tv_feedback.pack(fill='x', pady=5)

    def mo_tab_thong_bao():
        for w in content_area.winfo_children(): w.destroy()
        tk.Label(content_area, text="GỬI THÔNG BÁO CHO ĐOÀN KHÁCH", font=('Times New Roman', 18, 'bold'), fg='#b91c1c', bg='#f1f5f9').pack(pady=(0, 10))
        tk.Label(content_area, text="Nhập nội dung (SMS/App):", font=('Times New Roman', 13), bg='#f1f5f9').pack(anchor='w')
        txt = tk.Text(content_area, height=8, font=('Times New Roman', 14)); txt.pack(fill='x', pady=10)
        tk.Button(content_area, text="XÁC NHẬN GỬI", bg='#b91c1c', fg='white', font=('Times New Roman', 14, 'bold'), 
                  padx=20, pady=10, command=lambda: messagebox.showinfo("Gửi", "Đã gửi thông báo thành công!")).pack()

    # --- MENU SIDEBAR ---
    btn_style = {"font": ('Times New Roman', 14, 'bold'), "bg": '#1e293b', "fg": 'white', "bd": 0, "pady": 15, "anchor": 'w', "padx": 20, "cursor": 'hand2'}
    
    tk.Button(sidebar, text="Danh Sách Tour", command=mo_tab_danh_sach_tour, **btn_style).pack(fill='x')
    tk.Button(sidebar, text="Thống Kê Báo Cáo", command=mo_tab_thong_ke, **btn_style).pack(fill='x')
    tk.Button(sidebar, text="Gửi Thông Báo", command=mo_tab_thong_bao, **btn_style).pack(fill='x')
    tk.Button(sidebar, text="Đăng Xuất", command=root.quit, **btn_style).pack(fill='x', side='bottom')

    mo_tab_danh_sach_tour() # Mặc định mở danh sách tour