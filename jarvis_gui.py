import math
import threading
import time
import tkinter as tk

import speech_recognition as sr

from assistant_core import handle_command
from tts import speak


# ---------- SPEECH RECOGNITION SETUP ----------

r = sr.Recognizer()
mic = sr.Microphone()

WAKE_WORD = "jarvis"

STOP_PHRASES = [
    "stop listening",
    "go to sleep",
    "sleep now",
    "jarvis sleep",
    "goodbye jarvis",
    "exit conversation",
    "jarvis stop",
]


class JarvisGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("J.A.R.V.I.S - Strategic Assistant")
        self.root.geometry("560x380")
        self.root.resizable(False, False)

        self.root.configure(bg="#050816")

        self.running = False
        self.conversation_mode = False
        self.mic_pulse_state = 0
        self.radar_angle = 0

        # ---------- HEADER PANEL ----------
        header_frame = tk.Frame(root, bg="#050816")
        header_frame.pack(pady=5, fill="x")

        self.title_label = tk.Label(
            header_frame,
            text="J.A.R.V.I.S",
            font=("Segoe UI", 16, "bold"),
            fg="#44ccff",
            bg="#050816",
        )
        self.title_label.pack(side="left", padx=10)

        self.subtitle_label = tk.Label(
            header_frame,
            text="Just A Rather Very Intelligent System",
            font=("Segoe UI", 9),
            fg="#557799",
            bg="#050816",
        )
        self.subtitle_label.pack(side="left", padx=10)

        right_header = tk.Frame(header_frame, bg="#050816")
        right_header.pack(side="right", padx=10)

        self.status_label = tk.Label(
            right_header,
            text="STATUS: IDLE",
            font=("Consolas", 9, "bold"),
            fg="#00ffcc",
            bg="#050816",
        )
        self.status_label.pack(anchor="e")

        self.mic_label = tk.Label(
            right_header,
            text="🎙️",
            font=("Segoe UI Emoji", 20),
            fg="#224455",
            bg="#050816",
        )
        self.mic_label.pack(anchor="e")

        border = tk.Frame(root, height=2, bg="#0f2847")
        border.pack(fill="x", padx=8, pady=(0, 4))

        # ---------- CENTRAL PANEL ----------
        center_frame = tk.Frame(root, bg="#050816")
        center_frame.pack(fill="both", expand=True, padx=8)

        # ---- LEFT RADAR PANEL ----
        left_hud = tk.Frame(center_frame, bg="#050816")
        left_hud.pack(side="left", fill="y", padx=(0, 6), pady=2)

        self.radar_canvas = tk.Canvas(
            left_hud,
            width=130,
            height=130,
            bg="#020714",
            highlightthickness=0,
        )
        self.radar_canvas.pack(pady=4)

        self.left_label = tk.Label(
            left_hud,
            text="SCANNER\nONLINE",
            font=("Consolas", 8, "bold"),
            fg="#00ffcc",
            bg="#050816",
            justify="left",
        )
        self.left_label.pack(anchor="n", pady=4)

        # ---- CONVERSATION PANEL ----
        convo_frame = tk.Frame(center_frame, bg="#050816")
        convo_frame.pack(side="left", fill="both", expand=True)

        self.text_box = tk.Text(
            convo_frame,
            height=12,
            width=52,
            font=("Segoe UI", 10),
            state="disabled",
            wrap="word",
            bg="#020615",
            fg="#e0f7ff",
            insertbackground="#44ccff",
            relief="flat",
        )
        self.text_box.pack(fill="both", expand=True)

        scroll = tk.Scrollbar(convo_frame, command=self.text_box.yview)
        self.text_box.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        self.text_box.tag_configure("user", foreground="#33bbff", font=("Segoe UI", 10, "bold"))
        self.text_box.tag_configure("jarvis", foreground="#00ff99")
        self.text_box.tag_configure("system", foreground="#8899aa", font=("Consolas", 9, "italic"))

        # ---------- CONTROL PANEL ----------
        bottom_frame = tk.Frame(root, bg="#050816")
        bottom_frame.pack(pady=6, fill="x")

        self.start_button = tk.Button(
            bottom_frame,
            text="POWER ON",
            command=self.start_jarvis,
            width=14,
            font=("Segoe UI", 9, "bold"),
            fg="#00ffcc",
            bg="#062235",
            activebackground="#0b3f63",
            activeforeground="#00ffcc",
            relief="flat",
        )
        self.start_button.pack(side="left", padx=(10, 5))

        self.stop_button = tk.Button(
            bottom_frame,
            text="POWER OFF",
            command=self.stop_jarvis,
            width=14,
            font=("Segoe UI", 9, "bold"),
            fg="#ff7070",
            bg="#22090d",
            activebackground="#4a1119",
            activeforeground="#ffaaaa",
            relief="flat",
            state="disabled",
        )
        self.stop_button.pack(side="left", padx=5)

        self.hint_label = tk.Label(
            bottom_frame,
            text="Say 'Jarvis' to activate • Say 'stop listening' to sleep",
            font=("Segoe UI", 8),
            fg="#446688",
            bg="#050816",
        )
        self.hint_label.pack(side="right", padx=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Animations
        self.animate_mic_pulse()
        self.animate_radar()

    # ---------- UI HELPERS ----------

    def animate_mic_pulse(self):
        self.mic_pulse_state = (self.mic_pulse_state + 1) % 20
        color = "#1f8fff" if self.mic_pulse_state < 10 else "#44ccff"
        self.title_label.config(fg=color)
        self.root.after(120, self.animate_mic_pulse)

    def animate_radar(self):
        """
        Draws a simple radar: concentric circles + rotating sweep line.
        """
        self.radar_canvas.delete("all")
        w = int(self.radar_canvas["width"])
        h = int(self.radar_canvas["height"])
        cx, cy = w // 2, h // 2
        max_r = min(cx, cy) - 4

        # Background
        self.radar_canvas.create_oval(
            cx - max_r,
            cy - max_r,
            cx + max_r,
            cy + max_r,
            outline="#094059",
            width=2,
        )

        # Concentric circles
        for frac in (0.25, 0.5, 0.75):
            r = int(max_r * frac)
            self.radar_canvas.create_oval(
                cx - r,
                cy - r,
                cx + r,
                cy + r,
                outline="#062235",
            )

        # Crosshair
        self.radar_canvas.create_line(cx - max_r, cy, cx + max_r, cy, fill="#062235")
        self.radar_canvas.create_line(cx, cy - max_r, cx, cy + max_r, fill="#062235")

        # Rotating sweep line
        angle_rad = math.radians(self.radar_angle)
        x_end = cx + max_r * math.cos(angle_rad)
        y_end = cy + max_r * math.sin(angle_rad)
        self.radar_canvas.create_line(
            cx,
            cy,
            x_end,
            y_end,
            fill="#00ff99",
            width=2,
        )

        # Light glow circle near end of line
        glow_r = 4
        self.radar_canvas.create_oval(
            x_end - glow_r,
            y_end - glow_r,
            x_end + glow_r,
            y_end + glow_r,
            outline="#00ff99",
        )

        # Update angle
        self.radar_angle = (self.radar_angle + 6) % 360

        # Schedule next frame
        self.root.after(60, self.animate_radar)

    def set_status(self, text: str, color: str = "#00ffcc"):
        def _update():
            self.status_label.config(text=f"STATUS: {text.upper()}", fg=color)
        self.root.after(0, _update)

    def set_mic_state(self, state: str):
        def _update():
            if state == "listening":
                self.mic_label.config(text="🎙️", fg="#ff5555")
            elif state == "thinking":
                self.mic_label.config(text="💭", fg="#33aaff")
            else:
                self.mic_label.config(text="🎙️", fg="#224455")
        self.root.after(0, _update)

    def append_text(self, text: str, tag: str | None = None):
        def _update():
            self.text_box.config(state="normal")
            start = self.text_box.index("end-1c")
            self.text_box.insert("end", text + "\n")
            end = self.text_box.index("end-1c")
            if tag:
                self.text_box.tag_add(tag, start, end)
            self.text_box.see("end")
            self.text_box.config(state="disabled")
        self.root.after(0, _update)

    def append_text_animated(self, text: str, tag: str | None = None):
        def _animate(i=0):
            if i == 0:
                self.text_box.config(state="normal")
            if i < len(text):
                start = self.text_box.index("end-1c")
                self.text_box.insert("end", text[i])
                end = self.text_box.index("end-1c")
                if tag:
                    self.text_box.tag_add(tag, start, end)
                self.text_box.see("end")
                self.root.after(12, _animate, i + 1)
            else:
                self.text_box.insert("end", "\n")
                self.text_box.config(state="disabled")
        self.root.after(0, _animate)

    # ---------- CONTROL BUTTONS ----------

    def start_jarvis(self):
        if self.running:
            return
        self.running = True
        self.conversation_mode = False
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

        self.append_text("Jarvis: Systems online. Awaiting your command, boss Suman.", tag="jarvis")
        speak("Systems online. Awaiting your command, boss Suman.")

        t = threading.Thread(target=self.jarvis_loop, daemon=True)
        t.start()

    def stop_jarvis(self):
        self.running = False
        self.conversation_mode = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.set_status("Stopped", "#ff5555")
        self.set_mic_state("idle")
        self.append_text("Jarvis: Shutting down listening protocols.", tag="jarvis")
        speak("Shutting down listening protocols.")

    def on_close(self):
        self.running = False
        self.conversation_mode = False
        self.root.destroy()

    # ---------- VOICE HANDLING ----------

    def listen_once(self) -> str | None:
        with mic as source:
            self.set_status("Listening", "#ffaa00")
            self.set_mic_state("listening")
            print("Listening...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, phrase_time_limit=6)

        self.set_mic_state("idle")

        try:
            self.set_status("Recognizing", "#ffaa00")
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Didn't catch that.")
            self.append_text("System: Didn't catch that.", tag="system")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            self.append_text(f"System: Speech recognition error: {e}", tag="system")
            return None

    def jarvis_loop(self):
        self.set_status("Waiting for 'Jarvis'", "#00ffcc")
        self.set_mic_state("idle")

        while self.running:
            heard = self.listen_once()
            if not self.running:
                break
            if not heard:
                self.set_status("Waiting for 'Jarvis'", "#00ffcc")
                continue

            lower = heard.lower().strip()

            # --- NOT IN CONVERSATION MODE ---
            if not self.conversation_mode:
                if lower == WAKE_WORD:
                    self.conversation_mode = True
                    self.append_text("You: Jarvis", tag="user")
                    msg = "Continuous conversation mode is online. You may talk freely, boss Suman."
                    self.append_text_animated(f"Jarvis: {msg}", tag="jarvis")
                    speak(msg)
                    self.set_status("Conversation mode", "#00ffcc")
                    continue

                if lower.startswith(WAKE_WORD + " "):
                    command = lower[len(WAKE_WORD) + 1 :].strip()
                    self.conversation_mode = True
                    self.append_text(f"You: {heard}", tag="user")
                    self.set_status("Thinking", "#33aaff")
                    self.set_mic_state("thinking")
                    print(f"Command for Jarvis: {command}")
                    response = handle_command(command)
                    self.append_text_animated(f"Jarvis: {response}", tag="jarvis")
                    speak(response)
                    speak("You can keep talking, boss.")
                    self.set_status("Conversation mode", "#00ffcc")
                    self.set_mic_state("idle")
                    continue

                print("Wake word not detected, ignoring.")
                self.set_status("Waiting for 'Jarvis'", "#00ffcc")
                self.set_mic_state("idle")
                time.sleep(0.2)
                continue

            # --- IN CONVERSATION MODE ---
            if any(phrase in lower for phrase in STOP_PHRASES):
                self.append_text(f"You: {heard}", tag="user")
                msg = "Going to sleep. Say my name when you need me again."
                self.append_text_animated(f"Jarvis: {msg}", tag="jarvis")
                speak(f"Going to sleep. Say my name when you need me again, boss Suman.")
                self.conversation_mode = False
                self.set_status("Waiting for 'Jarvis'", "#00ffcc")
                self.set_mic_state("idle")
                continue

            command = lower
            self.append_text(f"You: {heard}", tag="user")
            self.set_status("Thinking", "#33aaff")
            self.set_mic_state("thinking")
            print(f"[Conversation] Command for Jarvis: {command}")
            response = handle_command(command)
            self.append_text_animated(f"Jarvis: {response}", tag="jarvis")
            speak(response)
            self.set_status("Conversation mode", "#00ffcc")
            self.set_mic_state("idle")

            time.sleep(0.3)


# ---------- MAIN ----------

if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisGUI(root)
    root.mainloop()
