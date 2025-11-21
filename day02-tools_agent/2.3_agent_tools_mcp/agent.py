import asyncio
import base64
import uuid
from pathlib import Path

from google.genai import types

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from google.adk.apps.app import App, ResumabilityConfig
from google.adk.tools.function_tool import FunctionTool
from google.adk.runners import InMemoryRunner


print("✅ ADK components imported successfully.")

from dotenv import load_dotenv

load_dotenv()



retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

# MCP integration with Everything Server
mcp_image_server = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",  # Run MCP server via npx
            args=[
                "-y",  # Argument for npx to auto-confirm install
                "@modelcontextprotocol/server-everything",
            ],
            tool_filter=["getTinyImage"],
        ),
        timeout=30,
    )
)

print("✅ MCP Tool created")


image_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="ImageAgent",
    instruction="""
    You are an image analysis assistant. Your task is to generate a image for user request.
    """,
    tools=[mcp_image_server],
)


runner = InMemoryRunner(agent=image_agent)

response = asyncio.run(runner.run_debug("Provide a sample tiny image", verbose=True))


def handle_image_content(response) -> None:
    """Display images inline when possible and always save them as PNG files."""

    try:
        from IPython.display import display, Image as IPImage  # type: ignore

        can_display = True
    except ImportError:
        display = None  # type: ignore
        IPImage = None  # type: ignore
        can_display = False

    output_dir = Path("generated_images")
    output_dir.mkdir(parents=True, exist_ok=True)

    image_count = 0

    for event in response:
        if not (event.content and event.content.parts):
            continue

        for part in event.content.parts:
            if not (hasattr(part, "function_response") and part.function_response):
                continue

            for item in part.function_response.response.get("content", []):
                if item.get("type") != "image":
                    continue

                img_bytes = base64.b64decode(item["data"])
                file_path = output_dir / f"tool_image_{image_count}.png"
                file_path.write_bytes(img_bytes)
                print(f"🖼️ Saved tool image to {file_path}")

                if can_display and display and IPImage:
                    display(IPImage(data=img_bytes))

                image_count += 1

    if image_count == 0:
        print("ℹ️ No image data was returned in the response.")


handle_image_content(response)
