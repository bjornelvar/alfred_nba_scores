import requests
from bs4 import BeautifulSoup
import os
import time

def download_image(image_url, filename):
    """
    Download and save an image from a given URL.
    """
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)

# Base URL of the NBA website
base_url = 'https://www.nba.com/teams'

# Send a GET request to the NBA website
response = requests.get(base_url)

# Parse the HTML content of the page
soup = BeautifulSoup(response.text, 'html.parser')

# Find all <a> tags with the specific class
team_links = soup.find_all('a', class_='Anchor_anchor__cSc3P TeamFigureLink_teamFigureLink__uqnNO')

# Extract team IDs from the href attribute
team_ids = [link['href'].split('/')[2] for link in team_links if '/team/' in link['href']]

# Base URL for the logo images
logo_base_url = 'https://cdn.nba.com/logos/nba/{}/global/L/logo.svg'

# Create URLs for each team's logo
logo_urls = {team_id: logo_base_url.format(team_id) for team_id in team_ids}

# Print or download the logos
for team_id, logo_url in logo_urls.items():
    print(f"Team ID: {team_id}, Logo URL: {logo_url}")

    # Uncomment the following lines if you want to download the logos
    filename = f"{team_id}.svg"
    download_image(logo_url, filename)
