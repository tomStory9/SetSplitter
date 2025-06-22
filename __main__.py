import os
import pandas as pd
import ffmpeg
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps


def load_character_image(character_name, sprites_dir="thumbnail/sprites"):
    """Charge l'image du personnage depuis le dossier des sprites"""
    try:
        image_path = os.path.join(sprites_dir, f"{character_name}.png")
        if not os.path.exists(image_path):
            print(f"Erreur: Image de personnage non trouvée: {image_path}")
            return None
        return Image.open(image_path)
    except Exception as e:
        print(f"Erreur lors du chargement de l'image: {e}")
        return None


def get_font_size_for_text(text, max_width, font_path, base_size, min_size=20):
    """Calcule la taille de police optimale pour que le texte rentre dans la largeur donnée"""
    font_size = base_size
    while font_size > min_size:
        try:
            font = ImageFont.truetype(font_path, font_size)
            # Créer un objet draw temporaire pour mesurer le texte
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
    """Génère un nom de fichier unique en ajoutant un numéro si le fichier existe déjà"""
    if not os.path.exists(base_path):
        return base_path

    # Séparer le nom et l'extension
    name, ext = os.path.splitext(base_path)
    counter = 1

    while True:
        new_path = f"{name}_{counter}{ext}"
        if not os.path.exists(new_path):
            return new_path
        counter += 1


