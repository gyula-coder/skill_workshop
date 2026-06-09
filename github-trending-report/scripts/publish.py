#!/usr/bin/env python3
"""
微信公众号文章发布 - 主流程脚本

整合所有模块，实现从Markdown文章到微信公众号草稿箱的一键发布：
1. 读取Markdown文章
2. 处理文章中的图片（下载+上传到微信）
3. 转换为微信兼容HTML（内联样式排版）
4. 准备封面图
5. 调用API创建草稿

用法：
    python publish.py --input article.md --author "作者名"
    python publish.py --input article.md --cover cover.jpg --title "自定义标题"
    python publish.py --html article.html --cover cover.jpg --title "标题"
"""

import sys
import re
import json
import argparse
import tempfile
from pathlib import Path
from typing import Optional

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from wechat_api import (
    publish_article,
    get_access_token,
    set_account,
    get_config,
    ConfigError,
)
from html_converter import convert_markdown_to_wechat_html, load_theme
from image_handler import process_article_images
from cover_generator import generate_cover, infer_cover_spec_from_path


# ============================================================
# Markdown 文本处理工具
# ============================================================

# 成对行内标记(标记符必须成对出现),共用一个替换函数
_INLINE_PAIR_MARKERS = [
    (r"\*\*", r"\*\*"),   # **粗体**
    (r"==",   r"=="),      # ==黄色高亮==
    (r"\+\+", r"\+\+"),   # ++蓝色高亮++
    (r"%%",   r"%%"),      # %%粉色高亮%%
    (r"&&",   r"&&"),      # &&绿色高亮&&
    (r"!!",   r"!!"),      # !!红色强调!!
    (r"@@",   r"@@"),      # @@蓝色强调@@
    (r"\^\^", r"\^\^"),   # ^^橙色强调^^
]


def _strip_inline_markers(text: str) -> str:
    """剥离 Markdown 行内排版标记(加粗/斜体/自定义标色),保留文字内容本身。

    处理成对标记(比如 `**foo**` → `foo`),同时清除末尾没配对的孤立符号,
    避免摘要里冒出 `**` 之类的裸标记。
    """
    # 先处理成对标记
    for open_pat, close_pat in _INLINE_PAIR_MARKERS:
        text = re.sub(rf"{open_pat}([^\n]+?){close_pat}", r"\1", text)
    # 斜体(单星号)
    text = re.sub(r"\*([^*\n]+)\*", r"\1", text)
    # 剩余的孤立标记符号一律剥掉,避免摘要里冒出 `**` 之类
    text = re.sub(r"\*\*|==|\+\+|%%|&&|!!|@@|\^\^", "", text)
    # 反引号
    text = text.replace("`", "")
    return text


def _strip_front_matter(md_content: str) -> str:
    """如果文章以 YAML front matter(--- ... ---)开头,去掉整段 front matter。"""
    if md_content.lstrip().startswith("---"):
        # 找到起始 `---` 后的第二个 `---` 行
        m = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n", md_content, flags=re.DOTALL)
        if m:
            return md_content[m.end():]
    return md_content


def extract_title_from_markdown(md_content):
    """从Markdown中提取标题（第一个#标题）。

    回退顺序:
      1. 第一个 `# ` 标题
      2. 跳过 YAML front matter 后的第一行非空文本(排除引用/列表/图片等)
    """
    match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    if match:
        return _strip_inline_markers(match.group(1).strip())

    # 回退前先剥掉 YAML front matter,避免把 `---` 或 `title: xxx` 当成标题
    body = _strip_front_matter(md_content)
    for line in body.split("\n"):
        line = line.strip()
        if not line:
            continue
        # 排除引用、图片、分隔线、列表项
        if line.startswith((">", "!", "-", "*", "+")):
            continue
        if set(line) <= {"-", "=", " "}:  # 纯分隔线
            continue
        return _strip_inline_markers(line)[:50]
    return "未命名文章"


def extract_digest_from_markdown(md_content):
    """从Markdown中提取摘要（blockquote或前120字）。

    清理所有行内排版标记(`**foo**`, `==foo==` 等)后再截断,避免摘要里
    残留 `**`、`==` 这类裸标记符号。
    """
    # 优先使用 blockquote
    match = re.search(r'^>\s+(.+)$', md_content, re.MULTILINE)
    if match:
        cleaned = _strip_inline_markers(match.group(1).strip())
        return cleaned[:120]

    # 回退：提取正文前120字
    text = _strip_front_matter(md_content)
    # 去掉标题符号、引用符号、图片链接
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = _strip_inline_markers(text)
    # 剥掉剩余的方括号
    text = re.sub(r'[\[\]]', '', text)
    text = " ".join(text.split())
    return text[:120]


def remove_title_from_content(md_content):
    """从内容中移除标题行（避免在正文中重复显示标题）"""
    lines = md_content.split("\n")
    result = []
    title_removed = False
    for line in lines:
        if not title_removed and re.match(r'^#\s+', line.strip()):
            title_removed = True
            continue
        result.append(line)
    return "\n".join(result)


