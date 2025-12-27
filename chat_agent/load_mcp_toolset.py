import yaml
import logging
from pathlib import Path
from typing import List

from google.adk.tools.tool_configs import ToolArgsConfig
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

logger = logging.getLogger(__name__)

def load_mcp_toolsets() -> List[McpToolset]:
    """
    Load multiple MCP toolset configurations from the default mcp_toolset.yaml file.
    
    Returns:
        A list of initialized McpToolset objects. Returns an empty list if 
        the file is missing or contains no server configurations.
    """
    # Default to config.yaml in the project root
    root_path = Path(__file__).parent.parent
    file_path = root_path / "config.yaml"

    if not file_path.exists():
        logger.warning(f"MCP toolset configuration file not found at: {file_path}")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)
        
        if not raw_config or "mcpServers" not in raw_config:
            logger.warning(f"MCP configuration is empty or 'mcpServers' key is missing: {file_path}")
            return []

        mcp_servers_config = raw_config["mcpServers"]
        if not isinstance(mcp_servers_config, list):
            logger.error(f"'mcpServers' must be a list in {file_path}")
            return []

        toolsets = []
        for server_config in mcp_servers_config:
            try:
                tool_args_config = ToolArgsConfig.model_validate(server_config)
                toolset = McpToolset.from_config(
                    config=tool_args_config, 
                    config_abs_path=str(file_path.absolute())
                )
                toolsets.append(toolset)
                logger.info(f"Loaded MCP server configuration: {server_config.get('tool_name_prefix', 'unnamed')}")
            except Exception as e:
                logger.error(f"Failed to load individual MCP server config: {e}")

        logger.info(f"Successfully loaded {len(toolsets)} MCP toolsets from {file_path}")
        return toolsets

    except Exception as e:
        logger.error(f"Failed to load MCP toolsets: {e}", exc_info=True)
        return []
