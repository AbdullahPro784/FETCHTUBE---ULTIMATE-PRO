import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import yt_dlp
import threading
import os

# --- APP CONFIG ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue") # Options: "blue", "green", "dark-blue"

class FetchTube(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("FETCHTUBE - ULTIMATE PRO")
        self.geometry("1100x700")
        
        # Load Logo (Optional: if you have a 'logo.png' in the folder)
        try:
            self.logo_image = ctk.CTkImage(light_image=Image.open("logo.png"),
                                          dark_image=Image.open("logo.png"),
                                          size=(100, 100))
        except:
            self.logo_image = None

        self.save_path = os.path.join(os.path.expanduser("~"), "Downloads")

        # --- GRID SYSTEM ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR (THE FLEX) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        if self.logo_image:
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, image=self.logo_image, text="")
            self.logo_label.pack(pady=20)
        
        self.title_label = ctk.CTkLabel(self.sidebar_frame, text="FETCHTUBE", font=ctk.CTkFont(size=24, weight="bold", family="Impact"))
        self.title_label.pack(pady=10)

        self.info_btn = ctk.CTkButton(self.sidebar_frame, text="V2.0 STABLE", state="disabled", fg_color="transparent")
        self.info_btn.pack(pady=10)

        self.mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance:", anchor="w")
        self.mode_label.pack(padx=20, pady=(100, 0))
        self.mode_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light"], command=self.change_appearance)
        self.mode_menu.pack(padx=20, pady=10)

        # --- MAIN CONTENT ---
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # URL Input
        self.url_label = ctk.CTkLabel(self.content_frame, text="ENTER TARGET URL", font=ctk.CTkFont(size=14, weight="bold"))
        self.url_label.pack(pady=(10, 5), anchor="w")
        
        self.url_entry = ctk.CTkEntry(self.content_frame, placeholder_text="https://...", height=45, font=("Consolas", 14))
        self.url_entry.pack(fill="x", pady=5)

        self.fetch_btn = ctk.CTkButton(self.content_frame, text="FETCH OPTIONS", command=self.fetch_formats, 
                                        height=45, fg_color="#E63946", hover_color="#A8202A", font=ctk.CTkFont(weight="bold"))
        self.fetch_btn.pack(fill="x", pady=10)

        # Scrollable Quality List
        self.scroll_frame = ctk.CTkScrollableFrame(self.content_frame, label_text="QUALITY DASHBOARD", label_font=("Arial", 12, "bold"))
        self.scroll_frame.pack(fill="both", expand=True, pady=10)
        self.format_var = ctk.StringVar(value="None")

        # Footer Actions
        self.footer = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.footer.pack(fill="x", pady=10)

        self.path_btn = ctk.CTkButton(self.footer, text="📁 BROWSE FOLDER", command=self.browse_folder, fg_color="#457B9D")
        self.path_btn.pack(side="left", padx=5)

        self.download_btn = ctk.CTkButton(self.footer, text="START DOWNLOAD", command=self.start_download, 
                                          state="disabled", fg_color="#2A9D8F", hover_color="#1D6F65", height=45, width=300)
        self.download_btn.pack(side="right", padx=5)

        # Progress
        self.status_label = ctk.CTkLabel(self.content_frame, text="IDLE", font=("Arial", 11))
        self.status_label.pack(pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(self.content_frame, width=800, height=15, progress_color="#F4A261")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

    # --- LOGIC ---
    def change_appearance(self, mode):
        ctk.set_appearance_mode(mode)

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path: self.save_path = path

    def fetch_formats(self):
        url = self.url_entry.get().strip()
        if not url: return
        self.status_label.configure(text="🛰️ CONTACTING SERVERS...")
        for w in self.scroll_frame.winfo_children(): w.destroy()
        threading.Thread(target=self.extract_logic, args=(url,), daemon=True).start()

    def extract_logic(self, url):
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                for f in info.get('formats', []):
                    res = f.get('resolution')
                    if f.get('vcodec') != 'none' and res:
                        size = f.get('filesize') or f.get('filesize_approx') or 0
                        text = f"📺 {res} ({f.get('ext')}) - {round(size/1e6,1)}MB"
                        rb = ctk.CTkRadioButton(self.scroll_frame, text=text, variable=self.format_var, value=f.get('format_id'))
                        rb.pack(anchor="w", padx=20, pady=8)
            self.status_label.configure(text="✅ TARGET ACQUIRED")
            self.download_btn.configure(state="normal")
        except:
            self.status_label.configure(text="❌ CONNECTION FAILED")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%','').strip()
            self.progress_bar.set(float(p)/100)
            self.status_label.configure(text=f"SPEED: {d.get('_speed_str')} | ETA: {d.get('_eta_str')}")

    def start_download(self):
        threading.Thread(target=self.download_logic, args=(self.url_entry.get(), self.format_var.get()), daemon=True).start()

    def download_logic(self, url, fid):
        self.download_btn.configure(state="disabled")
        opts = {
            'format': f'{fid}+bestaudio/best',
            'outtmpl': f'{self.save_path}/%(title)s.%(ext)s',
            'progress_hooks': [self.progress_hook],
            'merge_output_format': 'mp4'
        }
        with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
        self.download_btn.configure(state="normal")

if __name__ == "__main__":
    app = FetchTube()
    app.mainloop()