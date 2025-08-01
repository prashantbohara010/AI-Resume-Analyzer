# Improved Resume Analysis Module

import requests
from bs4 import BeautifulSoup

def fetch_indeed_jobs(query="software engineer", location=""):
    """
    Scrape Indeed for real-time job vacancies based on query and location.
    Returns a list of dicts: {title, company, link}
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    url = f"https://www.indeed.com/jobs?q={query.replace(' ', '+')}&l={location}"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    jobs = []
    # Try to find job cards (robust to minor HTML changes)
    for card in soup.find_all('a', attrs={'data-jk': True, 'tabindex': True}):
        title = card.find('span')
        company = card.find_next('span', class_='companyName')
        link = card.get('href')
        if title and company and link:
            jobs.append({
                'title': title.text.strip(),
                'company': company.text.strip(),
                'link': 'https://www.indeed.com' + link
            })
    # Fallback to previous selector if above fails
    if not jobs:
        for div in soup.find_all('div', class_='job_seen_beacon'):
            title = div.find('h2', class_='jobTitle')
            company = div.find('span', class_='companyName')
            link = div.find('a', href=True)
            if title and company and link:
                jobs.append({
                    'title': title.text.strip(),
                    'company': company.text.strip(),
                    'link': 'https://www.indeed.com' + link['href']
                })
    return jobs
