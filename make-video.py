import subprocess
import os


import subprocess


def create_video(file_name, art_scale, art_x_position_ratio, art_y_position_ratio, is_vertical=False):
    title, artist = file_name.split(' - ')
    audio_file = f"{file_name}.mp3"
    image_file = f"{file_name}.jpg"

    orientation = "[세로 화면]" if is_vertical else "[가로 화면]"
    result_file = f"{file_name} {orientation}.mp4"

    # Set font options
    font_file = "./font/NanumSquareNeo-Bold.ttf"
    font_size = 36
    font_padding = 10

    # Set image size based on orientation
    if is_vertical:
        image_size = "1080x1920"
    else:
        image_size = "1920x1080"

    # Create a video from the audio and image
    filter_complex = (
        f"[1:v]scale={art_scale}:-1[fg];"
        f"color=s={image_size}:c=white[bg];"
        f"[bg][fg]overlay=(main_w-overlay_w)/{art_x_position_ratio}:(main_h-overlay_h)/{art_y_position_ratio}[video];"
        f"[video]drawtext=fontfile={font_file}: "
        f"text='{title} - {artist}': "
        f"fontsize={font_size}: fontcolor=black: "
        f"x=(w-{art_scale})/{art_x_position_ratio}+{font_padding}: "
        f"y=(h-{art_scale})/{art_y_position_ratio}-text_h-{font_padding}"
    )

    command = [
        "ffmpeg", "-i", audio_file, "-loop", "1", "-i", image_file, "-c:v",
        "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
        "-filter_complex", filter_complex,
        "-pix_fmt", "yuv420p", "-t", "30", "-shortest", result_file, "-y"
    ]

    subprocess.run(command, check=True)


# Example usage
create_video("연인 - 박효신", 700, 7, 2)  # Horizontal mode
create_video("연인 - 박효신", 700, 2, 7, True)  # Vertical mode
