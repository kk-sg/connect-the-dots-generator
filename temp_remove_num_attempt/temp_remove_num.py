from PIL import Image, ImageDraw
import pytesseract

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'../../../usr/bin/tesseract'  # Update this path

# Load the image
image_path = 'input_image.jpg'
image = Image.open(image_path)

# Use OCR to get the text
numbers = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

# Create a drawing context
draw = ImageDraw.Draw(image)

# Extract bounding box information for recognized numbers
for i in range(len(numbers['text'])):
    text = numbers['text'][i]
    if text.isdigit() and int(text) > 0:
        (x, y, w, h) = (numbers['left'][i], numbers['top']
                        [i], numbers['width'][i], numbers['height'][i])
        # Draw a white rectangle over the number
        draw.rectangle([(x, y), (x + w, y + h)], fill="white")

# Save the modified image
image.save('output_image.jpg')
