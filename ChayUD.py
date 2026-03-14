import tkinter as tk
from tkinter import messagebox

# Import các hàm giao diện từ các file khác
from GUI.Admin.Admin import main as hien_thi_admin
from GUI.HuongDV.Guide import khoi_tao_hdv as hien_thi_guide
from GUI.Khach.user import khoi_tao_khach as hien_thi_khach

class TravelSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống Quản lý Du lịch 2026")
        self.root.geometry("450x600")
        self.root.configure(bg="#f0f2f5")

        # Database giả lập
        self.db_users = {"Khach": "123"}
        self.db_guides = {"HDV01": "123"}
        self.db_admin = {"admin": "123"}

        self.main_frame = tk.Frame(self.root, bg="#f0f2f5")
        self.main_frame.pack(expand=True, fill="both")

        self.show_role_selection()

    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_role_selection(self):
        self.clear_screen()
        # Đặt lại kích thước nhỏ cho màn hình Login
        self.root.geometry("450x600")
        tk.Label(self.main_frame, text="BẠN LÀ AI?", font=("Arial", 18, "bold"), 
                 bg="#f0f2f5", fg="#1a73e8").pack(pady=40)

        roles = [
            ("ADMIN (Quản trị)", "#eb4d4b", "admin"),
            ("GUIDE (Hướng dẫn viên)", "#f0932b", "guide"),
            ("USER (Khách du lịch)", "#6ab04c", "user")
        ]

        for text, color, role_type in roles:
            btn = tk.Button(self.main_frame, text=text, bg=color, fg="white",
                            font=("Arial", 11, "bold"), width=25, height=2,
                            command=lambda r=role_type: self.show_login_screen(r))
            btn.pack(pady=10)

    def show_login_screen(self, role):
        self.clear_screen()
        self.current_role = role
        role_name = {"admin": "QUẢN TRỊ VIÊN", "guide": "HƯỚNG DẪN VIÊN", "user": "KHÁCH DU LỊCH"}
        
        tk.Label(self.main_frame, text=f"ĐĂNG NHẬP\n[{role_name[role]}]", 
                 font=("Arial", 16, "bold"), bg="#f0f2f5").pack(pady=30)

        tk.Label(self.main_frame, text="Tài khoản:", bg="#f0f2f5").pack()
        self.ent_user = tk.Entry(self.main_frame, width=30, font=("Arial", 11))
        self.ent_user.pack(pady=5)

        tk.Label(self.main_frame, text="Mật khẩu:", bg="#f0f2f5").pack()
        self.ent_pass = tk.Entry(self.main_frame, width=30, font=("Arial", 11), show="*")
        self.ent_pass.pack(pady=5)

        tk.Button(self.main_frame, text="ĐĂNG NHẬP", bg="#1a73e8", fg="white",
                  width=20, command=self.handle_login).pack(pady=20)

        if role == "user":
            tk.Button(self.main_frame, text="Đăng ký khách mới", fg="#1a73e8", bd=0, 
                      bg="#f0f2f5", command=self.show_register_screen).pack()
        
        tk.Button(self.main_frame, text="← Quay lại", bd=0, bg="#f0f2f5", 
                  command=self.show_role_selection).pack(pady=10)

    def handle_login(self):
        u, p = self.ent_user.get(), self.ent_pass.get()
        target_db = {"admin": self.db_admin, "guide": self.db_guides, "user": self.db_users}
        db = target_db[self.current_role]
        
        if u in db and db[u] == p:
            messagebox.showinfo("Thành công", f"Chào mừng {u}!")
            self.redirect_to_interface(u)
        else:
            messagebox.showerror("Lỗi", "Sai tài khoản hoặc mật khẩu!")

    def redirect_to_interface(self, username):
        """Hàm quan trọng: Xóa màn hình login và mở giao diện chính"""
        self.main_frame.destroy() # Xóa toàn bộ khung login
        
        # Mở rộng kích thước cửa sổ cho giao diện làm việc
        self.root.geometry("1400x850") 

        if self.current_role == "admin":
            hien_thi_admin(self.root)
            
        elif self.current_role == "guide":
            user_data = {"name": username, "id": "HDV_GEN"} # Có thể lấy từ DB thật
            hien_thi_guide(self.root, user_data)
            
        elif self.current_role == "user":
            user_data = {"name": username, "id": "KH_GEN"}
            hien_thi_khach(self.root, user_data)

    def show_register_screen(self):
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = TravelSystem(root)
    root.mainloop()