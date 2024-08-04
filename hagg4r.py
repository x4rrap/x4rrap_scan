import requests
from bs4 import BeautifulSoup
import pyfiglet
from termcolor import colored
import re
import argparse

def banner():
    ascii_banner = pyfiglet.figlet_format("Hagg4rweb-Scanner")
    print(colored(ascii_banner, 'green'))

def parse_arguments():
    parser = argparse.ArgumentParser(description="Web Recon Scanner")
    parser.add_argument("target", help="Target website to scan")
    return parser.parse_args()

def bypass_cloudflare(target):
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    try:
        response = session.get(f"https://api.bypasscf.com/api/{target}?key=YOUR_BYPASSCF_API_KEY")
        if response.status_code == 200:
            return response.json()['result']
        else:
            print(colored("Failed to bypass Cloudflare.", 'red'))
            return None
    except Exception as e:
        print(colored(f"Error: {e}", 'red'))
        return None

def find_emails(target):
    try:
        response = requests.get(target)
        soup = BeautifulSoup(response.text, 'html.parser')
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', soup.get_text())
        return list(set(emails))
    except Exception as e:
        print(colored(f"Error: {e}", 'red'))
        return []

def find_credentials(target):
    credentials = []
    try:
        response = requests.get(target)
        soup = BeautifulSoup(response.text, 'html.parser')
        for form in soup.find_all('form'):
            action = form.get('action')
            method = form.get('method', 'GET').upper()
            inputs = [input.get('name') for input in form.find_all('input') if input.get('name')]
            credentials.append((action, method, inputs))
    except Exception as e:
        print(colored(f"Error: {e}", 'red'))
    return credentials

def find_admin_pages(target):
    admin_pages = []
    try:
        response = requests.get(target)
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and 'admin' in href.lower():
                admin_pages.append(href)
    except Exception as e:
        print(colored(f"Error: {e}", 'red'))
    return admin_pages

def main():
    banner()
    args = parse_arguments()
    target = args.target
    print(colored(f"\n[] Target: {target}", 'yellow'))
    bypassed_target = bypass_cloudflare(target)
    if bypassed_target:
        target = bypassed_target
    print(colored("\n[] Found emails:", 'yellow'))
    emails = find_emails(target)
    for email in emails:
        print(f"- {email}")
    print(colored("\n[] Found potential credentials:", 'yellow'))
    credentials = find_credentials(target)
    for cred in credentials:
        print(f"- Action: {cred[0]}, Method: {cred[1]}, Inputs: {', '.join(cred[2])}")
    print(colored("\n[] Found potential admin pages:", 'yellow'))
    admin_pages = find_admin_pages(target)
    for page in admin_pages:
        print(f"- {page}")

if __name__ == "__main__":
    main()
