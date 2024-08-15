from PIL import Image, ImageDraw, ImageFont
import textwrap
import random
import re
def create_image_from_text(title, content, max_width=800, font_size=20):
    title = title.upper()
    img = Image.new('RGB', (max_width, 1000), color='white')
    d = ImageDraw.Draw(img)

    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    bold_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size + 15)
    
    # Calculate the width of the title text using font.getbbox()
    title_bbox = title_font.getbbox(title)
    title_width = title_bbox[2] - title_bbox[0]
    
    # Calculate the x-coordinate to center the title
    title_x = (max_width - title_width) // 2
    
    # Draw a decorative header
    d.rectangle([0, 0, max_width, 60], fill=(255, 255, 255))
    
    # Draw the centered title with a slight shadow effect
    d.text((title_x, 20), title, font=title_font, fill=(0, 0, 0))
    
    # The rest of the function remains the same
    lines = improved_wrap(content, font, max_width - 40)
    y_text = 80
    for line in lines:
        ## if line is 'Example {number}:' or 'Explanation:' or 'Constraints:', make it bold
        if re.match(r'Example \d+:|Explanation:|Constraints:', line):
            d.text((20, y_text), line, font=bold_font, fill=(0, 0, 0))
        else:
            d.text((20, y_text), line, font=font, fill=(0, 0, 0))
        y_text += font_size + 5

    img = img.crop((0, 0, max_width, y_text + 30))
    d.rectangle([0, 0, max_width-1, y_text+29], outline=(150, 150, 200))
    
    return img
def improved_wrap(text, font, max_width):
    lines = []
    paragraphs = text.split('\n')

    for i, paragraph in enumerate(paragraphs):
        # if paragraph is 'Example {number}:' or 'Explanation:' or 'Constraints:', leading_spaces = 0
        leading_spaces = 0 if re.match(r'Example \d+:|Explanation:|Constraints:', paragraph) else 2
        paragraph = paragraph.strip()
        words = paragraph.split()
        current_line = []
        current_width = 0
        # Add leading spaces to the first word
        if leading_spaces and words:
            words[0] = ' ' * leading_spaces + words[0]
        for word in words:
            word_width = font.getbbox(word)[2]
            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width + font.getbbox(' ')[2]  # Add space width
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width

        if current_line:
            lines.append(' '.join(current_line))


    return lines