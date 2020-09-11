import json
import sys
from itertools import count

import requests
import bs4
import lxml


def process_municipality_term(term_div):
    name = term_div.find("h2").text.strip()
    number_field = term_div.find(class_="field--name-field-municipality-number")
    number = number_field.find(class_="field__item").text.strip()
    neighbors_blk = term_div.find(class_="field--name-field-neighboring-municipalities")
    neighbors = (
        [nli.text for nli in neighbors_blk.find_all("a")] if neighbors_blk else None
    )
    return {"name": name, "number": number, "neighbors": neighbors}


def scrape_kuntaliitto():
    sess = requests.Session()

    outf = open("kunnat.jsonl", "w", encoding="UTF-8")

    for page in count(0):
        print(page, file=sys.stderr)
        resp = sess.get(
            "https://www.kuntaliitto.fi/municipalities-all", params={"page": page}
        )
        if resp.status_code == 500:
            print("error 500, lul", file=sys.stderr)
            continue
        resp.raise_for_status()
        soup = bs4.BeautifulSoup(
            resp.text, features="lxml"
        )  # lxml required for correct parsing
        results = soup.find_all("div", class_="taxonomy-term vocabulary-municipalities")
        if not results:
            break
        for term_div in results:
            datum = process_municipality_term(term_div)
            print(json.dumps(datum, ensure_ascii=False), file=outf)


if __name__ == "__main__":
    scrape_kuntaliitto()
