import pytesseract
from PIL import Image

# Optional: Set path to Tesseract if not in system PATH (Mac Homebrew example)
# pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

# Image file path
image_path = "/Users/garvit/Desktop/Screenshot 2025-07-31 at 2.48.01 PM.png"

# Output text file path
output_file_path = "/Users/garvit/Desktop/extracted_text.txt"

# Open the image using Pillow
try:
    img = Image.open(image_path)
except FileNotFoundError:
    print(f"Error: Image file not found at {image_path}")
    exit()

# Extract text using Tesseract OCR
text = pytesseract.image_to_string(img)

# Print extracted text to console
print("Extracted Text:\n")
print(text)

# Save the extracted text to a file
try:
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"\nText successfully extracted and saved to: {output_file_path}")
except IOError:
    print(f"Error: Could not write to file {output_file_path}")
