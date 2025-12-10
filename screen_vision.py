import mss
import pyautogui
import pytesseract
from PIL import Image


# If Tesseract is not on PATH, set it manually:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def capture_screen() -> Image.Image:
    """
    Capture the entire primary screen and return a PIL Image.
    """
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # primary monitor
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        return img


def find_text_on_screen(query: str, min_confidence: int = 60):
    """
    Find the first occurrence of 'query' text on the screen using OCR.
    Returns (x, y) center coordinates or None if not found.
    """
    img = capture_screen()
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    n = len(data["text"])
    query_lower = query.lower()

    best_idx = None
    for i in range(n):
        txt = data["text"][i].strip()
        if not txt:
            continue
        conf_str = data["conf"][i]
        conf = int(float(conf_str)) if conf_str != "-1" else 0
        if conf < min_confidence:
            continue

        if query_lower in txt.lower():
            best_idx = i
            break

    if best_idx is None:
        return None

    x = data["left"][best_idx]
    y = data["top"][best_idx]
    w = data["width"][best_idx]
    h = data["height"][best_idx]

    center_x = x + w // 2
    center_y = y + h // 2
    return center_x, center_y


def click_text(query: str, move_duration: float = 0.3) -> bool:
    """
    Try to find text on the screen and click its center.
    Returns True if clicked, False if not found.
    """
    pos = find_text_on_screen(query)
    if not pos:
        return False

    x, y = pos
    pyautogui.moveTo(x, y, duration=move_duration)
    pyautogui.click()
    return True
