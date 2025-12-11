#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VideoSlim - A video compression application using x264
Refactored version: v1.8
"""

import logging
import tkinter as tk

from src.controller import Controller
from src.service import init_services
from src.view import View


def setup_logging():
    """
    配置日志记录功能
    该函数用于设置Python的日志记录系统，将日志信息写入到文件中。
    配置包括日志级别、输出文件、文件写入模式以及日志格式。
    """
    logging.basicConfig(
        level=logging.INFO,
        filename="log.txt",
        filemode="w",
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8",
    )


def main():
    setup_logging()

    init_services()

    root = tk.Tk()
    app = View(root, Controller())
    root.mainloop()


if __name__ == "__main__":
    main()
