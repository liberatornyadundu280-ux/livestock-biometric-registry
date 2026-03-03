import tkinter as tk

from gui.landing import LandingPage
from gui.login_authority import AuthorityLogin
from gui.login_farmer import FarmerLogin
from gui.authority_dashboard import AuthorityDashboard
from gui.farmer_dashboard import FarmerDashboard


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Livestock Biometric Registry System")
        self.geometry("900x600")
        self.configure(bg="#f4f6f9")

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