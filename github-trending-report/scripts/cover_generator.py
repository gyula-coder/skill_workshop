#!/usr/bin/env python3
"""
GitHub Trending 公众号封面生成工具。

基于 assets/covers/{daily|weekly|monthly}.png 叠加日期文案，输出可直接作为
微信公众号图文封面的 PNG 文件。优先使用 macOS 自带 Swift/AppKit 渲染，避免给
定时任务额外引入 Python 图片库依赖。
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple


ROOT_DIR = Path(__file__).resolve().parents[1]
COVER_ASSET_DIR = ROOT_DIR / "assets" / "covers"
DEFAULT_OUTPUT_ROOT = Path("/Users/suoer/iCloud/Documents/github-trending")
PERIODS = {"daily", "weekly", "monthly"}


SWIFT_RENDERER = r'''
import AppKit
import Foundation

func fail(_ message: String) -> Never {
    FileHandle.standardError.write((message + "\n").data(using: .utf8)!)
    exit(1)
}

let args = CommandLine.arguments
if args.count < 5 {
    fail("usage: render.swift <base> <output> <periodText> <dateText>")
}

let basePath = args[1]
let outputPath = args[2]
let periodText = args[3]
let dateText = args[4]

guard let baseImage = NSImage(contentsOfFile: basePath) else {
    fail("base image not found or unreadable: \(basePath)")
}

let size = baseImage.size
let canvas = NSImage(size: size)
canvas.lockFocus()

baseImage.draw(in: NSRect(origin: .zero, size: size), from: .zero, operation: .sourceOver, fraction: 1.0)

let scale = min(size.width / 1672.0, size.height / 941.0)
let boxWidth = size.width * 0.46
let boxHeight = size.height * 0.18
let marginX = size.width * 0.07
let marginY = size.height * 0.075
let boxRect = NSRect(x: marginX, y: marginY, width: boxWidth, height: boxHeight)
let cornerRadius = 24.0 * scale

let panel = NSBezierPath(roundedRect: boxRect, xRadius: cornerRadius, yRadius: cornerRadius)
NSColor(calibratedWhite: 0.04, alpha: 0.62).setFill()
panel.fill()

let stroke = NSBezierPath(roundedRect: boxRect.insetBy(dx: 1.5 * scale, dy: 1.5 * scale), xRadius: cornerRadius, yRadius: cornerRadius)
NSColor(calibratedWhite: 1.0, alpha: 0.18).setStroke()
stroke.lineWidth = 2.0 * scale
stroke.stroke()

let periodFont = NSFont.systemFont(ofSize: 30.0 * scale, weight: .semibold)
let dateFont = NSFont.monospacedDigitSystemFont(ofSize: 54.0 * scale, weight: .bold)

let paragraph = NSMutableParagraphStyle()
paragraph.alignment = .left
paragraph.lineBreakMode = .byTruncatingTail

let periodAttrs: [NSAttributedString.Key: Any] = [
    .font: periodFont,
    .foregroundColor: NSColor(calibratedWhite: 1.0, alpha: 0.78),
    .paragraphStyle: paragraph
]

let dateAttrs: [NSAttributedString.Key: Any] = [
    .font: dateFont,
    .foregroundColor: NSColor.white,
    .paragraphStyle: paragraph
]

let textLeft = boxRect.minX + 34.0 * scale
let periodRect = NSRect(
    x: textLeft,
    y: boxRect.maxY - 60.0 * scale,
    width: boxRect.width - 68.0 * scale,
    height: 36.0 * scale
)
let dateRect = NSRect(
    x: textLeft,
    y: boxRect.minY + 30.0 * scale,
    width: boxRect.width - 68.0 * scale,
    height: 68.0 * scale
)

periodText.draw(in: periodRect, withAttributes: periodAttrs)
dateText.draw(in: dateRect, withAttributes: dateAttrs)

canvas.unlockFocus()

guard let tiff = canvas.tiffRepresentation,
      let bitmap = NSBitmapImageRep(data: tiff),
      let png = bitmap.representation(using: .png, properties: [:]) else {
    fail("failed to encode png")
}

do {
    let outputURL = URL(fileURLWithPath: outputPath)
    try FileManager.default.createDirectory(
        at: outputURL.deletingLastPathComponent(),
        withIntermediateDirectories: true
    )
    try png.write(to: outputURL)
} catch {
    fail("failed to write output: \(error)")
}
'''


def period_title(period: str) -> str:
    return {
        "daily": "GitHub 趋势日报",
        "weekly": "GitHub 趋势周报",
        "monthly": "GitHub 趋势月报",
    }[period]


def default_date_label(period: str, date: str) -> str:
    if period == "monthly":
        return date[:7]
    if period == "weekly":
        return f"截至 {date}"
    return date


def default_output_path(period: str, date: str) -> Path:
    return DEFAULT_OUTPUT_ROOT / period / f"cover_{period}_{date}.png"


def infer_cover_spec_from_path(path: Path) -> Optional[Tuple[str, str]]:
    """从 trending_{period}_{YYYY-MM-DD}.md 或父目录名推断封面周期和日期。"""
    match = re.search(r"trending_(daily|weekly|monthly)_(\d{4}-\d{2}-\d{2})\.md$", path.name)
    if match:
        return match.group(1), match.group(2)

    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", path.name)
    if not date_match:
        return None

    for part in [path.parent.name, *path.parts]:
        if part in PERIODS:
            return part, date_match.group(1)
    return None


def generate_cover(period: str, date: str, output: Optional[Path] = None, label: Optional[str] = None) -> Path:
    if period not in PERIODS:
        raise ValueError(f"未知周期：{period}")

    base_path = COVER_ASSET_DIR / f"{period}.png"
    if not base_path.exists():
        raise FileNotFoundError(f"封面 base 图片不存在：{base_path}")

    output_path = Path(output) if output else default_output_path(period, date)
    date_label = label or default_date_label(period, date)

    with tempfile.NamedTemporaryFile("w", suffix=".swift", delete=False, encoding="utf-8") as f:
        f.write(SWIFT_RENDERER)
        renderer_path = Path(f.name)

    cache_dir = Path(tempfile.mkdtemp(prefix="swift_module_cache_"))
    try:
        env = os.environ.copy()
        env["CLANG_MODULE_CACHE_PATH"] = str(cache_dir)
        env["MODULE_CACHE_DIR"] = str(cache_dir)
        cmd = [
            "swift",
            str(renderer_path),
            str(base_path),
            str(output_path),
            period_title(period),
            date_label,
        ]
        subprocess.run(cmd, check=True, env=env)
    except FileNotFoundError as exc:
        raise RuntimeError("找不到 swift，无法生成封面图。请在 macOS/Xcode Command Line Tools 环境运行。") from exc
    finally:
        renderer_path.unlink(missing_ok=True)
        shutil.rmtree(cache_dir, ignore_errors=True)

    return output_path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="基于 assets/covers 生成公众号封面图")
    parser.add_argument("--period", choices=sorted(PERIODS), help="报告周期")
    parser.add_argument("--date", help="日期，格式 YYYY-MM-DD")
    parser.add_argument("--output", help="输出 PNG 路径")
    parser.add_argument("--label", help="覆盖默认日期文案")
    parser.add_argument("--input", help="从报告 Markdown 路径自动推断 period/date")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    period = args.period
    date = args.date
    if args.input:
        inferred = infer_cover_spec_from_path(Path(args.input))
        if not inferred:
            parser.error("无法从 --input 推断周期和日期，请显式提供 --period 和 --date")
        period = period or inferred[0]
        date = date or inferred[1]

    if not period or not date:
        parser.error("请提供 --period/--date，或提供可推断的 --input")

    output = Path(args.output) if args.output else None
    cover_path = generate_cover(period, date, output=output, label=args.label)
    print(cover_path)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"生成封面失败：{e}", file=sys.stderr)
        sys.exit(1)
