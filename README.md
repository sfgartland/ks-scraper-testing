## KUDOS_verktøy

Laster ned alle KUDOS-rapportene funnet ved bruk av søkeverktøyet på KUDOS-nettstedet. For å bruke det, gjør først et søk på KUDOS-nettstedet, og kopier deretter URL-en som et argument inn i følgende kommando:

`poetry run python main.py <url> --output-dir <output_folder> --log-level <log_level>`

`--output-dir` er valgfri, og standard til gjeldende katalog.
`--log-level` er valgfri, og standard til INFO. Sett til DEBUG for mer detaljert output.



## Kommandoer for å skrape, laste ned og organisere FoU-rapporter

### 1. Skrape FoU-oversikt JSON-fil
For å skrape FoU-oversikt JSON-fil, kan du bruke følgende kommando:
`cd ./scrapy_kommune_pdf_scraper scrapy crawl FoU_spider --loglevel DEBUG -o FoU-overview.json`


### 2. Last ned PDF-filene fra FoU-oversikt JSON-fil

For å laste ned PDF-filene fra FoU-oversikt JSON-fil, kan du bruke følgende kommando:
```cd ./scrapy_kommune_pdf_scraper python .\scrapy_kommune_pdf_scraper\helper_scripts\download_and_organize_FoU.py download-files .\FoU-overview.json ./data/FoU```



### 3. Organisere PDF-filene i mapper basert på FoU-oversikt JSON-fil

For å organisere PDF-filene i mapper basert på FoU-oversikt JSON-fil, kan du bruke følgende kommando:

```cd ./scrapy_kommune_pdf_scraper python .\scrapy_kommune_pdf_scraper\helper_scripts\download_and_organize_FoU.py organize-by-theme .\FoU-overview.json ./data/FoU ./data/FoU_by_theme```