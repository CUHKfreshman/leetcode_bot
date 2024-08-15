from html import unescape
import re
def clean_string(input_string):
    # unescape HTML entities
    input_string = unescape(input_string)
    # Remove HTML tags
    cleaned = re.sub('<[^<]+?>', '', input_string)
    # special case: <= and >=
    cleaned = cleaned.replace('<=', '≤').replace('>=', '≥')
    #print(cleaned)
    # Strip leading/trailing whitespace
    #cleaned = cleaned.strip()
    
    return cleaned