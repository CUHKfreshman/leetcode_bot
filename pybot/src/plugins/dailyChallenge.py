from nonebot import on_command
from nonebot.adapters.qq import Message, MessageEvent, MessageSegment
from nonebot.params import CommandArg
from io import BytesIO
import random
import datetime
from ..utils import create_image_from_text, fetch_daily_challenge, get_problem_body
from ..utils import REDIRECT_BASE_URL, RANDOM_ENDINGS, RANDOM_APPELLATION
dailyChallenge = on_command("每日挑战", aliases={"每日大赛","daily"})
# BUFFER
img_buffer = BytesIO()
text_buffer = ""
last_updated = None
# HARDCODE
@dailyChallenge.handle()
async def get_daily_challenge(event: MessageEvent, args:Message = CommandArg()):
    global img_buffer, text_buffer, last_updated
    if last_updated == datetime.date.today():
        img = img_buffer.getvalue()
        # if img is not empty, send the image
        if img is None:
            await dailyChallenge.send("哎哟，网卡了，等下再试试吧~")
            return
    else:
        data = fetch_daily_challenge()
        if data is not None:
            title, content = get_problem_body(data['question'], language='cn')
            short_url = f"{REDIRECT_BASE_URL}/problems/{data['question']['titleSlug']}"
            # we need reset buffer
            img_buffer = BytesIO()
            # Create image from text
            img = create_image_from_text(title, content, 'cn')
            img.save(img_buffer, format="PNG")
            img = img_buffer.getvalue()
            text_buffer = "🎯今天的挑战是... \n"+title+"！\n{random_ending}\n" + short_url
            # update time after all states are updated
            last_updated = datetime.date.today()

        else:
            await dailyChallenge.send("哎哟，网卡了，等下再试试吧~")
    # Send the image
    random_ending = random.choice(RANDOM_ENDINGS)
    random_ending = random_ending.format(appellation=random.choice(RANDOM_APPELLATION))
    text_filled = text_buffer.format(random_ending=random_ending)
    msg = Message([MessageSegment.text(text_filled), MessageSegment.file_image(img)])
    await dailyChallenge.send(msg)
