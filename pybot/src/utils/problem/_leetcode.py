import requests
from requests import RequestException
from nonebot import get_driver
config = get_driver().config
REDIRECT_BASE_URL = getattr(config, "redirect_base_url", "(leetcode_url)")
NODE_SERVER_BASE_URL = getattr(config, "node_server_base_url", "xxx")
def fetch_problems_total_number()->int:
    API_URL = "http://localhost:3000/api/total-problems/"
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()['total']
    raise RequestException("Failed to fetch total problems number")
def fetch_daily_challenge():
    API_URL = "http://localhost:3000/api/daily-challenge/"
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    raise RequestException("Failed to fetch daily challenge")

def fetch_problem(question_frontend_id:int | None=None):
    API_URL = f"http://localhost:3000/api/problem/{question_frontend_id}"
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    raise RequestException(f"Failed to fetch problem {question_frontend_id}")
def fetch_paid_problems()->list[int]:
    API_URL = "http://localhost:3000/api/paid-problems/"
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    raise RequestException("Failed to fetch paid only problems")