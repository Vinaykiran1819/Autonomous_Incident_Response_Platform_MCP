from mcp.server.fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv

# 1. Load environment variables from the .env file
load_dotenv()

# Initialize
mcp = FastMCP("GitHub Sentinel")

# 2. Get variables safely
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")

# Safety Check: Warn if token is missing
if not GITHUB_TOKEN:
    raise ValueError("❌ Error: GITHUB_TOKEN not found. Did you create the .env file?")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

@mcp.tool()
def create_incident_issue(title: str, description: str, severity: str = "High") -> str:
    """Creates a GitHub Issue to report an incident."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    
    body = f"**Severity:** {severity}\n\n{description}\n\n_Reported by Autonomous AI Agent_"
    
    data = {
        "title": f"[INCIDENT] {title}",
        "body": body,
        "labels": ["incident", "automated"]
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=data)
        if response.status_code == 201:
            return f"✅ Incident Report Created: {response.json()['html_url']}"
        else:
            return f"❌ Failed to create issue ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def check_recent_commits(limit: int = 5) -> str:
    """Fetches the last N commits."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits?per_page={limit}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            commits = response.json()
            summary = []
            for c in commits:
                msg = c['commit']['message'].split('\n')[0]
                author = c['commit']['author']['name']
                date = c['commit']['author']['date']
                summary.append(f"- [{date}] {author}: {msg}")
            return "\n".join(summary)
        else:
            return f"❌ Failed to fetch commits: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_file_content(file_path: str) -> str:
    """
    Fetches the actual code/content of a file from the repository.
    Use this to audit code logic or check configuration files.
    """
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            # GitHub returns file content as a base64 encoded string
            # We must decode it to plain text for the AI to read it
            file_bytes = base64.b64decode(data['content'])
            content = file_bytes.decode('utf-8')
            return f"--- Content of {file_path} ---\n\n{content}"
        elif response.status_code == 404:
            return f"❌ Error: File '{file_path}' not found in the repository."
        else:
            return f"❌ Failed to fetch file: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()