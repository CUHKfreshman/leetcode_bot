from nonebot import on_command, logger
from nonebot.adapters.qq import Message, MessageEvent, MessageSegment
from nonebot.params import CommandArg
from io import BytesIO
import random
import datetime
from ...utils import create_image_from_text, fetch_daily_challenge, get_problem_body
from ...utils import REDIRECT_BASE_URL, RANDOM_ENDINGS, RANDOM_APPELLATION
dailyChallenge = on_command("每日挑战", aliases={"每日大赛","daily", "daily-challenge"},priority=1,block=True, force_whitespace=True)
# BUFFER
img_buffer = {
    'cn': BytesIO(),
    'en': BytesIO()
}
# need text buffer to store short url
text_buffer = ""
last_updated = None
# HARDCODE
@dailyChallenge.handle()
async def get_daily_challenge(event: MessageEvent, args:Message = CommandArg()):
    # actually we don't need to use global here for img_buffer but it's fine, just to make format consistent
    global img_buffer, text_buffer, last_updated
    try:
        if "daily" in event.get_plaintext():
            language = 'en'
        else:
            language = 'cn'
        if last_updated == datetime.date.today():
            img = img_buffer[language].getvalue()
            if img == b'':
                raise ValueError("Image buffer is empty")
        else:
            data = fetch_daily_challenge()
            if data is not None:
                # update both language
                for lang in ['cn', 'en']:
                    title, content = get_problem_body(data['question'], lang)
                    # we need reset buffer
                    img_buffer[lang] = BytesIO()
                    # Create image from text & save to buffer
                    create_image_from_text(title, content, lang).save(img_buffer[lang], format="PNG")
                # now back to user query
                title, content = get_problem_body(data['question'], language)
                short_url = f"{REDIRECT_BASE_URL}/problems/{data['question']['titleSlug']}"
                img = img_buffer[language].getvalue()
                text_buffer = "🎯今天的挑战是... \n"+title+"！\n{random_ending}\n" + short_url
                # update time after all states are updated
                last_updated = datetime.date.today()
            else:
                raise ValueError("Failed to fetch daily challenge")
        # Send the image
        random_ending = random.choice(RANDOM_ENDINGS)
        random_ending = random_ending.format(appellation=random.choice(RANDOM_APPELLATION))
        text_filled = text_buffer.format(random_ending=random_ending)
        msg = Message([MessageSegment.text(text_filled), MessageSegment.file_image(img)])
        await dailyChallenge.send(msg)
    except Exception as e:
        logger.error(f"Failed to fetch daily challenge due to {e}")
        await dailyChallenge.finish("哎哟，网卡了，等下再试试吧~")