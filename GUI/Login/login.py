import tkinter as tk
from tkinter import messagebox
import os
import sys

# Thêm đường dẫn để import từ Admin
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from GUI.Admin.Admin import THEME

# --- CẤU HÌNH FONT ---
FONT_STYLE = ("Times New Roman", 13)
FONT_BOLD = ("Times New Roman", 13, "bold")
FONT_TITLE = ("Times New Roman", 22, "bold")

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
    root.configure(bg=THEME["bg"])
    
    # Card container
    card = tk.Frame(root, bg=THEME["surface"], padx=40, pady=40,
                   highlightbackground=THEME["border"], highlightthickness=1)
    card.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(card, text="HỆ THỐNG DU LỊCH", font=FONT_TITLE, 
             bg=THEME["surface"], fg=THEME["primary"]).pack(pady=(0, 30))

    roles = [
        ("ADMIN (Quản trị)", THEME["danger"], "admin"),
        ("GUIDE (Hướng dẫn viên)", THEME["warning"], "guide"),
        ("USER (Khách du lịch)", THEME["success"], "user")
    ]

    for text, color, role_type in roles:
        tk.Button(card, text=text, bg=color, fg="white", font=FONT_BOLD,
                  width=25, height=2, cursor="hand2", bd=0,
                  command=lambda r=role_type: show_login_screen(r)).pack(pady=10)
    
    tk.Label(card, text="Phiên bản 2026", font=("Times New Roman", 10),
             bg=THEME["surface"], fg=THEME["muted"]).pack(pady=(20, 0))

# --- MÀN HÌNH 2: ĐĂNG NHẬP ---
def show_login_screen(role):
    global current_role
    current_role = role
    clear_screen()
    
    role_name = {"admin": "QUẢN TRỊ VIÊN", "guide": "HƯỚNG DẪN VIÊN", "user": "KHÁCH DU LỊCH"}
    
    # Card container
    card = tk.Frame(root, bg=THEME["surface"], padx=40, pady=40,
                   highlightbackground=THEME["border"], highlightthickness=1)
    card.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(card, text="ĐĂNG NHẬP", font=FONT_TITLE, 
             bg=THEME["surface"], fg=THEME["text"]).pack(pady=(0, 5))
    
    tk.Label(card, text=role_name[role], font=FONT_BOLD, 
             bg=THEME["surface"], fg=THEME["primary"]).pack(pady=(0, 25))

    tk.Label(card, text="Tài khoản:", font=FONT_STYLE, bg=THEME["surface"], fg=THEME["text"]).pack(anchor="w")
    ent_user = tk.Entry(card, width=30, font=FONT_STYLE, bd=1, relief="solid")
    ent_user.pack(pady=(5, 15), ipady=5)

    tk.Label(card, text="Mật khẩu:", font=FONT_STYLE, bg=THEME["surface"], fg=THEME["text"]).pack(anchor="w")
    ent_pass = tk.Entry(card, width=30, font=FONT_STYLE, show="*", bd=1, relief="solid")
    ent_pass.pack(pady=(5, 25), ipady=5)

    def handle_login():
        u, p = ent_user.get(), ent_pass.get()
        target_db = {"admin": db_admin, "guide": db_guides, "user": db_users}
        db = target_db[current_role]
        
        if u in db and db[u] == p:
            messagebox.showinfo("Thành công", f"Chào {u}! Đăng nhập thành công.")
        else:
            messagebox.showerror("Lỗi", "Tài khoản hoặc mật khẩu không chính xác!")

    tk.Button(card, text="ĐĂNG NHẬP", bg=THEME["primary"], fg="white", font=FONT_BOLD,
              width=25, height=2, cursor="hand2", bd=0, command=handle_login).pack(pady=10)

    if role == "user":
        tk.Button(card, text="Chưa có tài khoản? Đăng ký", fg=THEME["primary"], bd=0, 
                  bg=THEME["surface"], font=FONT_STYLE, cursor="hand2", 
                  command=show_register_screen).pack(pady=5)
    
    tk.Button(card, text="← Quay lại", bd=0, bg=THEME["surface"], font=FONT_STYLE, 
              fg=THEME["muted"], cursor="hand2", command=show_role_selection).pack(pady=5)

# --- MÀN HÌNH 3: ĐĂNG KÝ (USER ONLY) ---
def show_register_screen():
    clear_screen()
    
    # Card container
    card = tk.Frame(root, bg=THEME["surface"], padx=40, pady=30,
                   highlightbackground=THEME["border"], highlightthickness=1)
    card.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(card, text="ĐĂNG KÝ", font=FONT_TITLE, 
             bg=THEME["surface"], fg=THEME["success"]).pack(pady=(0, 20))

    tk.Label(card, text="Tên tài khoản:", font=FONT_STYLE, bg=THEME["surface"], fg=THEME["text"]).pack(anchor="w")
    reg_user = tk.Entry(card, width=30, font=FONT_STYLE, bd=1, relief="solid")
    reg_user.pack(pady=(5, 10), ipady=5)

    tk.Label(card, text="Mật khẩu mới:", font=FONT_STYLE, bg=THEME["surface"], fg=THEME["text"]).pack(anchor="w")
    reg_pass = tk.Entry(card, width=30, font=FONT_STYLE, show="*", bd=1, relief="solid")
    reg_pass.pack(pady=(5, 25), ipady=5)

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

    tk.Button(card, text="ĐĂNG KÝ NGAY", bg=THEME["success"], fg="white", font=FONT_BOLD,
              width=25, height=2, cursor="hand2", bd=0, command=handle_register).pack(pady=10)
    
    tk.Button(card, text="← Quay lại", bd=0, bg=THEME["surface"], font=FONT_STYLE, 
              fg=THEME["muted"], cursor="hand2", command=lambda: show_login_screen("user")).pack()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Login System")
    root.geometry("500x700")
    show_role_selection()
    root.mainloop()