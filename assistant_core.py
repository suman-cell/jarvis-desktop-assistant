import json
import time
import os
import pyautogui
import webbrowser
import subprocess
from datetime import datetime
from screen_vision import click_text
from memory import (
    remember_fact_advanced,
    forget_fact,
    get_fact,
    list_all_memory,
    search_memory,
    get_all_facts,
)
import re

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---- USER PROFILE ----
USER_NAME = "boss suman"
USER_SHORT_NAME = "boss"
# ---------- PC CONTROL HELPERS (NEW) ----------

APP_PATHS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    # if that path doesn't exist, try this one:
    # "chrome": r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "vscode": r"C:\Users\HP\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "notepad": "notepad",  # can be called directly
}

FOLDER_PATHS = {
    "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
    "documents": os.path.join(os.path.expanduser("~"), "Documents"),
    "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
}


def open_known_app(name: str) -> str:
    name = name.lower()
    if name in APP_PATHS:
        path = APP_PATHS[name]
        try:
            subprocess.Popen(path)
            return f"Opening {name}."
        except Exception as e:
            print("Error opening app:", e)
            return f"Sorry boss, I could not open {name}."
    else:
        return f"I don't know where {name} is installed. Please update my app paths."


def open_known_folder(name: str) -> str:
    name = name.lower()
    if name in FOLDER_PATHS:
        path = FOLDER_PATHS[name]
        if os.path.isdir(path):
            subprocess.Popen(["explorer", path])
            return f"Opening your {name} folder."
        else:
            return f"Your {name} folder does not seem to exist."
    else:
        return f"I don't know that folder, boss."


def mouse_move(direction: str, amount: int = 200):
    if direction == "left":
        pyautogui.moveRel(-amount, 0, duration=0.2)
    elif direction == "right":
        pyautogui.moveRel(amount, 0, duration=0.2)
    elif direction == "up":
        pyautogui.moveRel(0, -amount, duration=0.2)
    elif direction == "down":
        pyautogui.moveRel(0, amount, duration=0.2)


def scroll(direction: str, amount: int = 800):
    if direction == "down":
        pyautogui.scroll(-amount)
    elif direction == "up":
        pyautogui.scroll(amount)

def ask_el(prompt: str) -> str:
    """
    Send the user's question or command to Groq LLM.
    Uses a current Groq model and returns a short answer.
    """
    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Jarvis (Jarvis-style), a desktop voice assistant for 'boss suman'. "
                        "Reply in short, clear sentences because your answer will be spoken aloud. "
                        "Be friendly and helpful."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )

        return chat.choices[0].message.content.strip()
    except Exception as e:
        # Fallback if API fails
        print("Groq error:", e)
        return "Sorry boss, I had a problem talking to the AI."



# ----------- ACTIONS: CONTROL THE PC -----------

def open_website(url: str):
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)

def open_app(path: str):
    """
    Open a desktop app by path.
    Example: r'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
    """
    try:
        subprocess.Popen(path)
    except Exception as e:
        print(f"Failed to open app: {e}")

def type_text(text: str):
    pyautogui.write(text, interval=0.02)

def press_hotkey(*keys):
    pyautogui.hotkey(*keys)

def press_key(key: str):
    pyautogui.press(key)
def get_time_string() -> str:
    now = datetime.now()
    return now.strftime("It is %I:%M %p on %A, %d %B %Y.")
def youtube_search(query: str):
    """
    Focus YouTube search bar, type query, press Enter.
    Assumes YouTube tab is active.
    """
    # '/' is the YouTube shortcut to focus the search bar
    press_key("/")
    time.sleep(0.3)
    type_text(query)
    time.sleep(0.2)
    press_key("enter")


def open_youtube_result(index: int = 1):
    """
    Roughly open the Nth video in the search results using keyboard.
    This is approximate and may need tweaking.
    """
    # Give page time to load results
    time.sleep(2.0)

    # Make sure the page has focus
    press_key("tab")
    time.sleep(0.1)

    # This number of tabs may need tuning based on layout
    # Move focus down until we reach first video
    for _ in range(8):
        press_key("tab")
        time.sleep(0.05)

    # Move down to the correct index (1 = first, 2 = second, etc.)
    for _ in range(index - 1):
        press_key("tab")
        time.sleep(0.05)

    press_key("enter")


