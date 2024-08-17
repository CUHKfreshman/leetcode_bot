from html import unescape
import re
# texts

RANDOM_APPELLATION = ["大哥哥", "小哥哥", "大姐姐", "小姐姐", "大佬", "小可爱", "大可爱", "小宝贝", "大宝贝", "小天使", "大天使", "小可爱", "大可爱", "小宝贝", "大宝贝", "小天使", "大天使"]
RANDOM_ENDINGS = ["加油啊，{appellation}~ ^_^", "加油吧，{appellation}。。", "⭐加油，{appellation}！⭐", "加油哦，{appellation}？❤"]

# Compile regex pattern only once
TAG_PATTERN = re.compile('<[^<]+?>')
# Global compiled patterns
SPECIAL_HEADERS = {
    'en': re.compile(r'^(Example \d+:|Constraints:|Follow-up:|Note:)'),
    'cn': re.compile(r'^(示例\s*\d*：|提示：|后续问题：|说明：)')
}
BOLD_PATTERN = {
    'en': re.compile(r'(Example \d+:|Constraints:|Follow-up:|Note:)'),
    # note that the Chinese pattern is actually different
    # this is because SPECIAL HEADERS is matched before string cleaning, but BOLD_PATTERN is matched after string cleaning
    'cn': re.compile(r'(示例\d*：|提示：|后续问题：|说明：)')
}

# Pre-define replacements
REPLACEMENTS = {
    # this is dealt before tag removal
    'before_tag_removal':{
        '<sup>': '^',
        '<sub>': '_',
        '<li>': '• ',
        '<ul>': '\n',
    },
    'after_tag_removal':{
        '<=': '≤',
        '>=': '≥'
    }
}
CHINESE_PUNCTUATION = '，。、；：？！“”‘’（）【】《》—…'
CHINESE_CHAR_PATTERN = re.compile(r'[\u4e00-\u9fff]+')

def break_sentence_to_words(text: str, language='en') -> list:
    if language == 'en':
        # Split by space
        return text.split()
    # Remove spaces
    text = text.replace(' ', '')
    # Split by chinese characters, 
    # typically we do not split character with punctuation, but we can add it if needed

    # there are also other chars in the text, need to keep them as well
    # For Chinese, we'll process character by character
    words = []
    current_word = ''
    
    for char in text:
        if CHINESE_CHAR_PATTERN.match(char):
            # If it's a Chinese character and we have a current word, add it to words
            if current_word:
                words.append(current_word)
                current_word = ''
            # Add the Chinese character as a separate word
            words.append(char)
        else:
            # For non-Chinese characters, we accumulate them
            current_word += char
    
    # Add any remaining characters in current_word
    if current_word:
        words.append(current_word)
    
    return words

def clean_string(input_string: str, language='en') -> str:
    # Use html.unescape instead of html.parser.unescape
    input_string = unescape(input_string)
    for old, new in REPLACEMENTS['before_tag_removal'].items():
        input_string = input_string.replace(old, new)
    input_string = TAG_PATTERN.sub('', input_string)
    # Use a single pass to replace multiple patterns
    for old, new in REPLACEMENTS['after_tag_removal'].items():
        input_string = input_string.replace(old, new)
    
    if language == 'cn':
        # if punctuation has space before, remove it
        for p in CHINESE_PUNCTUATION:
            input_string = input_string.replace(f' {p}', p)
    return input_string


def get_problem_body(data: dict, language='en') -> tuple:

    if language == 'cn':
        title = data['translatedTitle']
        content = clean_string(data['translatedContent'], language='cn')
    else:
        title = data['title']
        content = clean_string(data['content'], language='en')
    return title, content