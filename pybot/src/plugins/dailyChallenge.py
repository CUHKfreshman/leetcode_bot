from nonebot import on_command, logger
from nonebot.adapters.qq import Message, MessageEvent, MessageSegment
from nonebot.params import CommandArg
from io import BytesIO
import random
import datetime
from ..utils import create_image_from_text, fetch_daily_challenge, get_problem_body
from ..utils import REDIRECT_BASE_URL, RANDOM_ENDINGS, RANDOM_APPELLATION
dailyChallenge = on_command("每日挑战", aliases={"每日大赛","daily", "daily-challenge"},priority=1,block=True, force_whitespace=True)
# BUFFER
img_buffer = {
    'cn': BytesIO(),
    'en': BytesIO()
}
# need text buffer to store short url
text_buffer = ""
last_updated = {
    'cn': None,
    'en': None
}
# HARDCODE
@dailyChallenge.handle()
async def get_daily_challenge(event: MessageEvent, args:Message = CommandArg()):
    # actually we don't need to use global here for img_buffer and last_updated but it's fine, just to make it noticed
    global img_buffer, text_buffer, last_updated
    user_query = event.get_plaintext()
    if user_query[0] == '/':
        user_query = user_query[1:]
    if user_query.startswith("daily"):
        language = 'en'
    else:
        language = 'cn'
    if last_updated[language] == datetime.date.today():
        img = img_buffer[language].getvalue()
    else:
        data = fetch_daily_challenge()
        if data is not None:
            title, content = get_problem_body(data['question'], language)
            short_url = f"{REDIRECT_BASE_URL}/problems/{data['question']['titleSlug']}"
            # we need reset buffer
            img_buffer[language] = BytesIO()
            # Create image from text
            img = create_image_from_text(title, content, language)
            img.save(img_buffer[language], format="PNG")
            img = img_buffer[language].getvalue()
            text_buffer = "🎯今天的挑战是... \n"+title+"！\n{random_ending}\n" + short_url
            # update time after all states are updated
            last_updated[language] = datetime.date.today()

        else:
            logger.error("Failed to fetch daily challenge due to network error")
            await dailyChallenge.send("哎哟，网卡了，等下再试试吧~")
    # if img is not empty, send the image
    if img is None:
        await dailyChallenge.send("哎哟，网卡了，等下再试试吧~")
        return
    # Send the image
    random_ending = random.choice(RANDOM_ENDINGS)
    random_ending = random_ending.format(appellation=random.choice(RANDOM_APPELLATION))
    text_filled = text_buffer.format(random_ending=random_ending)
    msg = Message([MessageSegment.text(text_filled), MessageSegment.file_image(img)])
    await dailyChallenge.send(msg)
