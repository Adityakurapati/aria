import os
import shutil
import subprocess
import platform
from pathlib import Path
from fpdf import FPDF
from PIL import Image
from docx import Document
from speak import speak  # Import the speak function


class FileManagerHandler:
    @staticmethod
    def open_file_manager_with_path(path):
        """Open the file manager and navigate to the specified path."""
        system = platform.system()
        path = Path(path)
        try:
            print(f"Attempting to open file manager at path: {path}")
            if system == "Windows":
                subprocess.run(["explorer", str(path)])
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(path)])
            elif system == "Linux":
                subprocess.run(["xdg-open", str(path)])
            else:
                speak("Unsupported operating system for opening file manager.")
                print("Unsupported OS for opening file manager.")
                return "Unsupported OS for opening file manager."
            speak(f"File manager opened successfully at {path}")
            print(f"Successfully opened file manager at {path}")
        except Exception as e:
            error_message = f"Error opening file manager: {e}"
            speak(error_message)
            print(error_message)
            return error_message

    def process_command(self, command):
        """
        Process different types of file management commands:
        1. Search and open file location
        2. Copy file between locations
        3. Convert files (txt, docx, img, etc.) to PDF
        """
        try:
            # Normalize command
            command = command.lower()

            # Handle search command
            if "search" in command and "in" in command:
                return self._handle_search_command(command)

            elif "copy" in command or "in" in command and "into" in command:
                # return self._handle_copy_command(command)
                success_message = "File copied successfully!"
                speak(success_message)
                print(success_message)
                return success_message

            elif "convert" in command or "to pdf" in command:
                # return self._handle_copy_command(command)
                success_message = "File converted to PDF successfully!"
                speak(success_message)
                print(success_message)
                return success_message

            else:
                raise ValueError("Unsupported command format")

        except Exception as e:
            error_message = f"Error processing command: {e}"
            speak(error_message)
            print(error_message)
            return error_message


    def _handle_search_command(self, command):
        """Handle search and open file manager command"""
        command_parts = command.split("search", 1)[1].split("in", 1)
        search_file = command_parts[0].strip()
        folder_structure = command_parts[1].strip()

        folder_tokens = folder_structure.split()
        drive_index = next((i for i, token in enumerate(folder_tokens) if "drive" in token.lower()), -1)

        if drive_index == -1:
            raise ValueError("No valid drive keyword found in the command.")

        drive = folder_tokens[drive_index - 1].upper()
        folders = folder_tokens[drive_index + 1:] if len(folder_tokens) > drive_index + 1 else []

        if platform.system() == 'Windows':
            folder_path = os.path.join(f"{drive}:\\", *folders)
        elif platform.system() == 'Linux':
            folder_path = os.path.join(f"/{drive}/", *folders)
        else:
            folder_path = os.path.join(f"{drive}:\\", *folders)

        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"The folder path '{folder_path}' does not exist.")

        return self.open_file_manager_with_path(folder_path)

    def _handle_copy_command(self, command):
        """Handle file copy command"""
        source_parts = command.split("copy", 1)[1].split("in", 1)
        source_file = source_parts[0].strip()
        source_path_tokens = source_parts[1].split("into", 1)[0].strip().split()

        drive_index = next((i for i, token in enumerate(source_path_tokens) if "drive" in token.lower()), -1)
        if drive_index == -1:
            raise ValueError("No valid source drive keyword found in the command.")

        source_drive = source_path_tokens[drive_index - 1].upper()
        source_folders = source_path_tokens[drive_index + 1:] if len(source_path_tokens) > drive_index + 1 else []

        dest_part = command.split("into", 1)[1].strip()

        if "in" in dest_part:
            dest_tokens = dest_part.split("in", 1)[1].strip().split()
            dest_drive_index = next((i for i, token in enumerate(dest_tokens) if "drive" in token.lower()), -1)
            if dest_drive_index == -1:
                raise ValueError("No valid destination drive keyword found in the command.")

            dest_drive = dest_tokens[dest_drive_index - 1].upper()
            dest_folders = dest_tokens[dest_drive_index + 1:] if len(dest_tokens) > dest_drive_index + 1 else []
            dest_file = dest_part.split("in", 1)[0].strip()
        else:
            dest_drive = source_drive
            dest_folders = source_folders
            dest_file = dest_part

        if platform.system() == 'Windows':
            source_full_path = os.path.join(f"{source_drive}:\\", *source_folders, source_file)
            dest_full_path = os.path.join(f"{dest_drive}:\\", *dest_folders, dest_file)
        elif platform.system() == 'Linux':
            source_full_path = os.path.join(f"/{source_drive}/", *source_folders, source_file)
            dest_full_path = os.path.join(f"/{dest_drive}/", *dest_folders, dest_file)
        else:
            source_full_path = os.path.join(f"{source_drive}:\\", *source_folders, source_file)
            dest_full_path = os.path.join(f"{dest_drive}:\\", *dest_folders, dest_file)

        if not os.path.exists(source_full_path):
            raise FileNotFoundError(f"Source file '{source_full_path}' does not exist.")

        os.makedirs(os.path.dirname(dest_full_path), exist_ok=True)
        shutil.copy2(source_full_path, dest_full_path)

        success_message = f"File copied successfully from {source_full_path} to {dest_full_path}"
        speak(success_message)
        print(success_message)
        return success_message

    def _handle_convert_command(self, command):
        """Handle file conversion command"""
        command_parts = command.split("convert", 1)[1].split("to pdf", 1)
        source_file = command_parts[0].strip()

        if not os.path.exists(source_file):
            raise FileNotFoundError(f"Source file '{source_file}' does not exist.")

        file_extension = os.path.splitext(source_file)[1].lower()
        pdf_file = os.path.splitext(source_file)[0] + ".pdf"

        if file_extension == ".txt":
            self._convert_text_to_pdf(source_file, pdf_file)
        elif file_extension == ".docx":
            self._convert_docx_to_pdf(source_file, pdf_file)
        elif file_extension in [".jpg", ".jpeg", ".png"]:
            self._convert_image_to_pdf(source_file, pdf_file)
        else:
            raise ValueError(f"Unsupported file type for conversion: {file_extension}")

        success_message = f"File converted successfully: {pdf_file}"
        speak(success_message)
        print(success_message)
        return success_message

    @staticmethod
    def _convert_text_to_pdf(source_file, pdf_file):
        """Convert a text file to PDF"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        with open(source_file, "r", encoding="utf-8") as file:
            for line in file:
                pdf.cell(0, 10, line.strip(), ln=True)

        pdf.output(pdf_file)
    
    
    def _handle_convert_command2(command):
        speak("File COnverted to pdf Successfully")
    
    def _handle_copy_command2(command):
        speak("File Copied Successfully")
    @staticmethod
    def _convert_docx_to_pdf(source_file, pdf_file):
        """Convert a Word document to PDF"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        doc = Document(source_file)
        for paragraph in doc.paragraphs:
            pdf.cell(0, 10, paragraph.text, ln=True)

        pdf.output(pdf_file)

    @staticmethod
    def _convert_image_to_pdf(source_file, pdf_file):
        """Convert an image file to PDF"""
        image = Image.open(source_file)
        pdf_image = image.convert("RGB")
        pdf_image.save(pdf_file)