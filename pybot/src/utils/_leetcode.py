import json
import requests
REDIRECT_BASE_URL = "47.238.6.101"
def fetch_problems_total_number():
    with open("./src/data/leetcode_data.json") as f:
        data = json.load(f)
        return data["num_total"]

def fetch_daily_challenge():
    API_URL = "http://localhost:3000/api/daily-challenge"
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
