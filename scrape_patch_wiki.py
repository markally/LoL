# Scrape Lol Wiki for Patch Info

from bs4 import BeautifulSoup
import requests
import pandas as pd

def ParseLoLWikiRow(row):
    """Scrape and clean elements of interest from row. Return as tuple."""
    patch = row[0].text.strip()
    date = row[1].text.strip()
    new_champion = row[2].text.strip()
    other = row[3].text.strip()
    link = row[4].find("a")["href"].strip()
    parsed_row = (patch, date, new_champion, other, link)
    return parsed_row


def ParseTable(table):
    """Parse LoL wiki table and return header and data as lists"""
    parsedtable = []
    headers = table.find_all("th")
    tablewidth = len(headers)
    columnnames = [h.text.strip() for h in headers]
    rows = table.find_all("tr")
    for row in rows:
        data = row.find_all("td")
        if data:
            parsedtable.append(ParseLoLWikiRow(data))
    return parsedtable, columnnames


def ScrapeTable(url):
    """Scrape LoL Wiki for the patch table and return it as a DataFrame"""
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, "html.parser")

    table = soup.find("table", class_="wikitable")
    parsedtable, headers = ParseTable(table)
    return pd.DataFrame(data = parsedtable, columns = headers)

def main():
    """Scrape LoL Patch info from the Wiki, return it and save it as a csv."""
    url = "http://leagueoflegends.wikia.com/wiki/Patch"
    df = ScrapeTable(url)
    pd.to_csv('patch_table')
    return df
