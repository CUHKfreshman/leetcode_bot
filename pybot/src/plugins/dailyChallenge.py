from nonebot import on_command
from nonebot.adapters.qq import Message, MessageEvent, MessageSegment
from nonebot.params import CommandArg
import requests
from io import BytesIO
import datetime
from ..utils.image import create_image_from_text
from ..utils.string import clean_string
dailyChallenge = on_command("每日挑战", aliases={"每日大赛","daily"})
API_URL = "http://localhost:3000/api/daily-challenge"
buffer = BytesIO()
last_updated = None

@dailyChallenge.handle()
async def get_daily_challenge(event: MessageEvent, args:Message = CommandArg()):
    global buffer
    global last_updated
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        title = data['question']['title']
        content = clean_string(data['question']['content'])
        if last_updated != datetime.date.today():
            # we need reset buffer
            buffer = BytesIO()
            last_updated = datetime.date.today()
            # Create image from text
            img = create_image_from_text(title, content)
            img.save(buffer, format="PNG")

        img = buffer.getvalue()
        
        # Send the image
        await dailyChallenge.send(MessageSegment.file_image(img))
    else:
        await dailyChallenge.send("Failed to fetch daily challenge, please try again later.")
