"""
xlsx_export.py: Contains functions to export the search results and metadata to an Excel file with two tabs.
"""

import os
import pandas as pd
from datetime import datetime
from src.utils.database import SearchResult, Metadata

def check_filename(filename):
    """
    Check if the filename is valid.
    - Filename should not be empty.
    - Filename should not contain slashes.
    - Filename should end with .xlsx
    - If no extension is provided, append .xlsx.
    - If no folder path is provided, use "data" as the default folder.
    - Ensure the output folder exists.
    - If filename does not contain folder path, prepend it.
    - Return the full path of the filename.
    """
    if not filename:
        raise ValueError("Filename cannot be empty.")

    if "/" in filename or "\\" in filename:
        raise ValueError("Filename should not contain slashes.")

    if not filename.endswith(".xlsx"):
        filename += ".xlsx"

    if not os.path.splitext(filename)[1]:
        filename += ".xlsx"

    if not os.path.exists("data"):
        os.makedirs("data")

    if not filename.startswith("data"):
        filename = os.path.join("data", filename)

    return filename

def export_to_excel(session, metadata_id, filename="output.xlsx"):
    """
    Export search results and metadata to an Excel file with two sheets.
    Sheet1: Search Results
    Sheet2: Metadata
    """
    # Retrieve data from database
    results = session.query(SearchResult).filter(SearchResult.metadata_id == metadata_id).all()
    metadata = session.query(Metadata).filter(Metadata.id == metadata_id).first()

    # Create DataFrame for search results
    results_data = []
    for result in results:
        results_data.append({
            "PMID": result.pmid,
            "Title": result.title,
            "Authors": result.authors,
            "Abstract": result.abstract,
            "DOI": result.doi,
            "Link": result.link,
            "Year": result.year
        })
    df_results = pd.DataFrame(results_data)

    # Create DataFrame for metadata
    metadata_data = {
        "min_year": [metadata.min_year],
        "max_year": [metadata.max_year],
        "research_purpose": [metadata.research_purpose],
        "mesh_strategy": [metadata.mesh_strategy],
        "export_date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    }
    df_metadata = pd.DataFrame(metadata_data)

    # Check the filename
    filename = check_filename(filename)

    # Export to Excel with two sheets
    with pd.ExcelWriter(filename) as writer:
        df_results.to_excel(writer, sheet_name="Search Results", index=False)
        df_metadata.to_excel(writer, sheet_name="Metadata", index=False)
