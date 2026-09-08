# Windows walkthrough

## 1. Install Ollama

Install Ollama for Windows.

Then in PowerShell:

```powershell
ollama pull qwen3:4b
ollama run qwen3:4b
```

Ask a test question, then type:

```text
/bye
```

## 2. Open the project in VS Code

Extract the ZIP.

Then:

```text
File -> Open Folder -> secure-enterprise-rag-platform
Terminal -> New Terminal
```

## 3. Create the environment

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Start Streamlit

```powershell
streamlit run app.py
```

## 5. First demo

- Knowledge Base -> Load sample knowledge base
- Ask -> role `engineering`
- Ask: `What authentication is required for privileged API operations?`
- Role `hr`
- Ask: `Who may access individual compensation records?`
- Role `engineering`
- Ask the same HR question and verify the HR policy is not retrieved
- Evaluation -> Run sample benchmark

## 6. Troubleshooting

Check Ollama:

```powershell
ollama list
python scripts/check_setup.py
```

The retriever still works without Ollama; you will see retrieval-only evidence.

## 7. Tests

```powershell
pip install -r requirements-dev.txt
pytest -q
```
