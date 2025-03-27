from typing import List, Dict, Optional
from Bio import Entrez
from datetime import datetime
import xml.etree.ElementTree as ET
import logging

class PubMedFetcher:
    def __init__(self, email: str, api_key: Optional[str] = None):
        """Initialize the PubMed fetcher with email and optional API key."""
        Entrez.email = email
        if api_key:
            Entrez.api_key = api_key
        self.logger = logging.getLogger(__name__)

    def search_papers(self, query: str, max_results: int = 100) -> List[str]:
        """Search PubMed and return list of paper IDs."""
        try:
            with Entrez.esearch(db="pubmed", term=query, retmax=max_results) as handle:
                record = Entrez.read(handle)
            return record["IdList"]
        except Exception as e:
            self.logger.error(f"Error searching PubMed: {e}")
            raise

    def fetch_paper_details(self, paper_id: str) -> Dict:
        """Fetch detailed information for a single paper."""
        try:
            # Fetch details in XML format for more comprehensive data
            with Entrez.efetch(db="pubmed", id=paper_id, retmode="xml") as handle:
                xml_data = handle.read()
            
            root = ET.fromstring(xml_data)
            article = root.find(".//PubmedArticle")
            
            if article is None:
                return {}
            
            return self._parse_article_xml(article)
        except Exception as e:
            self.logger.error(f"Error fetching paper details for {paper_id}: {e}")
            return {}

    def _parse_article_xml(self, article: ET.Element) -> Dict:
        """Parse XML data for a single article into a structured dictionary."""
        medline = article.find(".//MedlineCitation")
        pubmed = article.find(".//PubmedData")
        
        # Basic information
        paper = {
            "PubmedID": medline.find(".//PMID").text if medline.find(".//PMID") is not None else "",
            "Title": self._get_article_title(medline),
            "PublicationDate": self._get_publication_date(medline),
            "Authors": [],
            "Affiliations": [],
            "Emails": []
        }
        
        # Author information
        author_list = medline.find(".//AuthorList")
        if author_list is not None:
            for author in author_list.findall(".//Author"):
                author_data = {
                    "LastName": author.find(".//LastName").text if author.find(".//LastName") is not None else "",
                    "ForeName": author.find(".//ForeName").text if author.find(".//ForeName") is not None else "",
                    "AffiliationInfo": [],
                    "Email": ""
                }
                
                # Extract affiliations
                affiliations = author.findall(".//Affiliation")
                for affil in affiliations:
                    if affil.text:
                        author_data["AffiliationInfo"].append(affil.text)
                
                paper["Authors"].append(author_data)
        
        # Corresponding author emails
        if pubmed is not None:
            for article_id in pubmed.findall(".//ArticleId"):
                if article_id.attrib.get("IdType", "") == "doi":
                    paper["DOI"] = article_id.text
        
        return paper

    def _get_article_title(self, medline: ET.Element) -> str:
        """Extract article title from XML."""
        article = medline.find(".//Article")
        if article is not None:
            title = article.find(".//ArticleTitle")
            if title is not None:
                return "".join(title.itertext())
        return ""

    def _get_publication_date(self, medline: ET.Element) -> str:
        """Extract publication date from XML."""
        article_date = medline.find(".//ArticleDate")
        if article_date is not None:
            year = article_date.find(".//Year").text if article_date.find(".//Year") is not None else ""
            month = article_date.find(".//Month").text if article_date.find(".//Month") is not None else ""
            day = article_date.find(".//Day").text if article_date.find(".//Day") is not None else ""
            return f"{year}-{month}-{day}"
        
        # Fallback to PubDate
        pub_date = medline.find(".//PubDate")
        if pub_date is not None:
            year = pub_date.find(".//Year").text if pub_date.find(".//Year") is not None else ""
            month = pub_date.find(".//Month").text if pub_date.find(".//Month") is not None else ""
            day = pub_date.find(".//Day").text if pub_date.find(".//Day") is not None else ""
            return f"{year}-{month}-{day}"
        
        return ""