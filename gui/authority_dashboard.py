import tkinter as tk
from tkinter import filedialog, messagebox

from core.embedding import get_embedding_list
from core.config import get_match_threshold
from core.id_generator import generate_livestock_id
from core.input_validator import validate_biometric_input
from core.verifier import check_duplicate, verify_global_livestock
from core.registry_service import register_livestock_transaction
from core.database import (
    append_livestock_embedding,
    count_livestock,
    get_all_farmers,
    register_farmer,
    reset_livestock_registry,
)
from core.vector_index import add_vector, build_index, get_index_size


class AuthorityDashboard(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f9")

        self.controller = controller
        self.selected_image_path = None
        self.search_image_path = None
        self.farmers_by_username = {}

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
        # DEMO UTILITIES
        # ==========================
        tk.Label(
            self,
            text="Demo Utilities",
            font=("Arial", 12, "bold"),
            bg="#f4f6f9"
        ).pack(pady=10)

        tk.Button(
            self,
            text="Reset Demo Livestock",
            bg="#e67e22",
            fg="white",
            command=self.reset_demo_livestock
        ).pack(pady=5)

        # ==========================
        # LOGOUT
        # ==========================

        tk.Button(
            self,
            text="Logout",
            command=self.logout
        ).pack(pady=10)

        tk.Button(
            self,
            text="Back to Landing",
            command=self.back_to_landing
        ).pack(pady=20)

    # --------------------------
    # Load Farmers (MongoDB)
    # --------------------------

    def load_farmers(self):

        farmers = get_all_farmers()
        if not farmers:
            demo_farmer = {
                "farmer_id": "F0001",
                "username": "demo_farmer",
                "password": "demo123"
            }
            register_farmer(demo_farmer)
            farmers = get_all_farmers()

        menu = self.farmer_dropdown["menu"]
        menu.delete(0, "end")
        self.farmers_by_username = {}

        for farmer in farmers:
            username = farmer["username"]
            self.farmers_by_username[username] = farmer
            menu.add_command(
                label=username,
                command=lambda value=username: self.farmer_var.set(value)
            )

        if farmers:
            self.farmer_var.set(farmers[0]["username"])
        else:
            self.farmer_var.set("")

    # --------------------------
    # Select Image
    # --------------------------

    def select_image(self):

        self.selected_image_path = filedialog.askopenfilename()

        if self.selected_image_path:
            self.image_label.config(text="Image Selected")

    # --------------------------
    # Registration Logic
    # --------------------------

    def register_livestock(self):

        if not self.selected_image_path:
            self.status_label.config(text="Select an image", fg="red")
            return

        validation = validate_biometric_input(self.selected_image_path)
        if not validation["valid"]:
            self.status_label.config(
                text=f"Invalid image: {validation['reason']}",
                fg="red"
            )
            return

        selected_username = self.farmer_var.get()
        farmer = self.farmers_by_username.get(selected_username)
        if not farmer:
            self.status_label.config(text="No valid farmer selected", fg="red")
            return

        embedding = get_embedding_list(self.selected_image_path)

        threshold = get_match_threshold()
        duplicate_check = check_duplicate(embedding, threshold=threshold)

        if duplicate_check["duplicate"]:
            existing_id = duplicate_check["existing_id"]
            dtype = duplicate_check.get("duplicate_type", "HARD")

            action = messagebox.askyesnocancel(
                "Duplicate Detected",
                f"Type: {dtype}\n"
                f"Existing ID: {existing_id}\n"
                f"Owner: {duplicate_check['owner_name']}\n"
                f"Similarity: {duplicate_check['similarity']:.4f}\n\n"
                f"Yes: Attach this as a new angle to existing ID\n"
                f"No: Force new livestock ID\n"
                f"Cancel: Stop registration"
            )

            if action is None:
                self.status_label.config(text="Registration cancelled", fg="orange")
                return

            if action is True:
                appended = append_livestock_embedding(existing_id, embedding)
                if appended:
                    add_vector(embedding, existing_id)
                    self.status_label.config(
                        text=f"Added new angle to {existing_id} (no new entity created).",
                        fg="green"
                    )
                else:
                    self.status_label.config(
                        text="Could not append angle to existing livestock.",
                        fg="red"
                    )
                return

            if dtype == "HARD":
                proceed = messagebox.askyesno(
                    "Hard Duplicate Warning",
                    "This appears to be a strong duplicate.\n"
                    "Force-registering a new ID may create false data.\n\n"
                    "Do you still want to continue?"
                )
                if not proceed:
                    self.status_label.config(text="Registration cancelled", fg="orange")
                    return

        livestock_id = generate_livestock_id()

        record = {
            "livestock_id": livestock_id,
            "livestock_type": "cattle",
            "biometric_type": "muzzle",
            "owner_id": farmer["farmer_id"],
            "owner_name": farmer["username"],
            "embedding": embedding,
            "embedding_gallery": [embedding]
        }

        tx = register_livestock_transaction(record)
        if not tx["ok"]:
            self.status_label.config(
                text=f"Registration failed ({tx['stage']}): {tx['error']}",
                fg="red"
            )
            return

        self.status_label.config(
            text=f"{livestock_id} registered successfully",
            fg="green"
        )

    # --------------------------
    # Global Search
    # --------------------------

    def select_search_image(self):
        self.search_image_path = filedialog.askopenfilename()

    def search_livestock(self):

        if not self.search_image_path:
            self.search_result_label.config(text="Select image first", fg="red")
            return

        result = verify_global_livestock(self.search_image_path, threshold=get_match_threshold())

        if result["status"] == "INVALID_INPUT":
            self.search_result_label.config(
                text=f"INVALID IMAGE\nReason: {result['reason']}",
                fg="red"
            )
            return

        if result["status"] == "FOUND":

            self.search_result_label.config(
                text=f"FOUND\n"
                     f"ID: {result['livestock_id']}\n"
                     f"Owner: {result['owner_name']}\n"
                     f"Similarity: {result['similarity']:.4f}\n"
                     f"Confidence: {result.get('confidence', 'N/A')}",
                fg="green"
            )

        else:

            self.search_result_label.config(
                text=f"NOT FOUND\n"
                     f"Similarity: {result['similarity']:.4f}\n"
                     f"Confidence: {result.get('confidence', 'N/A')}",
                fg="red"
            )
            messagebox.showinfo("Not Found", "No matching livestock found in the system registry.")

    def reset_demo_livestock(self):
        confirm = messagebox.askyesno(
            "Confirm Reset",
            "This will delete all livestock records for demo reset.\nProceed?"
        )
        if not confirm:
            return

        removed = reset_livestock_registry()
        build_index()
        self.status_label.config(
            text=f"Demo reset complete. Removed {removed} records. "
                 f"DB={count_livestock()} FAISS={get_index_size()}",
            fg="green"
        )
        self.search_result_label.config(text="")
        self.selected_image_path = None
        self.search_image_path = None

    # --------------------------

    def logout(self):

        self.controller.current_user = None
        self.controller.show_frame_by_name("LandingPage")

    def back_to_landing(self):
        self.logout()

    def reset(self):

        self.status_label.config(text="")
        self.search_result_label.config(text="")

        self.selected_image_path = None
        self.search_image_path = None

        self.image_label.config(text="No image selected")