def auto_memory_from_text(text: str) -> list[str]:
    """
    Try to automatically extract facts about the user from what they say
    and store them into memory. Returns a list of descriptions of what was stored.
    """
    notes: list[str] = []
    if not text:
        return notes

    # Don't auto-store very sensitive stuff
    lower = text.lower()
    sensitive_words = ["password", "otp", "one time password", "pin", "cvv", "card number"]
    if any(word in lower for word in sensitive_words):
        return notes

    # Use regex on original text (case-insensitive)
    # 1) "my name is X"
    m = re.search(r"\bmy name is\s+(.+)", text, re.IGNORECASE)
    if m:
        name = m.group(1).strip().rstrip(".!")
        remember_fact_advanced("name", name, category="profile")
        notes.append(f"your name is {name}")

    # 2) "my birthday is X"
    m = re.search(r"\bmy birthday is\s+(.+)", text, re.IGNORECASE)
    if m:
        birthday = m.group(1).strip().rstrip(".!")
        remember_fact_advanced("birthday", birthday, category="profile")
        notes.append(f"your birthday is {birthday}")

    # 3) "my age is X" or "I am X years old"
    m = re.search(r"\bmy age is\s+(.+)", text, re.IGNORECASE)
    if m:
        age = m.group(1).strip().rstrip(".!")
        remember_fact_advanced("age", age, category="profile")
        notes.append(f"your age is {age}")
    m = re.search(r"\bi am\s+(\d{1,2})\s+years old", text, re.IGNORECASE)
    if m:
        age = m.group(1).strip()
        remember_fact_advanced("age", age, category="profile")
        notes.append(f"your age is {age}")

    # 4) "my favorite X is Y" / "my favourite X is Y"
    m = re.search(r"\bmy (favorite|favourite)\s+(\w+)\s+is\s+(.+)", text, re.IGNORECASE)
    if m:
        thing = m.group(2).strip().lower()
        value = m.group(3).strip().rstrip(".!")
        key = f"favorite {thing}"
        remember_fact_advanced(key, value, category="preferences")
        notes.append(f"your {key} is {value}")

    # 5) "my school name is X"
    m = re.search(r"\bmy school name is\s+(.+)", text, re.IGNORECASE)
    if m:
        school = m.group(1).strip().rstrip(".!")
        remember_fact_advanced("school name", school, category="profile")
        notes.append(f"your school name is {school}")

    # 6) "i like X"  (keep it simple – one like)
    m = re.search(r"\bi like\s+(.+)", text, re.IGNORECASE)
    if m:
        like = m.group(1).strip().rstrip(".!")
        # store as a preference; we don't overwrite previous likes, just add a fact
        remember_fact_advanced(f"like: {like}", like, category="preferences")
        notes.append(f"you like {like}")

    return notes

# ----------- SIMPLE COMMAND PARSER -----------

