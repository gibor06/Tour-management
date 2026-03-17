import tkinter as tk
from tkinter import messagebox, ttk

from GUI.Admin.Admin import DataStore, THEME, main as hien_thi_admin
from GUI.HuongDV.Guide import khoi_tao_hdv as hien_thi_guide
from GUI.Khach.user import khoi_tao_khach as hien_thi_khach
from core.auth import AuthService

LOGIN_WINDOW_SIZE = "620x760"
WORKSPACE_WINDOW_SIZE = "1400x850"


class TravelSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống Quản lý Du lịch 2026")
        self.root.geometry(LOGIN_WINDOW_SIZE)
        self.root.minsize(560, 680)
        self.root.configure(bg=THEME["bg"])

        self.ds = DataStore()
        self.auth_service = AuthService(self.ds)

        self.main_frame = tk.Frame(self.root, bg=THEME["bg"])
        self.main_frame.pack(expand=True, fill="both")

        self.show_role_selection()

    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def _build_auth_shell(self, title, subtitle, accent):
        self.clear_screen()
        self.root.geometry(LOGIN_WINDOW_SIZE)

        shell = tk.Frame(self.main_frame, bg=THEME["bg"])
        shell.pack(fill="both", expand=True)

        banner = tk.Frame(shell, bg=accent, height=170)
        banner.pack(fill="x")
        banner.pack_propagate(False)

        tk.Label(
            banner,
            text="VIETNAM TRAVEL 2026",
            font=("Times New Roman", 12, "bold"),
            bg=accent,
            fg="white",
        ).pack(anchor="w", padx=26, pady=(22, 2))

        tk.Label(
            banner,
            text=title,
            font=("Times New Roman", 25, "bold"),
            bg=accent,
            fg="white",
        ).pack(anchor="w", padx=26)

        tk.Label(
            banner,
            text=subtitle,
            font=("Times New Roman", 12),
            bg=accent,
            fg="#e2e8f0",
        ).pack(anchor="w", padx=26, pady=(8, 0))

        body = tk.Frame(shell, bg=THEME["bg"])
        body.pack(fill="both", expand=True, padx=20, pady=20)

        card = tk.Frame(
            body,
            bg=THEME["surface"],
            padx=28,
            pady=24,
            highlightbackground=THEME["border"],
            highlightthickness=1,
        )
        card.place(relx=0.5, rely=0.06, anchor="n")

        def sync_card(event=None):
            available_w = max(340, body.winfo_width())
            available_h = max(420, body.winfo_height())
            card_width = min(620, max(360, available_w - 10))
            card.place_configure(width=card_width, rely=0.04 if available_h < 560 else 0.08)
            if available_h < 560:
                card.configure(padx=20, pady=18)
            else:
                card.configure(padx=28, pady=24)

        body.bind("<Configure>", sync_card)
        sync_card()
        return card

    def _auth_entry(self, parent, label_text, show=""):
        tk.Label(
            parent,
            text=label_text,
            font=("Times New Roman", 11, "bold"),
            bg=THEME["surface"],
            fg=THEME["text"],
            anchor="w",
        ).pack(anchor="w")
        entry = tk.Entry(
            parent,
            font=("Times New Roman", 12),
            bd=1,
            relief="solid",
            show=show,
        )
        entry.pack(fill="x", pady=(5, 12), ipady=6)
        return entry

    def show_role_selection(self):
        card = self._build_auth_shell(
            "Đăng nhập hệ thống",
            "Chào mừng bạn đến với Vietnam Travel 2026",
            THEME["primary"],
        )

        tk.Label(
            card,
            text="CHỌN VAI TRÒ ĐỂ TIẾP TỤC",
            font=("Times New Roman", 18, "bold"),
            bg=THEME["surface"],
            fg=THEME["text"],
        ).pack(anchor="w", pady=(0, 8))

        roles = [
            ("ADMIN", "Quản trị hệ thống & dữ liệu", THEME["danger"], "admin"),
            ("GUIDE", "Điều phối đoàn và cập nhật tour", THEME["warning"], "guide"),
            ("USER", "Đặt tour, thanh toán và theo dõi", THEME["success"], "user"),
        ]

        for role_title, role_desc, color, role_type in roles:
            btn = tk.Button(
                card,
                text=f"{role_title}\n{role_desc}",
                bg=color,
                fg="white",
                font=("Times New Roman", 12, "bold"),
                justify="left",
                anchor="w",
                padx=14,
                pady=10,
                cursor="hand2",
                bd=0,
                activebackground=color,
                activeforeground="white",
                command=lambda r=role_type: self.show_login_screen(r),
            )
            btn.pack(fill="x", pady=6)

        tk.Label(
            card,
            text="Vietnam Travel • Bản quyền 2026",
            font=("Times New Roman", 10),
            bg=THEME["surface"],
            fg=THEME["muted"],
        ).pack(anchor="w", pady=(16, 0))

    def show_login_screen(self, role):
        self.current_role = role
        role_name = {
            "admin": "QUẢN TRỊ VIÊN",
            "guide": "HƯỚNG DẪN VIÊN",
            "user": "KHÁCH DU LỊCH",
        }
        accent = {
            "admin": THEME["danger"],
            "guide": THEME["warning"],
            "user": THEME["success"],
        }.get(role, THEME["primary"])

        card = self._build_auth_shell(
            "Đăng nhập",
            f"Cổng {role_name[role]}",
            accent,
        )

        tk.Label(
            card,
            text=role_name[role],
            font=("Times New Roman", 15, "bold"),
            bg=THEME["surface"],
            fg=accent,
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            card,
            text="Nhập tài khoản để truy cập nhanh và an toàn.",
            font=("Times New Roman", 11, "italic"),
            bg=THEME["surface"],
            fg=THEME["muted"],
        ).pack(anchor="w", pady=(0, 14))

        self.ent_user = self._auth_entry(card, "Tài khoản")
        self.ent_pass = self._auth_entry(card, "Mật khẩu", show="*")
        self.ent_user.focus_set()
        self.ent_user.bind("<Return>", lambda _e: self.handle_login())
        self.ent_pass.bind("<Return>", lambda _e: self.handle_login())

        tk.Button(
            card,
            text="ĐĂNG NHẬP",
            bg=accent,
            fg="white",
            font=("Times New Roman", 12, "bold"),
            height=2,
            cursor="hand2",
            bd=0,
            command=self.handle_login,
        ).pack(fill="x", pady=(6, 10))

        if role == "user":
            tk.Button(
                card,
                text="Đăng ký khách hàng mới",
                font=("Times New Roman", 11),
                fg=accent,
                bd=0,
                bg=THEME["surface"],
                cursor="hand2",
                command=self.show_register_screen,
            ).pack(anchor="w", pady=(0, 4))

        tk.Button(
            card,
            text="← Quay lại",
            font=("Times New Roman", 11),
            fg=THEME["text"],
            bg=THEME["surface"],
            activebackground="#f1f5f9",
            activeforeground=THEME["text"],
            highlightbackground=THEME["border"],
            highlightthickness=1,
            cursor="hand2",
            command=self.show_role_selection,
        ).pack(fill="x")

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

        shell = tk.Frame(self.main_frame, bg=THEME["bg"])
        shell.pack(fill="both", expand=True)

        banner = tk.Frame(shell, bg=THEME["success"], height=156)
        banner.pack(fill="x")
        banner.pack_propagate(False)

        tk.Label(
            banner,
            text="VIETNAM TRAVEL 2026",
            font=("Times New Roman", 12, "bold"),
            bg=THEME["success"],
            fg="white",
        ).pack(anchor="w", padx=26, pady=(20, 2))

        tk.Label(
            banner,
            text="Tạo tài khoản",
            font=("Times New Roman", 24, "bold"),
            bg=THEME["success"],
            fg="white",
        ).pack(anchor="w", padx=26)

        tk.Label(
            banner,
            text="Điền thông tin để bắt đầu đăng ký tour nhanh chóng",
            font=("Times New Roman", 12),
            bg=THEME["success"],
            fg="#ecfdf5",
        ).pack(anchor="w", padx=26, pady=(8, 0))

        container = tk.Frame(shell, bg=THEME["bg"])
        container.pack(fill="both", expand=True, padx=20, pady=18)

        card = tk.Frame(
            container,
            bg=THEME["surface"],
            highlightbackground=THEME["border"],
            highlightthickness=1,
        )
        card.pack(fill="both", expand=True)

        canvas = tk.Canvas(card, bg=THEME["surface"], highlightthickness=0, bd=0)
        scroll_y = ttk.Scrollbar(card, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll_y.set)

        scroll_y.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        form_inner = tk.Frame(canvas, bg=THEME["surface"], padx=24, pady=20)
        win = canvas.create_window((0, 0), window=form_inner, anchor="nw")

        def on_inner_configure(_event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfigure(win, width=event.width)

        form_inner.bind("<Configure>", on_inner_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        def on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass

        canvas.bind("<Enter>", lambda _e: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda _e: canvas.unbind_all("<MouseWheel>"))

        tk.Label(
            form_inner,
            text="ĐĂNG KÝ KHÁCH HÀNG MỚI",
            font=("Times New Roman", 16, "bold"),
            bg=THEME["surface"],
            fg=THEME["success"],
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            form_inner,
            text="Thông tin chính xác giúp hệ thống xác thực nhanh hơn.",
            font=("Times New Roman", 11, "italic"),
            bg=THEME["surface"],
            fg=THEME["muted"],
        ).pack(anchor="w", pady=(0, 14))

        fields = [
            ("Tên đăng nhập", "user"),
            ("Mật khẩu", "pass"),
            ("Họ và tên", "name"),
            ("Số điện thoại", "phone"),
        ]

        self.reg_widgets = {}
        for label_text, key in fields:
            entry = self._auth_entry(form_inner, label_text, show="*" if key == "pass" else "")
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

        self.reg_widgets["user"].focus_set()
        for key in ["user", "pass", "name", "phone"]:
            self.reg_widgets[key].bind("<Return>", lambda _e: perform_register())

        action_fr = tk.Frame(form_inner, bg=THEME["surface"])
        action_fr.pack(fill="x", pady=(10, 0))

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
        ).pack(fill="x", pady=(0, 10))

        tk.Button(
            action_fr,
            text="← Quay lại",
            font=("Times New Roman", 11),
            fg=THEME["text"],
            bg=THEME["surface"],
            activebackground="#f1f5f9",
            activeforeground=THEME["text"],
            highlightbackground=THEME["border"],
            highlightthickness=1,
            cursor="hand2",
            command=lambda: self.show_login_screen("user"),
        ).pack(fill="x")


if __name__ == "__main__":
    root = tk.Tk()
    app = TravelSystem(root)
    root.mainloop()
