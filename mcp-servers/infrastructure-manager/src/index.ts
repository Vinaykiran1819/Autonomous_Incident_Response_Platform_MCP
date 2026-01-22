import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import Docker from "dockerode";
import { z } from "zod";
import os from "os";

// =============================================================================
// 1. WINDOWS COMPATIBILITY FIX
// Docker on Windows uses a Named Pipe. Linux uses a Socket File.
// We detect the OS to choose the correct connection path.
// =============================================================================
const isWindows = os.platform() === "win32";
const socketPath = isWindows ? "//./pipe/docker_engine" : "/var/run/docker.sock";

console.error(`🔌 Connecting to Docker at: ${socketPath}`);

const docker = new Docker({ socketPath });

// =============================================================================
// 2. INITIALIZE MCP SERVER
// =============================================================================
const server = new McpServer({
    name: "Infrastructure Manager",
    version: "1.0.0",
});

// =============================================================================
// TOOL 1: LIST CONTAINERS
// =============================================================================
server.tool(
    "list_containers",
    "List all active containers to check their health status and names.",
    {}, // No arguments needed
    async () => {
        try {
            const containers = await docker.listContainers({ all: true });

            if (containers.length === 0) {
                return {
                    content: [{ type: "text", text: "No containers found. Is Docker running?" }],
                };
            }

            const summary = containers.map(c => ({
                id: c.Id.substring(0, 12),
                name: c.Names[0].replace("/", ""), // Remove leading slash
                state: c.State,
                status: c.Status,
                image: c.Image
            }));

            return {
                content: [{ type: "text", text: JSON.stringify(summary, null, 2) }],
            };
        } catch (error) {
            return {
                content: [{ type: "text", text: `Error listing containers: ${error}` }],
                isError: true,
            };
        }
    }
);

// =============================================================================
// TOOL 2: RESTART CONTAINER (The "Action")
// =============================================================================
server.tool(
    "restart_container",
    "Restarts a specific Docker container to fix crashes or memory leaks.",
    {
        container_name: z.string().describe("The name of the container to restart (e.g., prod_payment_service)"),
    },
    async ({ container_name }) => {
        try {
            // 1. Find the container by name
            const containers = await docker.listContainers({ all: true });
            const target = containers.find(c => c.Names.some(n => n.includes(container_name)));

            if (!target) {
                return {
                    content: [{ type: "text", text: `Container '${container_name}' not found.` }],
                    isError: true,
                };
            }

            // 2. Get the container object
            const container = docker.getContainer(target.Id);

            // 3. Restart it
            await container.restart();

            return {
                content: [{ type: "text", text: `Successfully restarted container: ${container_name}` }],
            };
        } catch (error) {
            return {
                content: [{ type: "text", text: `Failed to restart ${container_name}: ${error}` }],
                isError: true,
            };
        }
    }
);

// =============================================================================
// START SERVER
// =============================================================================
async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("🚀 Infrastructure Manager running on stdio");
}

main().catch((error) => {
    console.error("Fatal error:", error);
    process.exit(1);
});