import requests
from bs4 import BeautifulSoup
import time
import random

def get_mock_jobs(query="software developer", location=""):
    """
    Generate mock job recommendations based on the query.
    This provides reliable job recommendations when web scraping fails.
    """
    mock_jobs = {
        "software developer": [
            {
                "title": "Senior Software Developer",
                "company": "TechCorp Solutions",
                "location": "Remote / New York, NY",
                "link": "https://example.com/job1",
                "description": "Full-stack development with React, Node.js, and Python"
            },
            {
                "title": "Full Stack Developer",
                "company": "InnovateTech Inc",
                "location": "San Francisco, CA",
                "link": "https://example.com/job2",
                "description": "Building scalable web applications using modern technologies"
            },
            {
                "title": "Python Developer",
                "company": "DataFlow Systems",
                "location": "Austin, TX",
                "link": "https://example.com/job3",
                "description": "Backend development with Django, Flask, and PostgreSQL"
            },
            {
                "title": "Frontend Developer",
                "company": "WebCraft Studios",
                "location": "Seattle, WA",
                "link": "https://example.com/job4",
                "description": "React, Vue.js, and modern CSS frameworks"
            },
            {
                "title": "DevOps Engineer",
                "company": "CloudScale Technologies",
                "location": "Remote",
                "link": "https://example.com/job5",
                "description": "AWS, Docker, Kubernetes, and CI/CD pipelines"
            }
        ],
        "data scientist": [
            {
                "title": "Senior Data Scientist",
                "company": "AnalyticsPro",
                "location": "Boston, MA",
                "link": "https://example.com/job6",
                "description": "Machine learning, statistical analysis, and predictive modeling"
            },
            {
                "title": "ML Engineer",
                "company": "AI Innovations",
                "location": "Palo Alto, CA",
                "link": "https://example.com/job7",
                "description": "Building and deploying machine learning models"
            },
            {
                "title": "Data Analyst",
                "company": "InsightCorp",
                "location": "Chicago, IL",
                "link": "https://example.com/job8",
                "description": "Data visualization, SQL, and business intelligence"
            }
        ],
        "web developer": [
            {
                "title": "Web Developer",
                "company": "Digital Solutions",
                "location": "Miami, FL",
                "link": "https://example.com/job9",
                "description": "HTML, CSS, JavaScript, and responsive design"
            },
            {
                "title": "WordPress Developer",
                "company": "WebWorks Agency",
                "location": "Denver, CO",
                "link": "https://example.com/job10",
                "description": "Custom WordPress themes and plugins"
            }
        ],
        "android developer": [
            {
                "title": "Android Developer",
                "company": "MobileTech Solutions",
                "location": "Los Angeles, CA",
                "link": "https://example.com/job11",
                "description": "Native Android development with Kotlin and Java"
            },
            {
                "title": "Mobile App Developer",
                "company": "AppCraft Studios",
                "location": "Portland, OR",
                "link": "https://example.com/job12",
                "description": "Cross-platform development with React Native"
            }
        ],
        "ios developer": [
            {
                "title": "iOS Developer",
                "company": "AppleTech Solutions",
                "location": "Cupertino, CA",
                "link": "https://example.com/job13",
                "description": "Native iOS development with Swift and SwiftUI"
            },
            {
                "title": "Mobile Developer",
                "company": "AppInnovate",
                "location": "San Diego, CA",
                "link": "https://example.com/job14",
                "description": "iOS and Android development with Flutter"
            }
        ],
        "ui/ux designer": [
            {
                "title": "UI/UX Designer",
                "company": "DesignStudio Pro",
                "location": "Brooklyn, NY",
                "link": "https://example.com/job15",
                "description": "User interface design, wireframing, and prototyping"
            },
            {
                "title": "Product Designer",
                "company": "Creative Solutions",
                "location": "Austin, TX",
                "link": "https://example.com/job16",
                "description": "User experience design and design systems"
            }
        ],
        "python": [
            {
                "title": "Python Developer",
                "company": "DataFlow Systems",
                "location": "Austin, TX",
                "link": "https://example.com/job17",
                "description": "Backend development with Django, Flask, and PostgreSQL"
            },
            {
                "title": "Python Engineer",
                "company": "TechInnovate",
                "location": "Seattle, WA",
                "link": "https://example.com/job18",
                "description": "Data processing, automation, and API development"
            }
        ],
        "java": [
            {
                "title": "Java Developer",
                "company": "Enterprise Solutions",
                "location": "Boston, MA",
                "link": "https://example.com/job19",
                "description": "Enterprise application development with Spring Boot"
            },
            {
                "title": "Java Engineer",
                "company": "FinTech Corp",
                "location": "New York, NY",
                "link": "https://example.com/job20",
                "description": "Financial software development and system integration"
            }
        ],
        "javascript": [
            {
                "title": "JavaScript Developer",
                "company": "WebTech Solutions",
                "location": "San Francisco, CA",
                "link": "https://example.com/job21",
                "description": "Frontend development with React, Vue.js, and Node.js"
            },
            {
                "title": "Full Stack JS Developer",
                "company": "Digital Innovations",
                "location": "Los Angeles, CA",
                "link": "https://example.com/job22",
                "description": "End-to-end web application development"
            }
        ],
        "react": [
            {
                "title": "React Developer",
                "company": "Frontend Masters",
                "location": "Chicago, IL",
                "link": "https://example.com/job23",
                "description": "Modern React development with hooks and context"
            },
            {
                "title": "React Native Developer",
                "company": "Mobile Solutions",
                "location": "Denver, CO",
                "link": "https://example.com/job24",
                "description": "Cross-platform mobile app development"
            }
        ],
        "machine learning": [
            {
                "title": "Machine Learning Engineer",
                "company": "AI Solutions",
                "location": "Palo Alto, CA",
                "link": "https://example.com/job25",
                "description": "ML model development and deployment"
            },
            {
                "title": "ML Research Engineer",
                "company": "Research Labs",
                "location": "Cambridge, MA",
                "link": "https://example.com/job26",
                "description": "Advanced ML research and implementation"
            }
        ],
        "nepal": [
            {
                "title": "Software Developer",
                "company": "TechNepal Solutions",
                "location": "Kathmandu, Nepal",
                "link": "https://example.com/job27",
                "description": "Full-stack development for local and international clients"
            },
            {
                "title": "Web Developer",
                "company": "Digital Nepal",
                "location": "Lalitpur, Nepal",
                "link": "https://example.com/job28",
                "description": "E-commerce and business website development"
            },
            {
                "title": "Python Developer",
                "company": "NepalTech Innovations",
                "location": "Pokhara, Nepal",
                "link": "https://example.com/job29",
                "description": "Backend development and API integration"
            },
            {
                "title": "React Developer",
                "company": "Himalayan Digital",
                "location": "Kathmandu, Nepal",
                "link": "https://example.com/job30",
                "description": "Frontend development for tourism and business applications"
            }
        ]
    }
    
    # Find the best matching category
    query_lower = query.lower()
    best_matches = []
    
    # Check for exact matches first
    for category in mock_jobs.keys():
        if category in query_lower or query_lower in category:
            best_matches.append(category)
    
    # If no exact matches, check for partial matches
    if not best_matches:
        for category in mock_jobs.keys():
            # Check if any word in the query matches the category
            query_words = query_lower.split()
            for word in query_words:
                if word in category or category in word:
                    best_matches.append(category)
                    break
    
    # If still no matches, use default
    if not best_matches:
        best_matches = ["software developer"]
    
    # Collect jobs from all matching categories
    all_jobs = []
    for match in best_matches:
        if match in mock_jobs:
            all_jobs.extend(mock_jobs[match])
    
    # Remove duplicates and shuffle
    unique_jobs = []
    seen_titles = set()
    for job in all_jobs:
        if job['title'] not in seen_titles:
            unique_jobs.append(job)
            seen_titles.add(job['title'])
    
    random.shuffle(unique_jobs)
    return unique_jobs[:5]  # Return up to 5 jobs

