# Copilot Studio Testing
this is a simple repo for valuating the Copilot Studio chatbots
metrics in reference to:
https://medium.com/walmartglobaltech/evaluation-of-rag-metrics-using-raga-0cd9bf001a76
https://docs.ragas.io/en/latest/concepts/metrics/faithfulness.html

**This evaluation repo is solely for simple / loophole testing purposes, do not treat this as standard**

## Set Up
add this in .env at root
```
OPENAI_API_KEY=<ur openai api key, starts with "sk">
COPILOT_INIT=<copilot init api endpoint>
COPILOT_CHAT=<copilot chat api endpoint>
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

