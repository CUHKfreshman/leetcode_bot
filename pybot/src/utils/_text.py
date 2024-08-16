from html import unescape
import re

HTML_TAG_PATTERN = re.compile('<[^<]+?>')
SPECIAL_CHARS_PATTERN = re.compile(r'(<=|>=|<sup>|</sup>)')

def clean_string(input_string):
    # Unescape HTML entities
    input_string = unescape(input_string)
    
    # Remove HTML tags and replace special characters
    cleaned = SPECIAL_CHARS_PATTERN.sub(lambda m: {'<=': '≤', '>=': '≥', '<sup>': '^', '</sup>': ''}[m.group()], 
                                        HTML_TAG_PATTERN.sub('', input_string))
    
    return cleaned