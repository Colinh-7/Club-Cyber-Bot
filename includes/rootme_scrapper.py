import requests
import csv
from urllib.error import HTTPError

ROOTME_URL = "https://api.www.root-me.org/"

def csv_parsing(file):
    users = []
    with open(file, 'r', newline='') as csvfile:
        dict_read = csv.reader(csvfile, delimiter=';')
        for line in dict_read:
            users.append(line[0])
        return users

def check_if_user_exists(username):
    url = f"https://www.root-me.org/{username}"

    response = requests.get(url, headers={"User-agent" : "Club Cyber EIJV"})
    if response.status_code == 200:
        return True
    else:
        return False

async def get_auteur_info(username, api_key):
    cookies = {"api_key" : api_key }

    # Get auteur id and name
    resp = requests.get(f"{ROOTME_URL}/auteurs?nom={username}", cookies=cookies, headers={"User-agent" : "Club Cyber EIJV"})
    if resp.status_code != 200 :
        raise HTTPError(url="", msg="Error", code=resp.status_code, fp=None, hdrs="")
    
    data = resp.json()
    id_auteur = data[0]["0"]["id_auteur"]

    # Get all infos, challenges, etc    
    resp = requests.get(f"{ROOTME_URL}/auteurs/{id_auteur}", cookies=cookies, headers={"User-agent" : "Club Cyber EIJV"})
    if resp.status_code != 200 :
        raise HTTPError(url="", msg="Error", code=resp.status_code, fp=None, hdrs="")

    return resp.json()
        
def get_challenge_info(challenge, api_key):
    cookies = {"api_key" : api_key}

    resp = requests.get(f"{ROOTME_URL}/challenges?titre={challenge}", cookies=cookies, headers={"User-agent" : "Club Cyber EIJV"})
    if resp.status_code != 200 :
        raise HTTPError(url="", msg="Error", code=resp.status_code, fp=None, hdrs="")
    
    data = resp.json()
    id_challenge = data[0]["0"]["id_challenge"]

    resp = requests.get(f"{ROOTME_URL}/challenges/{id_challenge}", cookies=cookies, headers={"User-agent" : "Club Cyber EIJV"})
    if resp.status_code != 200 :
        raise HTTPError(url="", msg="Error", code=resp.status_code, fp=None, hdrs="")

    return resp.json()