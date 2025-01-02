import pyttsx3

class SpeakModule:
    def __init__(self):
        """Initialize text-to-speech engine"""
        self.engine = pyttsx3.init()
        # Optional: Configure voice properties
        self.engine.setProperty('rate', 150)    # Speaking rate
        self.engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
        
        # Get available voices and set a female voice if available
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "female" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

    def speak(self, text):
        """
        Convert text to speech
        Args:
            text (str): Text to be converted to speech
        """
        try:
            print(f"Speaking: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Speech error: {e}")
            
    def update_voice(self, gender="female", rate=150, volume=1.0):
        """
        Update voice properties
        Args:
            gender (str): Preferred voice gender ("male" or "female")
            rate (int): Speaking rate (words per minute)
            volume (float): Volume level (0.0 to 1.0)
        """
        try:
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if gender.lower() in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            print(f"Error updating voice properties: {e}")

# Create a global instance
speaker = SpeakModule()

# Function to be imported and used in other files
def speak(text):
    """
    Global speak function to be used in other files
    Args:
        text (str): Text to be converted to speech
    """
    speaker.speak(text)

if __name__ == "__main__":
    # Test the speaking functionality
    speak("Speech module initialized and ready to use")