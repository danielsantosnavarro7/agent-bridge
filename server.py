import os
import time
import asyncio
from fastmcp import FastMCP

mcp = FastMCP("AgentBridge")

messages = []
tasks = {}

@mcp.tool()
def send_message(sender: str, recipient: str, content: str) -> str:
    """Send a message to another agent."""
    msg = {
        "id": len(messages) + 1,
        "sender": sender,
        "recipient": recipient,
        "content": content,
        "timestamp": time.time(),
        "read": False,
    }
    messages.append(msg)
    return f"Message #{msg['id']} sent to {recipient}."

@mcp.tool()
def read_messages(recipient: str, unread_only: bool = True) -> list[dict]:
    """Read messages addressed to you."""
    results = []
    for m in messages:
        if m["recipient"] == recipient and (not unread_only or not m["read"]):
            m["read"] = True
            results.append(m)
    return results

@mcp.tool()
async def wait_for_message(recipient: str, timeout_seconds: int = 120) -> dict | str:
    """Block and wait until a new unread message arrives for you."""
    start = time.time()
    while time.time() - start < timeout_seconds:
        for m in messages:
            if m["recipient"] == recipient and not m["read"]:
                m["read"] = True
                return m
        await asyncio.sleep(2)
    return "No new messages before timeout. Call wait_for_message again to keep listening."

@mcp.tool()
def claim_task(agent: str, task_name: str) -> str:
    """Claim a task so the other agent doesn't duplicate work."""
    if task_name in tasks:
        return f"Task '{task_name}' is already claimed by {tasks[task_name]}."
    tasks[task_name] = agent
    return f"Task '{task_name}' claimed by {agent}."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
    