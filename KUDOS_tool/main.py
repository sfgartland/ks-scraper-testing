from urllib.parse import urlparse, parse_qsl
from collections import defaultdict
from loguru import logger

import requests
import json
import os

import typer

app = typer.Typer()

def getDataFromKUDOSUrl(url):
    """Extracts the filters from a KUDOS URL and returns them as a dictionary."""
    # Parse the URL into components
    parts = urlparse(url)
    logger.debug(f"Parsed URL components: {parts}")

    # Parse the query string into a list of pairs, sort, and re-encode it
    query_pairs = parse_qsl(parts.query)
    sorted_query_pairs = sorted(query_pairs)
    logger.debug(f"Sorted query pairs: {sorted_query_pairs}")

    filters = [
        pair[1].split("$")
        for pair in sorted_query_pairs
        if pair[0].startswith("filters")
    ]
    logger.debug(f"Extracted filters: {filters}")

    query = next((pair[1] for pair in sorted_query_pairs if pair[0] == "query"), None)
    searchType = next(
        (pair[1] for pair in sorted_query_pairs if pair[0] == "searchType"), "fulltext"
    )
    logger.debug(f"Search query: {query}, Search type: {searchType}")

    # Create a defaultdict where each key maps to a list
    result = defaultdict(list)

    # Populate the defaultdict
    for key, value in filters:
        result[key].append(value)

    logger.debug(f"Final filters dictionary: {result}")

    # Convert to a regular dict if necessary (optional)
    return dict(result), query, searchType


def fetch_all_documents(filters, query, search_type):
    """Fetches all documents from Kudos API given filters and other parameters."""

    base_url = "https://kudos.dfo.no/api/v0/documents/search"

    all_documents = []
    page = 1

    while True:
        query_params = {
            "filters": json.dumps(filters),  # Convert filters dict to JSON string
            "query": query,
            "search_type": search_type,
            "page": page,
        }

        response = requests.get(base_url, params=query_params)
        logger.debug(f"Fetched page {page}... Used url: {response.url}")

        if response.status_code != 200:
            logger.error(f"Error fetching data: {response.status_code} - {response.text}")
            break

        data = response.json()
        logger.debug(f"Fetched {len(data['data'])} documents on page {page}")

        # Add documents from current page to all_documents list
        all_documents.extend(data["data"])

        # Check if this is the last page
        if page >= data["meta"]["last_page"]:
            logger.debug(f"Reached last page: {page}")
            break

        page += 1

    return all_documents


def download_documents(documents, download_folder):
    """Downloads documents to the specified folder."""
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
        logger.debug(f"Created download folder: {download_folder}")

    for document in documents:
        document_id = document.get("id")
        files = document.get("files", [])
        if not files:
            logger.warning(f"No files available for document ID {document_id}")
            continue

        for file_info in files:
            file_url = file_info.get("url")
            if not file_url:
                logger.warning(f"No URL available for a file in document ID {document_id}")
                continue

            try:
                response = requests.get(file_url, stream=True)
                if response.status_code == 200:
                    file_name = os.path.basename(urlparse(file_url).path)
                    file_path = os.path.join(download_folder, file_name)
                    with open(file_path, "wb") as file:
                        for chunk in response.iter_content(1024):
                            file.write(chunk)
                    logger.info(f"Downloaded: {file_name}")
                else:
                    logger.error(
                        f"Failed to download document file {document_id}, status code {response.status_code} (File URL: {file_url})"
                    )
            except Exception as e:
                logger.exception(f"Error downloading file {document_id}: {str(e)}")



@app.command()
def main(
    kudos_url: str,
    output_dir: str = typer.Option("../data/downloaded_documents", help="Directory to save downloaded documents"),
    log_level: str = typer.Option("INFO", help="Logging level")
):
    """Fetch documents from a KUDOS URL and download them to a specified directory."""
    
    logger.remove()
    logger.add(lambda msg: print(msg, end=""), format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level=log_level.upper())

    filters, query, searchType = getDataFromKUDOSUrl(kudos_url)

    documents = fetch_all_documents(filters, query, searchType)

    logger.info(f"Found {len(documents)} documents")

    download_documents(documents, output_dir)


if __name__ == "__main__":
    app()
