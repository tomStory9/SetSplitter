import os
import sys
import pandas as pd
import ffmpeg
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def safe_print(message):
    try:
        print(message)
    except UnicodeEncodeError:
        safe_message = message.encode("ascii", "replace").decode("ascii")
        print(safe_message)


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
):
    if not reset_thumbnails:
        output_path = get_unique_filename(output_path)
    try:
        background = Image.open(background_path)
    except Exception as e:
        safe_print(f"Erreur lors de l'ouverture du fond: {e}")
        return False
    try:
        brush = Image.open("thumbnail/assets/Brush.png")
    except Exception as e:
        safe_print(f"Erreur lors de l'ouverture de la brush: {e}")
        return False
    try:
        center_bar = Image.open("thumbnail/assets/MiddleBar.png")
    except Exception as e:
        safe_print(f"Erreur lors de l'ouverture de la barre: {e}")
        return False
    try:
        center_logo_img = Image.open(center_logo)
    except Exception as e:
        safe_print(f"Erreur lors de l'ouverture du logo: {e}")
        return False

    width, height = background.size

    player1_img = load_character_image(player1_skin, sprites_dir)
    player2_img = load_character_image(player2_skin, sprites_dir)

    if not player1_img or not player2_img:
        safe_print(
            f"Impossible de charger les images des skins: {player1_skin}, {player2_skin}"
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
        safe_print(f"Erreur lors de l'ajout du texte: {e}")
        draw = ImageDraw.Draw(background)
        draw.text((p1_position[0], int(height * 0.75)), player1_name, fill=text_color)
        draw.text((p2_position[0], int(height * 0.75)), player2_name, fill=text_color)
        draw.text((width / 2 - 100, int(height * 0.2)), set_name, fill=text_color)
    background.save(output_path)
    safe_print(f"[OK] Thumbnail generee: {output_path}")
    return True


def get_video_info(input_video_path):
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
        safe_print(f"Erreur lors de l'obtention des infos video: {e}")
        return None


def extract_clips_ffmpeg(input_video_path, clips_data, temp_dir):
    temp_files = []
    for i, (start_sec, end_sec) in enumerate(clips_data):
        temp_file = os.path.join(temp_dir, f"temp_clip_{i}.mp4")
        try:
            safe_print(f"Extraction clip {i+1}: {start_sec}s -> {end_sec}s")
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
            safe_print(f"Erreur lors de l'extraction du clip {i+1}: {e}")
            continue
    return temp_files


def concatenate_clips_ffmpeg(temp_files, output_path):
    if not temp_files:
        safe_print("Aucun clip a concatener")
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
            safe_print(f"Erreur lors de la copie du clip unique: {e}")
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
        safe_print(f"Erreur lors de la concatenation: {e}")
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
):
    os.makedirs(output_dir, exist_ok=True)
    thumbnail_dir = os.path.join(output_dir, "thumbnails")
    os.makedirs(thumbnail_dir, exist_ok=True)
    df = pd.read_csv(csv_path, encoding="utf-8")
    safe_print("Mode generation de thumbnails uniquement")
    safe_print(f"Dossier de sortie: {thumbnail_dir}")
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
                safe_print(f"Generation thumbnail pour: {set_name}")
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
                )
            except Exception as e:
                safe_print(
                    f"Erreur lors de la generation de la thumbnail pour {set_name}: {e}"
                )
        else:
            safe_print(f"Donnees manquantes pour le set: {set_name}")
    safe_print("[OK] Generation des thumbnails terminee!")


def process_video(
    input_video_path,
    csv_path,
    background_path,
    output_dir="sets_output",
    sprites_dir="thumbnail/sprites",
    reset_thumbnails=False,
    center_logo="thumbnail/assets/LogoBC/LogoBC16.png",
):
    os.makedirs(output_dir, exist_ok=True)
    thumbnail_dir = os.path.join(output_dir, "thumbnails")
    temp_dir = os.path.join(output_dir, "temp")
    os.makedirs(thumbnail_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    df = pd.read_csv(csv_path, encoding="utf-8")
    video_info = get_video_info(input_video_path)
    if not video_info:
        safe_print("Impossible d'obtenir les informations de la video")
        return
    safe_print(f"Video chargee: {input_video_path}")
    safe_print(f"FPS: {video_info['fps']}")
    safe_print(f"Audio: {video_info['has_audio']}")
    safe_print(f"Duree: {video_info['duration']:.2f}s")
    for index, row in df.iterrows():
        safe_print(f"\n{'='*50}")
        safe_print(f"Traitement du set: {row['set_name']}")
        safe_print(f"{'='*50}")
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
                )
            except Exception as e:
                safe_print(f"Erreur lors de la generation de la thumbnail: {e}")
        for i in range(1, 6):
            start_tc = row.get(f"start{i}")
            end_tc = row.get(f"end{i}")
            start_sec = timecode_to_seconds(start_tc)
            end_sec = timecode_to_seconds(end_tc)
            if start_sec is not None and end_sec is not None and start_sec < end_sec:
                safe_print(
                    f"Clip {i} ajoute: {start_tc} -> {end_tc} ({start_sec}s - {end_sec}s)"
                )
                clips_data.append((start_sec, end_sec))
        if clips_data:
            temp_files = extract_clips_ffmpeg(input_video_path, clips_data, temp_dir)
            if temp_files:
                output_path = os.path.join(output_dir, f"{set_name}.mp4")
                safe_print(f"Concatenation vers: {output_path}")
                if concatenate_clips_ffmpeg(temp_files, output_path):
                    safe_print(f"[OK] Export termine: {set_name}")
                else:
                    safe_print(f"[ERREUR] Erreur lors de l'export: {set_name}")
                for temp_file in temp_files:
                    try:
                        os.remove(temp_file)
                    except Exception as e:
                        safe_print(f"Impossible de supprimer {temp_file}: {e}")
            else:
                safe_print(f"Aucun clip extrait pour le set: {set_name}")
        else:
            safe_print(f"Aucun clip valide trouve pour le set: {set_name}")
    try:
        os.rmdir(temp_dir)
    except:
        pass
    safe_print(f"\n[OK] Traitement termine!")
