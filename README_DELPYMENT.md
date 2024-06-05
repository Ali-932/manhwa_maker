## Enable virtual environment

```bash
source venv/Scripts/activate
```
## Install requirements

```bash
pip install -r requirements.txt
```

## run pyinstaller

```bash
pyinstaller --onefile -F frontend/main.py --collect-all customtkinter -w
```