def timecode_to_seconds(timecode):
    """Convertit un timecode (HH:MM:SS) en secondes"""
    if pd.isna(timecode) or timecode == "":
        return None

    try:
        # Support pour différents formats de timecode
        if isinstance(timecode, str):
            parts = timecode.split(":")
            if len(parts) == 3:  # HH:MM:SS
                hours, minutes, seconds = map(float, parts)
                return hours * 3600 + minutes * 60 + seconds
            elif len(parts) == 2:  # MM:SS
                minutes, seconds = map(float, parts)
                return minutes * 60 + seconds
            else:  # Assume it's just seconds
                return float(timecode)
        else:
            return float(timecode)
    except (ValueError, AttributeError):
        print(f"⚠️  Format de timecode invalide: {timecode}")
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
):
    """Crée une thumbnail avec les skins et les noms des joueurs sur un fond prédéfini"""
    # Gérer l'unicité du nom de fichier
    if not reset_thumbnails:
        output_path = get_unique_filename(output_path)

    # Charger le fond
    try:
        background = Image.open(background_path)
    except Exception as e:
        print(f"Erreur lors de l'ouverture du fond: {e}")
        return False

    # charger la brush
    try:
        brush = Image.open("thumbnail/assets/Brush.png")
    except Exception as e:
        print(f"Erreur lors de l'ouverture de la brush: {e}")
        return False

    # charger la barre centrale
    try:
        center_bar = Image.open("thumbnail/assets/MiddleBar.png")
    except Exception as e:
        print(f"Erreur lors de l'ouverture de la barre: {e}")
        return False

    # charger le logo central
    try:
        center_logo = Image.open("thumbnail/assets/LogoBC/LogoBC6.png")
    except Exception as e:
        print(f"Erreur lors de l'ouverture du logo: {e}")
        return False

    # Dimensions de la thumbnail (format YouTube recommandé: 1280x720)
    width, height = background.size

    # Charger les images des skins des joueurs depuis le dossier local
    player1_img = load_character_image(player1_skin, sprites_dir)
    player2_img = load_character_image(player2_skin, sprites_dir)

    if not player1_img or not player2_img:
        print(
            f"Impossible de charger les images des skins: {player1_skin}, {player2_skin}"
        )
        return False

    # Redimensionner les images des skins avec ratio 1.25x
    skin_height = int(height * 0.7 * 1.25)  # 70% de la hauteur de la thumbnail * 1.25

    # Conserver le ratio d'aspect
    p1_ratio = player1_img.width / player1_img.height
    p2_ratio = player2_img.width / player2_img.height

    player1_img = player1_img.resize(
        (int(skin_height * p1_ratio), skin_height), Image.LANCZOS
    )
    player2_img = player2_img.resize(
        (int(skin_height * p2_ratio), skin_height), Image.LANCZOS
    )

    # Appliquer un miroir horizontal au sprite de droite (player2)
    if player2_skin != "random":
        player2_img = player2_img.transpose(Image.FLIP_LEFT_RIGHT)

    # Positionnement des images
    p1_position = (int(width * 0.000005) - 20, int(height * 0.05) - 25)
    p2_position = (
        int(width * 1.05 - player2_img.width) - 20,
        int(height * 0.05) - 25,
    )

    # Créer un masque d'alpha pour la transparence si nécessaire
    if player1_img.mode == "RGBA":
        background.paste(player1_img, p1_position, player1_img)
    else:
        background.paste(player1_img, p1_position)

    if player2_img.mode == "RGBA":
        background.paste(player2_img, p2_position, player2_img)
    else:
        background.paste(player2_img, p2_position)

    # Positionnement de la barre centrale (de haut en bas)
    bar_position = (int(width * 0.5 - center_bar.width / 2), 0)
    if center_bar.mode == "RGBA":
        background.paste(center_bar, bar_position, center_bar)
    else:
        background.paste(center_bar, bar_position)

    # Positionnement du logo central (relevé de 15%)
    logo_position = (
        int(width * 0.5 - center_logo.width / 2),
        int(height * 0.5 - center_logo.height / 2) - 50,
    )
    if center_logo.mode == "RGBA":
        background.paste(center_logo, logo_position, center_logo)
    else:
        background.paste(center_logo, logo_position)

    # positionnement de la brush en bas de l'image
    brush_position = (int(width * 0.5 - brush.width / 2), int(height * 0.68))
    background.paste(brush, brush_position, brush)

    # Ajouter du texte avec la police Felipa
    try:
        font_path = "thumbnail/font/Felipa-Regular.ttf"
        set_font_path = "thumbnail/font/ssbu.ttf"

        # Calculer les zones disponibles pour les noms des joueurs
        # La brush fait environ 40% de la largeur de l'image, divisée en 2 pour chaque joueur
        max_text_width = int(
            brush.width * 0.4
        )  # 40% de la largeur de la brush pour chaque nom

        # Taille de base pour les noms des joueurs
        base_player_font_size = int(height * 0.12)

        # Calculer les tailles de police dynamiques pour chaque joueur
        player1_font_size = get_font_size_for_text(
            player1_name, max_text_width, font_path, base_player_font_size
        )
        player2_font_size = get_font_size_for_text(
            player2_name, max_text_width, font_path, base_player_font_size
        )

        # Charger les polices avec les tailles calculées
        player1_font = ImageFont.truetype(font_path, player1_font_size)
        player2_font = ImageFont.truetype(font_path, player2_font_size)
        set_font = ImageFont.truetype(set_font_path, int(height * 0.11))

        draw = ImageDraw.Draw(background)

        # Couleur rose/violette comme dans l'image
        text_color = "#F79FC8"  # Rose foncé/violet comme dans l'exemple
        set_text_color = "#5e0830"  # Rose foncé/violet comme dans l'exemple
        set_border_color = "#F79FC8"  # Bordure rose pour le nom du set

        # Calculer les positions parfaitement centrées des noms dans la brush
        brush_center_x = width // 2
        brush_y = brush_position[1]

        # Calculer les largeurs des textes
        player1_text_width = draw.textlength(player1_name, font=player1_font)
        player2_text_width = draw.textlength(player2_name, font=player2_font)

        # Calculer les hauteurs des textes pour un centrage vertical parfait
        player1_bbox = draw.textbbox((0, 0), player1_name, font=player1_font)
        player2_bbox = draw.textbbox((0, 0), player2_name, font=player2_font)
        player1_text_height = player1_bbox[3] - player1_bbox[1]
        player2_text_height = player2_bbox[3] - player2_bbox[1]

        # Position Y parfaitement centrée verticalement dans la brush
        player1_y = brush_y + (brush.height - player1_text_height) // 2 + 20
        player2_y = brush_y + (brush.height - player2_text_height) // 2 + 20

        # Positions X parfaitement centrées dans chaque moitié de la brush
        player1_x = (
            brush_center_x - brush.width // 4 - player1_text_width // 2 - 15
        )  # Centre de la moitié gauche
        player2_x = (
            brush_center_x + brush.width // 4 - player2_text_width // 2
        )  # Centre de la moitié droite

        # Texte principal du joueur 1 avec contour plus épais pour effet gras
        draw.text(
            (player1_x, player1_y),
            player1_name,
            fill=text_color,
            font=player1_font,
            stroke_width=3,
            stroke_fill=set_text_color,
        )

        # Texte principal du joueur 2 avec contour plus épais pour effet gras
        draw.text(
            (player2_x, player2_y),
            player2_name,
            fill=text_color,
            font=player2_font,
            stroke_width=3,
            stroke_fill=set_text_color,
        )

        # Positionner le nom du set en haut au centre
        set_text_width = draw.textlength(set_name, font=set_font)
        set_pos = (width / 2 - set_text_width / 2, int(height * 0.025) - 10)

        # Texte principal du set avec bordure rose
        draw.text(
            set_pos,
            set_name,
            fill=set_text_color,
            font=set_font,
            stroke_width=3,  # Bordure rose
            stroke_fill=set_border_color,
        )

    except Exception as e:
        print(f"Erreur lors de l'ajout du texte: {e}")
        # Continuer même si la police n'est pas disponible
        draw = ImageDraw.Draw(background)

        # Utiliser la police par défaut si Felipa n'est pas disponible
        draw.text((p1_position[0], int(height * 0.75)), player1_name, fill=text_color)
        draw.text((p2_position[0], int(height * 0.75)), player2_name, fill=text_color)
        draw.text((width / 2 - 100, int(height * 0.2)), set_name, fill=text_color)

    # Sauvegarder la thumbnail en PNG (conserve la transparence si présente)
    background.save(output_path)
    print(f"✅ Thumbnail générée: {output_path}")
    return True


