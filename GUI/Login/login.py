import tkinter as tk
from tkinter import messagebox

# --- CẤU HÌNH FONT ---
FONT_STYLE = ("Times New Roman", 14)
FONT_BOLD = ("Times New Roman", 14, "bold")

# --- DỮ LIỆU GIẢ LẬP ---
db_users = {"khach01": "123"}
db_guides = {"HDV01": "123"}
db_admin = {"admin": "123"}

current_role = ""

def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()

# --- MÀN HÌNH 1: CHỌN VAI TRÒ ---
def show_role_selection():
    clear_screen()
    tk.Label(root, text="HỆ THỐNG QUẢN LÝ DU LỊCH", font=("Times New Roman", 18, "bold"), 
             bg="#f0f2f5", fg="#1a73e8").pack(pady=40)

    # Nút Admin
    tk.Button(root, text="ADMIN (Quản trị)", bg="#eb4d4b", fg="white", font=FONT_BOLD,
              width=25, command=lambda: show_login_screen("admin")).pack(pady=10)
    
    # Nút Guide
    tk.Button(root, text="GUIDE (Hướng dẫn viên)", bg="#f0932b", fg="white", font=FONT_BOLD,
              width=25, command=lambda: show_login_screen("guide")).pack(pady=10)
    
    # Nút User
    tk.Button(root, text="USER (Khách du lịch)", bg="#6ab04c", fg="white", font=FONT_BOLD,
              width=25, command=lambda: show_login_screen("user")).pack(pady=10)

# --- MÀN HÌNH 2: ĐĂNG NHẬP ---
def show_login_screen(role):
    global current_role
    current_role = role
    clear_screen()
    
    role_name = {"admin": "QUẢN TRỊ VIÊN", "guide": "HƯỚNG DẪN VIÊN", "user": "KHÁCH DU LỊCH"}
    
    tk.Label(root, text=f"ĐĂNG NHẬP\n[{role_name[role]}]", 
             font=("Times New Roman", 16, "bold"), bg="#f0f2f5").pack(pady=20)

    tk.Label(root, text="Tài khoản:", font=FONT_STYLE, bg="#f0f2f5").pack()
    ent_user = tk.Entry(root, width=25, font=FONT_STYLE)
    ent_user.pack(pady=5)

    tk.Label(root, text="Mật khẩu:", font=FONT_STYLE, bg="#f0f2f5").pack()
    ent_pass = tk.Entry(root, width=25, font=FONT_STYLE, show="*")
    ent_pass.pack(pady=5)

    def handle_login():
        u, p = ent_user.get(), ent_pass.get()
        target_db = {"admin": db_admin, "guide": db_guides, "user": db_users}
        db = target_db[current_role]
        
        if u in db and db[u] == p:
            messagebox.showinfo("Thành công", f"Chào {u}! Bạn đang đăng nhập với vai trò {current_role}.")
            # Sau khi đăng nhập thành công, có thể gọi hàm mở giao diện chính ở đây
        else:
            messagebox.showerror("Lỗi", "Tài khoản hoặc mật khẩu không chính xác!")

    tk.Button(root, text="ĐĂNG NHẬP", bg="#1a73e8", fg="white", font=FONT_BOLD,
              width=15, command=handle_login).pack(pady=20)

    if role == "user":
        tk.Button(root, text="Chưa có tài khoản? Đăng ký", fg="#1a73e8", bd=0, 
                  bg="#f0f2f5", font=FONT_STYLE, command=show_register_screen).pack()
    
    tk.Button(root, text="← Quay lại", bd=0, bg="#f0f2f5", font=FONT_STYLE, 
              command=show_role_selection).pack(pady=10)

# --- MÀN HÌNH 3: ĐĂNG KÝ (USER ONLY) ---
def show_register_screen():
    clear_screen()
    tk.Label(root, text="ĐĂNG KÝ THÀNH VIÊN", font=("Times New Roman", 16, "bold"), 
             bg="#f0f2f5", fg="#6ab04c").pack(pady=30)

    tk.Label(root, text="Tên tài khoản mới:", font=FONT_STYLE, bg="#f0f2f5").pack()
    reg_user = tk.Entry(root, width=25, font=FONT_STYLE)
    reg_user.pack(pady=5)

    tk.Label(root, text="Mật khẩu mới:", font=FONT_STYLE, bg="#f0f2f5").pack()
    reg_pass = tk.Entry(root, width=25, font=FONT_STYLE, show="*")
    reg_pass.pack(pady=5)

    def handle_register():
        u, p = reg_user.get(), reg_pass.get()
        if u and p:
            if u in db_users:
                messagebox.showwarning("Lỗi", "Tên tài khoản này đã tồn tại!")
            else:
                db_users[u] = p
                messagebox.showinfo("Xong", "Đăng ký thành công! Mời bạn đăng nhập.")
                show_login_screen("user")
        else:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!")

    tk.Button(root, text="XÁC NHẬN ĐĂNG KÝ", bg="#6ab04c", fg="white", 
              font=FONT_BOLD, width=20, command=handle_register).pack(pady=20)
    
    tk.Button(root, text="Quay lại", bd=0, bg="#f0f2f5", font=FONT_STYLE, 
              command=lambda: show_login_screen("user")).pack()

# --- THIẾT LẬP CỬA SỔ CHÍNH ---
root = tk.Tk()
root.title("Quản lý Hành trình Du lịch")
root.geometry("450x600")
root.configure(bg="#f0f2f5")

# Chạy màn hình đầu tiên
show_role_selection()

root.mainloop()