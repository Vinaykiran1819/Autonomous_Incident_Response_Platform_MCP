# Autonomous-Incident-Response-Platform (MCP-Powered Agentic SRE)

An AI-native Observability and Remediation platform designed to automate root cause analysis and incident resolution for E-commerce microservice failures. This platform utilizes the **Model Context Protocol (MCP)** to eliminate the manual hours that engineers typically spend diagnosing root causes during system outages. Upon receiving an alert, the system automatically coordinates a fleet of AI agents to analyze distributed logs, inspect database performance, and execute infrastructure remediations. It simultaneously documents the entire process through GitHub Reports and Slack notifications.


---

## 🚀 The Problem
In a high-traffic E-commerce Platform, downtime results in immediate revenue loss. Traditionally, when a failure occurs in the microservices layer, a professional SRE must manually:

- Sift through thousands of log lines.

- Query databases to check for locks or latency.

- Inspect Docker container health.

- Audit recent code changes on GitHub.

This process is time-consuming and prone to human error.

---

## 🧠 The AI Solution (MCP Architecture)
To accelerate recovery, I built an AI Assistant using the Model Context Protocol (MCP). This assistant acts as an assistant for SREs, providing a unified reasoning engine that can interact with the entire system stack.

### MCP Servers (The Specialist Departments)
- **Log Analyst (Python)**: Automatically parses shared logs to identify error patterns in various microservices.

- **Database Inspector (Python/SQL)**: Investigates query performance and terminates "stuck" processes.

- **Infrastructure Manager (TypeScript)**: Monitors Docker health and performs surgical container restarts.

- **GitHub Sentinel**: Audits recent commits and creates incident issues for human review.

- **Notification Service**: Provides real-time updates to stakeholders via Slack/Teams.

### Host & Client Definition
- **Host**: Claude Desktop / Custom Python Client (The environment that manages the MCP lifecycle).

- **Client**: The MCP SDK integrated into the Host, acting as the bridge between the AI and local processes.

- **AI Agent**: The Claude 3.5 Sonnet LLM, which provides the reasoning logic to select the correct tools.

---


## 🏗 System Architecture

![System Architecture](./assets/infrastructure_image.png)

---

## ⚡ The Alert-to-Resolution Workflow

This platform is designed to handle the "Heavy Lifting" of incident response automatically:

1.  **Detection:** When an alert triggers in teh dashboard, the user interacts with claude Desktop (Host) to investigate a specific service failure.
2.  **Autonomous Diagnosis:** Instead of an engineer manually running queries, the AI uses the **Log Analyst** and **Database Inspector** to find the root cause in seconds.
3.  **Automated Remediation:** The AI executes a precise fix—such as killing a specific blocked database PID via **Database Inspector tools** or restarting a crashed container - via the **Infrastructure Manager tools**.
4.  **Audit & Notification:** The system simultaneously posts a full incident report to **GitHub Issues** and sends a summary of the fix to **Slack**, keeping the human team informed without requiring their manual intervention.

---

## 🚀 Key Features

* **Autonomous Triage:** The AI agent analyzes structured JSON logs to identify root causes without manual engineer intervention.
* **Database Self-Healing:** Capability to detect and terminate stuck database processes (PIDs) that cause system-wide hangs.
* **Safety Guardrails:** Implements **Human-in-the-Loop (HITL)** safety checks, requiring explicit confirmation before the AI executes destructive actions like container restarts.
* **Polyglot Integration:** A seamless mix of Python-based data analysis and Node.js-based infrastructure management unified under a single protocol.

---

### 🛠️ Microservice Incident & Tool Mapping

The platform monitors three critical microservices that form the backbone of the Ecommerce application:


| Microservice | Responsibility | Example Incident | Recommended MCP servers |
| :--- | :--- | :--- | :--- |
| **Auth Service** | Manages user sessions and identity. | `403 Forbidden: Token Issuer Mismatch` | **Log Analyst** |
| **Inventory Service** | Tracks stock levels and reservations. | `504 Gateway Timeout: Database Lock` | **Log Analyst**, **DB Inspector** |
| **Payment Service** | Processes financial transactions. | `Container Exit: Out of Memory (OOM)` | **Log Analyst**, **Infra Manager** |

---

## 🛠 Technology Stack

| Category | Tools |
| :--- | :--- |
| **Protocol** | Model Context Protocol (MCP) |
| **Languages** | Python 3.9, TypeScript, Node.js |
| **Infrastructure** | Docker, Docker Compose, PostgreSQL |
| **Libraries** | Pandas, FastAPI, Dockerode, Psycopg2 |
| **Notifications** | Slack Webhooks, GitHub API |

---

## 📖 Getting Started

### 1. Prerequisites
* Docker and Docker Compose installed.
* An MCP-compatible client (such as Claude Desktop).
* GitHub Personal Access Token and a Slack Webhook URL.

### 2. Configuration
Create a `.env` file in the root directory based on the provided example:
```env
GITHUB_TOKEN=your_github_token
REPO_OWNER=your_username
REPO_NAME=your_repo_name
SLACK_WEBHOOK_URL=your_slack_webhook
```

### 3. Deployment

``` Bash
docker-compose up -d
```
Connect the MCP servers located in the mcp-servers/ directory to your client configuration to begin autonomous monitoring.

## Example Use Case

**Scenario:** The Ecommerce Platform is throwing 504 Gateway Timeouts on the checkout page. Customers cannot complete purchases.


