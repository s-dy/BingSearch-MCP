"""
爬虫黑名单配置模块
定义禁止爬取的网站域名列表

爬虫黑名单 - 禁止抓取的网站域名
包括但不限于:
- 社交媒体平台 (知乎、小红书、微博等)
- 短视频平台 (抖音、TikTok等)
- 即时通讯平台 (微信公众号等)
- 视频平台 (B站等)
"""

from urllib.parse import urlparse

CRAWLER_BLACKLIST: list[str] = [
    # 知乎
    'zhihu.com',
    'www.zhihu.com',
    'zhuanlan.zhihu.com',

    # 小红书
    'xiaohongshu.com',
    'www.xiaohongshu.com',
    'xhs.com',

    # 微博
    'weibo.com',
    'www.weibo.com',
    'm.weibo.com',

    # 微信
    'weixin.qq.com',
    'mp.weixin.qq.com',

    # 抖音/TikTok
    'douyin.com',
    'www.douyin.com',
    'tiktok.com',
    'www.tiktok.com',

    # B站
    'bilibili.com',
    'www.bilibili.com',
    'm.bilibili.com',

    # CSDN
    'csdn.net',
    'www.csdn.net',
    'blog.csdn.net',
]


def is_url_blacklisted(url: str) -> bool:
    """
    检查URL是否在黑名单中
    :param url: 要检查的URL
    :return: 如果在黑名单中返回True，否则返回False
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False
        hostname = hostname.lower()

        for domain in CRAWLER_BLACKLIST:
            lower_domain = domain.lower()
            # 完全匹配 或 子域名匹配（如 user.zhihu.com 匹配 zhihu.com）
            if hostname == lower_domain or hostname.endswith('.' + lower_domain):
                return True
        return False

    except Exception as e:
        return False
