import scrapy
import json
from scrapy.http import JsonRequest
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urljoin, urlparse

def get_root_domain(url):
    parsed_url = urlparse(url)
    root_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return root_domain

class FoUSpider(scrapy.Spider):
    name = "FoU_spider"

    overview_JSON_url = "https://www.ks.no/api/fousearch?QueryString=&fromYear=0&toYear=0"
    root_url = get_root_domain(overview_JSON_url)

    link_extractor = LinkExtractor(allow=r'.*\.(pdf|doc|docx|xls|xlsx|ppt|pptx|txt|csv|rtf|odt|ods|zip)$', deny_extensions=[])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results_data = []

    def start_requests(self):
        yield JsonRequest(url=self.overview_JSON_url, callback=self.parse_json)

    def parse_json(self, response):
        json_res = response.json()
        
        filters = json_res.get("filters", [])
        self.filters_data = filters

        results = json_res.get("results", [])
        
        for result in results:
            yield scrapy.Request(
                url=urljoin(self.root_url, result["pageLink"]),
                callback=self.parse_result, 
                meta={"result": result}
            )

    def parse_result(self, response):
        links = self.link_extractor.extract_links(response)
        result = response.meta["result"]
        result['file_links'] = [link.url for link in links]
        self.results_data.append(result)

    def closed(self, reason):
        # Compile filters and results into the desired format
        yield {
            'filters': self.filters_data,
            'results': self.results_data
        }

        # # Writing to a JSON file or printing out
        # with open('output.json', 'w', encoding='utf-8') as f:
        #     json.dump(output_data, f, ensure_ascii=False, indent=4)

        # # Optionally print the output data
        # self.logger.info("Scraping completed")
        # self.logger.info(json.dumps(output_data, indent=4))

