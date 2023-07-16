import subprocess
import speech_recognition as sr
import os
import pylrc
import shutil
from pydub import AudioSegment

VIDEO_FOLDER = "./video"
MUSIC_FOLDER = "./music"
FONT_FOLDER = "./font"


def convert_to_wav(audio_file):
    folder_path, file = os.path.split(audio_file)
    file_name, file_extension = os.path.splitext(file)
    output_file = os.path.join(folder_path, file_name + ".wav")

    if file_extension == '.mp3':
        audio = AudioSegment.from_mp3(audio_file)
    elif file_extension == '.wav':
        audio = AudioSegment.from_wav(audio_file)

    audio.export(output_file, format='wav')
    return output_file


def convert_to_srt(lrc_file):
    with open(lrc_file, 'r', encoding='utf-8') as lrc:
        lrc_string = ''.join(lrc.readlines())

    subs = pylrc.parse(lrc_string)
    srt = subs.toSRT()

    srt_file = lrc_file.replace('.lrc', '.srt')
    with open(srt_file, 'w', encoding='utf-8') as f:
        f.write(srt)


def move_files_to_video_folder(music_name):
    output_folder_path = os.path.join(VIDEO_FOLDER, music_name)
    output_music_file = os.path.join(output_folder_path, "music.wav")
    output_lyrics_file = os.path.join(output_folder_path, "lyrics.srt")
    output_album_art_file = os.path.join(output_folder_path, "album-art.jpg")

    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    for file in os.listdir(MUSIC_FOLDER):
        file_name, file_extension = os.path.splitext(file)
        if file_name == music_name:
            input_file = os.path.join(MUSIC_FOLDER, file)

            if file_extension == ".wav":
                shutil.move(input_file, output_music_file)
            elif file_extension == ".srt":
                shutil.move(input_file, output_lyrics_file)
            elif file_extension == ".jpg":
                shutil.copy(input_file, output_album_art_file)


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


def create_video(music_name, is_vertical=False):
    print(os.getcwd())
    audio_file = os.path.join(VIDEO_FOLDER, music_name, "music.wav")
    image_file = os.path.join(VIDEO_FOLDER, music_name, "album-art.jpg")
    # srt_file = os.path.join(VIDEO_FOLDER, music_name, "lyrics.srt")
    srt_file = "video\\\\연인 - 박효신\\\\lyrics.srt"
    print(audio_file)
    print(image_file)
    print(srt_file)
    font_file = f"{FONT_FOLDER}/NanumSquareNeo-Bold.ttf"
    font_size = 36
    font_padding = 10

    # Set image size based on orientation
    if is_vertical:
        result_file = os.path.join(VIDEO_FOLDER, f"{music_name}-세로.mp4")
        art_scale = 700
        art_x_position_ratio = 2  # the smaller, the more to the left
        art_y_position_ratio = 8  # the smaller, the more to the top
        video_resolution = "1080x1920"
    else:
        result_file = os.path.join(VIDEO_FOLDER, f"{music_name}-가로.mp4")
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
        f"[bg][fg]overlay=(main_w-overlay_w)/{art_x_position_ratio}:(main_h-overlay_h)/{art_y_position_ratio},"

        # Add title text on top of the album art
        f"drawtext=fontfile={font_file}: "
        f"text='{music_name}': "
        f"fontsize={font_size}: fontcolor=black: "
        f"x=(w-{art_scale})/{art_x_position_ratio}+{font_padding}: "
        f"y=(h-{art_scale})/{art_y_position_ratio}-text_h-{font_padding}[video];"

        f"[video]subtitles=lyrics.srt"
    )

    command = [
        "ffmpeg", "-i", audio_file,  "-i", image_file, "-loop", "1", "-c:v",
        "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
        "-filter_complex", filter_complex,
        "-pix_fmt", "yuv420p",
        "-t", "30", "-shortest", result_file, "-y"
    ]

    # -t 30 -y 지우기

    subprocess.run(command, check=True)


# Example usage
# create_video("연인 - 박효신")
# create_video("연인 - 박효신", True)


if __name__ == "__main__":
    music_name = "연인 - 박효신"
    audio_file = f"{MUSIC_FOLDER}/{music_name}.mp3"
    lrc_file = f"{MUSIC_FOLDER}/{music_name}.lrc"
    convert_to_wav(audio_file)
    convert_to_srt(lrc_file)
    move_files_to_video_folder(music_name)

    create_video(music_name)
    # create_video(music_name, True)
