import json
def get_total_problems():
    with open('./src/data/leetcode_data.json') as f:
        data = json.load(f)
        return data['num_total']