import requests
import re

def extract_username(github_url: str) -> str:
    match = re.search(r'github\.com/([^/]+)', github_url)
    return match.group(1) if match else github_url.split('/')[-1] if github_url else None

def scrape_github(github_url: str) -> dict:
    """
    Pulls recent repositories directly from the public GitHub REST API.
    """
    username = extract_username(github_url)
    if not username:
        return {"error": "Invalid GitHub URL"}

    top_repos = []
    
    # Real integration utilizing the requests module:
    url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=3"
    headers = {"Accept": "application/vnd.github.v3+json"} 
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            for r in response.json():
                # Append raw features mapped for Gemini optimization logic
                top_repos.append({
                    "name": r.get("name"), 
                    "description": r.get("description"), 
                    "language": r.get("language")
                })
    except Exception as e:
        print(f"GitHub Scrape Exception: {e}")
        
    return {
        "username": username,
        "recent_repos": top_repos,
    }
