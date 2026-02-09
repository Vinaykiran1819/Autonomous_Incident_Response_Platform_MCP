from mcp.server.fastmcp import FastMCP
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Initialize
mcp = FastMCP("GitHub Sentinel")

# CONFIGURATION
# You need to set this env var, or hardcode it for testing (NOT recommended for prod)
github_token = os.getenv("GITHUB_TOKEN")

if not github_token:
    print("Error: GITHUB_TOKEN not found in environment.")
REPO_OWNER = "Vinaykiran1819"  # CHANGE THIS to your GitHub username
REPO_NAME = "Autonomous_Incident_Response_Platform_MCP" # CHANGE THIS to a repo you own

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

@mcp.tool()
def create_incident_issue(title: str, description: str, severity: str = "High") -> str:
    """
    Creates a GitHub Issue to report an incident. 
    Use this immediately after detecting or resolving a critical failure.
    """
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    
    # Add severity label to the body
    body = f"**Severity:** {severity}\n\n{description}\n\n_Reported by Autonomous AI Agent_"
    
    data = {
        "title": f"[INCIDENT] {title}",
        "body": body,
        "labels": ["incident", "automated"]
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=data)
        if response.status_code == 201:
            issue_data = response.json()
            return f"✅ Incident Report Created: {issue_data['html_url']}"
        else:
            return f"❌ Failed to create issue: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def check_recent_commits(limit: int = 5) -> str:
    """
    Fetches the last N commits.
    Use this to see if a recent code change might have caused the crash.
    """
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

if __name__ == "__main__":
    mcp.run()