import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os

def scrape_nber_working_papers(start_paper: int | None = None, end_paper: int | None = None, batch_size=10, output_file="data/nber_papers.parquet"):
    base_url = "https://www.nber.org/papers/"

    data = []
    counter = 0

    output_directory = os.path.dirname(output_file)
    if output_directory:
        os.makedirs(output_directory, exist_ok=True)

    if start_paper is None:
        start_paper = 1
        if os.path.exists(output_file):
            existing_df = pd.read_parquet(output_file)
            if not existing_df.empty:
                max_paper = existing_df["Working Paper Number"].max()
                start_paper = int(max_paper) + 1

    end_description = end_paper if end_paper is not None else "first non-200 response"
    print(f"Scraping papers from {start_paper} through {end_description}...")

    paper_number = start_paper
    while end_paper is None or paper_number <= end_paper:
        paper_url = f"{base_url}w{paper_number:04d}"
        print(f"Scraping {paper_url}...")
        
        # Send a GET request to the working paper page
        response = requests.get(paper_url)
        if response.status_code != 200:
            print(f"Failed to retrieve paper {paper_number}. Status code: {response.status_code}")
            break
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract information
        title_tag = soup.find('h1', class_='page-header__title')
        abstract_tag = soup.find('div', class_='page-header__intro-inner')
        citation_items = soup.find_all('div', class_='page-header__citation-item')
        issue_date_tag = citation_items[2] if len(citation_items) > 2 else None
        time_tag = issue_date_tag.find('time') if issue_date_tag else None
        author_tags = soup.find('div', class_='page-header__authors js-expandable-list')
        
        title = title_tag.text.strip() if title_tag else "No title available"
        abstract = abstract_tag.text.strip() if abstract_tag else "No abstract available"
        issue_date = time_tag.text.strip() if time_tag else "No issue date available"
        authors = [author.text.strip() for author in author_tags.find_all('a')] if author_tags else []
        authors_string = ", ".join(authors[:-1]) + " & " + authors[-1] if len(authors) > 1 else authors[0] if authors else ""
        citation_tag = soup.select_one(".citation-field")
        citation = citation_tag.get_text(" ", strip=True) if citation_tag else ""

        published_heading = next(
            (
                heading
                for heading in soup.select(".promo-grid__rich-text h2")
                if heading.get_text(" ", strip=True) == "Published Versions"
            ),
            None,
        )
        published_container = published_heading.parent if published_heading else None
        published_version = (
            " ".join(
                paragraph.get_text(" ", strip=True)
                for paragraph in published_container.find_all("p")
            )
            if published_container
            else ""
        )
        related = {}
        for item in soup.select(".info-grid__item"):
            item_title = item.select_one(".info-grid__item-title")
            if item_title:
                label = item_title.get_text(" ", strip=True)
                if label in ("Topics", "Programs"):
                    related[label] = "; ".join(
                        link.get_text(" ", strip=True)
                        for link in item.select(".info-grid__item-body a")
                    )

        data.append({"Working Paper Number": paper_number,
                    "Title": title,
                    "Authors": authors_string,
                    "Date": issue_date,
                    "Abstract": abstract,
                    "Citation": citation,
                    "Published": bool(published_version),
                    "Published Version": published_version,
                    "Topics": related.get("Topics", ""),
                    "Programs": related.get("Programs", "")})
        
        counter += 1
        
        # Save to parquet every batch_size papers
        if counter % batch_size == 0:
            batch_df = pd.DataFrame(data)
            try:
                existing_df = pd.read_parquet(output_file)
                combined_df = pd.concat([existing_df, batch_df], ignore_index=True)
            except FileNotFoundError:
                combined_df = batch_df
            combined_df.to_parquet(output_file, index=False)
            data = []  # Reset data list
            print(f"Saved batch of {batch_size} papers to {output_file}")
        
        # Pause to avoid overwhelming the server
        sleep_time = random.uniform(10, 30)  # Random sleep between 20 and 60 seconds
        print(f"Sleeping for {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)
        paper_number += 1
    
    # Save any remaining data
    if data:
        batch_df = pd.DataFrame(data)
        try:
            existing_df = pd.read_parquet(output_file)
            combined_df = pd.concat([existing_df, batch_df], ignore_index=True)
        except FileNotFoundError:
            combined_df = batch_df
        combined_df.to_parquet(output_file, index=False)
        print(f"Saved remaining data to {output_file}")
    
    print(f"Scraped data saved to {output_file}")

if __name__ == "__main__":
    scrape_nber_working_papers()