def _safe_error_message(exc: Exception) -> str:
    """脱敏异常文本，避免请求 URL 中的 secret/token 进入日志。"""
    message = str(exc)
    message = re.sub(r"(secret=)[^&\s)]+", r"\1***", message)
    message = re.sub(r"(access_token=)[^&\s)]+", r"\1***", message)
    return message


# ============================================================
# 默认临时目录
# ============================================================

def _default_temp_dir() -> str:
    """为本次运行创建一个独立的临时目录,避免并发运行互相覆盖文件。"""
    return tempfile.mkdtemp(prefix="wechat_images_")


# ============================================================
# 发布主流程
# ============================================================

def publish_from_markdown(
    md_path,
    title=None,
    author=None,
    digest=None,
    cover_path=None,
    source_url="",
    temp_dir=None,
    style_path=None,
    theme=None,
    account_name: Optional[str] = None,
    debug: bool = False,
):
    """
    从Markdown文件发布文章到微信公众号草稿箱。

    完整流程：
    1. 读取Markdown
    2. 提取/确认标题和摘要
    3. 处理图片（下载+上传微信）
    4. 转换HTML排版
    5. 准备封面图
    6. 创建草稿

    Args:
        md_path: Markdown文件路径
        title: 标题（可选，默认从Markdown提取）
        author: 作者名(默认从账号配置读取,再兜底到 "小神仙")
        digest: 摘要（可选，默认从Markdown提取）
        cover_path: 封面图路径（可选，默认使用文章第一张图）
        source_url: 原文链接
        temp_dir: 临时文件目录(默认为每次运行独立生成)
        style_path: 自定义样式文件路径
        theme: 排版主题名(默认从账号配置读取)
        account_name: 若指定,则在函数内部调用 set_account() 切换账号
        debug: True 时把生成的 HTML 保存到 temp_dir 下方便调试

    Returns:
        dict: 发布结果
    """
    # 如果库调用方指定了账号,立即切换
    if account_name:
        set_account(account_name)

    if temp_dir is None:
        temp_dir = _default_temp_dir()

    print("=" * 60)
    print("微信公众号文章发布")
    print("=" * 60)

    # 1. 读取文章
    md_path = Path(md_path)
    if not md_path.exists():
        raise FileNotFoundError(f"文章文件不存在：{md_path}")

    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    print(f"读取文章：{md_path} ({len(md_content)} 字符)")

    # 2. 提取标题和摘要
    if not title:
        title = extract_title_from_markdown(md_content)
    if not digest:
        digest = extract_digest_from_markdown(md_content)

    print(f"标题：{title}")
    print(f"摘要：{digest[:50]}...")

    # 3. 验证API连接
    print("\n[步骤1] 验证API连接...")
    try:
        token = get_access_token()
        print(f"  API连接正常，token已获取")
    except Exception as e:
        print(f"  API连接失败：{_safe_error_message(e)}")
        print("  请检查 config.yaml 中的 app_id / app_secret 配置")
        sys.exit(1)

    # 4. 处理图片
    print("\n[步骤2] 处理文章图片...")
    # 移除标题后处理（标题不包含在正文中）
    content_md = remove_title_from_content(md_content)
    processed_md, img_mapping, first_img = process_article_images(content_md, temp_dir)

    # 5. 转换HTML
    print("\n[步骤3] 转换HTML排版...")
    styles, highlights, divider_text, list_style = load_theme(
        theme_name=theme, style_path=style_path
    )
    print(f"  主题: {theme or '(默认)'}")
    html_content = convert_markdown_to_wechat_html(
        processed_md, styles, highlights, divider_text, list_style
    )
    print(f"  HTML生成完成 ({len(html_content)} 字符)")

    # 仅在 debug 模式下持久化中间 HTML(否则会堆满临时目录)
    if debug:
        html_path = Path(temp_dir) / "article_output.html"
        html_path.parent.mkdir(parents=True, exist_ok=True)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"  [debug] HTML已保存到：{html_path}")

    # 6. 准备封面图
    print("\n[步骤4] 准备封面图...")
    if cover_path and Path(cover_path).exists():
        print(f"  使用指定封面图：{cover_path}")
    elif first_img:
        cover_path = first_img
        print(f"  使用文章第一张图作为封面：{cover_path}")
    else:
        inferred = infer_cover_spec_from_path(md_path)
        if inferred:
            period, cover_date = inferred
            try:
                cover_path = str(generate_cover(period, cover_date))
                print(f"  已生成兜底封面图：{cover_path}")
            except Exception as e:
                print(f"  兜底封面生成失败：{e}")
                print("  微信公众号要求每篇文章必须有封面图")
                sys.exit(1)
        else:
            print("  警告：没有封面图，且无法从文章路径推断周期/日期")
            print("  请提供 --cover 参数，或使用 trending_{period}_{YYYY-MM-DD}.md 命名")
            print("  微信公众号要求每篇文章必须有封面图")
            sys.exit(1)

    # 7. 如未提供 author,从账号配置兜底读取
    if author is None:
        try:
            cfg = get_config(account_name)
            author = cfg.get("author", "") or "小神仙"
        except ConfigError:
            author = "小神仙"

    # 8. 发布到草稿箱
    print("\n[步骤5] 发布到草稿箱...")
    result = publish_article(
        title=title,
        html_content=html_content,
        cover_image_path=cover_path,
        author=author,
        digest=digest,
        source_url=source_url,
    )

    print("\n" + "=" * 60)
    print("发布完成！")
    print(f"  草稿 media_id: {result['media_id']}")
    print("  请登录微信公众平台查看草稿箱")
    print("=" * 60)

    return result


