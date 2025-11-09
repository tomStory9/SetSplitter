import os
import sys
import pandas as pd
import ffmpeg
from PIL import Image, ImageDraw, ImageFont
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
import queue

# ----- Méthodes utilitaires -----

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def safe_print(message, log_widget=None, log_queue=None):
    try:
        print(message)
        if log_widget:
            log_widget.insert(tk.END, message + "\n")
            log_widget.see(tk.END)
        if log_queue is not None:
            log_queue.put(message + "\n")
    except UnicodeEncodeError:
        safe_message = message.encode("ascii", "replace").decode("ascii")
        print(safe_message)
        if log_widget:
            log_widget.insert(tk.END, safe_message + "\n")
            log_widget.see(tk.END)
        if log_queue is not None:
            log_queue.put(safe_message + "\n")


def load_character_image(character_name, sprites_dir="thumbnail/sprites"):
    try:
        image_path = os.path.join(sprites_dir, f"{character_name}.png")
        if not os.path.exists(image_path):
            safe_print(f"Erreur: Image de personnage non trouvee: {image_path}")
            return None
        return Image.open(image_path)
    except Exception as e:
        safe_print(f"Erreur lors du chargement de l'image: {e}")
        return None


def get_font_size_for_text(text, max_width, font_path, base_size, min_size=20):
    font_size = base_size
    while font_size > min_size:
        try:
            font = ImageFont.truetype(font_path, font_size)
            temp_img = Image.new("RGB", (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            text_width = temp_draw.textlength(text, font=font)
            if text_width <= max_width:
                return font_size
            font_size -= 2
        except:
            break
    return max(min_size, font_size)


def get_unique_filename(base_path):
    if not os.path.exists(base_path):
        return base_path
    name, ext = os.path.splitext(base_path)
    counter = 1
    while True:
        new_path = f"{name}_{counter}{ext}"
        if not os.path.exists(new_path):
            return new_path
        counter += 1


def timecode_to_seconds(timecode):
    if pd.isna(timecode) or timecode == "":
        return None
    try:
        if isinstance(timecode, str):
            parts = timecode.split(":")
            if len(parts) == 3:
                hours, minutes, seconds = map(float, parts)
                return hours * 3600 + minutes * 60 + seconds
            elif len(parts) == 2:
                minutes, seconds = map(float, parts)
                return minutes * 60 + seconds
            else:
                return float(timecode)
        else:
            return float(timecode)
    except (ValueError, AttributeError):
        safe_print(f"Format de timecode invalide: {timecode}")
        return None


def create_thumbnail(
    background_path,
    player1_skin,
    player1_name,
    player2_skin,
    player2_name,
    set_name,
    output_path,
    sprites_dir="thumbnail/sprites",
    reset_thumbnails=False,
    center_logo="thumbnail/assets/LogoBC/LogoBC16.png",
    log_queue=None,
):
    if not reset_thumbnails:
        output_path = get_unique_filename(output_path)
    try:
        background = Image.open(background_path)
    except Exception as e:
        safe_print(f"Erreur lors de l'ouverture du fond: {e}", log_queue=log_queue)
        return False
    try:
        brush = Image.open("thumbnail/assets/Brush.png")
    except Exception as e:
        safe_print(f"Erreur lors de l'ouverture de la brush: {e}", log_queue=log_queue)
        return False
    try:
        center_bar = Image.open("thumbnail/assets/MiddleBar.png")
    except Exception as e:
        safe_print(f"Erreur lors de l'ouverture de la barre: {e}", log_queue=log_queue)
        return False
    try:
        center_logo_img = Image.open(center_logo)
    except Exception as e:
        safe_print(f"Erreur lors de l'ouverture du logo: {e}", log_queue=log_queue)
        return False

    width, height = background.size

    player1_img = load_character_image(player1_skin, sprites_dir)
    player2_img = load_character_image(player2_skin, sprites_dir)

    if not player1_img or not player2_img:
        safe_print(
            f"Impossible de charger les images des skins: {player1_skin}, {player2_skin}",
            log_queue=log_queue,
        )
        return False

    skin_height = int(height * 0.7 * 1.25)
    p1_ratio = player1_img.width / player1_img.height
    p2_ratio = player2_img.width / player2_img.height

    player1_img = player1_img.resize(
        (int(skin_height * p1_ratio), skin_height), Image.LANCZOS
    )
    player2_img = player2_img.resize(
        (int(skin_height * p2_ratio), skin_height), Image.LANCZOS
    )

    if player2_skin != "random":
        player2_img = player2_img.transpose(Image.FLIP_LEFT_RIGHT)

    p1_position = (int(width * 0.000005) - 20, int(height * 0.05) - 25)
    p2_position = (
        int(width * 1.05 - player2_img.width) - 20,
        int(height * 0.05) - 25,
    )

    if player1_img.mode == "RGBA":
        background.paste(player1_img, p1_position, player1_img)
    else:
        background.paste(player1_img, p1_position)

    if player2_img.mode == "RGBA":
        background.paste(player2_img, p2_position, player2_img)
    else:
        background.paste(player2_img, p2_position)

    bar_position = (int(width * 0.5 - center_bar.width / 2), 0)
    if center_bar.mode == "RGBA":
        background.paste(center_bar, bar_position, center_bar)
    else:
        background.paste(center_bar, bar_position)

    logo_position = (
        int(width * 0.5 - center_logo_img.width / 2),
        int(height * 0.5 - center_logo_img.height / 2) - 50,
    )
    if center_logo_img.mode == "RGBA":
        background.paste(center_logo_img, logo_position, center_logo_img)
    else:
        background.paste(center_logo_img, logo_position)

    brush_position = (int(width * 0.5 - brush.width / 2), int(height * 0.68))
    background.paste(brush, brush_position, brush)

    try:
        font_path = "thumbnail/font/Felipa-Regular.ttf"
        set_font_path = "thumbnail/font/ssbu.ttf"
        max_text_width = int(brush.width * 0.4)
        base_player_font_size = int(height * 0.12)
        player1_font_size = get_font_size_for_text(
            player1_name, max_text_width, font_path, base_player_font_size
        )
        player2_font_size = get_font_size_for_text(
            player2_name, max_text_width, font_path, base_player_font_size
        )
        player1_font = ImageFont.truetype(font_path, player1_font_size)
        player2_font = ImageFont.truetype(font_path, player2_font_size)
        set_font = ImageFont.truetype(set_font_path, int(height * 0.11))
        draw = ImageDraw.Draw(background)
        text_color = "#F79FC8"
        set_text_color = "#5e0830"
        set_border_color = "#F79FC8"
        brush_center_x = width // 2
        brush_y = brush_position[1]
        player1_text_width = draw.textlength(player1_name, font=player1_font)
        player2_text_width = draw.textlength(player2_name, font=player2_font)
        player1_bbox = draw.textbbox((0, 0), player1_name, font=player1_font)
        player2_bbox = draw.textbbox((0, 0), player2_name, font=player2_font)
        player1_text_height = player1_bbox[3] - player1_bbox[1]
        player2_text_height = player2_bbox[3] - player2_bbox[1]
        player1_y = brush_y + (brush.height - player1_text_height) // 2 + 20
        player2_y = brush_y + (brush.height - player2_text_height) // 2 + 20
        player1_x = brush_center_x - brush.width // 4 - player1_text_width // 2 - 15
        player2_x = brush_center_x + brush.width // 4 - player2_text_width // 2
        draw.text(
            (player1_x, player1_y),
            player1_name,
            fill=text_color,
            font=player1_font,
            stroke_width=3,
            stroke_fill=set_text_color,
        )
        draw.text(
            (player2_x, player2_y),
            player2_name,
            fill=text_color,
            font=player2_font,
            stroke_width=3,
            stroke_fill=set_text_color,
        )
        set_text_width = draw.textlength(set_name, font=set_font)
        set_pos = (width / 2 - set_text_width / 2, int(height * 0.025) - 10)
        draw.text(
            set_pos,
            set_name,
            fill=set_text_color,
            font=set_font,
            stroke_width=3,
            stroke_fill=set_border_color,
        )
    except Exception as e:
        safe_print(f"Erreur lors de l'ajout du texte: {e}", log_queue=log_queue)
        draw = ImageDraw.Draw(background)
        draw.text((p1_position[0], int(height * 0.75)), player1_name, fill=text_color)
        draw.text((p2_position[0], int(height * 0.75)), player2_name, fill=text_color)
        draw.text((width / 2 - 100, int(height * 0.2)), set_name, fill=text_color)
    background.save(output_path)
    safe_print(f"[OK] Thumbnail generee: {output_path}", log_queue=log_queue)
    return True


def get_video_info(input_video_path, log_queue=None):
    try:
        probe = ffmpeg.probe(input_video_path)
        video_stream = next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
            None,
        )
        audio_stream = next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "audio"),
            None,
        )
        fps = eval(video_stream["r_frame_rate"]) if video_stream else None
        has_audio = audio_stream is not None
        duration = float(probe["format"]["duration"])
        return {"fps": fps, "has_audio": has_audio, "duration": duration}
    except Exception as e:
        safe_print(
            f"Erreur lors de l'obtention des infos video: {e}", log_queue=log_queue
        )
        return None


