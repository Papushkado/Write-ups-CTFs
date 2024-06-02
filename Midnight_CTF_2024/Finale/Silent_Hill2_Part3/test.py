from PIL import Image
import codecs

def rot13(text):
    return codecs.encode(text, 'rot_13')

def bin_to_text(bin_data):
    chars = [bin_data[i:i+8] for i in range(0, len(bin_data), 8)]
    text = ''.join(chr(int(char, 2)) for char in chars)
    return text

def extract_message_from_image(image_path):
    image = Image.open(image_path)
    pixels = list(image.getdata())
    
    bin_message = ''
    for pixel in pixels:
        r, g, b = pixel
        bin_message += str(b & 1)
    
    # Split the binary string into bytes and look for the end marker
    #end_marker = '00000000'
    #if end_marker in bin_message:
        #bin_message = bin_message[:bin_message.index(end_marker)]
    
    # Convert binary to text and apply ROT13
    extracted_message = bin_to_text(bin_message)
    original_message = rot13(extracted_message)
    
    return original_message

# Usage example
image_path = 'This_is_the_end_or_no.png'
hidden_message = extract_message_from_image(image_path)
print(f"Message caché : {hidden_message}")
