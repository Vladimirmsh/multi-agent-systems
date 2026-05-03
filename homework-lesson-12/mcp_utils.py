import asyncio
from langchain_core.tools import StructuredTool

def mcp_tools_to_langchain(mcp_client):
    """Конвертує інструменти FastMCP у формат LangChain з логуванням."""
    langchain_tools = []
    
    async def fetch_tools():
        async with mcp_client:
            return await mcp_client.list_tools()
            
    try:
        tools = asyncio.run(fetch_tools())
    except Exception as e:
        print(f"❌ Помилка отримання інструментів з MCP: {e}")
        return []
    
    for t in tools:
        def create_tool_wrapper(tool_name, tool_desc):
            def wrapper(**kwargs):
                print(f"   🔧 [MCP Call] {tool_name} -> {kwargs}")
                async def execute_tool():
                    async with mcp_client:
                        res = await mcp_client.call_tool(tool_name, kwargs)
                        # Обробка різних форматів відповіді FastMCP 3.x
                        return res.data if hasattr(res, 'data') else str(res)
                
                try:
                    result = asyncio.run(execute_tool())
                    print(f"   📎 [MCP Result] {tool_name} успішно виконано (довжина: {len(str(result))})")
                    return result
                except Exception as e:
                    print(f"   ❌ [MCP Error] {tool_name}: {e}")
                    return f"Error calling tool {tool_name}: {str(e)}"
            
            wrapper.__doc__ = tool_desc or f"Tool {tool_name}"
            wrapper.__name__ = tool_name
            
            return StructuredTool.from_function(
                func=wrapper,
                name=tool_name,
                description=tool_desc or f"Tool {tool_name}"
            )
            
        langchain_tools.append(create_tool_wrapper(t.name, t.description))
        
    return langchain_tools