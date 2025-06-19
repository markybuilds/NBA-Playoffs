"""
sportsline_scraper.py
---------------------
Scrapes NBA player projections from SportsLine simulation page.
"""
import requests
import pandas as pd
from bs4 import BeautifulSoup

def fetch_sportsline_projections() -> pd.DataFrame:
    """
    Scrape NBA player projections from SportsLine and return as a DataFrame.
    Columns: Player, Team, Position, and all available stats/projections.
    """
    url = "https://www.sportsline.com/nba/expert-projections/simulation/"
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table")
    if not table:
        raise ValueError("No table found on SportsLine projections page.")
    headers = [th.get_text(strip=True) for th in table.find_all("th")]
    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(cells) == len(headers):
            rows.append(cells)
    df = pd.DataFrame(rows, columns=headers)
    return df
