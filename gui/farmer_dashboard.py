import tkinter as tk
from tkinter import filedialog, messagebox

from core.config import get_match_threshold
from core.database import get_farmer_livestock
from core.verifier import verify_farmer_livestock, verify_global_livestock


class FarmerDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f9")

        self.controller = controller
        self.selected_image_path = None
        self.global_search_image_path = None

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

        tk.Label(self, text="Verification Threshold:", bg="#f4f6f9").pack()
        self.threshold_slider = tk.Scale(
            self,
            from_=0.3,
            to=0.95,
            resolution=0.01,
            orient="horizontal",
            length=300
        )
        self.threshold_slider.set(get_match_threshold())
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

        # --- Global Availability Search ---
        tk.Label(
            self,
            text="Check Availability in Full Registry",
            font=("Arial", 14, "bold"),
            bg="#f4f6f9"
        ).pack(pady=10)

        tk.Button(
            self,
            text="Select Image for Global Search",
            command=self.select_global_search_image
        ).pack(pady=5)

        tk.Button(
            self,
            text="Search Full Registry",
            bg="#8e44ad",
            fg="white",
            command=self.search_global_registry
        ).pack(pady=5)

        self.global_result_label = tk.Label(self, text="", bg="#f4f6f9")
        self.global_result_label.pack(pady=10)

        tk.Button(
            self,
            text="Back to Landing",
            command=self.back_to_landing
        ).pack(pady=5)

        tk.Button(
            self,
            text="Logout",
            command=self.logout
        ).pack(pady=5)

    def load_livestock(self):
        self.livestock_listbox.delete(0, tk.END)

        farmer = self.controller.current_user
        if not farmer:
            return

        livestock = get_farmer_livestock(farmer["farmer_id"])

        for record in livestock:
            self.livestock_listbox.insert(
                tk.END,
                f"{record['livestock_id']} ({record['livestock_type']})"
            )

    def select_image(self):
        self.selected_image_path = filedialog.askopenfilename()

    def select_global_search_image(self):
        self.global_search_image_path = filedialog.askopenfilename()

    def verify(self):
        if not self.selected_image_path:
            self.result_label.config(text="Please select an image", fg="red")
            return

        threshold = self.threshold_slider.get()
        farmer = self.controller.current_user

        result = verify_farmer_livestock(self.selected_image_path, farmer["farmer_id"], threshold)
        if result["status"] == "INVALID_INPUT":
            self.result_label.config(
                text=f"INVALID IMAGE\nReason: {result['reason']}",
                fg="red"
            )
            return

        if result["status"] == "FOUND":
            self.result_label.config(
                text=f"FOUND\n"
                     f"ID: {result['livestock_id']}\n"
                     f"Similarity: {result['similarity']:.4f}\n"
                     f"Confidence: {result.get('confidence', 'N/A')}",
                fg="green"
            )
        else:
            self.result_label.config(
                text=f"NOT FOUND\n"
                     f"Similarity: {result['similarity']:.4f}\n"
                     f"Confidence: {result.get('confidence', 'N/A')}",
                fg="red"
            )
            messagebox.showinfo("Not Found", "No matching livestock found in your registered records.")

    def search_global_registry(self):
        if not self.global_search_image_path:
            self.global_result_label.config(text="Select image first", fg="red")
            return

        result = verify_global_livestock(
            self.global_search_image_path,
            threshold=get_match_threshold()
        )
        if result["status"] == "INVALID_INPUT":
            self.global_result_label.config(
                text=f"INVALID IMAGE\nReason: {result['reason']}",
                fg="red"
            )
            return

        if result["status"] == "FOUND":
            self.global_result_label.config(
                text=f"FOUND IN REGISTRY\n"
                     f"ID: {result['livestock_id']}\n"
                     f"Owner: {result['owner_name']}\n"
                     f"Similarity: {result['similarity']:.4f}\n"
                     f"Confidence: {result.get('confidence', 'N/A')}",
                fg="green"
            )
        else:
            self.global_result_label.config(
                text=f"NOT FOUND IN REGISTRY\n"
                     f"Similarity: {result['similarity']:.4f}\n"
                     f"Confidence: {result.get('confidence', 'N/A')}",
                fg="red"
            )
            messagebox.showinfo("Not Found", "This livestock image is not found in the system registry.")

    def logout(self):
        self.controller.current_user = None
        self.controller.show_frame_by_name("LandingPage")

    def back_to_landing(self):
        self.logout()

    def reset(self):
        self.load_livestock()
        self.result_label.config(text="")
        self.global_result_label.config(text="")
        self.selected_image_path = None
        self.global_search_image_path = None
