from nonebot import on_command, logger
from nonebot.adapters.qq import Message, MessageEvent, MessageSegment
from nonebot.params import CommandArg
from io import BytesIO
import random
import datetime
from ..utils import fetch_problem, fetch_problems_total_number, get_problem_body, create_image_from_text
from ..utils import REDIRECT_BASE_URL, RANDOM_APPELLATION, RANDOM_ENDINGS

problem = on_command("今天做什么", aliases={"随机","random","problem","题目","速速端上来罢"},priority=2,block=True)
# data json is in ../data/leetcode_data.json
TOTAL_PROBLEMS = fetch_problems_total_number()
last_updated = datetime.date.today()
def randomly_choose_language(p=0.05):
    return 'cn' if random.random() > p else 'en'
def generate_welcome_message(language:str, question_number:int, short_url:str, user_indicate_number:bool, user_indicate_language:bool) -> str:
    text = ""
    if user_indicate_number:
        text += f"这是你要的第{question_number}题哦~"
    else:
        text += f"那就随机给你挑一道题目哦，题号是{question_number}~"

    if language == 'en' and not user_indicate_language:
        text += "\n话说回来，要不要试试英文版题目？给你看看哦~"
    random_ending = random.choice(RANDOM_ENDINGS).format(appellation=random.choice(RANDOM_APPELLATION))
    text += f"\n{random_ending}\n{short_url}"
    return text
@problem.handle()
async def get_problem(event: MessageEvent, args:Message = CommandArg()):
    global last_updated, TOTAL_PROBLEMS
    user_query = event.get_plaintext()
    if user_query[0] == '/':
        user_query = user_query[1:]
    if user_query.startswith("problem") or user_query.startswith("random"):
        user_indicate_language = True
        language = 'en'
    else:
        user_indicate_language = False
        language = randomly_choose_language()
    # if user indicated a problem number, then fetch that problem
    # if not, fetch a random problem
    question_number = args.extract_plain_text()
    if question_number:
        try:
            question_number = int(question_number)
            if last_updated != datetime.date.today():
                TOTAL_PROBLEMS = fetch_problems_total_number()
                if TOTAL_PROBLEMS is None:
                    logger.warning("Failed to fetch total problems number, using default value")
                else:
                    last_updated = datetime.date.today()
            if question_number < 1 or question_number > TOTAL_PROBLEMS:
                raise ValueError
        except ValueError:
            await problem.send(f"诶，得输入一个1到{TOTAL_PROBLEMS}之间的数字呢~")
            return
    data = fetch_problem(question_number)
    if data is not None:
        title, content = get_problem_body(data, language)
        title_slug = data['titleSlug']
        short_url = f"{REDIRECT_BASE_URL}/problems/{title_slug}"
        
        img_buffer = BytesIO()
        # Create image from text
        img = create_image_from_text(title, content, language)
        img.save(img_buffer, format="PNG")
        text = generate_welcome_message(language, data['questionFrontendId'], short_url, bool(question_number),user_indicate_language)
        msg = Message([MessageSegment.text(text), MessageSegment.file_image(img_buffer.getvalue())])
        # Send the image
        await problem.send(msg)
    else:
        logger.error(f"Failed to fetch problem {question_number} because of network error")
        await problem.send("哎哟，网卡了，等下再试试吧~")
