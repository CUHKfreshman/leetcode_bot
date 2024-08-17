import json
import requests
from nonebot import get_driver
config = get_driver().config
REDIRECT_BASE_URL = getattr(config, "redirect_base_url", "xxx")
NODE_SERVER_BASE_URL = getattr(config, "node_server_base_url", "xxx")
def fetch_problems_total_number()->int:
    API_URL = "http://localhost:3000/api/total-problems/"
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()['total']
    return None
def fetch_daily_challenge():
    API_URL = "http://localhost:3000/api/daily-challenge/"
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    return None

def fetch_problem(question_number:int | None=None):
    API_URL = f"http://localhost:3000/api/problem/{question_number}"
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    return None
