import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import threading
import queue


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Interface de génération de thumbnails et vidéo")
        self.geometry("600x550")
        self.log_queue = queue.Queue()
        self.process = None

        self.create_widgets()
        self.check_queue()

    def create_widgets(self):
        padding_opts = {"padx": 10, "pady": 5}

        tk.Label(self, text="Fichier CSV :").grid(
            row=0, column=0, sticky="w", **padding_opts
        )
        self.csv_entry = tk.Entry(self, width=50)
        self.csv_entry.grid(row=0, column=1, **padding_opts)
        tk.Button(self, text="Parcourir...", command=self.browse_csv).grid(
            row=0, column=2, **padding_opts
        )

        tk.Label(self, text="Fichier vidéo :").grid(
            row=1, column=0, sticky="w", **padding_opts
        )
        self.video_entry = tk.Entry(self, width=50)
        self.video_entry.grid(row=1, column=1, **padding_opts)
        tk.Button(self, text="Parcourir...", command=self.browse_video).grid(
            row=1, column=2, **padding_opts
        )

        tk.Label(self, text="Image de fond :").grid(
            row=2, column=0, sticky="w", **padding_opts
        )
        self.background_entry = tk.Entry(self, width=50)
        self.background_entry.grid(row=2, column=1, **padding_opts)
        tk.Button(self, text="Parcourir...", command=self.browse_background).grid(
            row=2, column=2, **padding_opts
        )

        tk.Label(self, text="Dossier sprites :").grid(
            row=3, column=0, sticky="w", **padding_opts
        )
        self.sprites_entry = tk.Entry(self, width=50)
        self.sprites_entry.grid(row=3, column=1, **padding_opts)
        tk.Button(self, text="Parcourir...", command=self.browse_sprites).grid(
            row=3, column=2, **padding_opts
        )
        self.sprites_entry.insert(0, "thumbnail/sprites")

        tk.Label(self, text="Logo central :").grid(
            row=4, column=0, sticky="w", **padding_opts
        )
        self.logo_entry = tk.Entry(self, width=50)
        self.logo_entry.grid(row=4, column=1, **padding_opts)
        tk.Button(self, text="Parcourir...", command=self.browse_logo).grid(
            row=4, column=2, **padding_opts
        )
        self.logo_entry.insert(0, "thumbnail/assets/LogoBC/LogoBC16.png")

        tk.Label(self, text="Dossier sortie :").grid(
            row=5, column=0, sticky="w", **padding_opts
        )
        self.output_entry = tk.Entry(self, width=50)
        self.output_entry.grid(row=5, column=1, **padding_opts)
        tk.Button(self, text="Parcourir...", command=self.browse_output).grid(
            row=5, column=2, **padding_opts
        )
        self.output_entry.insert(0, "sets_output")

        self.thumbnails_only_var = tk.BooleanVar()
        tk.Checkbutton(
            self,
            text="Générer uniquement les thumbnails",
            variable=self.thumbnails_only_var,
        ).grid(row=6, column=1, sticky="w", **padding_opts)

        self.reset_thumbnails_var = tk.BooleanVar()
        tk.Checkbutton(
            self,
            text="Réinitialiser les thumbnails existants",
            variable=self.reset_thumbnails_var,
        ).grid(row=7, column=1, sticky="w", **padding_opts)

        self.run_button = tk.Button(
            self,
            text="Lancer le traitement",
            command=self.run_process,
            bg="green",
            fg="white",
        )
        self.run_button.grid(row=8, column=1, pady=10)

        self.progress = ttk.Progressbar(self, length=400, mode="indeterminate")
        self.progress.grid(row=9, column=0, columnspan=3, padx=10, pady=5)

        frame = tk.Frame(self)
        frame.grid(row=10, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text = tk.Text(
            frame, height=10, width=70, yscrollcommand=scrollbar.set
        )
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.output_text.yview)
        self.grid_rowconfigure(10, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def browse_csv(self):
        file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file:
            self.csv_entry.delete(0, tk.END)
            self.csv_entry.insert(0, file)

    def browse_video(self):
        file = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        if file:
            self.video_entry.delete(0, tk.END)
            self.video_entry.insert(0, file)

    def browse_background(self):
        file = filedialog.askopenfilename(
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        if file:
            self.background_entry.delete(0, tk.END)
            self.background_entry.insert(0, file)

    def browse_sprites(self):
        folder = filedialog.askdirectory()
        if folder:
            self.sprites_entry.delete(0, tk.END)
            self.sprites_entry.insert(0, folder)

    def browse_logo(self):
        file = filedialog.askopenfilename(
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        if file:
            self.logo_entry.delete(0, tk.END)
            self.logo_entry.insert(0, file)

    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder)

    def validate_inputs(self):
        csv_path = self.csv_entry.get()
        video_path = self.video_entry.get()
        background_path = self.background_entry.get()
        sprites_dir = self.sprites_entry.get()
        logo_path = self.logo_entry.get()
        thumbnails_only = self.thumbnails_only_var.get()
        if not os.path.exists(csv_path):
            messagebox.showerror(
                "Erreur", "Le fichier CSV est invalide ou n'existe pas."
            )
            return False
        if not os.path.exists(background_path):
            messagebox.showerror(
                "Erreur", "L'image de fond est invalide ou n'existe pas."
            )
            return False
        if not os.path.exists(sprites_dir):
            messagebox.showerror(
                "Erreur", "Le dossier des sprites est invalide ou n'existe pas."
            )
            return False
        if not os.path.exists(logo_path):
            messagebox.showerror(
                "Erreur", "Le fichier logo central est invalide ou n'existe pas."
            )
            return False
        if not thumbnails_only and (not os.path.exists(video_path) or video_path == ""):
            messagebox.showerror(
                "Erreur",
                "Le fichier vidéo est requis si 'Générer uniquement les thumbnails' n'est pas coché.",
            )
            return False
        return True

    def run_process(self):
        if not self.validate_inputs():
            return
        self.run_button.config(state="disabled")
        self.output_text.delete(1.0, tk.END)
        self.progress.start(10)
        thread = threading.Thread(target=self.process_thread, daemon=True)
        thread.start()

    def process_thread(self):
        csv_path = self.csv_entry.get()
        video_path = self.video_entry.get()
        background_path = self.background_entry.get()
        sprites_dir = self.sprites_entry.get()
        logo_path = self.logo_entry.get()
        output_dir = self.output_entry.get()
        thumbnails_only = self.thumbnails_only_var.get()
        reset_thumbnails = self.reset_thumbnails_var.get()
        cmd = [
            "python",
            "main.py",
            csv_path,
            background_path,
            "--sprites_dir",
            sprites_dir,
            "--output_dir",
            output_dir,
        ]
        if not thumbnails_only:
            cmd.extend(["--video", video_path])
        if thumbnails_only:
            cmd.append("--thumbnails-only")
        if reset_thumbnails:
            cmd.append("--reset-thumbnails")
        cmd.extend(["--center_logo", logo_path])
        self.log_queue.put("Lancement du traitement...\n")
        self.log_queue.put(f"Commande: {' '.join(cmd)}\n\n")
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            for line in process.stdout:
                self.log_queue.put(line)
            process.wait()
            if process.returncode == 0:
                self.log_queue.put("\n Traitement terminé avec succès.\n")
            else:
                self.log_queue.put(
                    f"\n Erreur: le processus s'est terminé avec le code {process.returncode}\n"
                )
        except Exception as e:
            self.log_queue.put(f"\n Erreur lors du traitement: {str(e)}\n")
        finally:
            self.log_queue.put("__DONE__")

    def check_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                if msg == "__DONE__":
                    self.progress.stop()
                    self.run_button.config(state="normal")
                else:
                    self.output_text.insert(tk.END, msg)
                    self.output_text.see(tk.END)
        except queue.Empty:
            pass
        self.after(100, self.check_queue)


if __name__ == "__main__":
    app = App()
    app.mainloop()
