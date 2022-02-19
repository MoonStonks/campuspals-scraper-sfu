import json
from random import randrange
from bs4 import BeautifulSoup
import urllib.request
import concurrent.futures


class Scraper:
    def __init__(self):
        self.baseurl = "https://go.sfss.ca"
        html = urllib.request.urlopen(f"{self.baseurl}/clubs/list")
        self.soup = BeautifulSoup(html, features="html.parser")
        self.tags = ['social', 'cultural', 'tech', 'wellbeing', 'innovation', 'health',
                     'friendship', 'club', 'food', 'dance', 'sports', 'arts', 'science', 'space']

    def create_thread(self, url):
        club = {}
        html = urllib.request.urlopen(f"{self.baseurl}{url}")
        soup = BeautifulSoup(html, features="html.parser")

        club['clubName'] = soup.find('h1').string
        imgs = soup.find_all('img')
        if len(imgs) > 1:
            club['imgURL'] = f"{self.baseurl}{imgs[1]['src']}"
        else:
            club['imgURL'] = f"{self.baseurl}{imgs[0]['src']}"

        section = soup.find('section', {"class": "page-intro"})
        b_tags = section.find_all('b')
        for b in b_tags:
            if "mandate" in b.string:
                club['description'] = b.next_sibling.strip()
            if "Email" in b.string:
                club['email'] = b.find_next_sibling().string.strip()
            if "Website" in b.string:
                club['website'] = b.find_next_sibling().string.strip()

        if 'description' not in club:
            club['description'] = ""
        if 'email' not in club:
            club['email'] = ""
        if 'website' not in club:
            club['website'] = ""
        if 'imgURL' not in club:
            club['imgURL'] = ""
        if 'clubName' not in club:
            club['clubName'] = ""


        club['university'] = 1
        club['tags'] = []

        idxs = set()
        while (len(idxs) < 3):
            idxs.add(randrange(len(self.tags)))

        for idx in list(idxs):
            club['tags'].append(self.tags[idx])

        return club

    def scrape(self):
        table = self.soup.find('table', id="club_listing")
        urls = set()
        for link in table.find_all('a'):
            urls.add(link.get('href'))

        result = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            results = executor.map(self.create_thread, list(urls))
            for r in results:
                result.append(r)

        with open("result.json", "w") as outfile:
            json.dump(result, outfile)


if __name__ == "__main__":
    Scraper().scrape()
