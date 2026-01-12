"""
网页爬虫模块
负责根据UUID抓取搜索结果中的网页内容
使用 trafilatura 智能提取网页正文，避免手动选择器的脆弱性
"""

import requests
import trafilatura
from typing import Dict, List
from fake_useragent import UserAgent

from .blacklist import is_url_blacklisted
from .models import PageResult

# 用户代理池
USER_AGENTS = UserAgent()

def fetch_web_page(url: str) -> str:
    """
    抓取并提取网页正文内容

    Args:
        url: 要抓取的完整URL

    Returns:
        提取的干净文本内容（纯文本，已去除HTML标签、广告、导航等）

    Raises:
        ValueError: 当URL在黑名单中、请求失败或内容无效时
    """
    # 1. 黑名单检查（合规优先）
    if is_url_blacklisted(url):
        raise ValueError(f"该网站在爬虫黑名单中，禁止抓取: {url}")

    try:
        # 2. 发起HTTP请求
        response = requests.get(
            url,
            headers={'User-Agent': USER_AGENTS.random},
            timeout=30,  # 30秒超时
            allow_redirects=True  # 允许重定向
        )
        response.raise_for_status()

        # 3. 设置正确编码（避免中文乱码）
        response.encoding = response.apparent_encoding or 'utf-8'

        # 4. 使用 trafilatura 提取正文
        content = trafilatura.extract(
            filecontent=response.text,
            url=url,
            output_format='txt',  # 返回纯文本
            include_comments=False,  # 不包含评论
            include_tables=True,  # 保留表格内容
            no_fallback=False,  # 主提取失败时启用回退策略
            favor_precision=False  # 宁可多提取，也不错漏（适合通用场景）
        )

        # 5. 验证内容有效性
        if not content or len(content.strip()) < 50:
            raise ValueError("提取的内容太少或为空")

        return content.strip()

    except requests.exceptions.Timeout:
        raise ValueError("抓取网页失败: 请求超时（30秒）")
    except requests.exceptions.ConnectionError:
        raise ValueError("抓取网页失败: 无法连接到服务器")
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"抓取网页失败: HTTP {e.response.status_code} - {e.response.reason}")
    except Exception as e:
        raise ValueError(f"抓取或解析网页失败: {str(e)}")


def crawl_web_pages(url_map: Dict[str, str]) -> List[PageResult]:
    """
    批量抓取多个网页内容

    Args:
        url_map: UUID 到 URL 的映射，例如 {"uuid1": "https://example.com"}

    Returns:
        抓取结果列表，每个元素为字典，包含以下字段：
        - uuid: 原始UUID
        - url: 抓取的URL
        - content: 成功时返回的文本内容（可选）
        - error: 失败时的错误信息（可选）
        - isBlacklisted: 是否因黑名单被拒绝（可选）
    """
    results: List[PageResult] = []

    for uuid_key, url in url_map.items():
        try:
            if is_url_blacklisted(url):
                result = PageResult(
                    uuid=uuid_key,
                    url=url,
                    error="该网站在爬虫黑名单中，禁止抓取",
                    isBlacklisted=True
                )
            else:
                content = fetch_web_page(url)
                result = PageResult(
                    uuid=uuid_key,
                    url=url,
                    content=content
                )
        except Exception as e:
            result = PageResult(
                uuid=uuid_key,
                url=url,
                error=str(e)
            )
        results.append(result)

    return results
