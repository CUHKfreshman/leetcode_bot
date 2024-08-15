from nonebot import on_command
from nonebot.adapters.qq import Message, MessageEvent, MessageSegment
from nonebot.params import CommandArg
import requests
from io import BytesIO
import datetime
from ..utils.image import create_image_from_text
from ..utils.string import clean_string
from ..utils.leetcode import get_total_problems
import json
problem = on_command("今天做什么", aliases={"随机","random","problem","题目"})
# data json is in ../data/leetcode_data.json
TOTAL_PROBLEMS = get_total_problems()

@problem.handle()
async def get_problem(event: MessageEvent, args:Message = CommandArg()):
    # if user indicated a problem number, then fetch that problem
    # if not, fetch a random problem
    print(args.extract_plain_text())
    question_number = args.extract_plain_text()#args.strip()
    if question_number:
        try:
            question_number = int(question_number)
            if question_number < 1 or question_number > TOTAL_PROBLEMS:
                raise ValueError
        except ValueError:
            await problem.send(f"Invalid problem number. Please enter a number between 1 and {TOTAL_PROBLEMS}")
            return
        API_URL = f"http://localhost:3000/api/problem/{question_number}"
    else:
        API_URL = "http://localhost:3000/api/problem"
    # check if user indicated a valid problem number in the range 1-max
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        await problem.send(f"{data}")
        # title = data['question']['title']
        # content = clean_string(data['question']['content'])
        # if last_updated != datetime.date.today():
        #     # we need reset buffer
        #     buffer = BytesIO()
        #     last_updated = datetime.date.today()
        #     # Create image from text
        #     img = create_image_from_text(title, content)
        #     img.save(buffer, format="PNG")

        # img = buffer.getvalue()
        
        # # Send the image
        # await problem.send(MessageSegment.file_image(img))
    else:
        await problem.send("Failed to fetch problem, please try again later.")
