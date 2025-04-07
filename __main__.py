import os
import pandas as pd
import moviepy as mv
from datetime import datetime


def timecode_to_seconds(tc):
    if pd.isna(tc) or not str(tc).strip():
        return None
    x = datetime.strptime(str(tc).strip(), "%H:%M:%S")
    return x.hour * 3600 + x.minute * 60 + x.second


def process_video(input_video_path, csv_path, output_dir="sets_output"):
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(csv_path)

    for index, row in df.iterrows():
        print(row)
        set_name = row["set_name"]
        clips = []

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
                clip.close()

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
        description="Découpe une vidéo en sets à partir d’un CSV."
    )
    parser.add_argument("video", help="Chemin vers la vidéo .mp4")
    parser.add_argument("csv", help="Chemin vers le fichier .csv")
    args = parser.parse_args()

    process_video(args.video, args.csv)
