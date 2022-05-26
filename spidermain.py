import sys
import threading
import re

import requests
from bs4 import BeautifulSoup

TO_CRAWL = []
CRAWLED = set()
EMAILS = set()


def find_emails(parsed_html):
    emails = re.findall(r'\w[\w\.]+\w@\w[\w\.]+\.[\w\.]+\w', parsed_html.text)
    for email in emails:
        if email not in EMAILS:
            EMAILS.add(email)


def crawl(target):
    try:
        answer = requests.get(target)
    except Exception as error:
        print('Unexpected error ', error)
        CRAWLED.add(target)
        return None

    if answer:
        parsed_html = BeautifulSoup(answer.text, 'html.parser')
        find_emails(parsed_html)
        atags = parsed_html.find_all('a', href=True)

        if atags:
            for tag in atags:
                link = tag['href']
                if link.startswith('http') and link not in CRAWLED and link not in TO_CRAWL:
                    TO_CRAWL.append(link)
                    CRAWLED.add(target)


def main():
    thread_cap = 10
    try:
        target = sys.argv[1]
        TO_CRAWL.append(target)
    except IndexError:
        print('Usage: spidermain.py <TARGET URL>')
        sys.exit(0)

    while TO_CRAWL:
        if len(TO_CRAWL) >= thread_cap:
            threads = [threading.Thread(target=crawl, args=[TO_CRAWL.pop()]) for _ in range(thread_cap)]
        else:
            threads = [threading.Thread(target=crawl, args=[TO_CRAWL.pop()]) for _ in range(len(TO_CRAWL))]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        print(EMAILS)

    print(CRAWLED)


if __name__ == '__main__':
   main()
