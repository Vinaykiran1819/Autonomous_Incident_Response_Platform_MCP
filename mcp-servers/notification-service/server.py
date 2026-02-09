from mcp.server.fastmcp import FastMCP
import requests
import os
import sys

# Initialize
mcp = FastMCP("Notification Service")

# ==============================================================================
# 1. WINDOWS ENCODING FIX
# ==============================================================================
try:
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding.lower() != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# ==============================================================================
# 2. GET URL FROM CONFIG
# ==============================================================================
# We don't need load_dotenv() anymore because Claude injects this variable for us!
WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

@mcp.tool()
def send_alert(message: str, severity: str = "INFO") -> str:
    """
    Sends a notification to the DevOps team chat (Slack).
    """
    # Format message with emojis
    try:
        emoji = "🚨" if severity == "CRITICAL" else "ℹ️"
        formatted_msg = f"{emoji} **[{severity}]** {message}"
    except:
        formatted_msg = f"**[{severity}]** {message}"

    # CHECK: Do we have the URL?
    if not WEBHOOK_URL:
        return "⚠️ CONFIG ERROR: SLACK_WEBHOOK_URL is missing from claude_desktop_config.json."

    if "hooks.slack.com" not in WEBHOOK_URL:
         return "⚠️ CONFIG ERROR: The URL in your config does not look like a Slack webhook."

    # SEND REAL ALERT
    payload = {"text": formatted_msg}
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            return "✅ SUCCESS: Message sent to Slack!"
        else:
            return f"❌ Slack Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()