def get_video_info(input_video_path):
    """Obtient les informations de la vidéo avec ffmpeg"""
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
        print(f"❌ Erreur lors de l'obtention des infos vidéo: {e}")
        return None


def extract_clips_ffmpeg(input_video_path, clips_data, temp_dir):
    """Extrait les clips avec ffmpeg et retourne la liste des fichiers temporaires"""
    temp_files = []

    for i, (start_sec, end_sec) in enumerate(clips_data):
        temp_file = os.path.join(temp_dir, f"temp_clip_{i}.mp4")

        try:
            print(f"⏳ Extraction clip {i+1}: {start_sec}s -> {end_sec}s")

            # Créer le stream d'entrée
            input_stream = ffmpeg.input(
                input_video_path, ss=start_sec, t=end_sec - start_sec
            )

            # Créer le stream de sortie avec les mêmes paramètres que l'original
            output_stream = ffmpeg.output(
                input_stream,
                temp_file,
                vcodec="libx264",
                acodec="aac",
                r=59.75,  # FPS
                ar=48000,  # Audio sample rate
                preset="ultrafast",
                avoid_negative_ts="make_zero",
            )

            # Exécuter la commande
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            temp_files.append(temp_file)

        except Exception as e:
            print(f"❌ Erreur lors de l'extraction du clip {i+1}: {e}")
            continue

    return temp_files


def concatenate_clips_ffmpeg(temp_files, output_path):
    """Concatène les clips avec ffmpeg"""
    if not temp_files:
        print("❌ Aucun clip à concaténer")
        return False

    if len(temp_files) == 1:
        # Si un seul clip, copier directement
        try:
            input_stream = ffmpeg.input(temp_files[0])
            output_stream = ffmpeg.output(
                input_stream, output_path, vcodec="copy", acodec="copy"
            )
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la copie du clip unique: {e}")
            return False

    # Créer un fichier de liste pour la concaténation
    concat_file = "temp_concat_list.txt"
    try:
        with open(concat_file, "w") as f:
            for temp_file in temp_files:
                f.write(f"file '{os.path.abspath(temp_file)}'\n")

        # Concaténer avec ffmpeg
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

        # Nettoyer le fichier de liste
        os.remove(concat_file)
        return True

    except Exception as e:
        print(f"❌ Erreur lors de la concaténation: {e}")
        # Nettoyer le fichier de liste en cas d'erreur
        if os.path.exists(concat_file):
            os.remove(concat_file)
        return False


def generate_thumbnails_only(
    csv_path,
    background_path,
    output_dir="sets_output",
    sprites_dir="thumbnail/sprites",
    reset_thumbnails=False,
):
    """Génère uniquement les thumbnails sans traiter les vidéos"""
    os.makedirs(output_dir, exist_ok=True)
    thumbnail_dir = os.path.join(output_dir, "thumbnails")
    os.makedirs(thumbnail_dir, exist_ok=True)

    df = pd.read_csv(csv_path)

    print("🖼️  Mode génération de thumbnails uniquement")
    print(f"📁 Dossier de sortie: {thumbnail_dir}")

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
                print(f"🖼️  Génération thumbnail pour: {set_name}")
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
                )
            except Exception as e:
                print(
                    f"❌ Erreur lors de la génération de la thumbnail pour {set_name}: {e}"
                )
        else:
            print(f"⚠️  Données manquantes pour le set: {set_name}")

    print("✅ Génération des thumbnails terminée!")


