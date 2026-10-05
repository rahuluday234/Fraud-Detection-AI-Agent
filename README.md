Fraud Detection Agent

A two-stage fraud review project that combines a scikit-learn Random Forest with a CrewAI workflow. The model flags higher-risk transaction rows; AI agents then analyze those supplied rows, document an audit review, and produce an operational report.

> **Important:** This project is a prototype for investigation support, not a production fraud-prevention system. Model scores and agent-written analysis are not proof of fraud and should be reviewed by a qualified person.

## What it does

1. Loads a labeled Excel transaction dataset and trains a Random Forest classifier.
2. Evaluates the model on a held-out test split and prints a classification report.
3. Flags test-split rows with a predicted fraud probability greater than `0.8`.
4. If any rows are flagged, appends them to `audit_trail.db` and writes `suspected_frauds.csv`.
5. Reads that CSV with a sequential CrewAI workflow consisting of a fraud analyst, audit reviewer, and report writer.
6. Writes the final agent report to `fraud_report.md`.
The model script expects a target column named `is_fraud`. The exported rows include the test-row index, predicted probability, and actual label; this means the current script is for labeled-data analysis and evaluation, not scoring new unlabeled production transactions.

## Requirements

- Python 3.10 or newer
- [uv](https://docs.astral.sh/uv/) (recommended)
- An Excel dataset with an `is_fraud` column
- A configured LLM provider for CrewAI when running the agent workflow

## Setup

From the project directory:

```powershell
uv sync
```

Configure the environment variables required by your chosen CrewAI LLM provider before running the agent workflow. Do not commit API keys or private transaction data to source control.

## Run the detection pipeline

The script currently loads its workbook from a path hard-coded in `src/fraud_agent.py`:

```python
def load_data(file_path=r"C:\Users\Rahul\OneDrive\Desktop\Fraud Detection Dataset.xlsx"):
```

Update that default to the location of your local Excel workbook, then run:

```powershell
uv run python src/fraud_agent.py
```

The script trains and evaluates the model, then writes `suspected_frauds.csv` and appends the flagged rows to `audit_trail.db` if any rows exceed the threshold. Both output paths are relative to the current working directory.

Run the CrewAI report workflow

After the detection step has created `suspected_frauds.csv`, run:

```powershell
uv run run_crew
```

The workflow reads the CSV from the project directory and creates `fraud_report.md`. It will report an error if the CSV is missing; if no rows exceeded the threshold, the current detection script does not create the CSV, so there will be no input for this step.



Project layout
```text
fraud-agent/
├── agents/                         # Agent definitions
├── fraud-detection/                # Fraud detection skill instructions
├── src/
│   ├── fraud_agent.py              # Model training, evaluation, and export
│   └── fraud_detection_agent/
│       ├── config/                 # CrewAI agent and task configuration
│       ├── crew.py                 # Sequential CrewAI workflow
│       └── main.py                 # Workflow entry point
├── workflows/                      # Workflow definition
├── pyproject.toml
└── suspected_frauds.csv            # Detection output / CrewAI input
```

## Data and output notes

- Keep transaction data and generated audit artifacts private; remove or anonymize real customer information before sharing project files.
- `audit_trail.db` stores records in the `audit_logs` table and is appended to on each run that finds suspected rows.
- `suspected_frauds.csv` is overwritten when suspected rows are exported.
- The current train/test split is random and does not set a split seed, so evaluation results can vary between runs.
- Agent output is generated from the CSV supplied to the workflow. The agents do not rerun or independently validate the model.
