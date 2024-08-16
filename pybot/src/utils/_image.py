from PIL import Image, ImageDraw, ImageFont
import textwrap
import random
import re
FONT_PATH = "/var/www/leetcode_bot/pybot/src/data/fonts/Urbanist-Regular.ttf"#"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD_FONT_PATH = "/var/www/leetcode_bot/pybot/src/data/fonts/Urbanist-Bold.ttf"#"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TITLE_FONT_PATH = "/var/www/leetcode_bot/pybot/src/data/fonts/Urbanist-Black.ttf"#"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def create_image_from_text(title, content, max_width=800, max_height=1000, font_size=20):
    font = ImageFont.truetype(FONT_PATH, font_size)
    bold_font = ImageFont.truetype(BOLD_FONT_PATH, font_size)
    title_font = ImageFont.truetype(TITLE_FONT_PATH, font_size + 15)

    title = title.upper()    
    # Calculate the width of the title text using font.getbbox()
    title_bbox = title_font.getbbox(title)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]
    # if title width is exceeding max_width, set max_width to title_width
    if title_width > max_width:
        max_width = title_width + 40
    # Calculate the height of image based on content
    lines = improved_wrap(content, font, max_width - 40)
    # not using line_height here because there are extra spaces between lines
    content_height = len(lines) * (font_size + 5) + title_height
    max_height = content_height + 100

    # Create a new image with a white background
    img = Image.new('RGB', (max_width, max_height), color='white')
    d = ImageDraw.Draw(img)
    
    # Calculate the x-coordinate to center the title
    title_x = (max_width - title_width) // 2
    
    # Draw a decorative header
    d.rectangle([0, 0, max_width, title_height + 20], fill=(255, 255, 255))
    
    # Draw the centered title with a slight shadow effect
    d.text((title_x, 20), title, font=title_font, fill=(0, 0, 0))
    
    y_text = 80
    for line in lines:
        ## if line is 'Example {number}:' or 'Explanation:' or 'Constraints:', make it bold
        if re.match(r'Example \d+:|Explanation:|Constraints:', line):
            d.text((20, y_text), line, font=bold_font, fill=(0, 0, 0))
        else:
            d.text((20, y_text), line, font=font, fill=(0, 0, 0))
        y_text += font_size + 5

    #img = img.crop((0, 0, max_width, y_text + 30))
    d.rectangle([0, 0, max_width-1, max_height-1], outline=(150, 150, 200))
    
    return img

def improved_wrap(text, font, max_width):
    lines = []
    # for 'Example {number}:' or 'Explanation:' or 'Constraints:', add \n to the end
    text = re.sub(r'(Example \d+:|Explanation:|Constraints:)', r'\1\n', text)
    paragraphs = text.split('\n')

    for i, paragraph in enumerate(paragraphs):
        # if paragraph is 'Example {number}:' or 'Explanation:' or 'Constraints:', leading_spaces = 0
        leading_spaces = 0 if re.match(r'Example \d+:|Explanation:|Constraints:', paragraph) else 2
        paragraph = paragraph.strip()
        words = paragraph.split()
        current_line = []
        current_width = 0
        # Add a blank line between paragraphs
        if i < len(paragraphs) - 1 and leading_spaces == 0:
            lines.append('')
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

def unit_test():
    title = "Two Sum"
    content = "Given an array of integers, return indices of the two numbers such that they add up to a specific target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element.\n\nExample 1:\n\nInput: nums = [2, 7, 11, 15], target = 9\nOutput: [0, 1]\nExplanation: Because nums[0] + nums[1]..." *10
    img = create_image_from_text(title, content)
    img.save("two_sum.png")