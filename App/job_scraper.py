import requests
from bs4 import BeautifulSoup

# Helper function to fetch and parse HTML

def get_soup(url, headers=None):
    if headers is None:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, 'html.parser'), resp.text

# Indeed Scraper
def scrape_indeed(query="software engineer", location=""):
    # Mock API response for Indeed
    return [
        {
            'title': 'Software Engineer',
            'company': 'Indeed Inc.',
            'link': 'https://www.indeed.com/viewjob?jk=12345'
        },
        {
            'title': 'Backend Developer',
            'company': 'Tech Solutions',
            'link': 'https://www.indeed.com/viewjob?jk=67890'
        }
    ]

# LinkedIn Scraper (public search, limited results)
def scrape_linkedin(query="software engineer", location=""):
    # Mock API response for LinkedIn
    return [
        {
            'title': 'Data Scientist',
            'company': 'LinkedIn Corp.',
            'link': 'https://www.linkedin.com/jobs/view/12345/'
        },
        {
            'title': 'Frontend Engineer',
            'company': 'Web Innovators',
            'link': 'https://www.linkedin.com/jobs/view/67890/'
        }
    ]

# Monster Scraper (basic, may be blocked)
def scrape_monster(query="software engineer", location=""):
    # Mock API response for Monster
    return [
        {
            'title': 'Full Stack Developer',
            'company': 'Monster Worldwide',
            'link': 'https://www.monster.com/job-openings/12345'
        },
        {
            'title': 'DevOps Engineer',
            'company': 'CloudOps',
            'link': 'https://www.monster.com/job-openings/67890'
        }
    ]

# MeroJobs Scraper
def scrape_merojobs(query="software engineer", location=""):
    # Mock API response for MeroJobs
    return [
        {
            'title': 'QA Engineer',
            'company': 'MeroJobs Pvt. Ltd.',
            'link': 'https://merojob.com/job/12345/'
        },
        {
            'title': 'Mobile App Developer',
            'company': 'App Creators',
            'link': 'https://merojob.com/job/67890/'
        }
    ]

# JobNepal Scraper
def scrape_jobnepal(query="software engineer", location=""):
    # Mock API response for JobNepal
    return [
        {
            'title': 'Network Engineer',
            'company': 'JobNepal Solutions',
            'link': 'https://www.jobnepal.com/job/12345/'
        },
        {
            'title': 'UI/UX Designer',
            'company': 'Creative Studio',
            'link': 'https://www.jobnepal.com/job/67890/'
        }
    ]

if __name__ == "__main__":
    # Example usage
    for site, func in [
        ("Indeed", scrape_indeed),
        ("LinkedIn", scrape_linkedin),
        ("Monster", scrape_monster),
        ("MeroJobs", scrape_merojobs),
        ("JobNepal", scrape_jobnepal),
    ]:
        print(f"\n{site} Jobs:")
        try:
            jobs = func()
            for job in jobs[:5]:  # Show only first 5 jobs per site
                print(job)
        except Exception as e:
            print(f"Error scraping {site}: {e}")
