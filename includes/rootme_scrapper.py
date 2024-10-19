from bs4 import BeautifulSoup 
from urllib.request import urlopen, HTTPError
import csv

def check_is_user_exists(username):
    url = f"https://www.root-me.org/{username}"
    try:
        response = urlopen(url)
        if response.status == 200:
            return True
        else:
            return False
    except HTTPError as e:
        return False

def split_words(list):
    # Month of the year in french
    month = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

    new = []
    for temp in list:
        done = False
        for m in month:
            if m in temp:
                part= temp.split(m)
                new.append(part[0])
                new.append(m)
                done = True
                break
        if not done:
            new.append(temp)
    return new

def normalize_challenges(list):
    new = []
    for tmp in list:
        line = ""
        if ('>' not in tmp and '<' not in tmp):
            for word in tmp:
                line += word
                line += " "
            new.append(line)
    return new
            
# CSV parsing
def csv_parsing(file):
    users = []
    with open(file, 'r', newline='') as csvfile:
        dict_read = csv.reader(csvfile, delimiter=';')
        for line in dict_read:
            users.append(line[0])
        return users
        
# Web response from the request
def https_request(username):
    url = f"https://www.root-me.org/{username}"
    page = urlopen(url)
    return BeautifulSoup(page.read().decode("utf-8"), 'html.parser')

# Get user's profile stats
def get_user_stats(userpage):
    stats = {}
    row = userpage.find_all("div", {"class": "small-6 medium-3 columns text-center"})
    for line in row:
        array = line.get_text().split()
        stats[array[1]] = array[0]
    return stats

# Get user's last challenges
def get_last_challenges(userpage):
    challenges = []
    find = False
    challenge_section = None

    sections = userpage.find_all("div", class_= "t-body tb-padding")
    for section in sections:
        activity = section.find_all("h3")
        for a in activity:
            if a.get_text().find("Activité") > -1:
                find = True
                break
        if find :
            challenge_section = section
            break
    
    if challenge_section != None :
        challenge_section = challenge_section.find_all("li")

        for line in challenge_section:
            challenges.append(split_words(line.get_text().split()))

    return challenges