def extract_clips_ffmpeg(input_video_path, clips_data, temp_dir, log_queue=None):
    temp_files = []
    for i, (start_sec, end_sec) in enumerate(clips_data):
        temp_file = os.path.join(temp_dir, f"temp_clip_{i}.mp4")
        try:
            safe_print(
                f"Extraction clip {i+1}: {start_sec}s -> {end_sec}s",
                log_queue=log_queue,
            )
            input_stream = ffmpeg.input(
                input_video_path, ss=start_sec, t=end_sec - start_sec
            )
            output_stream = ffmpeg.output(
                input_stream,
                temp_file,
                vcodec="libx264",
                acodec="aac",
                r=59.75,
                ar=48000,
                preset="ultrafast",
                avoid_negative_ts="make_zero",
            )
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            temp_files.append(temp_file)
        except Exception as e:
            safe_print(
                f"Erreur lors de l'extraction du clip {i+1}: {e}", log_queue=log_queue
            )
            continue
    return temp_files


def concatenate_clips_ffmpeg(temp_files, output_path, log_queue=None):
    if not temp_files:
        safe_print("Aucun clip a concatener", log_queue=log_queue)
        return False
    if len(temp_files) == 1:
        try:
            input_stream = ffmpeg.input(temp_files[0])
            output_stream = ffmpeg.output(
                input_stream, output_path, vcodec="copy", acodec="copy"
            )
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            return True
        except Exception as e:
            safe_print(
                f"Erreur lors de la copie du clip unique: {e}", log_queue=log_queue
            )
            return False
    concat_file = "temp_concat_list.txt"
    try:
        with open(concat_file, "w", encoding="utf-8") as f:
            for temp_file in temp_files:
                f.write(f"file '{os.path.abspath(temp_file)}'\n")
        input_stream = ffmpeg.input(concat_file, format="concat", safe=0)
        output_stream = ffmpeg.output(
            input_stream,
            output_path,
            vcodec="libx264",
            acodec="aac",
            r=59.75,
            ar=48000,
            preset="ultrafast",
        )
        ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
        os.remove(concat_file)
        return True
    except Exception as e:
        safe_print(f"Erreur lors de la concatenation: {e}", log_queue=log_queue)
        if os.path.exists(concat_file):
            os.remove(concat_file)
        return False


