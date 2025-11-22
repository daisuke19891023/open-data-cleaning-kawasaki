"""E2E tests for MCP interface functionality."""

import pytest
from fastmcp import Client

from kawasaki_etl.interfaces.factory import InterfaceFactory
from kawasaki_etl.interfaces.mcp import MCPInterface
from kawasaki_etl.types import InterfaceType


class TestMCPInterfaceE2E:
    """E2E tests for MCP interface."""

    @pytest.fixture
    def mcp_interface(self, monkeypatch: pytest.MonkeyPatch) -> MCPInterface:
        """Create an MCP interface instance."""
        monkeypatch.setenv("INTERFACE_TYPE", "mcp")
        factory = InterfaceFactory()
        interface = factory.create(InterfaceType.MCP)
        assert isinstance(interface, MCPInterface)
        return interface

    @pytest.mark.asyncio  # pyright: ignore [reportUnknownMemberType, reportUntypedFunctionDecorator, reportAttributeAccessIssue]
    async def test_welcome_tool(self, mcp_interface: MCPInterface) -> None:
        """Test that the welcome tool returns the correct message."""
        async with Client(mcp_interface.mcp) as client:
            result = await client.call_tool("welcome")
            assert "Welcome to Kawasaki ETL!" in str(result)
            assert "Type --help for more information" in str(result)
