import tkinter as tk
from tkinter import ttk, messagebox

def khoi_tao_khach(root, user_data=None):
    # Xóa giao diện cũ để nạp giao diện Dashboard
    for widget in root.winfo_children():
        widget.destroy()

    # --- CẤU HÌNH MÀU SẮC & FONT ---
    COLOR_SIDEBAR = "#1e293b"
    COLOR_BG = "#f1f5f9"
    COLOR_CARD = "#ffffff"
    COLOR_PRIMARY = "#2563eb"
    COLOR_SUCCESS = "#10b981"
    
    FONT_TNR = ("Times New Roman", 14)
    FONT_BOLD = ("Times New Roman", 14, "bold")

    # --- DỮ LIỆU GỐC (GIẢ LẬP) ---
    # Cấu trúc: [Mã, Địa điểm, Thời gian, Phương tiện, HDV, SĐT HDV, Đã ĐK, Đánh giá]
    ds_tour_goc = [
        ["T001", "Hà Giang - Lũng Cú", "3 ngày 2 đêm", "Ô tô", "Nguyễn Văn An", "0901.222.333", 15, "4.9 ⭐"],
        ["T002", "Đà Nẵng - Hội An", "4 ngày 3 đêm", "Máy bay", "Trần Thị Bình", "0905.111.222", 22, "4.8 ⭐"],
        ["T003", "Vịnh Hạ Long", "2 ngày 1 đêm", "Du thuyền", "Lê Minh", "0912.444.555", 10, "5.0 ⭐"],
        ["T004", "Sapa - Fansipan", "3 ngày 2 đêm", "Tàu hỏa", "Hoàng Dũng", "0988.777.888", 18, "4.7 ⭐"]
    ]
    ds_da_dat = [] # Lưu các tour khách đã bấm đăng ký

    # --- SIDEBAR ---
    sidebar = tk.Frame(root, bg=COLOR_SIDEBAR, width=280)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(sidebar, text="VIETNAM\nTRAVEL", bg=COLOR_SIDEBAR, fg="#38bdf8", 
             font=("Times New Roman", 22, "bold")).pack(pady=40)

    # --- KHUNG NỘI DUNG CHÍNH ---
    content_area = tk.Frame(root, bg=COLOR_BG)
    content_area.pack(side="right", fill="both", expand=True)

    def xoa_khung_cu():
        for widget in content_area.winfo_children():
            widget.destroy()

    # --- TAB 1: DANH SÁCH & ĐĂNG KÝ ---
    def show_danh_sach():
        xoa_khung_cu()
        
        # 1. Chọn phương tiện
        filter_fr = tk.LabelFrame(content_area, text="Lựa chọn phương tiện ", font=FONT_BOLD, bg=COLOR_CARD, fg=COLOR_PRIMARY)
        filter_fr.pack(fill="x", padx=20, pady=10)

        var_pt = tk.StringVar(value="Tất cả")
        for opt in ["Tất cả", "Máy bay", "Ô tô", "Tàu hỏa", "Du thuyền"]:
            tk.Radiobutton(filter_fr, text=opt, variable=var_pt, value=opt, font=FONT_TNR, bg=COLOR_CARD, 
                           command=lambda: loc_tour(var_pt.get(), tree)).pack(side="left", padx=15, pady=5)

        # 2. Bảng Tour
        table_fr = tk.Frame(content_area, bg=COLOR_CARD)
        table_fr.pack(fill="both", expand=True, padx=20)
        
        cols = ("id", "place", "time", "trans", "rate")
        tree = ttk.Treeview(table_fr, columns=cols, show="headings", height=8)
        for col, txt in [("id", "Mã"), ("place", "Địa điểm"), ("time", "Thời gian"), ("trans", "Phương tiện"), ("rate", "Đánh giá")]:
            tree.heading(col, text=txt); tree.column(col, anchor="center", width=120)
        tree.column("place", width=300, anchor="w")
        tree.pack(fill="both", expand=True)
        
        # 3. Khung Đăng ký & Chi tiết
        reg_fr = tk.LabelFrame(content_area, text="Đăng ký & Thông tin HDV ", font=FONT_BOLD, bg="#f0f9ff")
        reg_fr.pack(fill="x", padx=20, pady=15)
        
        lbl_info = tk.Label(reg_fr, text="Chọn tour để xem HDV và số khách...", font=FONT_TNR, bg="#f0f9ff", fg="#1e40af")
        lbl_info.pack(side="left", padx=20, pady=10)

        def update_info(e):
            sel = tree.focus()
            if not sel: return
            val = tree.item(sel, "values")
            tour = next(t for t in ds_tour_goc if t[0] == val[0])
            lbl_info.config(text=f"{tour[1]} | HDV: {tour[4]} | {tour[5]}\n Hiện có {tour[6]} khách đã đăng ký")

        tree.bind("<<TreeviewSelect>>", update_info)

        def thuc_hien_dk():
            sel = tree.focus()
            if not sel: return messagebox.showwarning("Lỗi", "Vui lòng chọn tour!")
            tour = next(t for t in ds_tour_goc if t[0] == tree.item(sel, "values")[0])
            tour[6] += 1
            ds_da_dat.append(tour)
            messagebox.showinfo("Thành công", f"Đã đăng ký tour {tour[1]}!")
            update_info(None)

        tk.Button(reg_fr, text="ĐĂNG KÝ NGAY", bg=COLOR_SUCCESS, fg="white", font=FONT_BOLD, 
                  padx=20, command=thuc_hien_dk).pack(side="right", padx=20)
        
        loc_tour("Tất cả", tree)

    def loc_tour(mode, tree):
        for row in tree.get_children(): tree.delete(row)
        for t in ds_tour_goc:
            if mode == "Tất cả" or t[3] == mode:
                tree.insert("", "end", values=(t[0], t[1], t[2], t[3], t[7]))

    # --- TAB 2: TOUR ĐÃ ĐĂNG KÝ ---
    def show_tour_da_dat():
        xoa_khung_cu()
        tk.Label(content_area, text="DANH SÁCH TOUR BẠN ĐÃ ĐẶT", font=FONT_BOLD, bg=COLOR_BG).pack(pady=20)
        if not ds_da_dat:
            tk.Label(content_area, text="Bạn chưa đăng ký tour nào.", font=FONT_TNR, bg=COLOR_BG).pack()
            return
        
        for tour in ds_da_dat:
            item = tk.Frame(content_area, bg=COLOR_CARD, pady=10, padx=20, relief="groove", bd=1)
            item.pack(fill="x", padx=40, pady=5)
            tk.Label(item, text=f"✅ {tour[1]} - HDV: {tour[4]} ({tour[5]})", font=FONT_TNR, bg=COLOR_CARD).pack(side="left")

    # --- TAB 3: GỬI ĐÁNH GIÁ ---
    def show_feedback():
        xoa_khung_cu()
        tk.Label(content_area, text="GỬI ĐÁNH GIÁ CHO ADMIN & HDV", font=FONT_BOLD, bg=COLOR_BG).pack(pady=20)
        txt = tk.Text(content_area, height=10, font=FONT_TNR)
        txt.pack(padx=40, fill="x", pady=10)
        tk.Button(content_area, text="GỬI NHẬN XÉT", font=FONT_BOLD, bg=COLOR_PRIMARY, fg="white", 
                  padx=30, pady=10, command=lambda: messagebox.showinfo("Cảm ơn", "Đã gửi đánh giá!")).pack()

    # --- SIDEBAR BUTTONS ---
    btn_style = {"bg": COLOR_SIDEBAR, "fg": "white", "font": FONT_TNR, "bd": 0, "anchor": "w", "padx": 25, "pady": 15, "cursor": "hand2"}
    
    tk.Button(sidebar, text="Danh sách Tour", **btn_style, command=show_danh_sach).pack(fill="x")
    tk.Button(sidebar, text="Tour đã đăng ký", **btn_style, command=show_tour_da_dat).pack(fill="x")
    tk.Button(sidebar, text="Gửi đánh giá", **btn_style, command=show_feedback).pack(fill="x")

    tk.Button(sidebar, text="ĐĂNG XUẤT", bg="#ef4444", fg="white", font=FONT_BOLD, 
              bd=0, pady=15, command=root.destroy).pack(side="bottom", fill="x", pady=20)

    # Mặc định mở tab đầu tiên
    show_danh_sach()

if __name__ == "__main__":
    win = tk.Tk()
    win.title("Vietnam Travel 2026")
    win.geometry("1400x850")
    khoi_tao_khach(win, {"name": "NHUNG"})
    win.mainloop()