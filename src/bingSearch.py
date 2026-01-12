"""
必应搜索API模块
负责发起HTTP请求并获取搜索页面HTML
"""
import uuid
import requests
from fake_useragent import UserAgent

# 用户代理池
USER_AGENTS = UserAgent()

# 基础配置
BING_SEARCH_URL = 'https://cn.bing.com/search'
DEFAULT_HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'referer': 'https://cn.bing.com/',
    'upgrade-insecure-requests': '1',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
}


def _generate_random_cvid() -> str:
    """生成随机 cvid（模拟浏览器行为）"""
    return str(uuid.uuid4()).upper().replace('-', '')


def fetch_bing_search(query: str, offset: int = 0) -> str:
    """
    执行必应搜索请求，返回原始HTML

    Args:
        query: 搜索关键词
        offset: 偏移量（从0开始），对应 Bing 的 first = offset + 1

    Returns:
        必应搜索结果页面的 HTML 字符串

    Raises:
        RuntimeError: 当请求失败时
    """
    # 构建参数（Bing 使用 first 表示起始位置，从1开始）
    params = {
        'q': query,
        'first': offset + 1,
        'form': 'QBLH',
        'sp': '-1',
        'lq': '0',
        'pq': query,
        'sc': '12-3',
        'qs': 'n',
        'sk': '',
        'cvid': _generate_random_cvid(),
        'FORM': 'PERE'
    }

    # 构建 headers
    headers = DEFAULT_HEADERS.copy()
    headers['User-Agent'] = USER_AGENTS.random

    try:
        response = requests.get(
            BING_SEARCH_URL,
            params=params,
            headers=headers,
            timeout=15,
            allow_redirects=True
        )
        response.raise_for_status()

        # 确保正确编码（避免中文乱码）
        response.encoding = response.apparent_encoding or 'utf-8'
        return response.text

    except requests.exceptions.Timeout:
        raise RuntimeError("必应搜索请求失败: 请求超时（15秒）")
    except requests.exceptions.ConnectionError:
        raise RuntimeError("必应搜索请求失败: 无法连接到服务器")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"必应搜索请求失败: HTTP {e.response.status_code} - {e.response.reason}")
    except Exception as e:
        raise RuntimeError(f"必应搜索请求失败: {str(e)}")
