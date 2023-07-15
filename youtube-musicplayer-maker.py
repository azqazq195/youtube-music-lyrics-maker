import subprocess
import speech_recognition as sr
import os
import math
import shutil
from pydub import AudioSegment

VIDEO_FOLDER = "./video"
MUSIC_FOLDER = "./music"
FONT_FOLDER = "./font"


def convert_to_wav(input_file):
    folder_path, file = os.path.split(input_file)
    file_name, file_extension = os.path.splitext(file)
    output_file = os.path.join(folder_path, file_name + ".wav")

    if file_extension == '.mp3':
        audio = AudioSegment.from_mp3(input_file)
    elif file_extension == '.wav':
        audio = AudioSegment.from_wav(input_file)

    audio.export(output_file, format='wav')
    return output_file


def move_music_file_to_video_folder(input_file):
    file = os.path.basename(input_file)
    file_name, _ = os.path.splitext(file)
    output_folder_path = os.path.join(VIDEO_FOLDER, file_name)
    output_file = os.path.join(output_folder_path, "music.wav")

    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    shutil.move(input_file, output_file)
    return output_file


def split_wav_file(wav_file):
    folder_path = os.path.dirname(wav_file)
    audio_file = AudioSegment.from_wav(wav_file)
    chunk_length_ms = 30 * 1000

    chunk_files = []
    chunks = []
    start_time = 0
    end_time = chunk_length_ms

    while end_time < len(audio_file):
        chunk = audio_file[start_time:end_time]
        chunks.append(chunk)
        start_time += chunk_length_ms
        end_time += chunk_length_ms

    # 나머지 부분 따로 처리
    if start_time < len(audio_file):
        last_chunk = audio_file[start_time:]
        chunks.append(last_chunk)

    # 분할된 파일 저장
    for i, chunk in enumerate(chunks):
        chunk_filename = os.path.join(folder_path, f"chunk{i+1}.wav")
        chunk.export(chunk_filename, format="wav")
        chunk_files.append(chunk_filename)

    return chunk_files


def delete_files(files):
    for file in files:
        os.remove(file)


def recognize_audio_chunks(audio_chunks, language):
    r = sr.Recognizer()
    text = ''
    for chunk in audio_chunks:
        print(chunk)
        with sr.AudioFile(chunk) as source:
            audio = r.record(source)
            try:
                chunk_text = r.recognize_google(
                    audio, language=language)
                text += chunk_text
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print("Error: ", str(e))

    return text


def create_video(file_name, is_vertical=False):
    audio_file = f"{MUSIC_FOLDER}/{file_name}.mp3"
    image_file = f"{MUSIC_FOLDER}/{file_name}.jpg"
    font_file = f"{FONT_FOLDER}/NanumSquareNeo-Bold.ttf"
    font_size = 36
    font_padding = 10

    # Set image size based on orientation
    if is_vertical:
        result_file = f"{file_name}-세로.mp4"
        art_scale = 700
        art_x_position_ratio = 2  # the smaller, the more to the left
        art_y_position_ratio = 8  # the smaller, the more to the top
        video_resolution = "1080x1920"
    else:
        result_file = f"{file_name}-가로.mp4"
        art_scale = 700
        art_x_position_ratio = 7  # the smaller, the more to the left
        art_y_position_ratio = 2  # the smaller, the more to the top
        video_resolution = "1920x1080"

    filter_complex = (
        # Add album art
        f"[1:v]scale={art_scale}:-1[temp];"
        # Round the corners of the album art
        f"[temp]geq=lum='p(X,Y)':a='if(gt(abs(W/2-X),W/2-20)*gt(abs(H/2-Y),H/2-20),if(lte(hypot(20-(W/2-abs(W/2-X)),20-(H/2-abs(H/2-Y))),20),255,0),255)'[fg];"

        # Add background color
        f"color=s={video_resolution}:c=white[bg];"
        # Overlay album art on the background
        f"[bg][fg]overlay=(main_w-overlay_w)/{art_x_position_ratio}:(main_h-overlay_h)/{art_y_position_ratio}[video];"

        # Add title text on top of the album art
        f"[video]drawtext=fontfile={font_file}: "
        f"text='{file_name}': "
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
    # -t 30 -y 지우기

    subprocess.run(command, check=True)


# Example usage
# create_video("연인 - 박효신")
# create_video("연인 - 박효신", True)


if __name__ == "__main__":
    input_file = f"{MUSIC_FOLDER}/연인 - 박효신.mp3"
    wav_file = convert_to_wav(input_file)
    wav_file = move_music_file_to_video_folder(wav_file)
    chunk_files = split_wav_file(wav_file)
    text = recognize_audio_chunks(chunk_files, 'ko-KR')
    delete_files(chunk_files)
    print(text)
