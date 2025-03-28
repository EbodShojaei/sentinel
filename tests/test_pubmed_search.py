"""
test_pubmed_search.py: A simple test file to verify the PubMed search functionality.
"""

# import logging
import sys
from src.utils.pubmed_search import run_pubmed_search


def test_pubmed_search():
    # Example search term for testing.
    # If you already include field tags (e.g., [Mesh]), don't append additional field tags.
    search_term = '("Osteoarthritis, Knee"[Mesh] OR knee osteoarthritis)'
    min_year = 2020
    max_year = 2025

    print(f"Testing PubMed search with search_term: {search_term}")
    articles = run_pubmed_search(search_term, min_year, max_year)
    print(f"Retrieved {len(articles)} articles.")

    # Add assertions to verify the results.
    assert isinstance(articles, list)  # check that the return is a list
    assert len(articles) > 0  # check that the list is not empty.
    if articles:
        # check that the first article has a title key.
        assert 'Title' in articles[0]
