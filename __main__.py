import os
import pandas as pd
import moviepy as mv
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps


def timecode_to_seconds(tc):
    if pd.isna(tc) or not str(tc).strip():
        return None
    x = datetime.strptime(str(tc).strip(), "%H:%M:%S")
    return x.hour * 3600 + x.minute * 60 + x.second


def load_character_image(character_name, sprites_dir="thumbnail/sprites"):
    """Charge l'image du personnage depuis le dossier des sprites"""
    try:
        image_path = os.path.join(sprites_dir, f"chara_1_{character_name}_01.png")
        if not os.path.exists(image_path):
            print(f"Erreur: Image de personnage non trouvée: {image_path}")
            return None
        return Image.open(image_path)
    except Exception as e:
        print(f"Erreur lors du chargement de l'image: {e}")
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
):
    """Crée une thumbnail avec les skins et les noms des joueurs sur un fond prédéfini"""
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
        center_logo = Image.open("thumbnail/assets/LogoBC/LogoBC11.png")
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
        # Charger les polices avec différentes tailles (plus grandes pour les pseudos)
        player_font = ImageFont.truetype(
            font_path, int(height * 0.15)
        )  # Augmenté de 15% à 18% pour plus de lisibilité
        set_font = ImageFont.truetype(
            set_font_path, int(height * 0.11)
        )  # 12% de la hauteur

        draw = ImageDraw.Draw(background)

        # Couleur rose/violette comme dans l'image
        text_color = "#F79FC8"  # Rose foncé/violet comme dans l'exemple
        set_text_color = "#5e0830"  # Rose foncé/violet comme dans l'exemple
        set_border_color = "#F79FC8"  # Bordure rose pour le nom du set

        # Positionner les noms des joueurs avec ombre - en bas de l'écran
        player1_pos = (int(width * 0.13), int(height * 0.80))  # En bas à gauche
        player2_pos = (int(width * 0.68), int(height * 0.80))  # En bas à droite

        # Texte principal du joueur 1 avec contour plus épais pour effet gras
        draw.text(
            player1_pos,
            player1_name,
            fill=text_color,
            font=player_font,
            stroke_width=3,  # Augmenté à 3 pour effet plus gras
            stroke_fill=set_text_color,
        )

        # Texte principal du joueur 2 avec contour plus épais pour effet gras
        draw.text(
            player2_pos,
            player2_name,
            fill=text_color,
            font=player_font,
            stroke_width=3,  # Augmenté à 3 pour effet plus gras
            stroke_fill=set_text_color,
        )

        # Positionner le nom du set en haut au centre
        set_text_width = draw.textlength(set_name, font=set_font)
        set_pos = (width / 2 - set_text_width / 2, int(height * 0.025))

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


def process_video(
    input_video_path,
    csv_path,
    background_path,
    output_dir="sets_output",
    sprites_dir="thumbnail/sprites",
):
    os.makedirs(output_dir, exist_ok=True)
    thumbnail_dir = os.path.join(output_dir, "thumbnails")
    os.makedirs(thumbnail_dir, exist_ok=True)

    df = pd.read_csv(csv_path)

    for index, row in df.iterrows():
        print(row)
        set_name = row["set_name"]
        clips = []

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
                )
            except Exception as e:
                print(f"Erreur lors de la génération de la thumbnail: {e}")

        for i in range(1, 6):
            start_tc = row.get(f"start{i}")
            end_tc = row.get(f"end{i}")

            start_sec = timecode_to_seconds(start_tc)
            end_sec = timecode_to_seconds(end_tc)

            if start_sec is not None and end_sec is not None:
                print(
                    f"⏳ Processing set: {set_name}, clip {i}: {start_sec} - {end_sec}"
                )
                clip = mv.VideoFileClip(input_video_path).subclipped(start_sec, end_sec)
                clips.append(clip)

        if clips:
            final_clip = mv.concatenate_videoclips(clips)
            output_path = os.path.join(output_dir, f"{set_name}.mp4")
            print(f"⏳ Exporting set: {set_name}")
            final_clip.write_videofile(
                output_path,
                temp_audiofile="temp-audio.m4a",
                remove_temp=True,
                codec="libx264",
                audio_codec="aac",
                threads=4,
                fps=60,
                preset="slower",
            )
            final_clip.close()
            for c in clips:
                c.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Découpe une vidéo en sets à partir d'un CSV et génère des thumbnails."
    )
    parser.add_argument("video", help="Chemin vers la vidéo .mp4")
    parser.add_argument("csv", help="Chemin vers le fichier .csv")
    parser.add_argument(
        "background", help="Chemin vers l'image de fond pour les thumbnails"
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

    process_video(
        args.video, args.csv, args.background, args.output_dir, args.sprites_dir
    )
