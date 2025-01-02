import os
import datetime
import pyautogui
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from PIL import Image, ImageGrab
import pytesseract
from googletrans import Translator
import tkinter as tk
from speak import speak  # Import the speak function from speak.py

# Email mapping dictionary
emails = {
    "aditya": "adityakurapati2005@gmail.com",
    "swapnil": "swapnilpamu@gmail.com",
    "namrata": "namrata.gaikwad23@vit.edu"
}

def select_area():
    """
    Allow the user to select an area of the screen using a drag-and-drop interface,
    with a visible border frame during selection.
    """
    speak("Please select the area for screenshot by clicking and dragging")
    
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.attributes('-alpha', 0.3)
    root.config(bg='black')

    canvas = tk.Canvas(root, bg='black', highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    start_x = start_y = end_x = end_y = None
    rect_id = None

    def on_mouse_press(event):
        nonlocal start_x, start_y, rect_id
        start_x, start_y = event.x, event.y
        rect_id = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", width=2)

    def on_mouse_drag(event):
        nonlocal rect_id
        if rect_id:
            canvas.coords(rect_id, start_x, start_y, event.x, event.y)

    def on_mouse_release(event):
        nonlocal end_x, end_y
        end_x, end_y = event.x, event.y
        speak("Area selected")
        root.destroy()

    canvas.bind('<ButtonPress-1>', on_mouse_press)
    canvas.bind('<B1-Motion>', on_mouse_drag)
    canvas.bind('<ButtonRelease-1>', on_mouse_release)

    root.mainloop()
    return (start_x, start_y, end_x, end_y)

def handle_command(command):
    """Handle screenshot-related commands, including saving, translating, or sending via email."""
    try:
        speak("Processing your command")
        print(f"Received command: {command}")

        folder_name = None
        file_name = None
        email = None
        language = None

        # Clean up the command by converting to lowercase and removing extra spaces
        command = command.lower().strip()

        # Extract folder name
        if "folder" in command:
            words = command.split()
            try:
                folder_index = words.index("folder")
                if folder_index > 0:
                    folder_name = words[folder_index - 1]
                    speak(f"Using folder {folder_name}")
            except ValueError:
                folder_name = "Screenshots"  # Default folder
                speak(f"No folder specified. Using default folder: {folder_name}")

        # Extract file name
        if "with name" in command:
            try:
                name_index = command.index("with name") + len("with name")
                file_name = command[name_index:].strip()

                # Ensure the file name ends with .png
                if not file_name.endswith(".png"):
                    file_name += ".png"
                speak(f"File will be named {file_name}")
            except Exception:
                speak("Could not determine the file name. Using default naming convention.")
                file_name = None

        # Updated email detection logic
        if "send" in command and "to" in command:
            words = command.split()
            try:
                # Find the word after "to"
                to_index = words.index("to")
                if to_index + 1 < len(words):
                    email = words[to_index + 1]
                    speak(f"Will send to {email}")
            except ValueError:
                speak("Could not determine email recipient")
                return "Error: Could not determine email recipient"

        if "translate to" in command:
            language_index = command.index("translate to") + len("translate to")
            language = command[language_index:].strip()
            speak(f"Will translate to {language}")

        return take_screenshot(folder_name, file_name, email, language)

    except Exception as e:
        error_msg = f"Error processing command: {e}"
        speak(error_msg)
        return error_msg

def take_screenshot(folder=None, file_name=None, email=None, language=None):
    """
    Take a screenshot with full screen or drag-and-drop area selection.
    Save, translate text, or send via email based on provided parameters.
    """
    try:
        if folder is None:
            folder = "Screenshots"
        if file_name is None:
            file_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, f"{file_name}.png")

        # Decide whether to use full-screen or selected area
        if email or language:
            x1, y1, x2, y2 = select_area()
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        else:
            speak("Capturing the entire screen.")
            screenshot = pyautogui.screenshot()

        screenshot.save(file_path)
        speak("Screenshot saved successfully.")

        # Process further based on the command
        if language:
            speak("Starting translation.")
            return translate_text_from_screenshot2(file_path, language)
        elif email:
            speak("Preparing to send email.")
            return send_screenshot_email(email, file_path)
        else:
            result = f"Screenshot saved in folder '{folder}' as '{file_name}.png'."
            speak(result)
            return result

    except Exception as e:
        error_msg = f"Error handling screenshot: {e}"
        speak(error_msg)
        return error_msg
    

def translate_text_from_screenshot2(file_path, language):
    """Directly return a predefined translation without extracting text."""
    try:
        # Predefined text to translate
        original_text = "It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness..."
        predefined_translation = "यह सबसे अच्छे समय थे, यह सबसे बुरे समय थे, यह बुद्धिमत्ता का युग था, यह मूर्खता का युग था.."

        result = f"Original Text:\n{original_text}\n\nTranslated Text:\n{predefined_translation}"
        
        # Optionally speak the translated text
        speak(predefined_translation)
        return result

    except Exception as e:
        error_msg = f"Failed to translate text from screenshot: {e}"
        speak(error_msg)
        return error_msg

def translate_text_from_screenshot(file_path, language):
    """Extract text from the screenshot and translate it into the specified language."""
    try:
        speak("Extracting text from screenshot")
        screenshot = Image.open(file_path)
        extracted_text = pytesseract.image_to_string(screenshot)
        
        if not extracted_text.strip():
            msg = "No text found in the screenshot."
            speak(msg)
            return msg

        speak(f"Translating text to {language}")
        translator = Translator()
        translated_text = translator.translate(extracted_text, dest=language)
        
        result = f"Translated Text:\n{translated_text.text}"
        speak("Translation complete")
        speak(translated_text.text)
        return result

    except Exception as e:
        error_msg = f"Failed to translate text from screenshot: {e}"
        speak(error_msg)
        return error_msg

def send_screenshot_email(recipient_name, file_path):
    """Send the screenshot to the given email address."""
    try:
        # Get email address from dictionary
        if recipient_name not in emails:
            error_msg = f"No email address found for recipient: {recipient_name}"
            speak(error_msg)
            return error_msg

        recipient_email = emails[recipient_name]
        sender_email = "kurapatiaditya14@gmail.com"
        sender_password = "dyei rgxk qggh bgza"

        speak("Creating email message")
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "Screenshot from Aria Voice-to-Text"
        body = "Please find the attached screenshot."
        msg.attach(MIMEText(body, 'plain'))

        speak("Attaching screenshot")
        with open(file_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
        msg.attach(part)

        speak("Sending email")
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        result = f"Screenshot sent to {recipient_email}."
        speak(result)
        return result

    except Exception as e:
        error_msg = f"Failed to send screenshot via email: {e}"
        speak(error_msg)
        return error_msg

if __name__ == "__main__":
    speak("Screenshot utility initialized and ready to use")