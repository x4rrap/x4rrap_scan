import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import subprocess
import os
import re

print("by hagg4r")

def is_admin_page(url):
    return "admin" in url.lower() or "login" in url.lower()

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

def main(args):
    session = requests.Session()

    # Bypass initial protections
    response = bypass_protection(session, args.url)

    soup = BeautifulSoup(response.text, "html.parser")

    # Find login form and extract credentials
    form = soup.find("form", {"method": "post"})
    if form and is_admin_page(args.url):
        username, password = extract_credentials(form)
        if username and password:
            credentials = f"{username}:{password}"
            print(f"[+] Found credentials: {credentials}")

            # Save results to a file on the desktop
            desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') if os.name == 'nt' else os.path.join(os.path.expanduser('~'), 'Desktop')
            result_file = os.path.join(desktop_path, "found_credentials.txt")
            save_results([credentials], result_file)

            return

    # Find all links on the page
    links = [urljoin(args.url, a["href"]) for a in soup.find_all("a", href=True)]

    # Scan for open ports
    open_ports = scan_ports(args.target)
    print(f"[+] Open ports: {', '.join(open_ports)}")

    # Filter out admin pages and perform brute force
    for link in links:
        if is_admin_page(link):
            print(f"[*] Found potential admin page: {link}")
            response = bypass_protection(session, link)
            soup = BeautifulSoup(response.text, "html.parser")
            form = soup.find("form", {"method": "post"})
            if form:
                username, password = extract_credentials(form)
                if username and password:
                    credentials = f"{username}:{password}"
                    print(f"[+] Found credentials: {credentials}")

                    # Save results to a file on the desktop
                    result_file = os.path.join(desktop_path, "found_credentials.txt")
                    save_results([credentials], result_file)

                    break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated web scanner for admin pages and credential extraction")
    parser.add
