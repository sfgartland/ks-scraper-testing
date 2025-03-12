import re
from bs4 import BeautifulSoup
from pathlib import Path


from main import scrapeURL



url = "https://www.regjeringen.no/no/dokument/nou-ar/id1767/"


def getListOfNOUs():
    # response = requests.get(url)

    response = ""
    with open("overview-list.html", "r", encoding="utf-8") as file:
        response = file.read()

    soup = BeautifulSoup(response, "html.parser")
    list = soup.find(id="customSelectortopic")
    links = list.find_all("a")

    NOU_category = []

    for link in links:
        title = re.sub(r"[\n\r\?]", "",link.text.strip())
        url = "https://www.regjeringen.no/"+link["href"]
        NOU_category.append((title, url))
        # scrapeURL(url, Path("NOUs") / title)


    return NOU_category



categories = getListOfNOUs()


for category in categories:

    match = re.search(r"\((\d+)\)", category[0])

    numberOfFilesinCat = int(match.group(1))
    folderPath = Path("NOUs") / category[0]

    numFilesInDir = len(list(folderPath.glob("*.pdf")))

    if numFilesInDir > numberOfFilesinCat:
        raise Exception("More files in directory than expected")
    elif numFilesInDir == numberOfFilesinCat:
        print(f"Already downloaded {category[0]}")
        # pass
    else:
        scrapeURL(category[1], folderPath)