def handle_command(command: str) -> str:
    """
    First handle fixed PC commands and workflows.
    Otherwise send it to the AI and get an answer.
    """
    cmd = command.lower().strip()

    # ---------- Workflow automation trigger ----------
    if "workflow" in cmd or "automation" in cmd or "automate" in cmd or cmd.startswith("run workflow"):
        # remove trigger words to get a clean description
        desc = cmd.replace("run workflow", "").replace("workflow", "").replace("automation", "")
        desc = desc.replace("automate", "").strip(" :")
        if not desc:
            desc = "open chrome and go to google.com"
        return run_automation(desc)

    # ---------- Identity ----------
    if "what is my name" in cmd or "what's my name" in cmd or "who am i" in cmd:
        return f"Your name is {USER_NAME}, and you are my boss."

    # ---------- Time ----------
    if "time" in cmd and "timer" not in cmd:
        return get_time_string()

    # ---------- Open websites ----------
    if "open youtube" in cmd:
        open_website("https://youtube.com")
        return "Opening YouTube for you, boss."

    if "open google" in cmd and "open chrome" not in cmd:
        open_website("https://google.com")
        return "Opening Google for you, boss."

    # ---------- Open apps ----------
    if "open chrome" in cmd:
        return open_known_app("chrome")

    if "open vs code" in cmd or "open vscode" in cmd or "open code" in cmd:
        return open_known_app("vscode")

    if "open notepad" in cmd:
        return open_known_app("notepad")

    # ---------- Open folders ----------
    if "open downloads" in cmd or "open download folder" in cmd:
        return open_known_folder("downloads")

    if "open documents" in cmd or "open document folder" in cmd:
        return open_known_folder("documents")

    if "open desktop" in cmd or "show desktop folder" in cmd:
        return open_known_folder("desktop")

    # ---------- Type text ----------
    if "type" in cmd and '"' in command:
        try:
            to_type = command.split('"', 1)[1].rsplit('"', 1)[0]
            type_text(to_type)
            return f"Typing: {to_type}"
        except Exception:
            pass

    # ---------- Mouse control ----------
    if "move mouse left" in cmd:
        mouse_move("left")
        return "Moving mouse left."

    if "move mouse right" in cmd:
        mouse_move("right")
        return "Moving mouse right."

    if "move mouse up" in cmd:
        mouse_move("up")
        return "Moving mouse up."

    if "move mouse down" in cmd:
        mouse_move("down")
        return "Moving mouse down."

    if "double click" in cmd:
        pyautogui.doubleClick()
        return "Double clicking."

    if "left click" in cmd or "click" in cmd:
        pyautogui.click()
        return "Clicking."

    # ---------- Scroll ----------
    if "scroll down" in cmd:
        scroll("down")
        return "Scrolling down."

    if "scroll up" in cmd:
        scroll("up")
        return "Scrolling up."

    # ---------- Keyboard: copy / paste / select ----------
    if "copy that" in cmd or "copy this" in cmd or "press control c" in cmd:
        press_hotkey("ctrl", "c")
        return "Copied, boss."

    if "paste that" in cmd or "paste here" in cmd or "press control v" in cmd:
        press_hotkey("ctrl", "v")
        return "Pasting now."

    if "select all" in cmd or "press control a" in cmd:
        press_hotkey("ctrl", "a")
        return "Selecting everything."

    # ---------- Browser controls ----------
    if "new tab" in cmd or "open new tab" in cmd:
        press_hotkey("ctrl", "t")
        return "Opening a new tab."

    if "close tab" in cmd or "close this tab" in cmd:
        press_hotkey("ctrl", "w")
        return "Closing this tab."

    if "refresh page" in cmd or "reload page" in cmd:
        press_hotkey("ctrl", "r")
        return "Refreshing the page."

    # ---------- Basic keys ----------
    if "press enter" in cmd or "hit enter" in cmd:
        press_key("enter")
        return "Pressed enter."

    if "press escape" in cmd or "hit escape" in cmd or "press esc" in cmd:
        press_key("esc")
        return "Pressed escape."

    if "press tab" in cmd:
        press_key("tab")
        return "Pressed tab."

    # ---------- Volume controls ----------
    if "volume up" in cmd:
        press_key("volumeup")
        return "Turning the volume up."

    if "volume down" in cmd:
        press_key("volumedown")
        return "Turning the volume down."

    if "mute volume" in cmd or "mute sound" in cmd:
        press_key("volumemute")
        return "Muting the volume."
        # ---------- YouTube search on current page ----------
    if "search for" in cmd:
        # Example: "search for lofi music"
        query = cmd.split("search for", 1)[1].strip()
        if query:
            youtube_search(query)
            return f"Searching for {query} on YouTube, boss."
        else:
            return "What should I search for, boss?"

    if cmd.startswith("search "):
        # Example: "search cat videos"
        query = cmd.split("search", 1)[1].strip()
        if query:
            youtube_search(query)
            return f"Searching for {query} on YouTube, boss."
        else:
            return "What should I search for, boss?"

    # ---------- Open a specific result (by number) ----------
    if "open first video" in cmd or "open 1st video" in cmd:
        open_youtube_result(1)
        return "Opening the first video."

    if "open second video" in cmd or "open 2nd video" in cmd:
        open_youtube_result(2)
        return "Opening the second video."

    if "open third video" in cmd or "open 3rd video" in cmd:
        open_youtube_result(3)
        return "Opening the third video."
        # ---------- Screen vision: click text on screen ----------
    # Examples you can say:
    # "click text play", "click text subscribe", "click text download"
    if "click text" in cmd:
        # get what comes after "click text"
        after = cmd.split("click text", 1)[1].strip()
        if not after:
            return "What text should I click, boss?"

        # e.g. "play button" -> just use first word or keep full
        # here we keep full phrase
        ok = click_text(after)
        if ok:
            return f"Trying to click text '{after}' on the screen."
        else:
            return f"Sorry boss, I could not find text '{after}' on the screen."

    # You can also support:
    if cmd.startswith("click on") and "on screen" in cmd:
        # Example: "click on play on screen"
        middle = cmd.replace("click on", "").replace("on screen", "").strip()
        if middle:
            ok = click_text(middle)
            if ok:
                return f"Trying to click '{middle}' on the screen."
            else:
                return f"Sorry boss, I could not see '{middle}' on the screen."

       # ---------- ADVANCED MEMORY SYSTEM ----------

    # Teach Jarvis something:
    # "remember my birthday is 29 september"
    # "remember my favorite game is valorant"
    # "remember that my sister name is pooja"
    if cmd.startswith("remember"):
        sentence = command.lower().replace("remember that", "").replace("remember", "").strip()

        # try to split "key is value"
        if " is " in sentence:
            key, value = sentence.split(" is ", 1)
        elif " are " in sentence:
            key, value = sentence.split(" are ", 1)
        else:
            return "Boss, please tell me in the format: remember <thing> is <value>."

        key = key.strip()
        value = value.strip()

        if not key or not value:
            return "I couldn't store that properly, boss. Please say it again clearly."

        remember_fact_advanced(key, value)
        return f"Okay boss, I will remember that your {key} is {value}."

    # Ask for a summary:
    # "what do you remember about me"
    # "summarize your memory"
    if "what do you remember about me" in cmd or "what do you know about me" in cmd or "summarize your memory" in cmd:
        return summarize_memory_with_ai()

    # Ask for specific memory:
    # "what is my birthday"
    # "what is my favorite color"
    if "what is my" in cmd:
        key = cmd.replace("what is my", "").strip()
        if key:
            val = get_fact(key)
            if val:
                return f"Your {key} is {val}, boss."
        # if not found, fall through to normal AI answer

    # Search in memory:
    # "search your memory for birthday"
    # "search your memory for valorant"
    if "search your memory for" in cmd:
        query = cmd.split("search your memory for", 1)[1].strip()
        results = search_memory(query)
        if not results:
            return f"I couldn't find anything in my memory related to '{query}', boss."
        # Make a short list
        lines = [f"- {f['key']}: {f['value']} (category: {f['category']})" for f in results[:5]]
        summary = "\n".join(lines)
        return f"Here is what I found related to '{query}':\n{summary}"

    # Forget something:
    # "forget my birthday"
    # "forget my favorite color"
    if "forget my" in cmd:
        key = cmd.replace("forget my", "").strip()
        if not key:
            return "What should I forget, boss?"
        ok = forget_fact(key)
        if ok:
            return f"Okay boss, I have forgotten your {key}."
        else:
            return f"I don't have any memory saved for {key}."


    # ---------- Default: ask AI ----------
    notes = auto_memory_from_text(command)
    base = ask_el(command)

    if notes:
        extra = " Also, I will remember that " + "; ".join(notes) + "."
        return base + "\n\n" + extra

    return base

   # ---------- WORKFLOW AUTOMATION ----------

