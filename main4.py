import tkinter as tk
from PIL import Image, ImageTk
import speech_recognition as sr
import threading
import os
import datetime
from concurrent.futures import ThreadPoolExecutor

import handle_screenshot
import handle_sms  # Import the new SMS handling module
import handle_file_system
import handle_system_health
from speak import speak  # Import the speak function

class SlideUpWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Aria Voice-to-Text")

        # Initialize system handlers
        self.sms_handler = handle_sms.SMSHandler()
        self.system_health_handler = handle_system_health.SystemHealthHandler()

        # Screen and window configurations
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.window_height = int(self.screen_height * 0.4)
        self.upper_width = int(self.screen_width * 0.2)
        self.upper_height = 60
        self.button_size = 30
        self.current_y = self.screen_height
        self.target_y = self.screen_height - self.window_height
        self.animation_speed = 30

        self.root.attributes("-alpha", 1, "-topmost", True)  # Removed transparency
        self.root.attributes('-transparentcolor', 'black')

        # Adjusted window geometry to fit the header
        self.root.geometry(f"{self.screen_width}x{self.window_height}+0+{self.screen_height}")
        self.root.overrideredirect(1)
        self.root.attributes("-alpha", 1, "-topmost", True)  # Removed transparency
        self.root.configure(bg='black')  # Set the background color

        # Hide the window initially
        self.root.withdraw()  # This hides the window at the start

        self.root.protocol("WM_DELETE_WINDOW", self.do_nothing)

        # Voice recognition setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.termux_mode_enabled = False  # Flag to control access based on toggle

        # Load and create UI components
        self.load_images()
        self.setup_ui()

        # Start listening in a separate thread
        threading.Thread(target=self.listen_for_activation_phrase, daemon=True).start()

    def do_nothing(self):
        """Prevent window from closing."""
        pass

    def load_images(self):
        """Load images used in the UI."""
        try:
            self.header_bg = ImageTk.PhotoImage(
                Image.open("public/images/upper.png").resize((self.upper_width, self.upper_height), Image.Resampling.LANCZOS)
            )
            self.mic_image = ImageTk.PhotoImage(
                Image.open("public/images/mic.png").resize((self.button_size, self.button_size), Image.Resampling.LANCZOS)
            )
            self.mic_active_image = ImageTk.PhotoImage(
                Image.open("public/images/mic_active.png").resize((self.button_size, self.button_size), Image.Resampling.LANCZOS)
            )
            self.close_icon = ImageTk.PhotoImage(
                Image.open("public/images/close.png").resize((self.button_size, self.button_size), Image.Resampling.LANCZOS)
            )
            self.toggle_icon = ImageTk.PhotoImage(
                Image.open("public/images/toggle_icon.png").resize((self.button_size, self.button_size), Image.Resampling.LANCZOS)
            )
            self.toggle_off_icon = ImageTk.PhotoImage(
                Image.open("public/images/toggle_off.png").resize((self.button_size, self.button_size), Image.Resampling.LANCZOS)
            )
        except Exception as e:
            print(f"Error loading images: {e}")
            self.header_bg = self.mic_image = self.mic_active_image = self.close_icon = self.toggle_icon = self.toggle_off_icon = None

    def setup_ui(self):
        """Set up the UI components."""
        self.container = tk.Frame(self.root, bg="black")
        self.container.place(x=0, y=0, width=self.screen_width, height=self.window_height)

        header_y_position = self.window_height - (self.window_height // 2.3) - self.upper_height
        self.header_frame = tk.Label(
            self.container,
            image=self.header_bg,
            bg=None,
            borderwidth=0,
            highlightthickness=0  # Removes any frame borders
        )
        self.header_frame.place(
            x=(self.screen_width - self.upper_width) // 2,
            y=header_y_position
        )

        button_frame = tk.Frame(self.header_frame, bg="#6005A6")
        button_frame.place(x=10, y=10)

        self.mic_button = tk.Button(
            button_frame, image=self.mic_image, bg="#6005A6", borderwidth=0, command=self.toggle_mic
        )
        self.mic_button.grid(row=0, column=0, padx=5)

        self.close_button = tk.Button(
            button_frame, image=self.close_icon, bg="#6005A6", borderwidth=0, command=self.close_window
        )
        self.close_button.grid(row=0, column=1, padx=5)

        self.toggle_button = tk.Button(
            button_frame, image=self.toggle_off_icon, bg="#6005A6", borderwidth=0, command=self.toggle_termux_mode
        )
        self.toggle_button.grid(row=0, column=2, padx=5)

    def listen_for_activation_phrase(self):
        """Listen for 'Hey Aria' to show the window."""
        while True:
            try:
                with self.microphone as source:
                    print("Listening for activation phrase...")
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=20)

                text = self.recognizer.recognize_google(audio).lower()
                print(f"Recognized: {text}")

                if "hey aria" or "hey assistant" in text:  # If "Hey Aria" is recognized, show the window
                    self.root.deiconify()  # Show the window
                    self.animate_window()  # Start the animation for sliding up
                    speak("How can I assist you?")
                    break

            except sr.UnknownValueError:
                pass  # Ignore errors where speech is not recognized
            except sr.RequestError as e:
                self.update_status_text(f"Speech recognition error: {e}")

    def animate_window(self):
        """Animate the window sliding up."""
        if self.current_y > self.target_y:
            self.current_y -= self.animation_speed
            self.root.geometry(f"{self.screen_width}x{self.window_height}+0+{self.current_y}")
            self.root.after(10, self.animate_window)

    def toggle_mic(self):
        """Toggle microphone listening state."""
        if not self.is_listening:
            self.mic_button.config(image=self.mic_active_image)
            self.is_listening = True
            threading.Thread(target=self.listen_for_speech, daemon=True).start()
        else:
            self.mic_button.config(image=self.mic_image)
            self.is_listening = False

    def listen_for_speech(self):
        """Handle speech recognition.""" 
        try:
            with self.microphone as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=20)

            text = self.recognizer.recognize_google(audio).lower()
            print(f"Recognized: {text}")
            self.parse_and_execute_command(text)

        except sr.UnknownValueError:
            self.update_status_text("Could not understand audio")
        except sr.RequestError as e:
            self.update_status_text(f"Speech recognition error: {e}")
        finally:
            self.reset_mic_button()

    def parse_and_execute_command(self, command):
        print(f"Received command: {command}")

        # Check if Termux mode is enabled only for system health commands
        if "check my system for vulnerabilities" in command or \
        "check my system is safe" in command or \
        "make port scanning for my system" in command or \
        "show devices connected to my network" in command:
            if not self.termux_mode_enabled:
                speak("Please enable Termux mode by toggling the button.")
                return

        # Now handle the commands
        if "send sms" in command:
            result = self.sms_handler.parse_and_send_sms(command)
        elif "screenshot" in command:
            result = handle_screenshot.handle_command(command)
        elif "open file manager" in command:
            file_manager = handle_file_system.FileManagerHandler()
            result = file_manager.process_command(command)
        elif "check my system for vulnerabilities" in command:
            result = self.system_health_handler.check_vulnerabilities()
        elif "check my system is safe" in command:
            result = self.system_health_handler.check_system_safety()
        elif "make port scanning for my system" in command:
            result = self.system_health_handler.perform_port_scan()
        elif "show devices connected to my network" in command:
            result = self.system_health_handler.list_connected_devices()
        else:
            result = "Sorry, I did not understand that command."

        self.update_status_text(result)

    def update_status_text(self, text):
        """Update status with text."""
        print(text)

    def reset_mic_button(self):
        """Reset mic button state after listening."""
        self.mic_button.config(image=self.mic_image)
        self.is_listening = False

    def toggle_termux_mode(self):
        """Enable or disable Termux mode."""
        self.termux_mode_enabled = not self.termux_mode_enabled
        icon = self.toggle_icon if self.termux_mode_enabled else self.toggle_off_icon
        self.toggle_button.config(image=icon)

    def close_window(self):
        """Close the window."""
        self.root.quit()


if __name__ == "__main__":
    window = SlideUpWindow()
    window.root.mainloop()
