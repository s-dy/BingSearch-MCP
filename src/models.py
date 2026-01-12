from pydantic import BaseModel
from typing import Optional

# 搜索结果项
class SearchResult(BaseModel):
  uuid: str         # 唯一标识符
  title: str        # 标题
  url: str          # 链接
  snippet: str      # 摘要/描述
  displayUrl: str  # 显示的URL


# 搜索响应
class BingSearchResponse(BaseModel):
  query: str           # 搜索查询词
  results: list[SearchResult] # 搜索结果列表
  totalResults: Optional[int] = 0   # 结果总数（估算）


# 搜索选项
class SearchOptions(BaseModel):
  count: int      # 返回结果数量，默认10
  offset: int     # 偏移量，用于分页
  market: str     # 市场/语言，默认zh-CN

# 单个网页抓取结果
class PageResult(BaseModel):
    uuid: str
    url: str
    content: Optional[str] = None
    error: Optional[str] = None
    isBlacklisted: bool = False
