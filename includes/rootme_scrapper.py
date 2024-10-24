import aiohttp
import csv
from urllib.error import HTTPError

ROOTME_URL = "https://api.www.root-me.org/"

async def csv_parsing(file):
    users = []
    with open(file, 'r', newline='') as csvfile:
        dict_read = csv.reader(csvfile, delimiter=';')
        for line in dict_read:
            users.append(line[0])
        return users

async def check_if_user_exists(username):
    url = f"https://www.root-me.org/{username}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"User-agent": "Club Cyber EIJV"}) as response:
            if response.status == 200:
                return True
            else:
                return False

async def get_auteur_info(username, api_key):
    cookies = {"api_key": api_key}

    async with aiohttp.ClientSession() as session:
        # Get auteur id and name
        async with session.get(f"{ROOTME_URL}/auteurs?nom={username}", cookies=cookies, headers={"User-agent": "Club Cyber EIJV"}) as resp:
            if resp.status != 200:
                raise HTTPError(url="", msg="Error", code=resp.status, fp=None, hdrs="")
            
            data = await resp.json()
            id_auteur = data[0]["0"]["id_auteur"]

        # Get all infos, challenges, etc    
        async with session.get(f"{ROOTME_URL}/auteurs/{id_auteur}", cookies=cookies, headers={"User-agent": "Club Cyber EIJV"}) as resp:
            if resp.status != 200:
                raise HTTPError(url="", msg="Error", code=resp.status, fp=None, hdrs="")

            return await resp.json()

async def get_challenge_info(challenge, api_key):
    cookies = {"api_key": api_key}

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{ROOTME_URL}/challenges?titre={challenge}", cookies=cookies, headers={"User-agent": "Club Cyber EIJV"}) as resp:
            if resp.status != 200:
                raise HTTPError(url="", msg="Error", code=resp.status, fp=None, hdrs="")
            
            data = await resp.json()
            id_challenge = data[0]["0"]["id_challenge"]

        async with session.get(f"{ROOTME_URL}/challenges/{id_challenge}", cookies=cookies, headers={"User-agent": "Club Cyber EIJV"}) as resp:
            if resp.status != 200:
                raise HTTPError(url="", msg="Error", code=resp.status, fp=None, hdrs="")

            return await resp.json()
