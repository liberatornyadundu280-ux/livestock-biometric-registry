import tkinter as tk
command=lambda: controller.show_frame_by_name("LandingPage")
from gui.authority_dashboard import AuthorityDashboard


class AuthorityLogin(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f9")

        self.controller = controller

        title = tk.Label(
            self,
            text="Authority Login",
            font=("Arial", 20, "bold"),
            bg="#f4f6f9"
        )
        title.pack(pady=30)

        tk.Label(self, text="Username:", bg="#f4f8f9").pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Password:", bg="#f8f4f9").pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(
            self,
            text="Login",
            command=self.login
        ).pack(pady=10)

        tk.Button(
            self,
            text="Back",
            command=lambda: self.controller.show_frame_by_name("LandingPage")
        ).pack(pady=5)

        self.message = tk.Label(self, text="", bg="#f4f6f9", fg="red")
        self.message.pack(pady=10)

    def login(self):
        self.message.config(text="")

        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "admin" and password == "admin123":
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.controller.show_frame_by_name("AuthorityDashboard")
        else:
            self.message.config(text="Invalid credentials")
            self.password_entry.delete(0, tk.END)
    def reset(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.message.config(text="")