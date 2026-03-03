import tkinter as tk


class LandingPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f9")

        self.controller = controller

        title = tk.Label(
            self,
            text="Livestock Biometric Registry System",
            font=("Arial", 22, "bold"),
            bg="#f4f6f9"
        )
        title.pack(pady=40)

        tk.Button(
            self,
            text="Login as Authority",
            width=25,
            height=2,
            command=lambda: controller.show_frame_by_name("AuthorityLogin")
        ).pack(pady=10)

        tk.Button(
            self,
            text="Login as Farmer",
            width=25,
            height=2,
            command=lambda: controller.show_frame_by_name("FarmerLogin")
        ).pack(pady=10)