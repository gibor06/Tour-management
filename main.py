import tkinter as tk
from tkinter import messagebox

from GUI.Admin.Admin import DataStore, THEME, main as hien_thi_admin
from GUI.HuongDV.Guide import khoi_tao_hdv as hien_thi_guide
from GUI.Khach.user import khoi_tao_khach as hien_thi_khach
from core.auth import AuthService

LOGIN_WINDOW_SIZE = "500x700"
WORKSPACE_WINDOW_SIZE = "1400x850"


class TravelSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống Quản lý Du lịch 2026")
        self.root.geometry(LOGIN_WINDOW_SIZE)
        self.root.configure(bg=THEME["bg"])

        self.ds = DataStore()
        self.auth_service = AuthService(self.ds)

        self.main_frame = tk.Frame(self.root, bg=THEME["bg"])
        self.main_frame.pack(expand=True, fill="both")

        self.show_role_selection()

    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_role_selection(self):
        self.clear_screen()
        self.root.geometry(LOGIN_WINDOW_SIZE)

        card = tk.Frame(
            self.main_frame,
            bg=THEME["surface"],
            padx=40,
            pady=40,
            highlightbackground=THEME["border"],
            highlightthickness=1,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            card,
            text="BẠN LÀ AI?",
            font=("Times New Roman", 22, "bold"),
            bg=THEME["surface"],
            fg=THEME["primary"],
        ).pack(pady=(0, 30))

        roles = [
            ("ADMIN (Quản trị)", THEME["danger"], "admin"),
            ("GUIDE (Hướng dẫn viên)", THEME["warning"], "guide"),
            ("USER (Khách du lịch)", THEME["success"], "user"),
        ]

        for text, color, role_type in roles:
            btn = tk.Button(
                card,
                text=text,
                bg=color,
                fg="white",
                font=("Times New Roman", 12, "bold"),
                width=25,
                height=2,
                cursor="hand2",
                bd=0,
                activebackground=color,
                activeforeground="white",
                command=lambda r=role_type: self.show_login_screen(r),
            )
            btn.pack(pady=10)

        tk.Label(
            card,
            text="Hệ thống Quản lý Du lịch 2026",
            font=("Times New Roman", 10),
            bg=THEME["surface"],
            fg=THEME["muted"],
        ).pack(pady=(20, 0))

    def show_login_screen(self, role):
        self.clear_screen()
        self.current_role = role
        role_name = {
            "admin": "QUẢN TRỊ VIÊN",
            "guide": "HƯỚNG DẪN VIÊN",
            "user": "KHÁCH DU LỊCH",
        }

        card = tk.Frame(
            self.main_frame,
            bg=THEME["surface"],
            padx=40,
            pady=40,
            highlightbackground=THEME["border"],
            highlightthickness=1,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            card,
            text="ĐĂNG NHẬP",
            font=("Times New Roman", 20, "bold"),
            bg=THEME["surface"],
            fg=THEME["text"],
        ).pack(pady=(0, 5))

        tk.Label(
            card,
            text=role_name[role],
            font=("Times New Roman", 12, "bold"),
            bg=THEME["surface"],
            fg=THEME["primary"],
        ).pack(pady=(0, 25))

        tk.Label(
            card,
            text="Tài khoản:",
            font=("Times New Roman", 11),
            bg=THEME["surface"],
            fg=THEME["text"],
        ).pack(anchor="w")
        self.ent_user = tk.Entry(card, width=30, font=("Times New Roman", 12), bd=1, relief="solid")
        self.ent_user.pack(pady=(5, 15), ipady=5)

        tk.Label(
            card,
            text="Mật khẩu:",
            font=("Times New Roman", 11),
            bg=THEME["surface"],
            fg=THEME["text"],
        ).pack(anchor="w")
        self.ent_pass = tk.Entry(
            card,
            width=30,
            font=("Times New Roman", 12),
            show="*",
            bd=1,
            relief="solid",
        )
        self.ent_pass.pack(pady=(5, 25), ipady=5)

        tk.Button(
            card,
            text="ĐĂNG NHẬP",
            bg=THEME["primary"],
            fg="white",
            font=("Times New Roman", 12, "bold"),
            width=25,
            height=2,
            cursor="hand2",
            bd=0,
            command=self.handle_login,
        ).pack(pady=10)

        if role == "user":
            tk.Button(
                card,
                text="Đăng ký khách hàng mới",
                font=("Times New Roman", 11),
                fg=THEME["primary"],
                bd=0,
                bg=THEME["surface"],
                cursor="hand2",
                command=self.show_register_screen,
            ).pack(pady=5)

        tk.Button(
            card,
            text="← Quay lại",
            font=("Times New Roman", 11),
            fg=THEME["muted"],
            bd=0,
            bg=THEME["surface"],
            cursor="hand2",
            command=self.show_role_selection,
        ).pack(pady=5)

    def handle_login(self):
        result = self.auth_service.authenticate(
            self.current_role,
            self.ent_user.get(),
            self.ent_pass.get(),
        )

        if result.success:
            messagebox.showinfo("Thành công", result.message)
            self.redirect_to_interface(result.username)
            return

        notifier = messagebox.showwarning if result.level == "warning" else messagebox.showerror
        notifier("Lỗi", result.message)

    def redirect_to_interface(self, username):
        self.main_frame.destroy()
        self.root.geometry(WORKSPACE_WINDOW_SIZE)

        if self.current_role == "admin":
            hien_thi_admin(self.root)

        elif self.current_role == "guide":
            hdv_info = self.ds.find_hdv(username)
            user_data = {
                "maHDV": username,
                "tenHDV": hdv_info["tenHDV"] if hdv_info else "Hướng Dẫn Viên",
            }
            hien_thi_guide(self.root, user_data)

        elif self.current_role == "user":
            user_info = self.ds.find_user(username)
            user_data = {
                "username": username,
                "name": user_info["fullname"] if user_info else username,
                "id": f"KH_{username}",
            }
            hien_thi_khach(self.root, user_data)

    def show_register_screen(self):
        self.clear_screen()
        self.root.geometry(LOGIN_WINDOW_SIZE)

        container = tk.Frame(self.main_frame, bg=THEME["bg"])
        container.pack(fill="both", expand=True, padx=20, pady=20)

        card = tk.Frame(
            container,
            bg=THEME["surface"],
            padx=28,
            pady=26,
            highlightbackground=THEME["border"],
            highlightthickness=1,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        def sync_register_card(event=None):
            available_w = max(320, container.winfo_width())
            target_w = min(620, max(360, available_w - 24))
            card.place_configure(width=target_w)

            # Khi chiều cao hẹp, đẩy card lên trên một chút để tránh cụm nút bị khuất.
            if container.winfo_height() < 560:
                card.place_configure(rely=0.45)
                card.configure(padx=20, pady=18)
            else:
                card.place_configure(rely=0.5)
                card.configure(padx=28, pady=26)

        container.bind("<Configure>", sync_register_card)
        sync_register_card()

        form_inner = tk.Frame(card, bg=THEME["surface"])
        form_inner.pack(fill="both", expand=True)

        tk.Label(
            form_inner,
            text="ĐĂNG KÝ",
            font=("Times New Roman", 20, "bold"),
            bg=THEME["surface"],
            fg=THEME["success"],
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            form_inner,
            text="Tạo tài khoản khách hàng mới",
            font=("Times New Roman", 11, "italic"),
            bg=THEME["surface"],
            fg=THEME["muted"],
        ).pack(anchor="w", pady=(0, 18))

        fields = [
            ("Tên đăng nhập:", "user"),
            ("Mật khẩu:", "pass"),
            ("Họ và tên:", "name"),
            ("Số điện thoại:", "phone"),
        ]

        self.reg_widgets = {}
        for label_text, key in fields:
            row_fr = tk.Frame(form_inner, bg=THEME["surface"])
            row_fr.pack(fill="x", pady=(0, 10))

            tk.Label(
                row_fr,
                text=label_text,
                font=("Times New Roman", 11, "bold"),
                bg=THEME["surface"],
                fg=THEME["text"],
                anchor="w",
                justify="left",
            ).pack(anchor="w")

            entry = tk.Entry(row_fr, font=("Times New Roman", 12), bd=1, relief="solid")
            if key == "pass":
                entry.config(show="*")
            entry.pack(fill="x", pady=(5, 0), ipady=5)
            self.reg_widgets[key] = entry

        def perform_register():
            result = self.auth_service.register_user(
                self.reg_widgets["user"].get(),
                self.reg_widgets["pass"].get(),
                self.reg_widgets["name"].get(),
                self.reg_widgets["phone"].get(),
            )

            if result.success:
                messagebox.showinfo("Thành công", result.message)
                self.show_login_screen("user")
                return

            notifier = messagebox.showwarning if result.level == "warning" else messagebox.showerror
            notifier("Lỗi", result.message)

        action_fr = tk.Frame(form_inner, bg=THEME["surface"])
        action_fr.pack(fill="x", pady=(12, 0))

        tk.Button(
            action_fr,
            text="ĐĂNG KÝ NGAY",
            bg=THEME["success"],
            fg="white",
            font=("Times New Roman", 12, "bold"),
            height=2,
            cursor="hand2",
            bd=0,
            command=perform_register,
        ).pack(fill="x")

        tk.Button(
            action_fr,
            text="← Quay lại",
            font=("Times New Roman", 11),
            fg=THEME["muted"],
            bd=0,
            bg=THEME["surface"],
            cursor="hand2",
            command=lambda: self.show_login_screen("user"),
        ).pack(pady=(10, 0))


if __name__ == "__main__":
    root = tk.Tk()
    app = TravelSystem(root)
    root.mainloop()
