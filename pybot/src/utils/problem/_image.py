import math
from PIL import Image, ImageDraw, ImageFont 
from nonebot import get_driver
from ..other._eval import timeit
from ._text import break_sentence_to_words,is_chinese_char
from ._text import SPECIAL_HEADERS, BOLD_PATTERN
config = get_driver().config
# Define the paths in .env file. If not defined, use the default paths.
FONT_PATHS = {
    'en': {
        'regular': "./src/data/fonts/en/Urbanist-Regular.ttf",
        'bold': "./src/data/fonts/en/Urbanist-Bold.ttf",
        'title': "./src/data/fonts/en/Urbanist-Black.ttf",
        'mono': "./src/data/fonts/en/NotoSansMono-Regular.ttf"
    },
    'cn': {
        'regular': "./src/data/fonts/cn/NotoSansSC-Regular.ttf",
        'bold': "./src/data/fonts/cn/NotoSansSC-Bold.ttf",
        'title': "./src/data/fonts/cn/NotoSansSC-Black.ttf",
        'mono': "./src/data/fonts/cn/NotoSansSC-Regular.ttf"
    }
}
THEME_COLORS = {
    "font":{
        "header": (15, 23, 42),
        "content": (30, 41, 59),
        "code": (248, 250, 252)
    },
    "background": {
        "header": (241, 245, 249),
        "content": (241, 245, 249),
        "code": (71, 85, 105)
    },
    "border": {
        "default": (100, 116, 139),
        "code": (51, 65, 85)
    }
}
#@timeit
def create_image_from_text(title: str, content: str, language='en',max_width=800, max_height=1000, font_size=20):
    regular_font = ImageFont.truetype(FONT_PATHS[language]["regular"], font_size)
    bold_font = ImageFont.truetype(FONT_PATHS[language]["bold"], font_size)
    title_font = ImageFont.truetype(FONT_PATHS[language]["title"], font_size + 15)
    code_font = ImageFont.truetype(FONT_PATHS[language]["mono"], font_size - 2)  # Smaller monospace font for code
    title = title.upper()
    # Calculate the width of the title text using font.getbbox()
    title_bbox = title_font.getbbox(title)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]
    # if title width is exceeding max_width, set max_width to title_width
    if title_width > max_width:
        max_width = math.ceil(title_width) + 40
    # Calculate the height of image based on content
    lines = image_text_wrap(content, regular_font, max_width - 40, language)
    # not using line_height here because there are extra spaces between lines
    content_height = math.ceil(len(lines) * (font_size + 5) + title_height)
    max_height = content_height + 100

    # Create a new image with a white background
    img = Image.new('RGB', (max_width, max_height), color='white')
    d = ImageDraw.Draw(img)
    
    # Calculate the x-coordinate to center the title
    title_x = (max_width - title_width) // 2
    
    # Draw a decorative background
    d.rectangle([0, 0, max_width, max_height], fill=THEME_COLORS["background"]["content"])
    # Draw a decorative header background
    d.rectangle([0, 0, max_width, title_height + 60], fill=THEME_COLORS["background"]["header"])
    # Draw the centered title with a slight shadow effect
    d.text((title_x, 20), title, font=title_font, fill=THEME_COLORS["font"]["header"])
    
    y_text = 80
    in_code_block = False
    code_blocks = []
    for line in lines:
        # toggle code block
        if "```" in line:
            if not in_code_block:
                # Start of code block
                code_blocks.append([y_text, '']) # Add 3 pixels for prevent overlap
            else:
                # End of code block
                code_blocks[-1][1] = y_text + 3
            in_code_block = not in_code_block
        y_text += font_size + 5
    # now draw the code blocks first before drawing the text to prevent overlap
    for start, end in code_blocks:
        d.rounded_rectangle([15, start-5, max_width-15, end+5], radius=10, fill=THEME_COLORS["background"]["code"], outline=THEME_COLORS["border"]["code"])
    # reset y_text
    y_text = 80
    in_code_block = False
    for line in lines:
        # toggle code block
        if "```" in line:
            line = line.replace("```", "")
            in_code_block = not in_code_block
        font_fill = THEME_COLORS["font"]["content"] if not in_code_block else THEME_COLORS["font"]["code"]
        curr_font = code_font if in_code_block else regular_font
        if BOLD_PATTERN[language].match(line):
            d.text((20, y_text), line, font=bold_font, fill=font_fill)
        else:
            d.text((20, y_text), line, font=curr_font, fill=font_fill)
        y_text += font_size + 5
    #img = img.crop((0, 0, max_width, y_text + 30))
    d.rounded_rectangle([0, 0, max_width-1, max_height-1], radius=10, outline=THEME_COLORS["border"]["default"], width=3)
    
    return img

def image_text_wrap(text: str, font: ImageFont.FreeTypeFont, max_width: int, language='en') -> list:
    max_width -= 40  # Add some padding
    lines = []
    # Split the text into paragraphs
    # text = BOLD_PATTERN[language].sub(r'\1\n', text)
    paragraphs = text.split('\n')
    is_code_block = False
    for paragraph in paragraphs:
        # if paragraph is 'Example {number}:' or 'Explanation:' or ..., leading_spaces = 0
        leading_spaces = 0 if SPECIAL_HEADERS[language].match(paragraph) else 2
        words_separate_space = 0 if language == 'cn' else font.getbbox(' ')[2]
        #paragraph = paragraph.strip()
        words = break_sentence_to_words(paragraph, language)
        current_line = []
        current_width = 0
        # Add a blank line between paragraphs for special headers
        if leading_spaces == 0:
            lines.append('')
        # Add a blank line before first ``` and after last ```
        if "```" in paragraph:
            # is start, then add at beginning
            if not is_code_block:
                lines.append('')
        # Add leading spaces to the first word
        if leading_spaces and words:
            words[0] = ' ' * leading_spaces + words[0]
        for word in words:
            word_width = font.getbbox(word)[2]
            
            if current_width + word_width <= max_width:
                if current_line:
                    # Check if we need to add space between the last word and this word
                    last_word = current_line[-1]
                    if is_chinese_char(last_word[-1]) and is_chinese_char(word[0]):
                        # Both are Chinese characters, don't add space
                        current_line.append(word)
                    else:
                        # Add space for non-Chinese characters
                        current_line.append(' ' + word)
                        current_width += words_separate_space
                else:
                    # First word in the line
                    current_line.append(word)
                
                current_width += word_width
            else:
                # Line is full, join the current line and start a new one
                current_line_text = ''.join(current_line)
                lines.append(current_line_text)
                current_line = [word]
                current_width = word_width

        if current_line:
            current_line_text = ''.join(current_line)
            lines.append(current_line_text)
        # check again for code block
        if "```" in paragraph:
            # is end, then add at end
            if is_code_block:
                lines.append('')
            is_code_block = not is_code_block
    return lines



def unit_test():
    title = "Two Sum"
    content = "Given an array of integers, return indices of the two numbers such that they add up to a specific target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element.\n\nExample 1:\n\nInput: nums = [2, 7, 11, 15], target = 9\nOutput: [0, 1]\nExplanation: Because nums[0] + nums[1]..." *10
    img = create_image_from_text(title, content)
    img.save("two_sum.png")