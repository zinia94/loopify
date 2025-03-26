# loopify

python3 -m venv venv

source venv/bin/activate

on Windows:
python -m venv venv

on Linux:
python3 -m venv venv

Activate the virtual environment:

on Windows:

venv/Scripts/activate

on Linux:
source venv/bin/activate

pip3 freeze > requirements.txt


pip3 install -r requirements.txt

python3 app.py

pytest tests/test_helpers.py

black .