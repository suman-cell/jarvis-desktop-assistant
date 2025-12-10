import os
import tempfile
from dotenv import load_dotenv
from elevenlabs import ElevenLabs
from playsound import playsound
import pyttsx3

load_dotenv()

# Create ElevenLabs client
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Choose any voice — these work in free tier
# Adam (male, default voice from docs)
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"



def speak(text: str):
    """
    Jarvis voice system:
    1. Use ElevenLabs advanced TTS (free tier supported)
    2. If it fails, fallback to offline pyttsx3
    """
    if not text:
        return

    print(f"Jarvis: {text}")

    try:
        # Generate speech using ElevenLabs NEW API
        audio_bytes = client.text_to_speech.convert(
            voice_id=VOICE_ID,
            model_id="eleven_multilingual_v2",
            text=text,
        )

        # Save temporary audio file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            for chunk in audio_bytes:
                f.write(chunk)
            file_path = f.name

        # Play audio
        playsound(file_path)

        # Delete temp file
        os.remove(file_path)
        return

    except Exception as e:
        print("[ElevenLabs error]:", e)
        fallback_tts(text)


# ---------- OFFLINE FALLBACK ----------
def fallback_tts(text: str):
    try:
        engine = pyttsx3.init("sapi5")
        voices = engine.getProperty("voices")
        engine.setProperty("voice", voices[0].id)
        engine.setProperty("rate", 180)
        engine.setProperty("volume", 1.0)

        engine.say(text)
        engine.runAndWait()
    except:
        print("Fallback TTS also failed.")
