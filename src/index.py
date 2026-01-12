"""
必应中文搜索 MCP 服务器
提供必应搜索和网页抓取工具给 MCP 客户端使用
"""
import asyncio
import json
from typing import Dict, List
from mcp.server import FastMCP
from mcp.types import TextContent,CallToolResult

from .bingSearch import fetch_bing_search
from .parser import parse_bing_search_results
from .crawler import crawl_web_pages

# 创建 MCP 服务器
server = FastMCP(name="bing-cn-search")

@server.tool()
async def bing_search(query: str,count: int = 10,offset: int = 0) -> CallToolResult:
    """
    使用必应中文搜索引擎搜索信息。返回搜索结果包括标题、链接和摘要。

    Args:
        query: 搜索关键词或查询语句
        count: 返回结果数量，默认10条，最多50条
        offset: 结果偏移量，用于分页，默认0
    """
    # 参数校验
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query 必须是非空字符串")
    if not (1 <= count <= 50):
        raise ValueError("count 必须在 1-50 之间")
    if offset < 0:
        raise ValueError("offset 不能小于 0")

    query = query.strip()
    # logger.info(f"执行必应搜索: '{query}', count={count}, offset={offset}")

    try:
        # 1. 获取 HTML
        html = await asyncio.to_thread(fetch_bing_search, query, offset)

        # 2. 解析结果
        search_response = parse_bing_search_results(html, query)

        # 3. 返回 JSON 文本
        content = json.dumps(search_response.model_dump(), ensure_ascii=False, indent=2)
        return CallToolResult(
            content=[TextContent(type="text", text=content)]
        )

    except Exception as e:
        error_msg = f"搜索失败: {str(e)}"
        # logger.error(error_msg)
        return CallToolResult(
            content=[TextContent(type="text", text=error_msg)],
            isError=True
        )


@server.tool()
async def crawl_webpage(uuids: List[str],url_map: Dict[str, str]) -> CallToolResult:
    """
    根据搜索结果的UUID抓取网页内容。支持批量抓取多个网页。
    会自动过滤黑名单中的网站。

    Args:
        uuids: 搜索结果的UUID列表
        url_map: UUID到URL的映射对象，格式: {"uuid1": "url1", ...}
    """
    if not isinstance(uuids, list) or len(uuids) == 0:
        raise ValueError("uuids 必须是非空列表")
    if not isinstance(url_map, dict):
        raise ValueError("url_map 必须是字典")

    # 验证所有 UUID 是否在 url_map 中
    missing = [uid for uid in uuids if uid not in url_map]
    if missing:
        error_msg = f"以下 UUID 在 url_map 中不存在: {', '.join(missing)}"
        # logger.error(error_msg)
        return CallToolResult(
            content=[TextContent(type="text", text=error_msg)],
            isError=True
        )

    # 构建目标映射
    target_url_map = {uid: url_map[uid] for uid in uuids}
    # logger.info(f"开始抓取网页，UUID数量: {len(target_url_map)}")

    try:
        # 执行抓取（在独立线程中避免阻塞事件循环）
        results = await asyncio.to_thread(crawl_web_pages, target_url_map)

        # 转换为 JSON
        serializable_results = [r.model_dump() for r in results]
        content = json.dumps(serializable_results, ensure_ascii=False, indent=2)

        return CallToolResult(
            content=[TextContent(type="text", text=content)]
        )

    except Exception as e:
        error_msg = f"抓取失败: {str(e)}"
        # logger.error(error_msg)
        return CallToolResult(
            content=[TextContent(type="text", text=error_msg)],
            isError=True
        )
