import argparse
import re
import requests
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

print("by hagg4r")
def is_login_page(response):
    # Simple check for login pages, you might want to add more conditions
    return "login" in response.url.lower() or "admin" in response.url.lower()

def extract_credentials(form):
    username_field = form.find("input", {"name": "username"}) or form.find("input", {"id": "username"})
    password_field = form.find("input", {"name": "password"}) or form.find("input", {"id": "password"})

    if username_field and password_field:
        username = username_field["value"] if "value" in username_field.attrs else ""
        password = password_field["value"] if "value" in password_field.attrs else ""
        return username, password

    # Try to extract credentials using regex patterns
    username_pattern = r'name="username" value="([^"]+)"'
    password_pattern = r'name="password" value="([^"]+)"'
    username = re.search(username_pattern, form.prettify(), re.IGNORECASE)
    password = re.search(password_pattern, form.prettify(), re.IGNORECASE)

    if username and password:
        return username.group(1), password.group(1)

    return "", ""

class AdminLoginSpider:
    name = "admin_login_spider"

    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def start_requests(self):
        yield self.driver.get(self.start_urls[0])

    def parse(self, response):
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        # Find login form and extract credentials
        form = soup.find("form", {"method": "post"})
        if form and is_login_page(response):
            username, password = extract_credentials(form)
            if username and password:
                print(f"\u2620 Found admin credentials:")
                print(f"  Username: {username}")
                print(f"  Password: {password}")
                self.driver.quit()
                return

        # Follow links and crawl further
        for link in soup.find_all("a", href=True):
            yield self.driver.get(link["href"])

def main(args):
    process = CrawlerProcess()
    process.crawl(AdminLoginSpider, start_urls=[args.url])
    process.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated web scanner for admin login pages and credential extraction")
    parser.add_argument("url", help="Target URL")
    args = parser.parse_args()

    main(args)