def scrape_indeed_jobs(query="software developer", location=""):
    """
    Scrape job listings from Indeed for a given query and location.
    Returns a list of jobs with title, company, location, and link.
    """
    jobs = []
    try:
        # Use a more robust approach with better headers and error handling
        base_url = "https://www.indeed.com/jobs"
        params = {
            "q": query,
            "l": location,
            "sort": "date"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        response = requests.get(base_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try multiple possible selectors for job cards
        job_cards = soup.find_all("a", class_="tapItem")
        if not job_cards:
            job_cards = soup.find_all("div", class_="job_seen_beacon")
        if not job_cards:
            job_cards = soup.find_all("div", {"data-jk": True})
        
        for card in job_cards[:10]:  # Limit to 10 jobs
            try:
                # Try multiple selectors for each field
                title_elem = (card.find("h2", class_="jobTitle") or 
                             card.find("a", class_="jcs-JobTitle") or
                             card.find("span", class_="jobTitle"))
                
                company_elem = (card.find("span", class_="companyName") or
                               card.find("div", class_="companyName") or
                               card.find("span", class_="company"))
                
                location_elem = (card.find("div", class_="companyLocation") or
                                card.find("span", class_="location") or
                                card.find("div", class_="location"))
                
                if title_elem and company_elem and location_elem:
                    title = title_elem.get_text(strip=True)
                    company = company_elem.get_text(strip=True)
                    location = location_elem.get_text(strip=True)
                    
                    # Get the job link
                    link = card.get("href", "")
                    if link and not link.startswith("http"):
                        link = "https://www.indeed.com" + link
                    
                    if title and company and location:
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "link": link,
                            "description": f"{title} at {company}"
                        })
            except Exception as e:
                continue  # Skip this job if there's an error
                
    except Exception as e:
        print(f"Error scraping Indeed: {e}")
    
    return jobs

