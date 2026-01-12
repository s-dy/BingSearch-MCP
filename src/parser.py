import re
import uuid
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

from .models import BingSearchResponse,SearchResult


def _parse_li_item(li, index: int) -> Optional[Dict[str, Any]]:
    """解析单个搜索结果项（从 BingSearch 类中提取并简化）"""
    result_item = {
        'title': '',
        'url': '',
        'snippet': '',
        'displayUrl': '',
    }

    # 只处理 b_algo 类型的常规搜索结果
    if 'b_algo' not in li.get('class', []):
        return None

    # 提取标题和链接
    title_elem = li.find('h2')
    if title_elem:
        link_elem = title_elem.find('a')
        if link_elem:
            result_item['title'] = link_elem.get_text().strip()
            result_item['url'] = link_elem.get('href', '')

    # 提取标题和主链接
    title_elem = li.find('h2')
    if title_elem:
        link_elem = title_elem.find('a')
        if not link_elem:
            # 降级,查找任意 a 标签
            link_elem = li.find('a', href=True)
        result_item['title'] = link_elem.get_text().strip()
        result_item['url'] = link_elem.get('href', '').strip()

    # 提取摘要
    caption_elem = li.find('div', class_='b_caption')
    if caption_elem:
        desc_elem = caption_elem.find('p')
        if desc_elem:
            result_item['snippet'] = desc_elem.get_text().strip()

    # 提取显示 URL（cite 元素）
    tpcn_elem = li.find('div', class_='b_tpcn')
    if tpcn_elem:
        cite_elem = tpcn_elem.find('cite')
        if cite_elem:
            result_item['displayUrl'] = cite_elem.get_text().strip()

    # 如果没有标题或链接，视为无效
    if not result_item['title'] or not result_item['url']:
        return None

    return result_item


def parse_bing_search_results(html: str, query: str,count:int=10) -> BingSearchResponse:
    """
    解析必应搜索结果HTML
    :param html: 必应搜索结果页面的HTML字符串
    :param query: 搜索查询词
    :param count: 返回结果数量，默认10条，最多50条
    :return: 解析后的搜索结果，格式为 {'query': str, 'results': List[SearchResult], 'totalResults': Optional[int]}
    """
    soup = BeautifulSoup(html, 'html.parser')
    results:list[SearchResult] = []

    # 查找主结果容器
    b_results = soup.find('ol', id='b_results')
    if not b_results:
        b_results = soup  # 降级：直接在整个文档中查找 .b_algo

    # 遍历每个 .b_algo 元素
    for index, element in enumerate(b_results.select('.b_algo')):
        try:
            parsed_item = _parse_li_item(element, index)
            if parsed_item:
                results.append(SearchResult(
                    uuid = str(uuid.uuid4()),
                    title = parsed_item['title'],
                    url = parsed_item['url'],
                    snippet = parsed_item['snippet'],
                    displayUrl = parsed_item['displayUrl'] or parsed_item['url'],
                ))
        except Exception as e:
            # 忽略单个结果解析错误
            continue

    # 尝试提取总结果数
    total_results: Optional[int] = None
    sb_count_elem = soup.select_one('.sb_count')
    if sb_count_elem:
        count_text = sb_count_elem.get_text()
        # 匹配数字（含逗号）
        match = re.search(r'[\d,]+', count_text)
        if match:
            total_str = match.group().replace(',', '')
            try:
                total_results = int(total_str)
            except ValueError:
                total_results = None

    return BingSearchResponse(
        query = query,
        results = results[:count],
        totalResults = total_results,
    )

