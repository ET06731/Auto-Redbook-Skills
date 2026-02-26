#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书笔记发布脚本

使用方法:
    # 基本发布
    python publish_new.py -t "标题" -d "正文描述" -i cover.png card_1.png card_2.png

    # 设为私密笔记
    python publish_new.py -t "标题" -d "正文描述" -i cover.png --private

    # 定时发布
    python publish_new.py -t "标题" -d "正文描述" -i cover.png --post-time "2024-12-01 10:00:00"

环境变量:
    在脚本同目录或项目根目录下创建 .env 文件，配置：

    XHS_COOKIE=your_cookie_string_here

    Cookie 获取方式：
    1. 在浏览器中登录小红书（https://www.xiaohongshu.com）
    2. 打开开发者工具（F12）
    3. 在 Network 标签中查看任意请求的 Cookie 头
    4. 复制完整的 cookie 字符串

依赖安装:
    pip install xhs python-dotenv requests
"""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import argparse
import os
import json
import re
from pathlib import Path
from typing import List, Optional, Dict, Any

try:
    from dotenv import load_dotenv
    import requests
except ImportError as e:
    print(f"缺少依赖: {e}")
    print("请运行: pip install python-dotenv requests")
    sys.exit(1)


def load_cookie() -> str:
    """从 .env 文件加载 Cookie，依次尝试当前目录、上级目录、再上级目录"""
    env_paths = [
        Path.cwd() / ".env",
        Path(__file__).parent.parent / ".env",
        Path(__file__).parent.parent.parent / ".env",
    ]

    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break

    cookie = os.getenv("XHS_COOKIE")
    if not cookie:
        print("❌ 错误: 未找到 XHS_COOKIE 环境变量")
        print("请创建 .env 文件，添加以下内容：")
        print("XHS_COOKIE=your_cookie_string_here")
        sys.exit(1)
    return cookie


def parse_cookie(cookie_string: str) -> Dict[str, str]:
    """解析 Cookie 字符串为字典"""
    cookies = {}
    for item in cookie_string.split(";"):
        item = item.strip()
        if "=" in item:
            key, value = item.split("=", 1)
            cookies[key.strip()] = value.strip()
    return cookies


def validate_cookie(cookie_string: str) -> bool:
    """验证 Cookie 是否包含必要的字段（a1 和 web_session）"""
    cookies = parse_cookie(cookie_string)
    required_fields = ["a1", "web_session"]
    missing = [f for f in required_fields if f not in cookies]
    if missing:
        print(f"⚠️  Cookie 可能不完整，缺少字段: {', '.join(missing)}")
        print("这可能导致签名失败，请确保 Cookie 包含 a1 和 web_session 字段")
        return False
    return True


def validate_images(image_paths: List[str]) -> List[str]:
    """验证图片文件是否存在，返回有效图片的绝对路径列表"""
    valid_images = []
    for path in image_paths:
        if os.path.exists(path):
            valid_images.append(os.path.abspath(path))
        else:
            print(f"⚠️  警告: 图片不存在 - {path}")
    if not valid_images:
        print("❌ 错误: 没有有效的图片文件")
        sys.exit(1)
    return valid_images


class LocalPublisher:
    """本地发布模式：直接使用 xhs 库进行签名和发布"""

    def __init__(self, cookie: str):
        self.cookie = cookie
        self.client = None

    def init_client(self):
        """初始化 xhs 客户端，使用 Cookie 中的 a1 值进行本地签名"""
        try:
            from xhs import XhsClient
            from xhs.help import sign as local_sign
        except ImportError:
            print("❌ 错误: 缺少 xhs 库")
            print("请运行: pip install xhs")
            sys.exit(1)

        # 解析 a1 值用于签名
        cookies = parse_cookie(self.cookie)
        a1 = cookies.get("a1", "")

        def sign_func(uri, data=None, a1="", web_session=""):
            # 使用 Cookie 中提取的 a1 值进行本地签名
            return local_sign(uri, data, a1=a1)

        self.client = XhsClient(cookie=self.cookie, sign=sign_func)

    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """获取当前登录用户信息，可用于验证 Cookie 是否有效"""
        try:
            info = self.client.get_self_info()
            print(f"👤 当前用户: {info.get('nickname', '未知')}")
            return info
        except Exception as e:
            print(f"⚠️  无法获取用户信息: {e}")
            return None

    def publish(
        self,
        title: str,
        desc: str,
        images: List[str],
        is_private: bool = False,
        post_time: str = None,
    ) -> Dict[str, Any]:
        """
        发布图文笔记。

        Args:
            title: 笔记标题（建议不超过 20 字）
            desc: 笔记正文描述
            images: 图片绝对路径列表
            is_private: 是否设为私密笔记
            post_time: 定时发布时间，格式 "2024-01-01 12:00:00"，None 表示立即发布
        """
        print(f"\n🚀 准备发布笔记（本地模式）...")
        print(f"  📌 标题: {title}")
        print(f"  📝 描述: {desc[:50]}..." if len(desc) > 50 else f"  📝 描述: {desc}")
        print(f"  🖼️  图片数量: {len(images)}")

        try:
            result = self.client.create_image_note(
                title=title,
                desc=desc,
                files=images,
                is_private=is_private,
                post_time=post_time,
            )

            print("\n✨ 笔记发布成功！")
            if isinstance(result, dict):
                note_id = result.get("note_id") or result.get("id")
                if note_id:
                    print(f"  📎 笔记ID: {note_id}")
                    print(f"  🔗 链接: https://www.xiaohongshu.com/explore/{note_id}")
            return result

        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ 发布失败: {error_msg}")

            # 提供具体的错误排查建议
            if "sign" in error_msg.lower() or "signature" in error_msg.lower():
                print("\n💡 签名错误排查建议：")
                print("1. 确保 Cookie 包含有效的 a1 和 web_session 字段")
                print("2. Cookie 可能已过期，请重新获取")
            elif "cookie" in error_msg.lower():
                print("\n💡 Cookie 错误排查建议：")
                print("1. 确保 Cookie 格式正确（从浏览器开发者工具 Network 标签复制）")
                print("2. Cookie 可能已过期，请重新登录小红书后重新获取")

            raise


def main():
    parser = argparse.ArgumentParser(
        description="将图片发布为小红书笔记",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 通过 md 文件传入正文（推荐）
  python publish_xhs.py -t "我的标题" -f note.md -i card_1.png card_2.png cover.png

  # 直接传入正文文本
  python publish_xhs.py -t "我的标题" -d "正文内容" -i cover.png

  # 设为私密笔记
  python publish_xhs.py -t "我的标题" -f note.md -i cover.png --private

  # 定时发布
  python publish_xhs.py -t "我的标题" -f note.md -i cover.png --post-time "2024-12-01 10:00:00"
""",
    )
    parser.add_argument("--title", "-t", required=True, help="笔记标题（建议不超过 20 字）")
    parser.add_argument("--desc", "-d", default="", help="笔记描述/正文内容（与 --desc-file 二选一）")
    parser.add_argument("--desc-file", "-f", default=None, help="从 Markdown 文件读取正文内容（优先于 --desc）")
    parser.add_argument("--images", "-i", nargs="+", required=True, help="图片文件路径（可以多个）")
    parser.add_argument("--private", action="store_true", help="是否设为私密笔记")
    parser.add_argument("--post-time", default=None, help="定时发布时间（格式：2024-01-01 12:00:00）")

    args = parser.parse_args()

    # 正文内容：优先从文件读取，其次使用 --desc 文本
    desc = args.desc
    if args.desc_file:
        desc_path = Path(args.desc_file)
        if not desc_path.exists():
            print(f"❌ 错误: 正文文件不存在 - {args.desc_file}")
            sys.exit(1)
        desc = desc_path.read_text(encoding="utf-8")
        print(f"📄 已读取正文文件: {args.desc_file} ({len(desc)} 字符)")

    cookie = load_cookie()
    validate_cookie(cookie)
    valid_images = validate_images(args.images)

    publisher = LocalPublisher(cookie)
    publisher.init_client()

    try:
        publisher.publish(
            title=args.title,
            desc=desc,
            images=valid_images,
            is_private=args.private,
            post_time=args.post_time,
        )
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
