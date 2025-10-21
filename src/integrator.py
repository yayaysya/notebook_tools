"""
内容整合引擎
协调各模块,完成笔记到文章的转换流程
"""
import logging
from typing import Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from src.parser import MarkdownParser, ParsedContent
from src.zhipu_client import ZhipuClient
from src.web_scraper import WebScraper

logger = logging.getLogger(__name__)


@dataclass
class ProcessingProgress:
    """处理进度信息"""
    total_images: int = 0
    processed_images: int = 0
    total_links: int = 0
    processed_links: int = 0
    current_stage: str = "初始化"


class ContentIntegrator:
    """内容整合引擎"""

    def __init__(self, api_key: Optional[str] = None, progress_callback: Optional[Callable] = None):
        """
        初始化整合引擎

        Args:
            api_key: 智谱 API Key
            progress_callback: 进度回调函数 callback(progress: ProcessingProgress)
        """
        self.parser = MarkdownParser()
        self.ai_client = ZhipuClient(api_key)
        self.scraper = WebScraper()
        self.progress_callback = progress_callback
        self.progress = ProcessingProgress()

    def process_markdown(self, markdown_text: str, max_workers: int = 5) -> str:
        """
        处理 Markdown 笔记,转换为优化后的文章

        Args:
            markdown_text: 原始 Markdown 文本
            max_workers: 并行处理的最大线程数

        Returns:
            str: 优化后的 Markdown 文章
        """
        try:
            # 阶段1: 解析 Markdown
            self._update_progress("解析 Markdown 内容...")
            parsed = self.parser.parse(markdown_text)
            logger.info(
                f"解析完成: {len(parsed.text_blocks)} 个文本块, "
                f"{len(parsed.images)} 张图片, {len(parsed.links)} 个链接"
            )

            # 阶段2: 并行处理图片和链接
            self._update_progress("处理图片和链接...")
            images_desc = self._process_images(parsed.images, max_workers)
            links_summary = self._process_links(parsed.links, max_workers)

            # 阶段3: 整合并重组文章
            self._update_progress("重组文章内容...")
            article = self._reorganize_content(
                parsed,
                images_desc,
                links_summary
            )

            self._update_progress("处理完成!")
            logger.info("内容整合完成")
            return article

        except Exception as e:
            logger.error(f"处理失败: {str(e)}")
            raise

    def _process_images(self, images: list, max_workers: int) -> list:
        """并行处理图片"""
        if not images:
            return []

        self.progress.total_images = len(images)
        self.progress.processed_images = 0
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_image = {
                executor.submit(self._analyze_single_image, img): img
                for img in images
            }

            for future in as_completed(future_to_image):
                img = future_to_image[future]
                try:
                    description = future.result()
                    results.append({
                        'url': img['url'],
                        'alt': img.get('alt', ''),
                        'description': description,
                        'context': img.get('context', '')
                    })
                except Exception as e:
                    logger.error(f"图片处理失败 ({img['url']}): {str(e)}")
                    results.append({
                        'url': img['url'],
                        'alt': img.get('alt', ''),
                        'description': f"[图片: {img.get('alt', '无描述')}]",
                        'context': img.get('context', '')
                    })
                finally:
                    self.progress.processed_images += 1
                    self._update_progress(
                        f"处理图片 ({self.progress.processed_images}/{self.progress.total_images})..."
                    )

        return results

    def _analyze_single_image(self, img: dict) -> str:
        """分析单张图片"""
        url = img['url']
        context = img.get('context', '')

        prompt = f"""请描述这张图片的内容,要求:
1. 简洁专业,100字以内
2. 适合作为图片说明插入文章
3. 如果图片与上下文相关,请结合上下文理解

上下文: {context[:100] if context else '无'}
"""
        return self.ai_client.analyze_image(url, prompt)

    def _process_links(self, links: list, max_workers: int) -> list:
        """并行处理链接"""
        if not links:
            return []

        self.progress.total_links = len(links)
        self.progress.processed_links = 0
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_link = {
                executor.submit(self._process_single_link, link): link
                for link in links
            }

            for future in as_completed(future_to_link):
                link = future_to_link[future]
                try:
                    summary_data = future.result()
                    results.append(summary_data)
                except Exception as e:
                    logger.error(f"链接处理失败 ({link['url']}): {str(e)}")
                    results.append({
                        'url': link['url'],
                        'title': link.get('title', '链接'),
                        'summary': '[内容获取失败]',
                        'context': link.get('context', '')
                    })
                finally:
                    self.progress.processed_links += 1
                    self._update_progress(
                        f"处理链接 ({self.progress.processed_links}/{self.progress.total_links})..."
                    )

        return results

    def _process_single_link(self, link: dict) -> dict:
        """处理单个链接"""
        url = link['url']
        title = link.get('title', '')
        context = link.get('context', '')

        # 抓取网页内容
        content = self.scraper.fetch_content(url)
        if not content:
            return {
                'url': url,
                'title': title,
                'summary': '[内容抓取失败]',
                'context': context
            }

        # 限制长度避免超过 token 限制
        if len(content) > 3000:
            content = content[:3000] + "..."

        # AI 总结
        summary = self.ai_client.summarize_text(content, context)

        return {
            'url': url,
            'title': title,
            'summary': summary,
            'context': context
        }

    def _reorganize_content(
        self,
        parsed: ParsedContent,
        images_desc: list,
        links_summary: list
    ) -> str:
        """使用 AI 重组内容为文章"""
        return self.ai_client.reorganize_article(
            original_text=parsed.text_blocks,
            images_desc=images_desc,
            links_summary=links_summary,
            tags=parsed.tags,
            front_matter=parsed.front_matter
        )

    def _update_progress(self, stage: str):
        """更新进度"""
        self.progress.current_stage = stage
        if self.progress_callback:
            try:
                self.progress_callback(self.progress)
            except Exception as e:
                logger.warning(f"进度回调失败: {str(e)}")


def process_markdown_file(
    file_path: str,
    api_key: Optional[str] = None,
    progress_callback: Optional[Callable] = None
) -> str:
    """
    处理 Markdown 文件的便捷函数

    Args:
        file_path: MD 文件路径
        api_key: 智谱 API Key
        progress_callback: 进度回调

    Returns:
        str: 优化后的文章
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    integrator = ContentIntegrator(api_key, progress_callback)
    return integrator.process_markdown(content)


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    def print_progress(progress: ProcessingProgress):
        print(f"[进度] {progress.current_stage}")

    test_md = """
# 测试笔记

这是一段测试文本。

![测试图片](https://example.com/test.jpg)

参考这篇文章: [测试链接](https://example.com/article)

更多内容...
"""

    try:
        integrator = ContentIntegrator(progress_callback=print_progress)
        result = integrator.process_markdown(test_md)
        print("\n=== 处理结果 ===")
        print(result)
    except Exception as e:
        print(f"错误: {str(e)}")
