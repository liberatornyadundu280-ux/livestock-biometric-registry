import tkinter as tk
from tkinter import filedialog
from core.verifier import verify_livestock
from database.db_handler import get_livestock_by_owner


class FarmerDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f9")

        self.controller = controller
        self.selected_image_path = None

        tk.Label(
            self,
            text="Farmer Dashboard",
            font=("Arial", 20, "bold"),
            bg="#f4f6f9"
        ).pack(pady=10)

        # --- My Livestock Section ---
        tk.Label(
            self,
            text="My Livestock",
            font=("Arial", 14, "bold"),
            bg="#f4f6f9"
        ).pack(pady=5)

        self.livestock_listbox = tk.Listbox(self, width=50)
        self.livestock_listbox.pack(pady=5)

        # --- Verification Section ---
        tk.Label(
            self,
            text="Verify Livestock",
            font=("Arial", 14, "bold"),
            bg="#f4f6f9"
        ).pack(pady=10)

        tk.Button(
            self,
            text="Select Image",
            command=self.select_image
        ).pack(pady=5)

        # Threshold slider
        tk.Label(self, text="Verification Threshold:", bg="#f4f6f9").pack()
        self.threshold_slider = tk.Scale(
            self,
            from_=0.3,
            to=0.95,
            resolution=0.01,
            orient="horizontal",
            length=300
        )
        self.threshold_slider.set(0.7)
        self.threshold_slider.pack(pady=5)

        tk.Button(
            self,
            text="Verify",
            bg="#2e86de",
            fg="white",
            command=self.verify
        ).pack(pady=10)

        self.result_label = tk.Label(self, text="", bg="#f4f6f9")
        self.result_label.pack(pady=10)

        tk.Button(
            self,
            text="Logout",
            command=self.logout
        ).pack(pady=10)

    # ------------------------------
    # Load farmer livestock
    # ------------------------------
    def load_livestock(self):
        self.livestock_listbox.delete(0, tk.END)

        farmer = self.controller.current_user
        if not farmer:
            return

        livestock = get_livestock_by_owner(farmer["farmer_id"])

        for record in livestock:
            self.livestock_listbox.insert(
                tk.END,
                f"{record['livestock_id']} ({record['livestock_type']})"
            )

    # ------------------------------
    # Image selection
    # ------------------------------
    def select_image(self):
        self.selected_image_path = filedialog.askopenfilename()

    # ------------------------------
    # Verification
    # ------------------------------
    def verify(self):
        if not self.selected_image_path:
            self.result_label.config(text="Please select an image", fg="red")
            return

        threshold = self.threshold_slider.get()

        farmer = self.controller.current_user

        result = verify_livestock(
            self.selected_image_path,
            threshold,
            farmer["farmer_id"]
        )
        if result["status"] == "VERIFIED":
            self.result_label.config(
                text=f"VERIFIED\n"
                     f"ID: {result['livestock_id']}\n"
                     f"Owner: {result['owner_name']}\n"
                     f"Similarity: {result['similarity']:.4f}",
                fg="green"
            )
        else:
            self.result_label.config(
                text=f"NOT VERIFIED\nSimilarity: {result['similarity']:.4f}",
                fg="red"
            )

    # ------------------------------
    def logout(self):
        self.controller.current_user = None
        self.controller.show_frame_by_name("LandingPage")

    # ------------------------------
    def reset(self):
        self.load_livestock()
        self.result_label.config(text="")
        self.selected_image_path = None