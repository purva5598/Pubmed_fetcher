from typing import List, Dict, Tuple
import re

class AffiliationAnalyzer:
    def __init__(self):
        # Keywords that typically indicate academic affiliations
        self.academic_keywords = [
            "university", "college", "institute", "academy", 
            "school", "faculty", "labs?", "laboratory", 
            "hospital", "clinic", "medical center",
            "government", "ministry", "agency", 
            "foundation", "non.?profit", "nonprofit",
            "research", "center", "centre"
        ]
        
        # Keywords that might indicate industry affiliations
        self.industry_keywords = [
            "pharma", "biotech", "bio.?tech", "pharmaceutical",
            "inc", "ltd", "llc", "corporation", "corp", 
            "company", "co\\.", "ag", "gmbh", "holding",
            "industr", "healthcare", "medical", "therapeutics",
            "genetics", "vaccin", "drug", "medicine"
        ]
        
        self.academic_regex = re.compile(
            "|".join(self.academic_keywords), 
            flags=re.IGNORECASE
        )
        self.industry_regex = re.compile(
            "|".join(self.industry_keywords), 
            flags=re.IGNORECASE
        )

    def analyze_affiliations(self, paper: Dict) -> Tuple[List[Dict], List[str]]:
        """Analyze authors and return industry-affiliated authors and their companies."""
        industry_authors = []
        companies = set()
        
        for author in paper.get("Authors", []):
            industry_affiliations = []
            author_companies = set()
            
            for affiliation in author.get("AffiliationInfo", []):
                if self._is_industry_affiliation(affiliation):
                    company = self._extract_company_name(affiliation)
                    if company:
                        author_companies.add(company)
                        industry_affiliations.append(affiliation)
            
            if author_companies:
                industry_authors.append({
                    "name": f"{author.get('ForeName', '')} {author.get('LastName', '')}".strip(),
                    "affiliations": industry_affiliations,
                    "companies": list(author_companies)
                })
                companies.update(author_companies)
        
        return industry_authors, list(companies)

    def _is_industry_affiliation(self, affiliation: str) -> bool:
        """Determine if an affiliation is likely from industry."""
        if not affiliation:
            return False
            
        # Check if it looks like an academic affiliation
        if self.academic_regex.search(affiliation):
            return False
            
        # Check if it has industry indicators
        return bool(self.industry_regex.search(affiliation))

    def _extract_company_name(self, affiliation: str) -> str:
        """Extract a clean company name from an affiliation string."""
        # Simple approach - take the first part before comma
        parts = [p.strip() for p in affiliation.split(",")]
        if parts:
            return parts[0]
        return affiliation