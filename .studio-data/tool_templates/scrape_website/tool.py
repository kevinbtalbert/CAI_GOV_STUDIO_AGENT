from typing import Type
from pydantic import BaseModel, Field
from pydantic import BaseModel as StudioBaseTool
from textwrap import dedent

import requests
from bs4 import BeautifulSoup

class UserParameters(BaseModel):
    pass

class WebsiteScraperTool(StudioBaseTool):
    class ToolParameters(BaseModel):
        website: str = Field(description="The website URL to search or fetch data from")

    name: str = "Website Scraper Tool"
    description: str = dedent(
        """
        Fetches and returns the main text content of a website using BeautifulSoup.

        :param url: The URL of the website to scrape.
        :return: The raw text content as a string.
        """
    )
    args_schema: Type[BaseModel] = ToolParameters
    user_parameters: UserParameters

    def _run(self, website: str) -> str:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        }
        
        try:
            # Send a GET request to fetch the HTML content
            response = requests.get(website, headers=headers)
            response.raise_for_status()  # Ensure we catch HTTP errors

            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text content from the page (e.g., from <p> tags)
            content = soup.get_text(separator="\n", strip=True)
            
            return content

        except requests.exceptions.RequestException as e:
            return f"An error occurred while scraping: {e}"
