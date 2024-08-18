from html import unescape
import re
import json
# texts

RANDOM_APPELLATION = ["大哥哥", "小哥哥", "大姐姐", "小姐姐", "大佬", "小可爱", "大可爱", "小宝贝", "大宝贝", "小天使", "大天使", "小可爱", "大可爱", "小宝贝", "大宝贝", "小天使", "大天使"]
RANDOM_ENDINGS = ["加油啊，{appellation}~ ^_^", "加油吧，{appellation}。。", "⭐加油，{appellation}！⭐", "加油哦，{appellation}？❤"]

# Compile regex pattern only once
TAG_PATTERN = re.compile('<[^<]+?>')
# Global compiled patterns
SPECIAL_HEADERS = {
    'en': re.compile(r'^(Example\s*\d*:|Constraints:|Follow-up:|Note:)'),
    'cn': re.compile(r'^(示例\s*\d*：|提示：|后续问题：|说明：)')
}
BOLD_PATTERN = {
    'en': re.compile(r'(Example\s*\d*:|Constraints:|Follow-up:|Note:)'),
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

def is_chinese_char(char):
    # This function checks if a character is Chinese
    return '\u4e00' <= char <= '\u9fff' or char in CHINESE_PUNCTUATION
def break_sentence_to_words(text: str, language='en') -> list:
    words = []
    # Check if the line is part of a code block (starts with spaces or tabs)
    if re.match(r'^\s+', text):
        # For code blocks, keep leading spaces only for the first word
        first_word = re.match(r'^\s+\S+', text)
        if first_word:
            # Keep original length of space but format it as " " * n
            space_num = len(first_word.group()) - len(first_word.group().lstrip())
            words.append(' ' * space_num + first_word.group().lstrip())
            remaining_text = text[first_word.end():]
            words.extend(remaining_text.split())
    else:
        # For regular text, split by spaces
        words.extend(text.split())
    if language == 'en':
        return words
    if language == 'cn':
        processed_words = []
        for idx, word in enumerate(words):
            if any('\u4e00' <= char <= '\u9fff' for char in word):
                # If the word contains Chinese characters
                current_word = ''
                for char in word:
                    if '\u4e00' <= char <= '\u9fff':
                        # If it's a Chinese character
                        if current_word:
                            processed_words.append(current_word)
                            current_word = ''
                        processed_words.append(char)
                    else:
                        current_word += char
                if current_word:
                    processed_words.append(current_word)
            else:
                processed_words.append(word)
        return processed_words
    else:
        raise ValueError(f"Invalid language: {language}")
def clean_string(input_string: str, language='en') -> str:
    #print(input_string)
    # gpt send real '\n' instead of \n, so we need to replace it
    #input_string = input_string.replace('\\n', '\n')
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

    