def generate_thumbnails_only(
    csv_path,
    background_path,
    output_dir="sets_output",
    sprites_dir="thumbnail/sprites",
    reset_thumbnails=False,
    center_logo="thumbnail/assets/LogoBC/LogoBC16.png",
    log_queue=None,
):
    os.makedirs(output_dir, exist_ok=True)
    thumbnail_dir = os.path.join(output_dir, "thumbnails")
    os.makedirs(thumbnail_dir, exist_ok=True)
    df = pd.read_csv(csv_path, encoding="utf-8")
    safe_print("Mode generation de thumbnails uniquement", log_queue=log_queue)
    safe_print(f"Dossier de sortie: {thumbnail_dir}", log_queue=log_queue)
    for index, row in df.iterrows():
        set_name = row["set_name"]
        if all(
            field in row
            for field in [
                "player1_skin",
                "player1_name",
                "player2_skin",
                "player2_name",
            ]
        ):
            thumbnail_path = os.path.join(thumbnail_dir, f"{set_name}_thumbnail.png")
            try:
                safe_print(
                    f"Generation thumbnail pour: {set_name}", log_queue=log_queue
                )
                create_thumbnail(
                    background_path,
                    row["player1_skin"],
                    row["player1_name"],
                    row["player2_skin"],
                    row["player2_name"],
                    set_name,
                    thumbnail_path,
                    sprites_dir,
                    reset_thumbnails,
                    center_logo,
                    log_queue=log_queue,
                )
            except Exception as e:
                safe_print(
                    f"Erreur lors de la generation de la thumbnail pour {set_name}: {e}",
                    log_queue=log_queue,
                )
        else:
            safe_print(
                f"Donnees manquantes pour le set: {set_name}", log_queue=log_queue
            )
    safe_print("[OK] Generation des thumbnails terminee!", log_queue=log_queue)


