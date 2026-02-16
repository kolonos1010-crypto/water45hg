# QUICK START ⚡

**Get started in 5 minutes!**

---

## 1️⃣ Create a Folder

Make a folder anywhere on your computer. Name it whatever you want:

```
my_bot_project/
```

---

## 2️⃣ Add Your Files

Put these files in that folder:

### **File 1: API_CONFIGURATION.txt**

Create a text file with your API keys:

```
====== API CONFIGURATION (EASY ACCESS) ======

🔑 MODULE: 1

🔑 API_KEYS:
your_key_1,your_key_2,your_key_3
```

Replace `your_key_1,your_key_2,your_key_3` with your actual API keys.

### **File 2: batch_001.txt** (and more)

Create text files with numbers:

```
100
200
150
```

Create as many as you need: `batch_001.txt`, `batch_002.txt`, `batch_003.txt`, etc.

### **File 3: Your Bot**

Put your bot file (`numcac.py` or whatever) in the same folder.

---

## 3️⃣ Final Folder Structure

Your folder should look like:

```
my_bot_project/
├─ API_CONFIGURATION.txt
├─ batch_001.txt
├─ batch_002.txt
├─ numcac.py
└─ (any other files)
```

---

## 4️⃣ Open Terminal

- **Windows**: Press `Win + R`, type `cmd`, press Enter
- - **Mac**: Open Terminal
  - - **Linux**: Open Terminal
   
    - ---

    ## 5️⃣ Go to Your Project

    Type this (change the path to your folder):

    ```bash
    cd /path/to/my_bot_project
    ```

    **Examples:**

    **Windows:**
    ```bash
    cd C:\Users\YourName\Desktop\my_bot_project
    ```

    **Mac:**
    ```bash
    cd /Users/YourName/my_bot_project
    ```

    ---

    ## 6️⃣ Run the Command

    Copy and paste this (change `my_bot_project` to your folder path):

    ```bash
    python -m src.main_simple --folder /path/to/my_bot_project --command "python numcac.py"
    ```

    **Example:**
    ```bash
    python -m src.main_simple --folder C:\Users\YourName\Desktop\my_bot_project --command "python numcac.py"
    ```

    ---

    ## 7️⃣ Watch It Work! 🚀

    The system will:
    1. ✅ Start your bot
    2. 2. ✅ Process your files automatically
       3. 3. ✅ Input bot counts automatically
          4. 4. ✅ Restart for each file
             5. 5. ✅ Generate a final report
               
                6. **You don't need to do anything else!**
               
                7. ---
               
                8. ## THAT'S IT! 🎉
               
                9. You're done! The system handles everything!
               
                10. ---
               
                11. ## Need Help?
               
                12. - Check `SIMPLE_MODE_GUIDE.md` for more details
                    - - Make sure your folder path is correct
                      - - Make sure files are named correctly (no spaces, exact names)
                        - - Make sure API keys are in `API_CONFIGURATION.txt`
                         
                          - ---

                          **Happy Automating!** 💪
                          
