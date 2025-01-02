import os
import pyttsx3

class SystemHealthHandler:
    def __init__(self):
        self.target_ip = "192.168.213.1"  # Default target IP for testing; replace with user input or dynamic values
        self.engine = pyttsx3.init()  # Initialize the TTS engine
        self.engine.setProperty('rate', 150)  # Set speaking rate
        self.engine.setProperty('voice', self.engine.getProperty('voices')[0].id)  # Set voice (optional)

    def speak(self, text):
        """Speak the given text using pyttsx3."""
        self.engine.say(text)
        self.engine.runAndWait()

    def run_nmap_command(self, command):
        """Open the command prompt and execute the given Nmap command."""
        try:
            print(f"Executing Nmap command in the command prompt: {command}")
            os.system(f"start cmd /k {command}")
            result_message = "Command executed successfully. Check the command prompt for results."
            self.speak(result_message)  # Speak the success message
            return result_message
        except Exception as e:
            error_message = f"Error while running Nmap command: {e}"
            self.speak(error_message)  # Speak the error message
            return error_message

    def check_vulnerabilities(self):
        """Run Nmap vulnerability scan."""
        command = f"nmap --script vuln {self.target_ip}"
        self.speak("Starting vulnerability scan. Please wait.")
        return self.run_nmap_command(command)

    def check_system_safety(self):
        """Run a basic Nmap safety check (port scanning)."""
        command = f"nmap {self.target_ip}"
        self.speak("Starting system safety check. Please wait.")
        return self.run_nmap_command(command)

    def perform_port_scan(self):
        """Run Nmap with additional options for detailed port scanning."""
        command = f"nmap -sV -O {self.target_ip}"
        self.speak("Starting detailed port scan. Please wait.")
        return self.run_nmap_command(command)
