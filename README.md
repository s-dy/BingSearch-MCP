# 必应中文搜索 MCP 工具

> 一个基于 **Model Context Protocol (MCP)** 的必应中文搜索引擎工具，支持关键词搜索与网页内容抓取。

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Docker](https://img.shields.io/badge/Docker-Supported-blue)

---

## 🌟 功能特性

- ✅ **必应中文搜索**：通过关键词获取高质量搜索结果（标题、链接、摘要）
- ✅ **智能网页抓取**：自动提取正文内容，过滤广告、导航栏等噪声
- ✅ **黑名单机制**：自动跳过反爬严格或低质量站点
- ✅ **MCP 兼容**：支持 `stdio` 和 `Streamable HTTP` 两种传输模式
- ✅ **生产就绪**：提供 Docker 部署方案，一键部署到服务器

---

## 📦 快速开始

### 前置要求

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)（推荐）或 pip
- Docker（可选）

### 1. 克隆项目

```bash
git clone https://github.com/s-dy/BingSearch-MCP.git
cd BingSearch-MCP
```

### 2. 安装依赖

使用 `uv`（推荐，速度极快）：
```bash
uv sync
```

或使用 pip：
```bash
pip install -r requirements.txt
```

### 3. 本地运行（HTTP 模式）

```bash
python main.py
```
---

## 🛠 部署方式

### 方式一：Docker 部署（推荐）

```bash
# 构建镜像
docker build -t bing-mcp .

# 运行容器（映射到主机 8080 端口）
docker run -d -p 8080:8080 --name bing-mcp bing-mcp
```

### 方式二：本地 Stdio 模式（用于 IDE 集成）

在 **Cursor / VS Code** 中添加工具：

- **类型**: Local Stdio Tool  
- **命令**: `/path/to/python`  
- **参数**: `["/path/to/BingSearch-MCP/main.py"]`  
- **工作目录**: `/path/to/BingSearch-MCP`

然后在聊天中使用：
```
@bing_cn_search 搜索北京美食推荐
```

---

## 🧩 MCP 工具说明

### 1. `bing_search` —— 执行搜索

```json
{
  "name": "bing_search",
  "arguments": {
    "query": "北京美食",
    "count": 5,
    "offset": 0
  }
}
```

**返回结构**：
```json
{
  "query": "北京美食",
  "results": [
    {
      "uuid": "auto-generated",
      "title": "必收藏！2025“食在朝阳”美食地图...",
      "url": "https://www.visitbeijing.com.cn/...",
      "snippet": "2025黑珍珠餐厅指南发布...",
      "displayUrl": "https://www.visitbeijing.com.cn"
    }
  ],
  "totalResults": 100
}
```

### 2. `crawl_webpage` —— 抓取网页内容

```json
{
  "name": "crawl_webpage",
  "arguments": {
    "uuids": ["uuid1", "uuid2"],
    "url_map": {
      "uuid1": "https://example.com/1",
      "uuid2": "https://example.com/2"
    }
  }
}
```

**返回结构**：
```json
[
  {
    "uuid": "uuid1",
    "url": "https://example.com/1",
    "content": "提取的正文内容...",
    "error": null,
    "isBlacklisted": false
  }
]
```

---

## 📁 项目结构

```
BingSearch/
├── main.py                 # 应用入口（HTTP 启动）
├── src/
│   ├── index.py            # MCP 服务器定义
│   ├── bingSearch.py       # 必应搜索请求
│   ├── parser.py           # 搜索结果解析
│   ├── crawler.py          # 网页内容抓取
│   ├── blacklist.py        # 黑名单规则
│   └── models.py           # Pydantic 数据模型
├── pyproject.toml          # 项目依赖与元数据
└── Dockerfile              # Docker 构建文件
```

---

## ⚙️ 配置说明

### 黑名单管理

编辑 `src/blacklist.py` 中的 `BLACKLISTED_DOMAINS` 列表：

```python
BLACKLISTED_DOMAINS = {
    "zhihu.com",
    "xiaohongshu.com",
    "weibo.com",
    # 添加更多域名...
}
```

### 端口修改

- **容器内端口**：由 `main.py` 中 `port=8080` 决定
- **外部访问端口**：通过 `docker run -p <host>:8080` 灵活映射，**无需重建镜像**

---

## 🔒 注意事项

1. **遵守 robots.txt**：本工具未显式检查，建议避免高频请求。
2. **反爬风险**：必应可能对异常流量限流，请合理使用。
3. **内容合规**：抓取内容仅用于个人学习，勿用于商业用途。
