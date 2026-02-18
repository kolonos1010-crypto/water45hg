# HOW TO RUN

---

## STEP 1 — Re-download the repo first
Go to GitHub, click the green **Code** button → **Download ZIP**
Extract it and replace your old folder.

---

## STEP 2 — Open Command Prompt
Press `Win + R`, type `cmd`, press Enter

---

## STEP 3 — Navigate to the project folder
⚠️ Do NOT cd into rickypo — go one level above it:

```
cd "C:\Users\user0\Downloads\water45hg-claude-devops-agent-prompt-VCHy5\water45hg-claude-devops-agent-prompt-VCHy5"
```

---

## STEP 4 — Run it

```
python main_simple.py --folder "C:\Users\user0\Downloads\water45hg-claude-devops-agent-prompt-VCHy5\water45hg-claude-devops-agent-prompt-VCHy5\rickypo" --command "python main_simple.py"
```

---

## ❌ COMMON MISTAKES

| Mistake | Fix |
|---|---|
| Running from inside `rickypo` | Run STEP 3 first — go one level above |
| `No module named src` | You are in the wrong folder — redo STEP 3 |
| `can't open file main_simple.py` | You are inside `rickypo` — redo STEP 3 |
| `No API_CONFIGURATION.txt found` | Add that file inside your `rickypo` folder |
| `No number files found` | Add your `.txt` batch files inside `rickypo` |
