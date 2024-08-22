this is a simple repo for valuating the Luis Copilot POC offering for Singtel

## Set Up
add this in .env at root
```
OPENAI_API_KEY=<ur openai api key, starts with "sk">
```

go to terminal and run:
```bash
python -m venv venv
pip install -r requirement.txt
```
enter venv (on linux)
```bash
source venv/bin/activate
```
run eval
```bash
python3 eval.py
```

## Development
linting
```bash
sh scripts/lint.sh
```

