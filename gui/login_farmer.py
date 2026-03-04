import tkinter as tk
from core.database import get_farmer, register_farmer
from core.id_generator import generate_farmer_id


class FarmerLogin(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f9")

        self.controller = controller

        tk.Label(
            self,
            text="Farmer Login",
            font=("Arial", 20, "bold"),
            bg="#f4f6f9"
        ).pack(pady=30)

        tk.Label(self, text="Username:", bg="#f4f6f9").pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Password:", bg="#f4f6f9").pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(
            self,
            text="Login",
            command=self.login
        ).pack(pady=10)

        tk.Button(
            self,
            text="Create Farmer Account",
            command=self.register
        ).pack(pady=5)

        tk.Button(
            self,
            text="Back",
            command=lambda: controller.show_frame_by_name("LandingPage")
        ).pack(pady=5)

        self.message = tk.Label(self, text="", bg="#f4f6f9", fg="red")
        self.message.pack(pady=10)

    def login(self):
    # Clear previous message first
        self.message.config(text="", fg="red")

        username = self.username_entry.get()
        password = self.password_entry.get()

        farmer = get_farmer(username)

        if farmer and farmer["password"] == password:
            self.controller.current_user = farmer
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.controller.show_frame_by_name("FarmerDashboard")
        else:
            self.message.config(text="Invalid credentials")
            self.password_entry.delete(0, tk.END)

    def register(self):
        self.message.config(text="", fg="red")

        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.message.config(text="Username and password are required")
            return

        existing = get_farmer(username)
        if existing:
            self.message.config(text="Username already exists")
            return

        farmer = {
            "farmer_id": generate_farmer_id(),
            "username": username,
            "password": password
        }
        register_farmer(farmer)

        self.message.config(text=f"Account created: {farmer['farmer_id']}", fg="green")
        self.password_entry.delete(0, tk.END)
    def reset(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.message.config(text="", fg="red")