def process_video(
    input_video_path,
    csv_path,
    background_path,
    output_dir="sets_output",
    sprites_dir="thumbnail/sprites",
    reset_thumbnails=False,
):
    os.makedirs(output_dir, exist_ok=True)
    thumbnail_dir = os.path.join(output_dir, "thumbnails")
    temp_dir = os.path.join(output_dir, "temp")
    os.makedirs(thumbnail_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)

    df = pd.read_csv(csv_path)

    # Obtenir les informations de la vidéo
    video_info = get_video_info(input_video_path)
    if not video_info:
        print("❌ Impossible d'obtenir les informations de la vidéo")
        return

    print(f"📹 Vidéo chargée: {input_video_path}")
    print(f"📊 FPS: {video_info['fps']}")
    print(f"🎵 Audio: {video_info['has_audio']}")
    print(f"⏱️  Durée: {video_info['duration']:.2f}s")

    for index, row in df.iterrows():
        print(f"\n{'='*50}")
        print(f"🎬 Traitement du set: {row['set_name']}")
        print(f"{'='*50}")

        set_name = row["set_name"]
        clips_data = []

        # Générer la thumbnail
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
                )
            except Exception as e:
                print(f"❌ Erreur lors de la génération de la thumbnail: {e}")

        # Collecter les timecodes valides
        for i in range(1, 6):
            start_tc = row.get(f"start{i}")
            end_tc = row.get(f"end{i}")

            start_sec = timecode_to_seconds(start_tc)
            end_sec = timecode_to_seconds(end_tc)

            if start_sec is not None and end_sec is not None and start_sec < end_sec:
                print(
                    f"📝 Clip {i} ajouté: {start_tc} -> {end_tc} ({start_sec}s - {end_sec}s)"
                )
                clips_data.append((start_sec, end_sec))

        if clips_data:
            # Extraire les clips
            temp_files = extract_clips_ffmpeg(input_video_path, clips_data, temp_dir)

            if temp_files:
                # Concaténer les clips
                output_path = os.path.join(output_dir, f"{set_name}.mp4")
                print(f"💾 Concaténation vers: {output_path}")

                if concatenate_clips_ffmpeg(temp_files, output_path):
                    print(f"✅ Export terminé: {set_name}")
                else:
                    print(f"❌ Erreur lors de l'export: {set_name}")

                # Nettoyer les fichiers temporaires
                for temp_file in temp_files:
                    try:
                        os.remove(temp_file)
                    except Exception as e:
                        print(f"⚠️  Impossible de supprimer {temp_file}: {e}")
            else:
                print(f"❌ Aucun clip extrait pour le set: {set_name}")
        else:
            print(f"⚠️  Aucun clip valide trouvé pour le set: {set_name}")

    # Nettoyer le dossier temporaire
    try:
        os.rmdir(temp_dir)
    except:
        pass

    print(f"\n🎉 Traitement terminé!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Découpe une vidéo en sets à partir d'un CSV et génère des thumbnails avec FFmpeg."
    )
    parser.add_argument("csv", help="Chemin vers le fichier .csv")
    parser.add_argument(
        "background", help="Chemin vers l'image de fond pour les thumbnails"
    )
    parser.add_argument(
        "--video",
        help="Chemin vers la vidéo .mp4 (requis si --thumbnails-only n'est pas utilisé)",
    )
    parser.add_argument(
        "--thumbnails-only",
        action="store_true",
        help="Génère uniquement les thumbnails sans traiter les vidéos",
    )
    parser.add_argument(
        "--reset-thumbnails",
        action="store_true",
        help="Écrase les thumbnails existantes au lieu d'ajouter un numéro",
    )
    parser.add_argument(
        "--output_dir",
        default="sets_output",
        help="Dossier de sortie pour les vidéos et les thumbnails",
    )
    parser.add_argument(
        "--sprites_dir",
        default="thumbnail/sprites",
        help="Dossier contenant les images des personnages",
    )

    args = parser.parse_args()

    # Vérifier que --video est fourni si --thumbnails-only n'est pas utilisé
    if not args.thumbnails_only and not args.video:
        parser.error(
            "L'argument --video est requis sauf si --thumbnails-only est utilisé"
        )

    if args.thumbnails_only:
        generate_thumbnails_only(
            args.csv,
            args.background,
            args.output_dir,
            args.sprites_dir,
            args.reset_thumbnails,
        )
    else:
        process_video(
            args.video,
            args.csv,
            args.background,
            args.output_dir,
            args.sprites_dir,
            args.reset_thumbnails,
        )
