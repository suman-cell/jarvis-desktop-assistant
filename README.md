# JARVIS Desktop Assistant (Python + Voice + PC Control)

A local, voice-controlled **desktop assistant for Windows** inspired by Iron Man’s JARVIS.

Features:

- 🎙️ **Always-on voice assistant** (wake word: `Jarvis`)
- 🧠 Uses **Groq AI** for smart answers
- 🗣️ **Realistic voice** using ElevenLabs (with offline fallback)
- 🖱️ **PC control**: open apps, websites, folders, mouse, scroll, hotkeys
- 👁️ Basic **screen “vision”** using OCR (click buttons by text)
- 💾 **Advanced memory**: Jarvis remembers things about the user
- 🧩 **Workflow automation**: multi-step PC actions
- 🖥️ **Futuristic GUI** with mic status & radar animation

> ⚠️ This project is designed for **Windows** (because of SAPI5, pyautogui behavior, etc.).

---

## 1. Prerequisites

Before installing, make sure you have:

- **Windows 10/11**
- **Python 3.11+** installed and added to PATH  
  Check with:

  ```bash
  python --version
git clone https://github.com/suman-cell/jarvis-desktop-assistant.git
cd jarvis-desktop-assistant

python -m venv .venv

# PowerShell (recommended)
.\.venv\Scripts\Activate.ps1

# or Command Prompt
.\.venv\Scripts\activate.bat

pip install --upgrade pip
pip install -r requirements.txt

# Linux/WSL
touch .env

# Windows PowerShell
ni .env


GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

python jarvis_gui.py



---

You should see a futuristic JARVIS window with:

Title: J.A.R.V.I.S

Status line

Mic icon

Radar animation

Conversation area

Buttons: POWER ON, POWER OFF

Usage Flow

Click POWER ON
Jarvis will say something like:

“Systems online. Awaiting your command, boss Suman.”

Say:

Jarvis

to enter continuous conversation mode.

Now you can talk normally without saying his name every time.
