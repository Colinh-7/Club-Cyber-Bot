import json, os

CHALLENGES_FILE = "data/challenges.json"

async def is_json_file_empty(file_path):
    if (os.path.exists(file_path)):
        if os.stat(file_path).st_size == 0:
            return True
    return False

async def load_challenges():
    if (os.path.exists(CHALLENGES_FILE) and not is_json_file_empty(CHALLENGES_FILE)):
        with open(CHALLENGES_FILE, "r") as f:
            return json.load(f)
    else:
        return {"ongoing_challenges": {}, "completed_challenges": {}}

async def save_challenges(challenges):
    with open(CHALLENGES_FILE, "w") as f:
        json.dump(challenges, f, indent=4)