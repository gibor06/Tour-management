import tkinter as tk

root = None


def set_root(external_root):
    global root
    root = external_root


def show_role_selection():
    if root is None:
        raise RuntimeError("Login root chưa được khởi tạo")

    from main import TravelSystem

    for widget in root.winfo_children():
        widget.destroy()

    TravelSystem(root)


if __name__ == "__main__":
    root = tk.Tk()
    show_role_selection()
    root.mainloop()
