import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
from scrapy.spiders import CrawlSpider, Rule, Spider

import re

from urllib.parse import urlparse
import json

from scrapy.utils.response import open_in_browser

from time import sleep


class PdfSpider(Spider):
    name = "pdf_spider"

    def __init__(self, *args, **kwargs):
        super(PdfSpider, self).__init__(*args, **kwargs)

        with open("kommuner.json", "r", encoding="utf-8") as f:
            self.municipalities = list(json.load(f))

        self.selectedMunicipalities = [
            m for m in self.municipalities if m["Fylke"] == "Finnmark"
        ]

        # try:
        #     self.selectedMunicipality = [
        #         m for m in self.municipalities if m["Kommunenavn"] == kommune
        #     ][0]
        # except IndexError:
        #     raise ValueError("Kommunen finnes ikke")

        self.allowed_domains = [
            m["Domene"].replace("https://www.", "") for m in self.selectedMunicipalities
        ]
        self.start_urls = [m["Domene"] for m in self.selectedMunicipalities]

        denied_extensions = [e for e in scrapy.linkextractors.IGNORED_EXTENSIONS if e != "pdf"]
        self.link_extractor = LinkExtractor(deny_extensions=denied_extensions)

    # start_urls = [m["Domene"] for m in filteredMunicipalities]

    # def start_requests(self):
    #     for m in self.selectedMunicipalities:
    #         yield scrapy.Request(m["Domene"], callback=self.parse)

    def getCurrentMunicipalityFromUrl(self, res_url):
        restring = r"(https?\:\/\/)?(www\.)?"

        currentMunicipality = [
            m
            for m in self.selectedMunicipalities
            if re.sub(restring, "", urlparse(m["Domene"]).netloc)
            == re.sub(restring, "", urlparse(res_url).netloc)
        ]

        if len(currentMunicipality) != 1:
            print(urlparse(res_url).netloc)
            raise Exception("Det oppstod en feil under identifisering av kommunen")
        else:
            currentMunicipality = currentMunicipality[0]

        return currentMunicipality



    def parse(self, response):

        for link in self.link_extractor.extract_links(response):
            if ".pdf" in link.url:
                print("Found PDF: " + link.url)
                currentMunicipality = self.getCurrentMunicipalityFromUrl(response.url)

                yield {
                    "kommune_navn": currentMunicipality["Kommunenavn"],
                    "fylke": currentMunicipality["Fylke"],
                    "målform": currentMunicipality["Målform"],
                    "kommune_nr": currentMunicipality["Nr"],
                    "from_url": response.url,
                    "pdf_link": response.urljoin(link.url),
                }
            else:
                yield response.follow(link.url, callback=self.parse)
