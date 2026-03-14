import tkinter as tk
from tkinter import messagebox

# Import các hàm giao diện từ các file khác
from GUI.Admin.Admin import main as hien_thi_admin, DataStore
from GUI.HuongDV.Guide import khoi_tao_hdv as hien_thi_guide
from GUI.Khach.user import khoi_tao_khach as hien_thi_khach

class TravelSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống Quản lý Du lịch 2026")
        self.root.geometry("450x650")
        self.root.configure(bg="#f0f2f5")

        # Khởi tạo DataStore để đồng bộ dữ liệu toàn hệ thống
        self.ds = DataStore()

        self.main_frame = tk.Frame(self.root, bg="#f0f2f5")
        self.main_frame.pack(expand=True, fill="both")

        self.show_role_selection()

    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_role_selection(self):
        self.clear_screen()
        # Đặt lại kích thước nhỏ cho màn hình Login
        self.root.geometry("450x650")
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
        u, p = self.ent_user.get().strip(), self.ent_pass.get().strip()
        
        # Làm mới dữ liệu từ file JSON trước khi kiểm tra
        self.ds.load()
        
        authenticated = False
        display_name = u

        if self.current_role == "admin":
            admin_data = self.ds.data.get("admin", {})
            if u == admin_data.get("username") and p == admin_data.get("password"):
                authenticated = True
                
        elif self.current_role == "guide":
            hdv = self.ds.find_hdv(u)
            if hdv and hdv.get("password") == p:
                authenticated = True
                display_name = hdv.get("tenHDV", u)
                
        elif self.current_role == "user":
            user = self.ds.find_user(u)
            if user and user.get("password") == p:
                authenticated = True
                display_name = user.get("fullname", u)
        
        if authenticated:
            messagebox.showinfo("Thành công", f"Chào mừng {display_name}!")
            self.redirect_to_interface(u)
        else:
            messagebox.showerror("Lỗi", "Sai tài khoản hoặc mật khẩu!")

    def redirect_to_interface(self, username):
        """Hàm quan trọng: Xóa màn hình login và mở giao diện chính"""
        self.main_frame.destroy() 
        
        # Mở rộng kích thước cửa sổ cho giao diện làm việc
        self.root.geometry("1400x850") 

        if self.current_role == "admin":
            hien_thi_admin(self.root)
            
        elif self.current_role == "guide":
            hdv_info = self.ds.find_hdv(username)
            user_data = {
                "maHDV": username, 
                "tenHDV": hdv_info["tenHDV"] if hdv_info else "Hướng Dẫn Viên"
            }
            hien_thi_guide(self.root, user_data)
            
        elif self.current_role == "user":
            user_info = self.ds.find_user(username)
            user_data = {
                "username": username,
                "name": user_info["fullname"] if user_info else username, 
                "id": f"KH_{username}"
            }
            hien_thi_khach(self.root, user_data)

    def show_register_screen(self):
        self.clear_screen()
        tk.Label(self.main_frame, text="ĐĂNG KÝ THÀNH VIÊN", 
                 font=("Arial", 16, "bold"), bg="#f0f2f5").pack(pady=20)

        fields = [
            ("Tên đăng nhập:", "user"),
            ("Mật khẩu:", "pass"),
            ("Họ và tên:", "name"),
            ("Số điện thoại:", "phone")
        ]
        
        self.reg_widgets = {}
        for label, key in fields:
            tk.Label(self.main_frame, text=label, bg="#f0f2f5").pack()
            e = tk.Entry(self.main_frame, width=30, font=("Arial", 11))
            if key == "pass": e.config(show="*")
            e.pack(pady=5)
            self.reg_widgets[key] = e

        def perform_register():
            u = self.reg_widgets["user"].get().strip()
            p = self.reg_widgets["pass"].get().strip()
            n = self.reg_widgets["name"].get().strip()
            ph = self.reg_widgets["phone"].get().strip()

            if not all([u, p, n]):
                return messagebox.showwarning("Lỗi", "Vui lòng nhập đủ các trường bắt buộc!")

            self.ds.load()
            if self.ds.find_user(u):
                return messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại!")

            new_user = {
                "username": u,
                "password": p,
                "fullname": n,
                "sdt": ph
            }
            self.ds.data["users"].append(new_user)
            self.ds.save()
            messagebox.showinfo("Thành công", "Đăng ký tài khoản thành công!")
            self.show_login_screen("user")

        tk.Button(self.main_frame, text="ĐĂNG KÝ NGAY", bg="#6ab04c", fg="white",
                  width=20, command=perform_register).pack(pady=20)
        
        tk.Button(self.main_frame, text="← Quay lại", bd=0, bg="#f0f2f5", 
                  command=lambda: self.show_login_screen("user")).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = TravelSystem(root)
    root.mainloop()