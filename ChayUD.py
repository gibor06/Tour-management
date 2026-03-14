import tkinter as tk
from tkinter import messagebox

# Import các hàm giao diện từ các file khác
from GUI.Admin.Admin import main as hien_thi_admin, DataStore, THEME
from GUI.HuongDV.Guide import khoi_tao_hdv as hien_thi_guide
from GUI.Khach.user import khoi_tao_khach as hien_thi_khach

class TravelSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống Quản lý Du lịch 2026")
        self.root.geometry("500x700")
        self.root.configure(bg=THEME["bg"])

        # Khởi tạo DataStore để đồng bộ dữ liệu toàn hệ thống
        self.ds = DataStore()

        self.main_frame = tk.Frame(self.root, bg=THEME["bg"])
        self.main_frame.pack(expand=True, fill="both")

        self.show_role_selection()

    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_role_selection(self):
        self.clear_screen()
        # Đặt lại kích thước nhỏ cho màn hình Login
        self.root.geometry("500x700")
        
        # Container chính (Card style)
        card = tk.Frame(self.main_frame, bg=THEME["surface"], padx=40, pady=40,
                       highlightbackground=THEME["border"], highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="BẠN LÀ AI?", font=("Times New Roman", 22, "bold"), 
                 bg=THEME["surface"], fg=THEME["primary"]).pack(pady=(0, 30))

        roles = [
            ("ADMIN (Quản trị)", THEME["danger"], "admin"),
            ("GUIDE (Hướng dẫn viên)", THEME["warning"], "guide"),
            ("USER (Khách du lịch)", THEME["success"], "user")
        ]

        for text, color, role_type in roles:
            btn = tk.Button(card, text=text, bg=color, fg="white",
                            font=("Times New Roman", 12, "bold"), width=25, height=2,
                            cursor="hand2", bd=0, activebackground=color, activeforeground="white",
                            command=lambda r=role_type: self.show_login_screen(r))
            btn.pack(pady=10)
            
        tk.Label(card, text="Hệ thống Quản lý Du lịch 2026", font=("Times New Roman", 10),
                 bg=THEME["surface"], fg=THEME["muted"]).pack(pady=(20, 0))

    def show_login_screen(self, role):
        self.clear_screen()
        self.current_role = role
        role_name = {"admin": "QUẢN TRỊ VIÊN", "guide": "HƯỚNG DẪN VIÊN", "user": "KHÁCH DU LỊCH"}
        
        # Container chính (Card style)
        card = tk.Frame(self.main_frame, bg=THEME["surface"], padx=40, pady=40,
                       highlightbackground=THEME["border"], highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="ĐĂNG NHẬP", font=("Times New Roman", 20, "bold"), 
                 bg=THEME["surface"], fg=THEME["text"]).pack(pady=(0, 5))
        
        tk.Label(card, text=role_name[role], font=("Times New Roman", 12, "bold"), 
                 bg=THEME["surface"], fg=THEME["primary"]).pack(pady=(0, 25))

        # Tài khoản
        tk.Label(card, text="Tài khoản:", font=("Times New Roman", 11), 
                 bg=THEME["surface"], fg=THEME["text"]).pack(anchor="w")
        self.ent_user = tk.Entry(card, width=30, font=("Times New Roman", 12),
                                bd=1, relief="solid")
        self.ent_user.pack(pady=(5, 15), ipady=5)

        # Mật khẩu
        tk.Label(card, text="Mật khẩu:", font=("Times New Roman", 11), 
                 bg=THEME["surface"], fg=THEME["text"]).pack(anchor="w")
        self.ent_pass = tk.Entry(card, width=30, font=("Times New Roman", 12), 
                                show="*", bd=1, relief="solid")
        self.ent_pass.pack(pady=(5, 25), ipady=5)

        # Nút Đăng nhập
        btn_login = tk.Button(card, text="ĐĂNG NHẬP", bg=THEME["primary"], fg="white",
                            font=("Times New Roman", 12, "bold"), width=25, height=2,
                            cursor="hand2", bd=0, command=self.handle_login)
        btn_login.pack(pady=10)

        if role == "user":
            tk.Button(card, text="Đăng ký khách hàng mới", font=("Times New Roman", 11),
                      fg=THEME["primary"], bd=0, bg=THEME["surface"], cursor="hand2",
                      command=self.show_register_screen).pack(pady=5)
        
        tk.Button(card, text="← Quay lại", font=("Times New Roman", 11),
                  fg=THEME["muted"], bd=0, bg=THEME["surface"], cursor="hand2",
                  command=self.show_role_selection).pack(pady=5)

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
        
        # Container chính (Card style)
        card = tk.Frame(self.main_frame, bg=THEME["surface"], padx=40, pady=30,
                       highlightbackground=THEME["border"], highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="ĐĂNG KÝ", font=("Times New Roman", 20, "bold"), 
                 bg=THEME["surface"], fg=THEME["success"]).pack(pady=(0, 20))

        fields = [
            ("Tên đăng nhập:", "user"),
            ("Mật khẩu:", "pass"),
            ("Họ và tên:", "name"),
            ("Số điện thoại:", "phone")
        ]
        
        self.reg_widgets = {}
        for label_text, key in fields:
            tk.Label(card, text=label_text, font=("Times New Roman", 11),
                     bg=THEME["surface"], fg=THEME["text"]).pack(anchor="w")
            e = tk.Entry(card, width=30, font=("Times New Roman", 12),
                        bd=1, relief="solid")
            if key == "pass": e.config(show="*")
            e.pack(pady=(5, 10), ipady=5)
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

        tk.Button(card, text="ĐĂNG KÝ NGAY", bg=THEME["success"], fg="white",
                  font=("Times New Roman", 12, "bold"), width=25, height=2,
                  cursor="hand2", bd=0, command=perform_register).pack(pady=20)
        
        tk.Button(card, text="← Quay lại", font=("Times New Roman", 11),
                  fg=THEME["muted"], bd=0, bg=THEME["surface"], cursor="hand2",
                  command=lambda: self.show_login_screen("user")).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = TravelSystem(root)
    root.mainloop()