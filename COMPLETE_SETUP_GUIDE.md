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
           
            8. ## PART 4 — NAVIGATE TO YOUR PROJECT ROOT ⚠️ DO THIS FIRST
           
            9. > ⚠️ **MOST COMMON MISTAKE:** Running the command from the wrong folder causes `No module named 'src'` error. You MUST run the cd command below BEFORE running the software.
               >
               > Type this and press Enter:
               >
               > ```
               > cd "C:\Users\user0\Downloads\water45hg-claude-devops-agent-prompt-VCHy5\water45hg-claude-devops-agent-prompt-VCHy5"
               > ```
               >
               > Do NOT cd into the `rickypo` folder — stay one level above it.
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
               > After completing Part 4, copy and paste this exactly, then press Enter:
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
               > | `No module named 'src'` | You forgot Part 4 — run the `cd` command first, then re-run Part 6 |
               > | `python is not recognized` | Reinstall Python and tick "Add Python to PATH" |
               > | `No API_CONFIGURATION.txt found` | Check the file is inside `rickypo` with that exact name |
               > | `No number files found` | Make sure your batch files end in `.txt` and are inside `rickypo` |
               > | `Command failed` | Make sure `main_simple.py` is inside `rickypo` |
               >
               > ---
               >
               > ## 📁 Your Correct Folder Structure
               >
               > ```
               > water45hg-claude-devops-agent-prompt-VCHy5/   ← RUN FROM HERE (Part 4)
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
               > ---
               >
               > ## 🔒 HOW TO MAKE THE REPO PRIVATE (Password Protect)
               >
               > 1. Go to your repo on GitHub
               > 2. 2. Click **Settings** (top right of the repo)
               >    3. 3. Scroll down to the **Danger Zone** section
               >       4. 4. Click **Change visibility** → select **Private**
               >          5. 5. Confirm it
               >            
               >             6. That's it — only you can access it now.
