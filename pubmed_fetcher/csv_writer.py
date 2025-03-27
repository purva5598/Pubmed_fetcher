import csv
from typing import List, Dict, Optional
import sys
import logging

class CSVWriter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def write_to_csv(self, papers: List[Dict], filename: Optional[str] = None) -> None:
        """Write paper data to CSV file or stdout."""
        if not papers:
            self.logger.warning("No papers to write")
            return

        fieldnames = [
            "PubmedID",
            "Title",
            "PublicationDate",
            "NonAcademicAuthors",
            "CompanyAffiliations",
            "CorrespondingAuthorEmail"
        ]

        try:
            if filename:
                with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self._prepare_rows(papers))
                self.logger.info(f"Successfully wrote results to {filename}")
            else:
                writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
                writer.writeheader()
                for row in self._prepare_rows(papers):
                    writer.writerow(row)
        except Exception as e:
            self.logger.error(f"Error writing CSV: {e}")
            raise

    def _prepare_rows(self, papers: List[Dict]) -> List[Dict]:
        """Prepare paper data for CSV output."""
        rows = []
        for paper in papers:
            row = {
                "PubmedID": paper.get("PubmedID", ""),
                "Title": paper.get("Title", ""),
                "PublicationDate": paper.get("PublicationDate", ""),
                "NonAcademicAuthors": "; ".join(
                    [auth["name"] for auth in paper.get("IndustryAuthors", [])]
                ),
                "CompanyAffiliations": "; ".join(
                    paper.get("Companies", [])
                ),
                "CorrespondingAuthorEmail": "; ".join(
                    paper.get("Emails", [])
                )
            }
            rows.append(row)
        return rows