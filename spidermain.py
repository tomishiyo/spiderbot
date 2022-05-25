import sys
import threading

import requests
from bs4 import BeautifulSoup

TO_CRAWL = []
CRAWLED = set()

def crawl(target):
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/101.0.4951.67 Safari/537.36",
              "Cookie": "cf_clearance=3B5_SSLzPKu8YX1dbOdbYMcBsTE3HTnq5SsfIKuEWF0-1653494424-0-150",
              "Referer": "http://www.bancocn.com/?__cf_chl_tk=LXUCI3v4NxLReGFBSRj2ZKCI.fC4Ogn_SDwm6U6kMZY-1653494422-0-gaNycGzNA_0",
              "Origin": "http://www.bancocn.com",
              "Host": "www.bancocn.com"}
    try:
        answer = requests.get(target, headers=header)
    except Exception as error:
        print('Unexpected error ', error)
        CRAWLED.add(target)
        return None

    if answer:
        parsed_html = BeautifulSoup(answer.text, 'html.parser')
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

        print(TO_CRAWL)


if __name__ == '__main__':
    main()