def publish_from_html(
    html_path,
    title,
    cover_path,
    author=None,
    digest="",
    source_url="",
    account_name: Optional[str] = None,
):
    """
    从已排版的HTML文件发布文章。

    适用于已经完成排版的HTML内容，直接上传。HTML 已经是微信专用排版,
    因此不支持多平台同步。

    Args:
        html_path: HTML文件路径
        title: 文章标题（必需）
        cover_path: 封面图路径（必需）
        author: 作者名(默认从账号配置读取,再兜底到 "小神仙")
        digest: 摘要
        source_url: 原文链接
        account_name: 若指定,则在函数内部调用 set_account() 切换账号

    Returns:
        dict: 发布结果
    """
    if account_name:
        set_account(account_name)

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 如未提供 author,从账号配置兜底读取
    if author is None:
        try:
            cfg = get_config(account_name)
            author = cfg.get("author", "") or "小神仙"
        except ConfigError:
            author = "小神仙"

    result = publish_article(
        title=title,
        html_content=html_content,
        cover_image_path=cover_path,
        author=author,
        digest=digest,
        source_url=source_url,
    )
    return result


# ============================================================
# 命令行入口
# ============================================================

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="微信公众号文章一键发布到草稿箱",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 从Markdown发布
  python publish.py --input article.md --author "张三"

  # 指定封面图和标题
  python publish.py --input article.md --cover cover.jpg --title "自定义标题"

  # 从HTML发布
  python publish.py --html article.html --cover cover.jpg --title "标题"
        """
    )

    parser.add_argument("--input", "-i", help="Markdown文件路径")
    parser.add_argument("--html", help="HTML文件路径（已排版）")
    parser.add_argument("--title", "-t", help="文章标题（默认从文章提取）")
    parser.add_argument("--cover", "-c", help="封面图路径")
    parser.add_argument("--author", "-a", default=None,
                        help="作者名（默认从账号配置获取，兜底：小神仙）")
    parser.add_argument("--digest", "-d", help="文章摘要（默认从文章提取）")
    parser.add_argument("--source-url", default="", help="原文链接")
    parser.add_argument("--style", help="自定义样式JSON路径")
    parser.add_argument("--theme", help="排版主题名(对应 assets/themes/<name>.json,默认从账号配置读取)")
    parser.add_argument(
        "--temp-dir",
        default=None,
        help="临时文件目录(默认每次运行独立生成,避免并发冲突)",
    )
    parser.add_argument("--account", help="指定公众号账号（对应 config.yaml 中的账号名）")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="调试模式:把生成的 HTML 保存到 temp_dir 方便排查",
    )
    return parser


def _resolve_config(args):
    """按命令行参数回读账号配置,填充 author/theme。"""
    needs_config = (
        args.author is None or args.theme is None
    )
    if not needs_config:
        return

    try:
        config = get_config()
    except ConfigError as e:
        if args.author is None:
            args.author = "小神仙"
        return

    if args.author is None:
        args.author = config.get("author", "") or "小神仙"
    if args.theme is None:
        args.theme = config.get("theme", "") or None


def main():
    parser = _build_parser()
    args = parser.parse_args()

    # 设置全局账号
    if args.account:
        set_account(args.account)

    # 从账号配置回读 author / theme
    _resolve_config(args)

    if args.html:
        if not args.title or not args.cover:
            parser.error("使用 --html 模式时，必须提供 --title 和 --cover")
        result = publish_from_html(
            html_path=args.html,
            title=args.title,
            cover_path=args.cover,
            author=args.author,
            digest=args.digest or "",
            source_url=args.source_url,
        )
    elif args.input:
        result = publish_from_markdown(
            md_path=args.input,
            title=args.title,
            author=args.author,
            digest=args.digest,
            cover_path=args.cover,
            source_url=args.source_url,
            temp_dir=args.temp_dir,
            style_path=args.style,
            theme=args.theme,
            debug=args.debug,
        )
    else:
        parser.error("请提供 --input (Markdown) 或 --html 参数")

    # 输出JSON结果
    print("\n" + json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
