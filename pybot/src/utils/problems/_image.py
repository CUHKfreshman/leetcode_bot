from PIL import Image, ImageDraw, ImageFont
from ._text import break_sentence_to_words, SPECIAL_HEADERS, BOLD_PATTERN
from nonebot import get_driver
config = get_driver().config
# Define the paths in .env file. If not defined, use the default paths.
FONT_PATHS = {
    'en': {
        'regular': "./src/data/fonts/en/Urbanist-Regular.ttf",
        'bold': "./src/data/fonts/en/Urbanist-Bold.ttf",
        'title': "./src/data/fonts/en/Urbanist-Black.ttf"
    },
    'cn': {
        'regular': "./src/data/fonts/cn/NotoSansSC-Regular.ttf",
        'bold': "./src/data/fonts/cn/NotoSansSC-Bold.ttf",
        'title': "./src/data/fonts/cn/NotoSansSC-Black.ttf"
    }
}
def create_image_from_text(title: str, content: str, language='en',max_width=800, max_height=1000, font_size=20):
    regular_font = ImageFont.truetype(FONT_PATHS[language]["regular"], font_size)
    bold_font = ImageFont.truetype(FONT_PATHS[language]["bold"], font_size)
    title_font = ImageFont.truetype(FONT_PATHS[language]["title"], font_size + 15)

    title = title.upper()
    # Calculate the width of the title text using font.getbbox()
    title_bbox = title_font.getbbox(title)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]
    # if title width is exceeding max_width, set max_width to title_width
    if title_width > max_width:
        max_width = title_width + 40
    # Calculate the height of image based on content
    lines = image_text_wrap(content, regular_font, max_width - 40, language)
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
        ## if line is 'Example {number}:' or 'Explanation:' or..., use bold font
        if BOLD_PATTERN[language].match(line):
            d.text((20, y_text), line, font=bold_font, fill=(0, 0, 0))
        else:
            d.text((20, y_text), line, font=regular_font, fill=(0, 0, 0))
        y_text += font_size + 5

    #img = img.crop((0, 0, max_width, y_text + 30))
    d.rectangle([0, 0, max_width-1, max_height-1], outline=(150, 150, 200))
    
    return img

def image_text_wrap(text: str, font: ImageFont.FreeTypeFont, max_width: int, language='en') -> list:
    lines = []
    # Split the text into paragraphs
    # text = BOLD_PATTERN[language].sub(r'\1\n', text)
    paragraphs = text.split('\n')
    for i, paragraph in enumerate(paragraphs):
        # if paragraph is 'Example {number}:' or 'Explanation:' or ..., leading_spaces = 0
        leading_spaces = 0 if SPECIAL_HEADERS[language].match(paragraph) else 2
        words_separate_space = 0 if language == 'cn' else font.getbbox(' ')[2]
        #paragraph = paragraph.strip()
        words = break_sentence_to_words(paragraph, language)
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
                current_width += word_width + words_separate_space  # Add space width
            else:
                current_line_text = ''.join(current_line) if language == 'cn' else ' '.join(current_line)
                lines.append(current_line_text)
                current_line = [word]
                current_width = word_width

        if current_line:
            current_line_text = ''.join(current_line) if language == 'cn' else ' '.join(current_line)
            lines.append(current_line_text)

    return lines

def unit_test():
    title = "Two Sum"
    content = "Given an array of integers, return indices of the two numbers such that they add up to a specific target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element.\n\nExample 1:\n\nInput: nums = [2, 7, 11, 15], target = 9\nOutput: [0, 1]\nExplanation: Because nums[0] + nums[1]..." *10
    img = create_image_from_text(title, content)
    img.save("two_sum.png")