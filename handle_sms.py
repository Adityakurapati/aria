import vonage
import re
from speak import speak  # Import the speak function from the speak.py module

# Configuration for Vonage API
VONAGE_API_KEY = 'e0e01efd'
VONAGE_API_SECRET = 'klP3b1gpcuDrxsBE'
VONAGE_BRAND_NAME = 'Aria'

# Map of names to phone numbers
numbers_map = {
    "aditya": "7507546319",
    "namrata": "9325410468"
}

class SMSHandler:
    def __init__(self):
        # Initialize the Vonage client
        self.client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
        self.sms = vonage.Sms(self.client)
        print("Initialized Vonage SMS client.")

    def send_sms(self, to, text):
        """Send SMS to a recipient and speak out the message."""
        print(f"Preparing to send SMS to: {to}")
        try:
            # Send the SMS
            response = self.sms.send_message({
                "from": VONAGE_BRAND_NAME,
                "to": to,
                "text": text
            })
            print(f"Response received: {response}")

            if response["messages"][0]["status"] == "0":
                log_message = f"SMS sent successfully to {to}"
                print(log_message)
                speak(log_message)  # Speak out the success message
                return log_message
            else:
                error = response["messages"][0]["error-text"]
                log_message = f"Failed to send SMS to {to}: {error}"
                print(log_message)
                speak(log_message)  # Speak out the failure message
                return log_message
        except Exception as e:
            error_message = f"Error sending SMS: {str(e)}"
            print(error_message)
            speak(error_message)  # Speak out the error message
            return error_message

    def parse_and_send_sms(self, command):
        """Parse a command and send SMS based on it, also speak out the result."""
        print(f"Parsing command: {command}")
        match = re.search(r"send sms (.+?) to (\w+)", command)
        if match:
            message = match.group(1).strip()
            name_or_number = match.group(2).strip()
            print(f"Extracted message: '{message}' and recipient: '{name_or_number}'")
            
            # Resolve phone number from the name or use provided phone number directly
            phone_number = numbers_map.get(name_or_number.lower(), name_or_number)
            print(f"Resolved phone number: {phone_number}")
            
            # Speak the parsed message and recipient
            speak(f"Sending message: {message} to {name_or_number}")
            
            return self.send_sms(phone_number, message)
        else:
            error_message = "Invalid SMS command format. Use 'send sms <message> to <name or phone_number>'."
            print(error_message)
            speak(error_message)  # Speak out the error message
            return error_message

# Example usage
if __name__ == "__main__":
    handler = SMSHandler()
    command = "send sms Hello! How are you? to aditya"
    print(handler.parse_and_send_sms(command))
