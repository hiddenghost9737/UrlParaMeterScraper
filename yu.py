import aiohttp
import asyncio
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from colorama import Fore, Style
import argparse

class CustomException(Exception):
    pass

async def fetch_html_content(session, url):
    try:
        async with session.get(url, verify=False) as response:
            response.raise_for_status()
            return await response.text()
    except aiohttp.ClientError as e:
        logging.error(f"Error fetching URL {url}: {e}")
        raise CustomException(f"Error fetching URL {url}: {e}")

def extract_urls_with_parameters(base_url, html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    urls_with_parameters = [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True) if '?' in a['href']]
    return urls_with_parameters

def write_to_file(urls, filename='url_parameters.txt'):
    with open(filename, 'w') as file:
        file.write(f"{Fore.GREEN}{Style.BRIGHT}Full URLs with Parameters:\n")
        for url in urls:
            file.write(f"{url}\n")

async def main():
    parser = argparse.ArgumentParser(description='Scrape URLs with parameters')
    parser.add_argument('url', type=str, help='URL to scrape')
    args = parser.parse_args()

    async with aiohttp.ClientSession() as session:
        try:
            print(f"Fetching HTML content from {args.url}...")
            html_content = await fetch_html_content(session, args.url)
            
            print("Extracting URLs with parameters...")
            base_url = args.url.rstrip('/')  # Remove trailing slash if present
            urls_with_parameters = extract_urls_with_parameters(base_url, html_content)
            
            print(f"Writing results to file ({len(urls_with_parameters)} URLs found)...")
            write_to_file(urls_with_parameters)
            
            print("Process completed successfully.")
        except CustomException as ce:
            print(f"An error occurred: {ce}")

if __name__ == "__main__":
    logging.basicConfig(filename='scraping_log.txt', level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logging.exception(f"An unexpected error occurred: {e}")
