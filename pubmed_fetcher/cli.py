#!/usr/bin/env python3
import argparse
import logging
import sys
from typing import Optional
from .fetcher import PubMedFetcher
from .affiliations import AffiliationAnalyzer
from .csv_writer import CSVWriter

def setup_logging(debug: bool = False) -> None:
    """Configure logging based on debug flag."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=level
    )

def main():
    parser = argparse.ArgumentParser(
        description="Fetch PubMed papers with industry affiliations"
    )
    parser.add_argument(
        "query",
        help="PubMed search query"
    )
    parser.add_argument(
        "-f", "--file",
        help="Output CSV file (default: print to stdout)"
    )
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "-e", "--email",
        required=True,
        help="Email address to identify yourself to PubMed"
    )
    parser.add_argument(
        "-k", "--api-key",
        help="PubMed API key for higher rate limits"
    )
    parser.add_argument(
        "-m", "--max-results",
        type=int,
        default=100,
        help="Maximum number of results to fetch (default: 100)"
    )
    
    args = parser.parse_args()
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize components
        fetcher = PubMedFetcher(email=args.email, api_key=args.api_key)
        analyzer = AffiliationAnalyzer()
        writer = CSVWriter()
        
        logger.info(f"Searching PubMed for: {args.query}")
        paper_ids = fetcher.search_papers(args.query, args.max_results)
        
        papers_with_industry = []
        for paper_id in paper_ids:
            paper = fetcher.fetch_paper_details(paper_id)
            if not paper:
                continue
                
            industry_authors, companies = analyzer.analyze_affiliations(paper)
            if industry_authors:
                paper["IndustryAuthors"] = industry_authors
                paper["Companies"] = companies
                papers_with_industry.append(paper)
        
        logger.info(f"Found {len(papers_with_industry)} papers with industry affiliations")
        writer.write_to_csv(papers_with_industry, args.file)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()