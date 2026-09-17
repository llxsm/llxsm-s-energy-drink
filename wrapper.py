import os
import sys
import webbrowser

import webview


def resource_path(rel):
    """PyInstaller 单文件模式下资源位于临时解包目录，否则在脚本同目录。"""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


class Api:
    """暴露给前端 JS 调用的接口。"""

    def open_url(self, url):
        webbrowser.open(url)


def main():
    html_path = resource_path("app.html")
    with open(html_path, encoding="utf-8") as f:
        html = f.read()

    webview.create_window(
        "浪里小神猫的能量小站",
        html=html,
        width=520,
        height=780,
        resizable=True,
        js_api=Api(),
    )
    webview.start()


if __name__ == "__main__":
    main()
