import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import Docker from "dockerode";
import { z } from "zod";
import * as os from "os";

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
// TOOL 2: RESTART CONTAINER (With Safety Check)
// =============================================================================
server.tool(
    "restart_container",
    "Restarts a specific Docker container. REQUIRES CONFIRMATION for safety.",
    {
        container_name: z.string().describe("The name of the container to restart"),
        confirm: z.boolean().describe("Set to true to actually execute the restart. If false, it only checks if the container exists."),
    },
    async ({ container_name, confirm }) => {
        try {
            // 1. Find the container
            const containers = await docker.listContainers({ all: true });
            const target = containers.find(c => c.Names.some(n => n.includes(container_name)));

            if (!target) {
                return {
                    content: [{ type: "text", text: `❌ Container '${container_name}' not found.` }],
                    isError: true,
                };
            }

            // 2. Safety Check
            if (confirm !== true) {
                return {
                    content: [{ type: "text", text: `⚠️ SAFETY PAUSE: I found container '${container_name}' (${target.Status}).\nTo actually restart it, you must explicitly confirm.\n\nRun the tool again with 'confirm: true'.` }],
                };
            }

            // 3. Execute Restart (Only if confirmed)
            const container = docker.getContainer(target.Id);
            await container.restart();

            return {
                content: [{ type: "text", text: `✅ SUCCESS: Container '${container_name}' has been restarted.` }],
            };
        } catch (error) {
            return {
                content: [{ type: "text", text: `❌ Failed to restart ${container_name}: ${error}` }],
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