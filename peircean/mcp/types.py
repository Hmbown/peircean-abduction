from pydantic import BaseModel


class ToolAnnotations(BaseModel):
    """Annotations for MCP tools."""
    readOnlyHint: bool = False
    idempotentHint: bool = False
