"""
网页内容抓取模块
实现双重策略: readability (主) + Jina AI Reader (备)
"""
import logging
from typing import Optional
import requests
from bs4 import BeautifulSoup
from readability import Document
from config import config

logger = logging.getLogger(__name__)


class WebScraper:
    """网页内容抓取器"""

    def __init__(self):
        self.timeout = config.REQUEST_TIMEOUT
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

    def fetch_content(self, url: str) -> Optional[str]:
        """
        抓取网页内容(自动尝试多种方法)

        Args:
            url: 网页 URL

        Returns:
            Optional[str]: 提取的正文内容,失败返回 None
        """
        logger.info(f"开始抓取: {url}")

        # 策略1: readability (快速)
        content = self._fetch_with_readability(url)
        if content:
            logger.info(f"成功使用 readability 抓取: {url}")
            return content

        # 策略2: Jina AI Reader (后备)
        logger.warning(f"readability 失败,尝试 Jina AI: {url}")
        content = self._fetch_with_jina(url)
        if content:
            logger.info(f"成功使用 Jina AI 抓取: {url}")
            return content

        logger.error(f"所有抓取方法均失败: {url}")
        return None

    def _fetch_with_readability(self, url: str) -> Optional[str]:
        """
        使用 readability-lxml 提取正文

        Args:
            url: 网页 URL

        Returns:
            Optional[str]: 正文内容
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()

            # 使用 readability 提取正文
            doc = Document(response.content)
            html_content = doc.summary()

            # 使用 BeautifulSoup 清洗 HTML
            soup = BeautifulSoup(html_content, 'lxml')

            # 移除脚本和样式
            for tag in soup(['script', 'style', 'nav', 'footer', 'aside']):
                tag.decompose()

            # 提取文本
            text = soup.get_text(separator='\n', strip=True)

            # 清洗空行
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            clean_text = '\n'.join(lines)

            if len(clean_text) < 100:
                logger.warning(f"提取的内容过短 ({len(clean_text)} 字): {url}")
                return None

            return clean_text

        except requests.RequestException as e:
            logger.error(f"请求失败 ({url}): {str(e)}")
            return None
        except Exception as e:
            logger.error(f"readability 解析失败 ({url}): {str(e)}")
            return None

    def _fetch_with_jina(self, url: str) -> Optional[str]:
        """
        使用 Jina AI Reader 提取正文

        Args:
            url: 网页 URL

        Returns:
            Optional[str]: 正文内容 (Markdown 格式)
        """
        try:
            jina_url = f"{config.JINA_READER_BASE}{url}"

            response = requests.get(
                jina_url,
                headers={'Accept': 'text/plain'},
                timeout=self.timeout
            )
            response.raise_for_status()

            content = response.text.strip()

            if len(content) < 100:
                logger.warning(f"Jina 返回内容过短 ({len(content)} 字): {url}")
                return None

            return content

        except requests.RequestException as e:
            logger.error(f"Jina AI 请求失败 ({url}): {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Jina AI 解析失败 ({url}): {str(e)}")
            return None

    def fetch_multiple(self, urls: list[str]) -> dict[str, Optional[str]]:
        """
        批量抓取多个网页

        Args:
            urls: URL 列表

        Returns:
            dict: {url: content} 映射
        """
        results = {}
        for url in urls:
            results[url] = self.fetch_content(url)
        return results


# 便捷函数
def fetch_webpage(url: str) -> Optional[str]:
    """
    抓取单个网页的便捷函数

    Args:
        url: 网页 URL

    Returns:
        Optional[str]: 正文内容
    """
    scraper = WebScraper()
    return scraper.fetch_content(url)


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    scraper = WebScraper()

    # 测试 URL (可替换为实际 URL)
    test_urls = [
        "https://example.com",  # 替换为实际测试 URL
    ]

    for url in test_urls:
        print(f"\n测试抓取: {url}")
        content = scraper.fetch_content(url)
        if content:
            print(f"成功! 内容长度: {len(content)} 字")
            print(f"前 200 字: {content[:200]}...")
        else:
            print("失败!")
