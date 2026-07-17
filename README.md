## Installation

```bash
git clone https://github.com/LightningChampion/browser-code-explorer.git
cd browser-code-explorer

python -m venv .venv
source .venv/bin/activate

pip install -e .
python -m playwright install chromium
```


## OpenAI API key on macOS

The project reads the OpenAI API key securely from macOS Keychain using the service name browser-code-explorer.

Run this to verify the connection:

    python check_openai_key.py

## Usage

```bash
python main.py pallets/flask
```

## Output

The tool generates reports in the `reports/` folder, including:

- repository-overview.md
- ai-summary.md
- final-report.md
- architecture.json
- code-analysis.json
- dependency-graph.md