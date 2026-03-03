import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from model.embedding import compare_images

class BiometricGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cattle Muzzle Biometric Identification System")
        self.root.geometry("850x600")
        self.root.configure(bg="#f4f6f9")

        self.img1_path = None
        self.img2_path = None

        # ===== Title =====
        title = tk.Label(
            root,
            text="Cattle Muzzle Biometric Verification System",
            font=("Arial", 20, "bold"),
            bg="#f4f6f9"
        )
        title.pack(pady=15)

        # ===== System Info Panel =====
        info_frame = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")
        info_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(info_frame, text="System Information",
                 font=("Arial", 14, "bold"),
                 bg="#ffffff").pack(anchor="w", padx=10, pady=5)

        system_text = (
            "Model: MobileNetV2 (Pretrained Backbone)\n"
            "Embedding Dimension: 1280\n"
            "Similarity Metric: Cosine Similarity\n"
            "Decision Method: Threshold-Based Verification\n"
            "Architecture: Siamese Neural Network (Conceptual)"
        )

        tk.Label(info_frame, text=system_text,
                 justify="left",
                 bg="#ffffff",
                 font=("Arial", 11)).pack(anchor="w", padx=10, pady=5)

        # ===== Buttons =====
        button_frame = tk.Frame(root, bg="#f4f6f9")
        button_frame.pack(pady=15)

        tk.Button(button_frame, text="Select Image 1", width=18,
                  command=self.load_image1).grid(row=0, column=0, padx=10)

        tk.Button(button_frame, text="Select Image 2", width=18,
                  command=self.load_image2).grid(row=0, column=1, padx=10)

        tk.Button(button_frame, text="Verify Identity",
                  width=18,
                  bg="#2e86de",
                  fg="white",
                  command=self.verify).grid(row=0, column=2, padx=10)

        # ===== Status Label =====
        self.status_label = tk.Label(
            root,
            text="Status: Awaiting image selection",
            font=("Arial", 13),
            bg="#f4f6f9",
            fg="black"
        )
        self.status_label.pack(pady=10)

        # ===== Image Display =====
        image_frame = tk.Frame(root, bg="#f4f6f9")
        image_frame.pack(pady=20)

        self.img_label1 = tk.Label(image_frame, bg="#dfe6e9", width=250, height=250)
        self.img_label1.pack(side="left", padx=40)

        self.img_label2 = tk.Label(image_frame, bg="#dfe6e9", width=250, height=250)
        self.img_label2.pack(side="right", padx=40)

    def load_image1(self):
        self.img1_path = filedialog.askopenfilename()
        self.display_image(self.img1_path, self.img_label1)
        self.status_label.config(text="Status: Image 1 Loaded", fg="#0984e3")

    def load_image2(self):
        self.img2_path = filedialog.askopenfilename()
        self.display_image(self.img2_path, self.img_label2)
        self.status_label.config(text="Status: Image 2 Loaded", fg="#0984e3")

    def display_image(self, path, label):
        img = Image.open(path)
        img = img.resize((250, 250))
        img = ImageTk.PhotoImage(img)
        label.config(image=img)
        label.image = img

    def verify(self):
        if self.img1_path and self.img2_path:
            similarity, result = compare_images(self.img1_path, self.img2_path)

            if similarity > 0.7:
                color = "#27ae60"  # green
                status_text = "Status: Identity Verified"
            elif similarity > 0.5:
                color = "#f39c12"  # orange (borderline)
                status_text = "Status: Borderline Similarity"
            else:
                color = "#c0392b"  # red
                status_text = "Status: Identity Not Verified"

            self.status_label.config(
                text=f"{status_text}\nSimilarity Score: {similarity:.4f}",
                fg=color
            )

        else:
            self.status_label.config(
                text="Status: Please select both images before verification",
                fg="#c0392b"
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = BiometricGUI(root)
    root.mainloop()