"""
日志工具模块
提供详细的调试日志功能
"""
import logging
import os
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Any, Dict


def setup_logger(
    name: str,
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_dir: str = "logs",
    log_file_prefix: str = "app",
    max_size_mb: int = 10,
    backup_count: int = 5
) -> logging.Logger:
    """
    配置日志记录器

    Args:
        name: Logger 名称
        log_level: 日志级别 (DEBUG/INFO/WARNING/ERROR)
        log_to_file: 是否输出到文件
        log_dir: 日志目录
        log_file_prefix: 日志文件名前缀
        max_size_mb: 单个日志文件最大大小(MB)
        backup_count: 保留的备份文件数量

    Returns:
        logging.Logger: 配置好的 logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.handlers.clear()  # 清除已有的 handlers

    # 控制台格式化器(简洁)
    console_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    # 文件格式化器(详细)
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 文件处理器
    if log_to_file:
        # 创建日志目录
        Path(log_dir).mkdir(exist_ok=True)

        # 生成日志文件名(带时间戳)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f"{log_dir}/{log_file_prefix}_{timestamp}.log"

        # 使用轮转文件处理器
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_size_mb * 1024 * 1024,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        logger.info(f"📝 日志文件: {log_file}")

    return logger


def log_section(logger: logging.Logger, title: str, char: str = "=", width: int = 70):
    """
    记录一个分隔区域

    Args:
        logger: Logger 实例
        title: 区域标题
        char: 分隔符字符
        width: 分隔线宽度
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(char * width)
        if title:
            logger.debug(title)
            logger.debug(char * width)


def log_dict(logger: logging.Logger, data: Dict[str, Any], indent: int = 2, max_length: int = 500):
    """
    记录字典数据

    Args:
        logger: Logger 实例
        data: 要记录的字典
        indent: 缩进空格数
        max_length: 字符串值的最大长度
    """
    if not logger.isEnabledFor(logging.DEBUG):
        return

    prefix = " " * indent
    for key, value in data.items():
        if isinstance(value, str) and len(value) > max_length:
            logger.debug(f"{prefix}{key}: {value[:max_length]}... (truncated)")
        elif isinstance(value, (list, tuple)) and len(value) > 10:
            logger.debug(f"{prefix}{key}: [{len(value)} items]")
        else:
            logger.debug(f"{prefix}{key}: {value}")


def log_list(logger: logging.Logger, title: str, items: list, max_items: int = 100):
    """
    记录列表数据

    Args:
        logger: Logger 实例
        title: 列表标题
        items: 列表项
        max_items: 最多显示的项数
    """
    if not logger.isEnabledFor(logging.DEBUG):
        return

    logger.debug(f"{title}: {len(items)} 项")
    for i, item in enumerate(items[:max_items], 1):
        if isinstance(item, str):
            preview = item[:100].replace('\n', '\\n')
            logger.debug(f"  [{i}] {preview}{'...' if len(item) > 100 else ''}")
        else:
            logger.debug(f"  [{i}] {item}")

    if len(items) > max_items:
        logger.debug(f"  ... 还有 {len(items) - max_items} 项未显示")


if __name__ == "__main__":
    # 测试日志工具
    logger = setup_logger(
        "test",
        log_level="DEBUG",
        log_to_file=True,
        log_dir="logs",
        log_file_prefix="test"
    )

    logger.info("这是一条 INFO 消息")
    logger.debug("这是一条 DEBUG 消息")

    log_section(logger, "测试区域")
    log_dict(logger, {"key1": "value1", "key2": "这是一个很长的字符串" * 50})
    log_list(logger, "测试列表", ["item1", "item2", "item3"])
    log_section(logger, "")

    print("✅ 日志测试完成,查看 logs/ 目录")
