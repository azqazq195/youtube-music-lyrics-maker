call python -m venv .venv
call .venv\Scripts\activate.bat
call pip install --upgrade pip
call pip install -r requirements.txt
call python youtube-musicplayer-maker.py
pause