ALLOWED_ACTIONS = [
    "open_website",
    "open_app",
    "open_folder",
    "type_text",
    "press_hotkey",
    "mouse_move",
    "scroll",
    "wait_seconds",
]

def plan_workflow(description: str) -> dict | None:
    """
    Ask Groq to turn a natural language instruction into a JSON workflow plan.
    """
    system_prompt = (
        "You are a workflow planner for a desktop assistant named Jarvis. "
        "Your job is to convert the user's request into a SAFE step-by-step plan. "
        "You MUST respond with ONLY a valid JSON object, no explanations, no markdown.\n\n"
        "JSON format:\n"
        "{\n"
        '  \"steps\": [\n'
        "    {\n"
        '      \"action\": \"open_website\" | \"open_app\" | \"open_folder\" |\n'
        '                 \"type_text\" | \"press_hotkey\" | \"mouse_move\" | \"scroll\" | \"wait_seconds\",\n'
        "      ... additional fields depending on action ...\n"
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Rules:\n"
        "- NEVER use dangerous actions like deleting files, formatting disks, or changing system settings.\n"
        "- open_app: {\"app\": \"chrome\" | \"vscode\" | \"notepad\"}\n"
        "- open_folder: {\"folder\": \"downloads\" | \"documents\" | \"desktop\"}\n"
        "- open_website: {\"url\": \"https://...\"}\n"
        "- type_text: {\"text\": \"...\"}\n"
        "- press_hotkey: {\"keys\": [\"ctrl\", \"t\"]}\n"
        "- mouse_move: {\"direction\": \"left\"|\"right\"|\"up\"|\"down\", \"amount\": 200}\n"
        "- scroll: {\"direction\": \"down\"|\"up\", \"amount\": 800}\n"
        "- wait_seconds: {\"seconds\": 1.5}\n"
    )

    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": description},
        ],
        temperature=0,
    )

    raw = chat.choices[0].message.content.strip()
    # Try to handle cases where model wraps JSON in ```json ... ```
    if raw.startswith("```"):
        raw = raw.strip("`")
        # remove possible json header
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()

    try:
        plan = json.loads(raw)
        if not isinstance(plan, dict) or "steps" not in plan:
            print("Workflow plan malformed:", plan)
            return None
        return plan
    except Exception as e:
        print("Failed to parse workflow JSON:", e)
        print("Raw response:", raw)
        return None


