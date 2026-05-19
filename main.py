import os
import time
import threading
import customtkinter as ctk
from tkinter import filedialog
from dotenv import load_dotenv
from google import genai
from PIL import Image
from pillow_heif import register_heif_opener

# 1. Setup
register_heif_opener()
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={'api_version': 'v1beta'}
)

class GeminiRenamerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window Configuration
        self.title("Gemini Batch Renamer")
        self.geometry("500x400")
        ctk.set_appearance_mode("dark")
        
        # UI Elements
        self.title_label = ctk.CTkLabel(self, text="AI FILE RENAMER", 
                                        font=("Arial Bold", 20))
        self.title_label.pack(pady=(20, 10))

        self.btn = ctk.CTkButton(self, text="SELECT IMAGES OR PDFS", 
                                 width=300, height=60, 
                                 command=self.select_files,
                                 font=("Arial Bold", 14))
        self.btn.pack(pady=40)

        self.status_label = ctk.CTkLabel(self, text="Ready to process files", 
                                         font=("Arial", 12))
        self.status_label.pack(pady=10)

        self.progress_label = ctk.CTkLabel(self, text="", font=("Arial", 11), text_color="gray")
        self.progress_label.pack(pady=5)

    def update_status(self, text, color="white"):
        self.status_label.configure(text=text, text_color=color)

    def select_files(self):
        # This opens the native Mac file selector
        file_paths = filedialog.askopenfilenames(
            title="Select Files to Rename",
            filetypes=[("Supported Files", "*.png *.jpg *.jpeg *.heic *.pdf")]
        )
        
        if file_paths:
            self.btn.configure(state="disabled")
            threading.Thread(target=self.process_files, args=(file_paths,), daemon=True).start()

    def process_files(self, files):
        count = len(files)
        for i, file_path in enumerate(files, 1):
            file_name = os.path.basename(file_path)
            directory = os.path.dirname(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()

            self.update_status(f"Processing {i}/{count}...", "yellow")
            self.progress_label.configure(text=f"Currently analyzing: {file_name}")

            try:
                if file_ext == '.pdf':
                    with open(file_path, "rb") as f:
                        doc_data = f.read()
                    content = [
                        "Describe this document for a filename. 3 words, underscores, no extension.",
                        {"inline_data": {"mime_type": "application/pdf", "data": doc_data}}
                    ]
                else:
                    img = Image.open(file_path)
                    content = ["Describe this image for a filename. 3 words, underscores, no extension.", img]

                response = client.models.generate_content(model="gemini-3.1-flash-lite", contents=content)
                
                suggested = response.text.strip().lower().replace(" ", "_")
                clean = "".join(c for c in suggested if c.isalnum() or c == '_')
                new_name = f"{clean}_{int(time.time() % 1000)}{file_ext}"
                new_path = os.path.join(directory, new_name)

                os.rename(file_path, new_path)
                print(f"✅ {file_name} -> {new_name}")

            except Exception as e:
                print(f"❌ Error: {e}")

        self.update_status("Batch Complete!", "lightgreen")
        self.progress_label.configure(text="")
        self.btn.configure(state="normal")

if __name__ == "__main__":
    app = GeminiRenamerApp()
    app.mainloop()
