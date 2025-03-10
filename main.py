import requests
from bs4 import BeautifulSoup

from time import sleep

from pathlib import Path

import os

from urllib.parse import urlparse

import typer

import re



def saveNOU(title, url, baseurl, parentDir=Path(".")):
    print(f"Saving {title}...")
    # Save the NOU to a file

    res = requests.get("https://" + baseurl + url)
    if res.status_code != 200:
        raise Exception("Failed to retrieve NOU specific page")

    soup = BeautifulSoup(res.content, "html.parser")

    list = soup.find(class_="longdoc-download-list")

    allDocLinks = list.find_all("a")

    for doc in allDocLinks:
        docUrl = doc["href"]
        if docUrl.endswith(".pdf"):
            print(f"Found PDF: {docUrl}... Downloading")
            pdfRes = requests.get("https://" + baseurl + docUrl)
            if pdfRes.status_code != 200:
                raise Exception("Failed to retrieve PDF")
            filePath: Path = (parentDir / f"{title.replace(':', '')}.pdf").resolve()
            print(filePath)
            os.makedirs(filePath.parent, exist_ok=True)
            with open(filePath, "wb") as f:
                f.write(pdfRes.content)
                print(f"Saved {filePath}")
                break


def generateTemplate(url: str):
    if "page=" in url:
        return re.sub(r"page=\d+", "page={page}", url)
    elif "?" in url:
        return url + "&page={page}"
    else:
        return url + "?page={page}"


def main(url: str, parentDir: Path = Path(".")):
    currentPage = 1
    endPageFound = False

    urlTemplate = generateTemplate(url)

    while not endPageFound:
        print(f"Processing page {currentPage}...")
        url = urlparse(urlTemplate.format(page=currentPage))

        res = requests.get(url.geturl())
        if res.status_code != 200:
            print(f"Failed to retrieve page {currentPage}")
            break

        soup = BeautifulSoup(res.content, "html.parser")

        # Check if the end of the pages is reached
        noResult = soup.find(class_="title gtm-search-zeroresults")
        if noResult is not None:
            print("Exeeded amount of pages.... Stopping")
            endPageFound = True
            break

        results = soup.find(class_="results")
        if results is None:
            raise Exception("No results found")

        listItems = results.find_all(class_="listItem")
        for item in listItems:
            titleElement = item.find("h2")
            title = titleElement.text.strip()
            link = titleElement.find("a")["href"]
            baseurl = url.hostname
            print(f"Found: {title}")

            saveNOU(title, link, baseurl, parentDir)

            endPageFound = True
            sleep(1)

        currentPage += 1



if __name__ == "__main__":
    typer.run(main)