def scrape_jobsnepal_jobs(query="software developer"):
    """
    Scrape job listings from JobsNepal for a given query.
    Returns a list of jobs with title, company, location, and link.
    """
    jobs = []
    try:
        base_url = "https://www.jobsnepal.com/search"
        params = {
            "q": query,
            "page": 1
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        response = requests.get(base_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try multiple possible selectors
        job_cards = soup.find_all("div", class_="job-listing")
        if not job_cards:
            job_cards = soup.find_all("div", class_="job-item")
        if not job_cards:
            job_cards = soup.find_all("div", class_="search-result")
        
        for card in job_cards[:10]:
            try:
                title_elem = (card.find("a", class_="job-title") or
                             card.find("h3") or
                             card.find("a", class_="title"))
                
                company_elem = (card.find("div", class_="company-name") or
                               card.find("span", class_="company") or
                               card.find("div", class_="employer"))
                
                location_elem = (card.find("div", class_="job-location") or
                                card.find("span", class_="location") or
                                card.find("div", class_="address"))
                
                if title_elem and company_elem and location_elem:
                    title = title_elem.get_text(strip=True)
                    company = company_elem.get_text(strip=True)
                    location = location_elem.get_text(strip=True)
                    
                    link = title_elem.get("href", "")
                    if link and not link.startswith("http"):
                        link = "https://www.jobsnepal.com" + link
                    
                    if title and company and location:
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "link": link,
                            "description": f"{title} at {company}"
                        })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Error scraping JobsNepal: {e}")
    
    return jobs

def scrape_merojob_jobs(query="software developer"):
    """
    Scrape job listings from MeroJob for a given query.
    Returns a list of jobs with title, company, location, and link.
    """
    jobs = []
    try:
        base_url = "https://merojob.com/jobs"
        params = {
            "search": query,
            "page": 1
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        response = requests.get(base_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try multiple possible selectors
        job_cards = soup.find_all("div", class_="job-listing")
        if not job_cards:
            job_cards = soup.find_all("div", class_="job-item")
        if not job_cards:
            job_cards = soup.find_all("div", class_="search-result")
        
        for card in job_cards[:10]:
            try:
                title_elem = (card.find("a", class_="job-title") or
                             card.find("h3") or
                             card.find("a", class_="title"))
                
                company_elem = (card.find("div", class_="company-name") or
                               card.find("span", class_="company") or
                               card.find("div", class_="employer"))
                
                location_elem = (card.find("div", class_="job-location") or
                                card.find("span", class_="location") or
                                card.find("div", class_="address"))
                
                if title_elem and company_elem and location_elem:
                    title = title_elem.get_text(strip=True)
                    company = company_elem.get_text(strip=True)
                    location = location_elem.get_text(strip=True)
                    
                    link = title_elem.get("href", "")
                    if link and not link.startswith("http"):
                        link = "https://merojob.com" + link
                    
                    if title and company and location:
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "link": link,
                            "description": f"{title} at {company}"
                        })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Error scraping MeroJob: {e}")
    
    return jobs

def get_global_jobs(query="software developer"):
    """
    Get job recommendations with fallback to mock data if scraping fails.
    """
    jobs = []
    
    # Try to get real jobs first
    try:
        jobs.extend(scrape_indeed_jobs(query=query))
        time.sleep(1)  # Be respectful to servers
    except Exception as e:
        print(f"Indeed scraping failed: {e}")
    
    # If we don't have enough jobs, add mock jobs
    if len(jobs) < 3:
        mock_jobs = get_mock_jobs(query=query)
        # Add mock jobs that aren't duplicates
        seen_titles = {job['title'] for job in jobs}
        for mock_job in mock_jobs:
            if mock_job['title'] not in seen_titles:
                jobs.append(mock_job)
                seen_titles.add(mock_job['title'])
    
    return jobs[:10]  # Return up to 10 jobs

def get_nepal_jobs(query="software developer"):
    """
    Get Nepal-specific job recommendations with fallback to mock data.
    """
    jobs = []
    
    # Try to get real Nepal jobs
    try:
        jobs.extend(scrape_jobsnepal_jobs(query=query))
        time.sleep(1)
    except Exception as e:
        print(f"JobsNepal scraping failed: {e}")
    
    try:
        jobs.extend(scrape_merojob_jobs(query=query))
        time.sleep(1)
    except Exception as e:
        print(f"MeroJob scraping failed: {e}")
    
    # If we don't have enough jobs, add mock jobs
    if len(jobs) < 3:
        mock_jobs = get_mock_jobs(query=query)
        # Add mock jobs that aren't duplicates
        seen_titles = {job['title'] for job in jobs}
        for mock_job in mock_jobs:
            if mock_job['title'] not in seen_titles:
                jobs.append(mock_job)
                seen_titles.add(mock_job['title'])
    
    return jobs[:10]  # Return up to 10 jobs
