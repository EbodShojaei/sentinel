"""
pubmed_search.py: Contains functions to interact with the PubMed API using a given search term (or MeSH strategy).
This version optionally uses a PubMed API key if provided in the .env file and formats the date range using the [dp] tag.
Example query format (when the search term already contains field tags):
    {search_term} AND ("{min_year}/01/01"[dp] : "{max_year}/12/31"[dp])
"""

# import logging
from typing import List, Dict
import time
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv
from Bio import Entrez

# Load environment variables from .env file
load_dotenv()

# Set your email for Entrez from the environment variable
ENTREZ_EMAIL = os.getenv("ENTREZ_EMAIL")
if not ENTREZ_EMAIL:
    raise ValueError("Please set ENTREZ_EMAIL in your .env file.")
Entrez.email = ENTREZ_EMAIL

# Optionally set the PubMed API key if provided
PUBMED_API_KEY = os.getenv("PUBMED_API_KEY")
if PUBMED_API_KEY:
    print("Using PubMed API key for enhanced rate limits.")
    Entrez.api_key = PUBMED_API_KEY


def run_pubmed_search(search_term: str, min_year: int, max_year: int) -> List[Dict]:
    """
    Execute a PubMed search using the provided search term (or MeSH strategy) and date range.
    Retrieve up to 250 articles sorted by relevance.
    Returns a list of dictionaries with article details.

    The query is formatted as:
      {search_term} AND ("{min_year}/01/01"[dp] : "{max_year}/12/31"[dp])
    """
    # Construct query with date filters.
    query = f'{search_term} AND "{min_year}/01/01"[dp] : "{max_year}/12/31"[dp]'
    # logging.info("Final query for PubMed: %s", query)
    print(f"Final query for PubMed: {query}")

    try:
        # Use Entrez.esearch to get a list of PubMed IDs (up to 250).
        handle = Entrez.esearch(db="pubmed", term=query,
                                retmax=250, sort="relevance")
        search_results = Entrez.read(handle)
        handle.close()
        id_list = search_results.get("IdList", [])
        # logging.info("Found %d PubMed IDs", len(id_list))
        print(f"Found {len(id_list)} PubMed IDs")
    except Exception as e:
        # logging.error("Error during Entrez.esearch: %s", str(e))
        print(f"Error during Entrez.esearch: {str(e)}")
        return []

    articles = []
    if id_list:
        try:
            # Fetch article details in batches to avoid overloading the API.
            batch_size = 50
            for start in range(0, len(id_list), batch_size):
                end = min(start + batch_size, len(id_list))
                batch_ids = id_list[start:end]
                fetch_handle = Entrez.efetch(
                    db="pubmed", id=batch_ids, retmode="xml")
                data = fetch_handle.read()
                fetch_handle.close()
                # Parse XML to extract article details.
                root = ET.fromstring(data)
                for article in root.findall(".//PubmedArticle"):
                    details = parse_article(article)
                    articles.append(details)
                time.sleep(0.5)  # Pause to comply with NCBI rate limits.
        except Exception as e:
            # logging.error("Error during Entrez.efetch: %s", str(e))
            print(f"Error during Entrez.efetch: {str(e)}")

    # Sort articles by publication year in descending order.
    articles.sort(key=lambda x: x.get("Year", 0), reverse=True)
    return articles


def parse_article(article_xml) -> dict:
    """
    Parse a PubMed article XML element and extract relevant details.
    """
    article_data = {}
    # Extract PMID.
    pmid_elem = article_xml.find(".//PMID")
    article_data["PMID"] = pmid_elem.text if pmid_elem is not None else "N/A"

    # Extract Title.
    title_elem = article_xml.find(".//ArticleTitle")
    article_data["Title"] = title_elem.text if title_elem is not None else "No Title"

    # Extract Abstract.
    abstract_texts = []
    for abstract in article_xml.findall(".//AbstractText"):
        if abstract.text:
            abstract_texts.append(abstract.text.strip())
    article_data["Abstract"] = " ".join(
        abstract_texts) if abstract_texts else "No Abstract"

    # Extract Authors.
    authors_list = []
    for author in article_xml.findall(".//Author"):
        last_name = author.find("LastName")
        fore_name = author.find("ForeName")
        if last_name is not None and fore_name is not None:
            authors_list.append(f"{fore_name.text} {last_name.text}")
    article_data["Authors"] = ", ".join(
        authors_list) if authors_list else "No Authors"

    # Extract DOI.
    doi = "N/A"
    for id_elem in article_xml.findall(".//ArticleId"):
        if id_elem.get("IdType") == "doi":
            doi = id_elem.text
            break
    article_data["DOI"] = doi

    # Create a link to the article on PubMed.
    article_data["Link"] = f"https://pubmed.ncbi.nlm.nih.gov/{article_data['PMID']}/"

    # Extract Publication Year.
    year = 0
    pub_date = article_xml.find(".//PubDate")
    if pub_date is not None:
        year_elem = pub_date.find("Year")
        if year_elem is not None and year_elem.text and year_elem.text.isdigit():
            year = int(year_elem.text)
    article_data["Year"] = year

    # Placeholder for internal RefID (to be assigned later).
    article_data["RefID"] = ""

    return article_data
