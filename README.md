## Commands to scrape, download, and organize FoU reports


### 1. Scrape the FoU overview JSON file
To scrape the FoU overview JSON file, you can use the following command:
```
cd ./scrapy_kommune_pdf_scraper
scrapy crawl FoU_spider --loglevel DEBUG  -o FoU-overview.json
```


### 2. Download the PDF files from the FoU overview JSON file

To download the PDF files from the FoU overview JSON file, you can use the following command:
```
cd ./scrapy_kommune_pdf_scraper
python .\scrapy_kommune_pdf_scraper\helper_scripts\download_and_organize_FoU.py download-files .\FoU-overview.json ./data/FoU
```


### 3. Organize the PDF files into folders based on the FoU overview JSON file

To organize the PDF files into folders based on the FoU overview JSON file, you can use the following command:
```
cd ./scrapy_kommune_pdf_scraper
python .\scrapy_kommune_pdf_scraper\helper_scripts\download_and_organize_FoU.py organize-by-theme .\FoU-overview.json ./data/FoU ./data/FoU_by_theme
```