# SIMPLIFIED MODE GUIDE 🚀

## THE EASIEST WAY - Just Point to a Folder!

Instead of specifying each file individually, **just point the system to a folder** and it automatically finds everything!

---

## SETUP (One-Time Only)

### Step 1: Create a Folder for Your Project
```
my_bot_project/
├─ API_CONFIGURATION.txt  (your API keys)
├─ batch_001.txt          (your numbers)
├─ batch_002.txt          (your numbers)
└─ numcac.py              (your bot)
```

### Step 2: Create `API_CONFIGURATION.txt`
Inside your folder, create a file named `API_CONFIGURATION.txt`:

```
====== API CONFIGURATION (EASY ACCESS) ======

🔑 MODULE: 1

🔑 API_KEYS:
key1,key2,key3
```

Replace `key1,key2,key3` with your actual API keys.

### Step 3: Create Your Number Files
Create `batch_001.txt`, `batch_002.txt`, etc. with your numbers:

**batch_001.txt:**
```
100
200
150
```

**batch_002.txt:**
```
50
75
125
```

### Step 4: Put Your Bot in the Folder
Place your `numcac.py` (or whatever bot you have) in the same folder.

---

## THE COMMAND - Super Simple!

```bash
python -m src.main_simple --folder /path/to/my_bot_project --command "python numcac.py"
```

### THAT'S IT! 🎉

No need to list files, no commas, no confusion. Just point to the folder!

---

## REAL WORLD EXAMPLE

Your folder structure:
```
/home/user/my_bot_project/
├─ API_CONFIGURATION.txt
├─ batch_001.txt
├─ batch_002.txt
└─ numcac.py
```

Your command:
```bash
python -m src.main_simple --folder /home/user/my_bot_project --command "python numcac.py"
```

The system will:
1. ✅ Find `API_CONFIGURATION.txt` automatically
2. 2. ✅ Find all `.txt` files (`batch_001.txt`, `batch_002.txt`)
   3. 3. ✅ Process them in alphabetical order
      4. 4. ✅ Run your bot
         5. 5. ✅ Input bot counts automatically
            6. 6. ✅ Generate a report
              
               7. ---
              
               8. ## HOW IT WORKS
              
               9. | Part | Does What |
               10. |------|-----------|
               11. | `--folder /path/to/folder` | Where all your files are |
               12. | `--command "python numcac.py"` | What bot to run |
              
               13. That's it! The system automatically:
               14. - Finds API configuration
                   - - Finds all number files
                     - - Processes them in order
                       - - Inputs bot counts
                         - - Makes a report
                          
                           - ---

                           ## WHAT IF YOU HAVE MANY FOLDERS?

                           No problem! Just run the command for each folder:

                           ```bash
                           # Process folder 1
                           python -m src.main_simple --folder /home/user/project_1 --command "python numcac.py"

                           # Process folder 2
                           python -m src.main_simple --folder /home/user/project_2 --command "python numcac.py"
                           ```

                           ---

                           ## OPTIONAL TIMEOUT

                           If you want to change how long it waits for bot count detection (default: 3 seconds):

                           ```bash
                           python -m src.main_simple --folder /path/to/folder --command "python numcac.py" --timeout 5.0
                           ```

                           ---

                           ## TROUBLESHOOTING

                           | Problem | Fix |
                           |---------|-----|
                           | "Folder not found" | Check the folder path is correct |
                           | "No API_CONFIGURATION.txt found" | Make sure file exists in folder with exact name |
                           | "No number files found" | Make sure `.txt` files exist (not `.text` or others) |
                           | "Command failed" | Make sure bot file is in the folder or use correct path |

                           ---

                           ## THAT'S THE WHOLE THING! 💪

                           **Old way:** Tedious, confusing, error-prone
                           **New way:** Just point to a folder!

                           Enjoy your simplified automation! 🚀
                           
