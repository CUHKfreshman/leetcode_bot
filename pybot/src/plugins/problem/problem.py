from nonebot import on_command, logger
from nonebot.exception import FinishedException
from nonebot.adapters.qq import Message, MessageEvent, MessageSegment
from nonebot.params import CommandArg
from io import BytesIO
import sys
import random
import datetime
from ...utils import fetch_problem, fetch_problems_total_number, get_problem_body, create_image_from_text
from ...utils import REDIRECT_BASE_URL, RANDOM_APPELLATION, RANDOM_ENDINGS
from ...utils import db_manager
problem = on_command("今天做什么", aliases={"随机","random","problem","题目","速速端上来罢"},priority=2,block=True, force_whitespace=True)
# data json is in ../data/leetcode_data.json
TOTAL_PROBLEMS = fetch_problems_total_number()
last_updated = datetime.date.today()
def randomly_choose_language(p=0.01):
    return 'cn' if random.random() > p else 'en'
def randomly_choose_problem_number(language:str) -> tuple[int, bool, bool]:
    while True:
        question_frontend_id = random.randint(1, TOTAL_PROBLEMS)
        is_exist, is_paid_only = db_manager.image_exists_and_is_paid_only(question_frontend_id, language)
        if not is_paid_only:
            break
    return question_frontend_id, is_exist, is_paid_only
def generate_welcome_message(language:str, question_frontend_id:int, short_url:str, user_indicate_number:bool, user_indicate_language:bool) -> str:
    text = ""
    if user_indicate_number:
        text += f"这是你要的第{question_frontend_id}题哦~"
    else:
        text += f"那就随机给你挑一道题目哦，题号是{question_frontend_id}~"

    if language == 'en' and not user_indicate_language:
        text += "\n话说回来，要不要试试英文版题目？给你看看哦~"
    random_ending = random.choice(RANDOM_ENDINGS).format(appellation=random.choice(RANDOM_APPELLATION))
    text += f"\n{random_ending}\n{short_url}"
    return text
@problem.handle()
async def get_problem(event: MessageEvent, args:Message = CommandArg()):
    global last_updated, TOTAL_PROBLEMS
    question_frontend_id = None
    try:
        user_query = event.get_plaintext()
        if "problem" in user_query or "random" in user_query:
            user_indicate_language = True
            language = 'en'
        else:
            user_indicate_language = False
            language = randomly_choose_language()
        # if user indicated a problem number, then fetch that problem
        # if not, fetch a random problem
        question_frontend_id = args.extract_plain_text()
        question_frontend_id = int(question_frontend_id.strip()) if question_frontend_id else None
        if question_frontend_id:
            user_indicate_number = True
            # Check if the image exists, early stop if it does
            if last_updated != datetime.date.today():
                TOTAL_PROBLEMS = fetch_problems_total_number()
                last_updated = datetime.date.today()
            if question_frontend_id < 1 or question_frontend_id > TOTAL_PROBLEMS:
                raise ValueError(f"Invalid question number {question_frontend_id}")
            is_exist, is_paid_only = db_manager.image_exists_and_is_paid_only(question_frontend_id, language)
            if is_paid_only:
                await problem.finish("嘛，好像碰到了付费题目呢，换一道试试吧~")
        else:
            user_indicate_number = False
            question_frontend_id, is_exist, is_paid_only = randomly_choose_problem_number(language)
            # if user didn't indicate a number, then fetch a random number which is not paid only
        # if image exists and is not paid only, then read & send the image
        if is_exist and not is_paid_only:
            img, title_slug = db_manager.read_image_and_slug(question_frontend_id, language)
            text = generate_welcome_message(language, question_frontend_id, f"{REDIRECT_BASE_URL}/problems/{title_slug}", user_indicate_number, user_indicate_language)
            msg = Message([MessageSegment.text(text), MessageSegment.file_image(img.getvalue())])
            await problem.finish(msg)
        else:
            data = fetch_problem(question_frontend_id)
            #logger.debug(f"Data fetched from node server: {data}")
            if data is not None:
                is_paid_only = data['isPaidOnly']
                title, content = get_problem_body(data, language)
                title_slug = data['titleSlug']
                short_url = f"{REDIRECT_BASE_URL}/problems/{title_slug}"
                img_buffer = BytesIO()
                # Create image from text
                img = create_image_from_text(title, content, language)
                img.save(img_buffer, format="PNG")
                text = generate_welcome_message(language, data['questionFrontendId'], short_url, user_indicate_number, user_indicate_language)
                msg = Message([MessageSegment.text(text), MessageSegment.file_image(img_buffer.getvalue())])
                # Send the image
                await problem.send(msg)
                # Store the image
                db_manager.store_image(question_frontend_id, language, img_buffer, title_slug, is_paid_only)
    except FinishedException:
        logger.debug(f"Problem request finished.")
    except ValueError as e:
        logger.error(f"Failed to fetch problem {question_frontend_id} due to {e}")
        await problem.send(f"诶，得输入一个1到{TOTAL_PROBLEMS}之间的数字呢~")
    except Exception as e:
        logger.error(f"Failed to fetch problem {question_frontend_id} due to {e}")
        # get trace
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error(f"Exception: {e}, exc_type: {exc_type}, exc_value: {exc_value}, at line: {exc_traceback.tb_lineno if exc_traceback else 0}")
        await problem.send("哎哟，网卡了，等下再试试吧~")
