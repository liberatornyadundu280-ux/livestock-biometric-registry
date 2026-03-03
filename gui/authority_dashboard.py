import tkinter as tk
from tkinter import filedialog, messagebox

from core.embedding import get_embedding_list
from core.id_generator import generate_livestock_id
from core.verifier import check_duplicate, verify_global_livestock
from database.db_handler import add_livestock_record, load_database


class AuthorityDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f9")

        self.controller = controller
        self.selected_image_path = None
        self.search_image_path = None

        tk.Label(
            self,
            text="Authority Dashboard",
            font=("Arial", 20, "bold"),
            bg="#f4f6f9"
        ).pack(pady=10)

        # ==========================
        # REGISTRATION SECTION
        # ==========================
        tk.Label(
            self,
            text="Register Livestock",
            font=("Arial", 14, "bold"),
            bg="#f4f6f9"
        ).pack(pady=10)

        tk.Button(
            self,
            text="Select Image",
            command=self.select_image
        ).pack(pady=5)

        self.image_label = tk.Label(self, text="No image selected", bg="#f4f6f9")
        self.image_label.pack(pady=5)

        tk.Label(self, text="Assign to Farmer:", bg="#f4f6f9").pack()

        self.farmer_var = tk.StringVar()
        self.farmer_dropdown = tk.OptionMenu(self, self.farmer_var, "")
        self.farmer_dropdown.pack(pady=5)

        self.load_farmers()

        tk.Button(
            self,
            text="Register",
            bg="#27ae60",
            fg="white",
            command=self.register_livestock
        ).pack(pady=10)

        self.status_label = tk.Label(self, text="", bg="#f4f6f9")
        self.status_label.pack(pady=5)

        # ==========================
        # GLOBAL SEARCH SECTION
        # ==========================
        tk.Label(
            self,
            text="Search Existing Livestock",
            font=("Arial", 14, "bold"),
            bg="#f4f6f9"
        ).pack(pady=20)

        tk.Button(
            self,
            text="Select Image for Search",
            command=self.select_search_image
        ).pack(pady=5)

        tk.Button(
            self,
            text="Search Registry",
            bg="#8e44ad",
            fg="white",
            command=self.search_livestock
        ).pack(pady=5)

        self.search_result_label = tk.Label(self, text="", bg="#f4f6f9")
        self.search_result_label.pack(pady=5)

        # ==========================
        # LOGOUT
        # ==========================
        tk.Button(
            self,
            text="Logout",
            command=self.logout
        ).pack(pady=20)

    # --------------------------
    # Load Farmers
    # --------------------------
    def load_farmers(self):
        db = load_database()
        farmers = db["farmers"]

        menu = self.farmer_dropdown["menu"]
        menu.delete(0, "end")

        for farmer in farmers:
            menu.add_command(
                label=farmer["username"],
                command=lambda value=farmer["username"]: self.farmer_var.set(value)
            )

        if farmers:
            self.farmer_var.set(farmers[0]["username"])

    # --------------------------
    # Registration Logic
    # --------------------------
    def select_image(self):
        self.selected_image_path = filedialog.askopenfilename()
        if self.selected_image_path:
            self.image_label.config(text="Image Selected")

    def register_livestock(self):
        if not self.selected_image_path:
            self.status_label.config(text="Select an image", fg="red")
            return

        db = load_database()
        farmer = next(
            (f for f in db["farmers"] if f["username"] == self.farmer_var.get()),
            None
        )

        embedding = get_embedding_list(self.selected_image_path)

        # Duplicate check
        duplicate_check = check_duplicate(embedding)

        if duplicate_check["duplicate"]:
            result = messagebox.askyesno(
                "Duplicate Detected",
                f"Existing ID: {duplicate_check['existing_id']}\n"
                f"Owner: {duplicate_check['owner_name']}\n"
                f"Similarity: {duplicate_check['similarity']:.4f}\n\n"
                f"Override?"
            )
            if not result:
                self.status_label.config(text="Registration cancelled", fg="orange")
                return

        livestock_id = generate_livestock_id()

        record = {
            "livestock_id": livestock_id,
            "livestock_type": "cattle",
            "biometric_type": "muzzle",
            "owner_id": farmer["farmer_id"],
            "owner_name": farmer["username"],
            "embedding": embedding
        }

        add_livestock_record(record)

        self.status_label.config(
            text=f"{livestock_id} registered successfully",
            fg="green"
        )

    # --------------------------
    # Global Search Logic
    # --------------------------
    def select_search_image(self):
        self.search_image_path = filedialog.askopenfilename()

    def search_livestock(self):
        if not self.search_image_path:
            self.search_result_label.config(text="Select image first", fg="red")
            return

        result = verify_global_livestock(self.search_image_path, threshold=0.7)

        if result["status"] == "FOUND":
            self.search_result_label.config(
                text=f"FOUND\n"
                     f"ID: {result['livestock_id']}\n"
                     f"Owner: {result['owner_name']}\n"
                     f"Similarity: {result['similarity']:.4f}",
                fg="green"
            )
        else:
            self.search_result_label.config(
                text=f"NOT FOUND\nSimilarity: {result['similarity']:.4f}",
                fg="red"
            )

    # --------------------------
    def logout(self):
        self.controller.current_user = None
        self.controller.show_frame_by_name("LandingPage")

    def reset(self):
        self.status_label.config(text="")
        self.search_result_label.config(text="")
        self.selected_image_path = None
        self.search_image_path = None
        self.image_label.config(text="No image selected")