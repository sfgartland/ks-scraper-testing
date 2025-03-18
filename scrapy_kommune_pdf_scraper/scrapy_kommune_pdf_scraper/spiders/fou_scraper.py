import scrapy
import json
from scrapy.http import JsonRequest
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urljoin, urlparse

import re

def get_root_domain(url):
    parsed_url = urlparse(url)
    root_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return root_domain

class FoUSpider(scrapy.Spider):
    name = "FoU_spider"

    overview_JSON_url = "https://www.ks.no/api/fousearch?QueryString=&fromYear=0&toYear=0"
    root_url = get_root_domain(overview_JSON_url)

    link_extractor = LinkExtractor(allow=r'.*\.(pdf|doc|docx|xls|xlsx|ppt|pptx|txt|csv|rtf|odt|ods|zip)$', deny_extensions=[])

    def start_requests(self):
        # Send a request to the JSON URL
        yield JsonRequest(url=self.overview_JSON_url, callback=self.parse_json)

    def parse_json(self, response):
        # Assuming the JSON response is a list of URLs
        json_res = response.json()

        results = json_res["results"]

        # Iterate over each URL from the JSON data and create a new request for each
        for result in results:
            yield scrapy.Request(url=urljoin(self.root_url, result["pageLink"]), callback=self.parse, meta={"results":result})

    def parse(self, response):
        links = self.link_extractor.extract_links(response)
        
        # Yield the results
        yield {
            **response.meta["results"],
            'file_links': [link.url for link in links],
        }
