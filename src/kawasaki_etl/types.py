"""Type definitions for kawasaki_etl."""

from enum import Enum


class InterfaceType(str, Enum):
    """Available interface types."""

    CLI = "cli"
    RESTAPI = "restapi"
    MCP = "mcp"