def process_video(
    input_video_path,
    csv_path,
    background_path,
    output_dir="sets_output",
    sprites_dir="thumbnail/sprites",
    reset_thumbnails=False,
    center_logo="thumbnail/assets/LogoBC/LogoBC16.png",
    log_queue=None,
):
    os.makedirs(output_dir, exist_ok=True)
    thumbnail_dir = os.path.join(output_dir, "thumbnails")
    temp_dir = os.path.join(output_dir, "temp")
    os.makedirs(thumbnail_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    df = pd.read_csv(csv_path, encoding="utf-8")
    video_info = get_video_info(input_video_path, log_queue=log_queue)
    if not video_info:
        safe_print(
            "Impossible d'obtenir les informations de la video", log_queue=log_queue
        )
        return
    safe_print(f"Video chargee: {input_video_path}", log_queue=log_queue)
    safe_print(f"FPS: {video_info['fps']}", log_queue=log_queue)
    safe_print(f"Audio: {video_info['has_audio']}", log_queue=log_queue)
    safe_print(f"Duree: {video_info['duration']:.2f}s", log_queue=log_queue)
    for index, row in df.iterrows():
        safe_print(f"\n{'='*50}", log_queue=log_queue)
        safe_print(f"Traitement du set: {row['set_name']}", log_queue=log_queue)
        safe_print(f"{'='*50}", log_queue=log_queue)
        set_name = row["set_name"]
        clips_data = []
        if all(
            field in row
            for field in [
                "player1_skin",
                "player1_name",
                "player2_skin",
                "player2_name",
            ]
        ):
            thumbnail_path = os.path.join(thumbnail_dir, f"{set_name}_thumbnail.png")
            try:
                create_thumbnail(
                    background_path,
                    row["player1_skin"],
                    row["player1_name"],
                    row["player2_skin"],
                    row["player2_name"],
                    set_name,
                    thumbnail_path,
                    sprites_dir,
                    reset_thumbnails,
                    center_logo,
                    log_queue=log_queue,
                )
            except Exception as e:
                safe_print(
                    f"Erreur lors de la generation de la thumbnail: {e}",
                    log_queue=log_queue,
                )
        for i in range(1, 6):
            start_tc = row.get(f"start{i}")
            end_tc = row.get(f"end{i}")
            start_sec = timecode_to_seconds(start_tc)
            end_sec = timecode_to_seconds(end_tc)
            if start_sec is not None and end_sec is not None and start_sec < end_sec:
                safe_print(
                    f"Clip {i} ajoute: {start_tc} -> {end_tc} ({start_sec}s - {end_sec}s)",
                    log_queue=log_queue,
                )
                clips_data.append((start_sec, end_sec))
        if clips_data:
            temp_files = extract_clips_ffmpeg(
                input_video_path, clips_data, temp_dir, log_queue=log_queue
            )
            if temp_files:
                output_path = os.path.join(output_dir, f"{set_name}.mp4")
                safe_print(f"Concatenation vers: {output_path}", log_queue=log_queue)
                if concatenate_clips_ffmpeg(
                    temp_files, output_path, log_queue=log_queue
                ):
                    safe_print(f"[OK] Export termine: {set_name}", log_queue=log_queue)
                else:
                    safe_print(
                        f"[ERREUR] Erreur lors de l'export: {set_name}",
                        log_queue=log_queue,
                    )
                for temp_file in temp_files:
                    try:
                        os.remove(temp_file)
                    except Exception as e:
                        safe_print(
                            f"Impossible de supprimer {temp_file}: {e}",
                            log_queue=log_queue,
                        )
            else:
                safe_print(
                    f"Aucun clip extrait pour le set: {set_name}", log_queue=log_queue
                )
        else:
            safe_print(
                f"Aucun clip valide trouve pour le set: {set_name}", log_queue=log_queue
            )
    try:
        os.rmdir(temp_dir)
    except:
        pass
    safe_print(f"\n[OK] Traitement termine!", log_queue=log_queue)


# ----- Interface Tkinter --------


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
        self.log_queue.put("Lancement du traitement...\n")
        try:
            if thumbnails_only:
                generate_thumbnails_only(
                    csv_path,
                    background_path,
                    output_dir,
                    sprites_dir,
                    reset_thumbnails,
                    logo_path,
                    log_queue=self.log_queue,
                )
            else:
                process_video(
                    video_path,
                    csv_path,
                    background_path,
                    output_dir,
                    sprites_dir,
                    reset_thumbnails,
                    logo_path,
                    log_queue=self.log_queue,
                )
            self.log_queue.put("\nTraitement terminé avec succès.\n")
        except Exception as e:
            self.log_queue.put(f"\nErreur lors du traitement: {str(e)}\n")
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
