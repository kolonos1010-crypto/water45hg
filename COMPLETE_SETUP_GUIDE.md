# COMPLETE SETUP GUIDE 🚀

Everything you need to get this software running with zero issues.

---

## PART 1 — SET UP YOUR FOLDER

Your project folder (called `rickypo`) must contain these files:

- `main_simple.py` — your bot file
- - `API_CONFIGURATION.txt` — your API keys file
  - - `batch_001.txt`, `batch_002.txt`, etc. — your number files
   
    - **If `API_CONFIGURATION.txt` is missing**, create a new text file inside `rickypo` named exactly `API_CONFIGURATION.txt` and paste this inside it:
   
    - ```
      ====== API CONFIGURATION (EASY ACCESS) ======

      MODULE: 1

      API_KEYS: your_key_1,your_key_2,your_key_3
      ```

      Replace `your_key_1,your_key_2,your_key_3` with your real API keys separated by commas.

      **If batch files are missing**, create a text file named `batch_001.txt` inside `rickypo` and put numbers in it, one per line:

      ```
      100
      200
      150
      ```

      ---

      ## PART 2 — INSTALL PYTHON (if not already installed)

      1. Go to **python.org/downloads** and download Python 3.10 or higher
      2. 2. During install, **tick the box that says "Add Python to PATH"** — this is very important!
         3. 3. Click Install
           
            4. ---
           
            5. ## PART 3 — OPEN COMMAND PROMPT
           
            6. Press `Win + R`, type `cmd`, press Enter
           
            7. ---
           
            8. ## PART 4 — NAVIGATE TO YOUR PROJECT ROOT
           
            9. The software lives one level **above** your `rickypo` folder. Type this and press Enter:
           
            10. ```
                cd "C:\Users\user0\Downloads\water45hg-claude-devops-agent-prompt-VCHy5\water45hg-claude-devops-agent-prompt-VCHy5"
                ```

                > ⚠️ Do NOT cd into the `rickypo` folder itself — stay one level above it.
                >
                > ---
                >
                > ## PART 5 — INSTALL DEPENDENCIES (one time only)
                >
                > Type this and press Enter, then wait for it to finish:
                >
                > ```
                > pip install -r requirements.txt
                > ```
                >
                > ---
                >
                > ## PART 6 — RUN THE SOFTWARE
                >
                > Copy and paste this exactly, then press Enter:
                >
                > ```
                > python -m src.main_simple --folder "C:\Users\user0\Downloads\water45hg-claude-devops-agent-prompt-VCHy5\water45hg-claude-devops-agent-prompt-VCHy5\rickypo" --command "python main_simple.py"
                > ```
                >
                > ---
                >
                > ## PART 7 — WATCH IT WORK 🎉
                >
                > The system will automatically:
                >
                > - Find your `API_CONFIGURATION.txt` and load your keys
                > - - Find all your `.txt` batch files
                >   - - Start `main_simple.py` for each file
                >     - - Input the bot counts automatically
                >       - - Rotate API keys if one fails
                >         - - Generate a final report when done
                >          
                >           - You don't need to touch anything after hitting Enter — it handles everything itself.
                >          
                >           - ---
                >
                > ## ⚠️ COMMON ISSUES & FIXES
                >
                > | Problem | Fix |
                > |---|---|
                > | `python is not recognized` | Reinstall Python and tick "Add Python to PATH" |
                > | `No module named src` | Make sure you ran Step 4 (cd to the folder ABOVE rickypo, not inside it) |
                > | `No API_CONFIGURATION.txt found` | Check the file is inside `rickypo` with that exact name |
                > | `No number files found` | Make sure your batch files end in `.txt` and are inside `rickypo` |
                > | `Command failed` | Make sure `main_simple.py` is inside `rickypo` |
                >
                > ---
                >
                > ## 📁 Your Correct Folder Structure
                >
                > ```
                > water45hg-claude-devops-agent-prompt-VCHy5/
                > ├── src/                        ← (do not touch)
                > ├── data/                       ← (do not touch)
                > ├── requirements.txt            ← (do not touch)
                > ├── rickypo/                    ← YOUR working folder
                > │   ├── API_CONFIGURATION.txt
                > │   ├── batch_001.txt
                > │   ├── batch_002.txt
                > │   └── main_simple.py
                > ```
                >
                > The most common mistake is running the command from inside `rickypo` — always run from the folder **above** it.
                > 
