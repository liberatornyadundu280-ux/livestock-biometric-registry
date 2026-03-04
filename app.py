import tkinter as tk
from tkinter import messagebox

from gui.landing import LandingPage
from gui.login_authority import AuthorityLogin
from gui.login_farmer import FarmerLogin
from gui.authority_dashboard import AuthorityDashboard
from gui.farmer_dashboard import FarmerDashboard

# FAISS vector index builder
from core.vector_index import build_index, get_index_size
from core.database import count_livestock, ensure_indexes, ping_database


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Livestock Biometric Registry System")
        self.geometry("900x600")
        self.configure(bg="#f4f6f9")

        # -----------------------------
        # Startup health checks + FAISS build
        # -----------------------------
        ok, reason = ping_database()
        if not ok:
            messagebox.showerror(
                "Database Error",
                f"MongoDB is not reachable.\n\nDetails: {reason}"
            )
            self.destroy()
            return

        idx_ok, idx_reason = ensure_indexes()
        if not idx_ok:
            messagebox.showerror(
                "Database Index Error",
                f"Could not initialize required indexes.\n\nDetails: {idx_reason}"
            )
            self.destroy()
            return

        print("Loading livestock embeddings into FAISS index...")
        build_index()
        db_count = count_livestock()
        index_count = get_index_size()
        print(f"FAISS index ready. DB records: {db_count}, index vectors: {index_count}")
        if db_count != index_count:
            messagebox.showwarning(
                "Index Warning",
                f"FAISS/DB count mismatch.\nDB: {db_count}\nFAISS: {index_count}\n"
                f"Consider rebuilding index."
            )

        self.current_user = None

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}

        for F in (
            LandingPage,
            AuthorityLogin,
            FarmerLogin,
            AuthorityDashboard,
            FarmerDashboard
        ):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame_by_name("LandingPage")

    def show_frame_by_name(self, name):
        frame = self.frames[name]

        # Reset screen state if reset method exists
        if hasattr(frame, "reset"):
            frame.reset()

        frame.tkraise()


if __name__ == "__main__":
    app = App()
    app.mainloop()