def execute_workflow(plan: dict) -> list[str]:
    """
    Execute a workflow plan created by plan_workflow.
    Returns a list of human-readable step summaries.
    """
    steps = plan.get("steps", [])
    summaries: list[str] = []

    for idx, step in enumerate(steps, start=1):
        action = step.get("action")
        if action not in ALLOWED_ACTIONS:
            summaries.append(f"Step {idx}: skipped unknown or disallowed action '{action}'.")
            continue

        try:
            if action == "open_website":
                url = step.get("url", "")
                open_website(url)
                summaries.append(f"Step {idx}: opened website {url}.")

            elif action == "open_app":
                app = step.get("app", "")
                msg = open_known_app(app)
                summaries.append(f"Step {idx}: {msg}")

            elif action == "open_folder":
                folder = step.get("folder", "")
                msg = open_known_folder(folder)
                summaries.append(f"Step {idx}: {msg}")

            elif action == "type_text":
                text = step.get("text", "")
                type_text(text)
                summaries.append(f"Step {idx}: typed some text.")

            elif action == "press_hotkey":
                keys = step.get("keys", [])
                if isinstance(keys, list) and keys:
                    press_hotkey(*keys)
                    summaries.append(f"Step {idx}: pressed hotkey {'+'.join(keys)}.")
                else:
                    summaries.append(f"Step {idx}: invalid hotkey data, skipped.")

            elif action == "mouse_move":
                direction = step.get("direction", "right")
                amount = int(step.get("amount", 200))
                mouse_move(direction, amount)
                summaries.append(f"Step {idx}: moved mouse {direction}.")

            elif action == "scroll":
                direction = step.get("direction", "down")
                amount = int(step.get("amount", 800))
                scroll(direction, amount)
                summaries.append(f"Step {idx}: scrolled {direction}.")

            elif action == "wait_seconds":
                seconds = float(step.get("seconds", 1.0))
                time.sleep(seconds)
                summaries.append(f"Step {idx}: waited {seconds} seconds.")

        except Exception as e:
            print(f"Error executing step {idx}:", e)
            summaries.append(f"Step {idx}: error while executing.")

    return summaries


def run_automation(description: str) -> str:
    """
    High-level function: plan a workflow from description and execute it.
    """
    plan = plan_workflow(description)
    if not plan:
        return "Sorry boss, I could not build a safe workflow for that."

    summaries = execute_workflow(plan)
    if not summaries:
        return "I planned a workflow, but nothing valid could be executed."

    # Combine a short spoken summary
    spoken = f"I ran a workflow with {len(summaries)} steps. For example: {summaries[0]}"
    print("Workflow summary:\n", "\n".join(summaries))
    return spoken
def summarize_memory_with_ai() -> str:
    """
    Use Groq to create a friendly summary of everything Jarvis remembers.
    """
    facts = get_all_facts()
    mem = list_all_memory()

    if not facts and not mem.get("profile") and not mem.get("preferences"):
        return "I don't have any memories about you yet, boss."

    mem_json = json.dumps(mem, ensure_ascii=False, indent=2)

    prompt = (
        "You are Jarvis, an AI desktop assistant for 'boss Suman'.\n"
        "Here is a JSON object that contains everything you currently remember "
        "about the user: profile, preferences, and individual facts.\n\n"
        f"{mem_json}\n\n"
        "Please summarize what you know about the user in a short, friendly way. "
        "Use 3–7 bullet points. Mention important details like birthday, hobbies, "
        "likes/dislikes or anything that feels key to understanding them."
    )

    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful summarizer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    return chat.choices[0].message.content.strip()
