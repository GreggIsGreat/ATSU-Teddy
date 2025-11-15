import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import random


def scrape_jobsbotswana(max_pages=5):
    base_url = "https://jobsbotswana.info"
    all_jobs = []

    for page in range(1, max_pages + 1):
        if page == 1:
            url = f"{base_url}/jobs/"
        else:
            url = f"{base_url}/jobs/page/{page}/"

        print(f"Scraping page {page}: {url}")

        try:
            # Add headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all job listings - update these selectors based on actual page structure
            job_listings = soup.select('article.job-list')  # Update this selector

            if not job_listings:
                print(f"No job listings found on page {page}")
                break

            for job in job_listings:
                try:
                    title_elem = job.select_one('h3 a')
                    company_elem = job.select_one('.company')
                    location_elem = job.select_one('.location')
                    date_elem = job.select_one('.date')
                    salary_elem = job.select_one('.salary')

                    job_data = {
                        'title': title_elem.get_text(strip=True) if title_elem else 'N/A',
                        'company': company_elem.get_text(strip=True) if company_elem else 'N/A',
                        'location': location_elem.get_text(strip=True) if location_elem else 'N/A',
                        'posted_date': date_elem.get_text(strip=True) if date_elem else 'N/A',
                        'salary': salary_elem.get_text(strip=True) if salary_elem else 'Not specified',
                        'link': urljoin(base_url, title_elem['href']) if title_elem and title_elem.has_attr(
                            'href') else 'N/A',
                        'source': 'jobsbotswana.info'
                    }

                    all_jobs.append(job_data)
                    print(f"Found job: {job_data['title']}")

                except Exception as e:
                    print(f"Error processing job listing: {e}")
                    continue

            # Add delay between requests to be respectful to the server
            time.sleep(random.uniform(1, 3))

        except requests.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break

    return all_jobs


def save_to_json(jobs, filename='job_listings.json'):
    import json
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(jobs)} jobs to {filename}")


if __name__ == "__main__":
    jobs = scrape_jobsbotswana(max_pages=3)  # Scrape first 3 pages
    save_to_json(jobs)