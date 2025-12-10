import time
import speech_recognition as sr

from assistant_core import handle_command
from tts import speak

# ---------- SPEECH TO TEXT (LISTENING) ----------

r = sr.Recognizer()
mic = sr.Microphone()

def listen_once() -> str | None:
    with mic as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source, phrase_time_limit=6)

    try:
        text = r.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Didn't catch that.")
        return None
    except sr.RequestError as e:
        print(f"Speech recognition error: {e}")
        return None


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

def main():
    speak("Hello boss Suman, I am Jarvis. Say my name to start talking.")

    conversation_mode = False  # False = waiting for wake word, True = continuous chat

    while True:
        heard = listen_once()
        if not heard:
            continue

        lower = heard.lower().strip()

        # --------- IF NOT IN CONVERSATION MODE ---------
        if not conversation_mode:
            # exact wake word
            if lower == WAKE_WORD:
                conversation_mode = True
                speak("Yes boss Suman, continuous conversation mode is on. You can talk to me freely.")
                continue

            # wake word + first command: "jarvis what is black hole"
            if lower.startswith(WAKE_WORD + " "):
                command = lower[len(WAKE_WORD) + 1 :].strip()
                conversation_mode = True
                print(f"Command for jarvis: {command}")
                response = handle_command(command)
                speak(response)
                speak("You can keep talking, boss.")
                continue

            # ignore anything without wake word
            print("Wake word not detected, ignoring.")
            time.sleep(0.2)
            continue

        # --------- IF IN CONVERSATION MODE ---------
        # Check if user wants to stop continuous mode
        if any(phrase in lower for phrase in STOP_PHRASES):
            speak("Okay boss Suman, I will stop listening. Say my name when you need me again.")
            conversation_mode = False
            continue

        # Treat everything as a command / question
        command = lower
        print(f"[Conversation] Command for jarvis: {command}")
        response = handle_command(command)
        speak(response)

        time.sleep(0.3)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        speak("Goodbye boss Suman.")
        print("\n[Jarvis] Stopped by user.")
