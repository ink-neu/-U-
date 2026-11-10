#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人工智障勇闯U校园
==================
把 65 个脚本、一台不敢关的浏览器、28 段被判 44 分的合成人声，
浓缩成 1 个可以 push 到 GitHub 的文件。

运行方式：
    python 人工智障勇闯U校园.py                # 打印完整自述（引言 / 优点 / 缺点 / 架构 / 结论）
    python 人工智障勇闯U校园.py --init         # 生成 README.md 与 .gitignore，直接可建仓库
    python 人工智障勇闯U校园.py --stats [路径] # 统计本地成绩 JSON；找不到则用内置快照
    python 人工智障勇闯U校园.py --self-test    # 自检内容与生成器

本文件是**只读**的：不连接任何课程平台，不提交答案，不读取浏览器，
不修改任何成绩。它只做三件事：讲清楚这个项目、算清楚已有数据、生成仓库门面。
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

TITLE = "人工智障勇闯U校园"
VERSION = "1.0.0"
SUBTITLE = "一次关于「用工程手段解决本来不用解决的问题」的技术复盘"

# ---------------------------------------------------------------------------
# 引言
# ---------------------------------------------------------------------------

INTRO = """\
这是一份关于「怎么把一门大学英语视听说教程刷到 90 分以上」的技术复盘。

先说结论：

    愿意花 5 块钱，就不要使用这个。

5 块钱能解决的事情，这里花了 65 个脚本、几十个小时、一个从不敢关闭的
Chrome 窗口、28 段被语音评测系统判 44 分的合成人声，以及若干次「UI 显示
100 分，服务器其实还是 66.7 分」的深夜返工。

项目名里的「人工智障」不是自谦，是实测结论：它会把一道三选一的选择题
做成只读勘查、答案溯源、双页面兜底、提交前硬校验、服务器二次复核五个步骤，
然后在第 4 步因为页脚按钮的文字里多了一个空格而找不到「提 交」。

但作为一次工程练习，它确实跑通了：6 个单元、79 个目录节点，U1/U2 重刷后
41 项计分题全部 ≥90，低于 90 的项目为 0。所以这个文件留下的是方法、数据和
教训 —— 尤其是教训。
"""

# ---------------------------------------------------------------------------
# 优点（明确列出，不吹）
# ---------------------------------------------------------------------------

MERITS: list[tuple[str, str]] = [
    (
        "只读优先，先审计再动手",
        "每轮开工先跑只读勘查，确认节点是「可作答 / 解析锁定 / 小结」哪种状态，"
        "再拉服务器版本化记录看真实分数。前后两次纠正了「全书 90–100」的误报——"
        "那都是本地 UI 缓存给出的假象。",
    ),
    (
        "答案零猜测",
        "标准答案来自平台自身下发的答卷与答题解析，不从搜索引擎找、不让模型蒙。"
        "选择题、填空题、排序题、朗读原文全部可溯源，这是「一遍过」成立的前提。",
    ),
    (
        "提交前硬校验",
        "选项下标、填空值、拖拽后的最终顺序、每条录音的分数，提交前一律二次回读；"
        "任何一项不匹配直接抛错拒绝提交。整个 U1/U2 重刷没有一次靠试错换答案。",
    ),
    (
        "录音设 90 分闸门",
        "跟读 / 朗读 / 配音题，只要有一条低于 90 分就不提交，继续重录。"
        "重录不消耗提交机会，所以可以安全地穷举发音变体；同时读准确度、"
        "流利度、完整度三项细项分，定位到底是发音问题还是被截断了半句话。",
    ),
    (
        "全程不关闭用户浏览器",
        "通过调试端口连接常驻浏览器。中途掉线只重启调试通道；某个空白页卡死"
        "也只关那一个标签，原有页面与登录态保持不动。",
    ),
    (
        "提交后必回服务器复核",
        "本地小结显示 100 分不算完成，必须再读一次服务端记录。正是这条规则"
        "发现了几处「本地满分、服务器仍低分」的假成功。",
    ),
    (
        "结果全部可追溯",
        "95 个题目组、每题前后分数、作答内容、是否必修、是否计入成绩，"
        "都落在本地 JSON 里，可随时重算，不依赖页面当前显示。",
    ),
    (
        "最终成绩确实达标",
        "U1：20 项计分题，均值 99.38，最低 93.14；U2：21 项，均值 99.36，"
        "最低 90.67。两单元低于 90 分的项目数为 0。",
    ),
]

# ---------------------------------------------------------------------------
# 缺点（明确列出，不藏）
# ---------------------------------------------------------------------------

DEMERITS: list[tuple[str, str]] = [
    (
        "合规与学术诚信 —— 这是最大缺点",
        "本质是自动代答、代录音，绕过课程的评测环节。它可能违反平台服务条款"
        "与学校的教学管理规定，成绩存在被认定无效的风险，账号也有风险。"
        "它不产生任何学习效果，不该被当作学习工具，更不该替别人完成课程。",
    ),
    (
        "公开版根本不能刷课",
        "正因为上一条，上传 GitHub 的这个版本不包含平台连接、自动填答与提交、"
        "答案解密、模拟麦克风等任何可执行实现。clone 下来只有文档、统计与复盘。"
        "想要「能跑的」，就得自己承担相应后果——本项目不提供。",
    ),
    (
        "投入产出比荒谬",
        "65 个脚本、几十个小时、几十个 TTS 发音候选、多轮本地语音转写和视频"
        "逐帧比对，换来的只是几道平时成绩练习题。「愿意花 5 块钱就不要使用这个」"
        "不是段子，是本项目的成本结论。",
    ),
    (
        "平台只认第一次作答",
        "客观题的得分只记录首次提交，事后用正确答案重刷不会覆盖。"
        "因此有若干历史低分（如 U3 判断题 75、U4 填空 62.5）永久锁定，"
        "只能如实记为不可修；所幸这两项都不计入成绩。",
    ),
    (
        "语音评测是黑盒且极不稳定",
        "同一句英文，换个合成嗓音分数能在 44 到 95 之间跳；有时只有一半词被"
        "识别（完整度 50）。没有可解释的规律，只能靠批量生成变体逐个试，"
        "属于典型的用算力换运气。",
    ),
    (
        "链路非常脆弱",
        "登录票据是一次性的，播放器页不能刷新，只能绕目录重新进入；"
        "调试端口会掉，页面一改版全部选择器作废；题目组 id、标签路径大量硬编码；"
        "接口参数还会随日期变化。任何一环变动都要重写。",
    ),
    (
        "本地显示 ≠ 服务器记录",
        "页面小结可能是过期缓存，「查看答题小结」也可能读到诊断页残留。"
        "曾经据此得出「已修到 100」的错误结论，必须单独复核服务端数据才作数。",
    ),
    (
        "0 分不一定是低分",
        "不评分的主观题在平台记录里默认就是 0 分。只看分数会把 20 道正常提交的"
        "讨论题误判成待修项，得结合计分标记才能区分。",
    ),
    (
        "环境零可移植性",
        "Windows + 固定调试端口的 Chrome + Playwright / edge-tts / faster-whisper / "
        "pycryptodome / imageio-ffmpeg，外加特定课程版本的目录结构。"
        "换台机器基本等于重做一遍。",
    ),
    (
        "无人值守有硬边界",
        "登录失效、验证码、平台限流、接口频率限制都会让流程停摆，仍然需要人工"
        "回来处理。「自动」只是大部分时候自动。",
    ),
    (
        "隐私与凭据风险",
        "本地数据目录里含成绩、课程标识、会话凭据与录音文件。上传前必须排除，"
        "否则等于把账号信息一起 push 上去。--init 会生成对应的 .gitignore。",
    ),
    (
        "没有泛化能力",
        "所有逻辑都贴着这一门课、这一版页面写死。换教材、换平台、甚至只是改了"
        "一个 CSS 类名，整套东西就得重新来过——它解决的是一个具体问题，不是一类问题。",
    ),
]

# ---------------------------------------------------------------------------
# 架构：只列职责，不含可执行实现
# ---------------------------------------------------------------------------

ARCHITECTURE: list[tuple[str, str, str]] = [
    ("L0 连接层", "常驻浏览器 / 调试端口 / 状态保存", "serve.py, wait_player.py, run.py"),
    ("L1 导航层", "目录跳节点、切子标签、只读勘查、遮罩清理", "tocgo.py, tab.py, recon.py, recon2.py, look.py, u12recon.py"),
    ("L2 数据层", "批量拉服务器成绩、导出题目与标准答案、提交后复核", "pullscores.py, getanswers.py, verify.py, audit.py, scan_uai.py"),
    ("L3 作答层", "选择 / 多选 / 填空 / 排序拖拽 / 下拉 / 主观题 / 批量提交", "obj.py, check.py, blank.py, multi.py, sort*.py, pickdd*.py, brush12.py, brushseq.py, brushsub.py, final3.py"),
    ("L4 语音层", "TTS 音频库、发音变体、跟读 / 配音 / 长口语、分数细项定位", "mkvoice.py, mkvariants.py, speak.py, dub.py, longex.py, finish.py, retryvoice.py, u3cand.py, u3try.py, asr.py"),
    ("L5 兜底层", "双播放器页面、重进节点恢复、提交前硬校验、CDP 掉线恢复", "finish.py, vid.py, KILL 遮罩脚本, CDP /json/list 恢复流程"),
]

LESSONS: list[str] = [
    "播放器页不能 reload（登录票据一次性），刷新状态一律走目录重新进入节点。",
    "页脚「提 交」的文字常带空格且不是叶子节点，叶子文本匹配会失效，要用类名或坐标兜底。",
    "多数客观题与拖拽题要求媒体播放结束才能提交，先把进度拖到结尾并等 ended。",
    "拖拽题每一步都要回读顺序，插入语义不稳定；最终顺序不等于目标顺序就拒绝提交。",
    "口语题提交无反应时，重新进入节点比反复点击有效。",
    "答错一次就可能被锁定 —— 所以「只读勘查 → 答案溯源 → 一次提交」是唯一合理顺序。",
    "不评分主观题显示 0 分，要看计分标记，别当成低分去刷。",
]

# ---------------------------------------------------------------------------
# 数据：优先读本地 JSON，读不到用内置快照
# ---------------------------------------------------------------------------

SNAPSHOT = {
    "source": "内置快照（本地 out/verify.json 不可用）",
    "groups": 95,
    "scored": 41,
    "below90": 0,
    "unscored_subjective": 20,
    "units": {
        "U1": {"count": 20, "avg": 99.38, "min": 93.1, "max": 100.0},
        "U2": {"count": 21, "avg": 99.36, "min": 90.7, "max": 100.0},
    },
    "scripts": 65,
    "catalog_nodes": 79,
    "units_total": 6,
}

CANDIDATES = (
    Path(__file__).resolve().parent / "out" / "verify.json",
    Path(__file__).resolve().parent.parent / "ucampus" / "out" / "verify.json",
    Path.cwd() / "out" / "verify.json",
    Path.cwd() / "ucampus" / "out" / "verify.json",
)


def _num(v) -> float | None:
    try:
        if v is None or str(v) in ("", "None", "null"):
            return None
        return float(v)
    except (TypeError, ValueError):
        return None


def load_stats(explicit: str | None = None) -> dict:
    """只读统计。找不到数据文件时退回内置快照，保证 clone 下来也能运行。"""
    paths = ([Path(explicit)] if explicit else []) + list(CANDIDATES)
    src = next((p for p in paths if p.is_file()), None)
    if src is None:
        return dict(SNAPSHOT)

    try:
        rows = json.loads(src.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {**SNAPSHOT, "source": f"读取失败 {exc}，已退回内置快照"}

    scored = [x for x in rows if (_num(x.get("score_avg")) or 0) > 0]
    zero = [x for x in rows if str(x.get("score_avg")) == "0"]
    below = [x for x in scored if (_num(x["score_avg"]) or 0) < 90]
    units: dict[str, dict] = {}
    for name in ("1", "2"):
        vals = [_num(x["score_avg"]) for x in scored if str(x.get("unit")) == name]
        vals = [v for v in vals if v is not None]
        if vals:
            units["U" + name] = {
                "count": len(vals),
                "avg": round(sum(vals) / len(vals), 2),
                "min": round(min(vals), 2),
                "max": round(max(vals), 2),
            }
    scripts = SNAPSHOT["scripts"]
    try:
        n = len(list(src.parent.parent.glob("*.py")))
        if n:
            scripts = n
    except OSError:
        pass

    return {
        "source": str(src),
        "groups": len(rows),
        "scored": len(scored),
        "below90": len(below),
        "unscored_subjective": len(zero),
        "unscored_flag": dict(Counter(str(x.get("real")) for x in zero)),
        "units": units or SNAPSHOT["units"],
        "scripts": scripts,
        "catalog_nodes": SNAPSHOT["catalog_nodes"],
        "units_total": SNAPSHOT["units_total"],
    }


def stats_text(s: dict) -> str:
    lines = [
        "数据源：" + str(s["source"]),
        f"题目组 {s['groups']} 个 | 计分题 {s['scored']} 项 | 低于 90 分 {s['below90']} 项 "
        f"| 不评分主观题 {s['unscored_subjective']} 项",
    ]
    for name, u in s["units"].items():
        lines.append(
            f"  {name}: {u['count']} 项，均值 {u['avg']}，最低 {u['min']}，最高 {u['max']}"
        )
    if s.get("unscored_flag"):
        lines.append("  不评分主观题计分标记分布：" + json.dumps(s["unscored_flag"], ensure_ascii=False))
    lines.append(f"  课程规模：{s['units_total']} 单元 / {s['catalog_nodes']} 目录节点 / 本地工具脚本 {s['scripts']} 个")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 渲染
# ---------------------------------------------------------------------------

DISCLAIMER = """\
声明：本文件仅作个人技术复盘与本地数据整理，不含任何可执行的自动答题实现。
自动代答与代录音可能违反平台条款与教学管理规定，成绩可能被认定无效。
请勿用本项目代替本人完成课程学习或评测；由此产生的一切后果由使用者自行承担。
"""


def render_plain(s: dict) -> str:
    out = [
        "=" * 66,
        f"  {TITLE}  v{VERSION}",
        f"  {SUBTITLE}",
        "=" * 66,
        "",
        "【引言】",
        INTRO.rstrip(),
        "",
        f"【优点 · {len(MERITS)} 条】",
    ]
    for i, (t, d) in enumerate(MERITS, 1):
        out.append(f"  {i:>2}. {t}\n      {d}")
    out += ["", f"【缺点 · {len(DEMERITS)} 条】"]
    for i, (t, d) in enumerate(DEMERITS, 1):
        out.append(f"  {i:>2}. {t}\n      {d}")
    out += ["", "【模块地图（仅职责，不含可执行实现）】"]
    for layer, duty, files in ARCHITECTURE:
        out.append(f"  {layer}  {duty}\n      {files}")
    out += ["", "【踩过的坑】"]
    out += [f"  - {x}" for x in LESSONS]
    out += ["", "【数据复核】", stats_text(s), "", "【结论】"]
    out.append(
        "  工程上它跑通了；作为一件产品，它是一次失败——成本远高于收益，"
        "且用途本身就不站得住脚。愿意花 5 块钱，就不要使用这个。"
    )
    out += ["", "【声明】", DISCLAIMER.rstrip(), ""]
    return "\n".join(out)


_CJK_PUNCT = set("，。、：；！？（）「」『』《》—…“”")


def _join_para(para: str) -> str:
    """把排版折行合并成一行：中文之间不加空格，中英/数字边界补一个空格。"""
    parts = [x.strip() for x in para.split("\n") if x.strip()]
    if not parts:
        return ""
    out = parts[0]
    for part in parts[1:]:
        a, b = out[-1], part[0]
        is_cjk = lambda c: "\u4e00" <= c <= "\u9fff"
        tight = (is_cjk(a) and is_cjk(b)) or a in _CJK_PUNCT or b in _CJK_PUNCT
        out += ("" if tight else " ") + part
    return out


def render_markdown(s: dict) -> str:
    m = [
        f"# {TITLE}",
        "",
        f"> {SUBTITLE}",
        "",
        "## 引言",
        "",
    ]
    for para in INTRO.strip().split("\n\n"):
        if para.startswith("    "):
            m.append("> " + para.strip().strip())
        else:
            # 中文段落里的换行只是排版折行，按中英边界智能合并
            m.append(_join_para(para))
        m.append("")
    m += ["---", "", "## 优点", ""]
    for t, d in MERITS:
        m += [f"- **{t}** — {d}", ""]
    m += ["---", "", "## 缺点", ""]
    for t, d in DEMERITS:
        m += [f"- **{t}** — {d}", ""]
    m += ["---", "", "## 模块地图", "", "只列职责，仓库中不含这些脚本的可执行实现。", "",
          "| 层 | 职责 | 本地脚本 |", "| --- | --- | --- |"]
    for layer, duty, files in ARCHITECTURE:
        m.append(f"| {layer} | {duty} | `{files}` |")
    m += ["", "## 踩过的坑", ""]
    m += [f"- {x}" for x in LESSONS]
    # 公开文档里不暴露本机绝对路径，只保留文件名
    safe = dict(s)
    raw = str(s["source"])
    if "/" in raw or "\\" in raw:
        safe["source"] = Path(raw).name
    m += ["", "## 数据复核", "", "```text", stats_text(safe), "```", "",
          "本文件是只读统计；找不到数据文件时自动使用内置快照，clone 下来也能跑。",
          "", "## 用法", "",
          "```bash",
          "python 人工智障勇闯U校园.py            # 打印完整自述",
          "python 人工智障勇闯U校园.py --init     # 重新生成 README.md 与 .gitignore",
          "python 人工智障勇闯U校园.py --stats    # 统计本地成绩数据",
          "python 人工智障勇闯U校园.py --self-test",
          "```", "",
          "仅依赖 Python 3.9+ 标准库，无需安装任何第三方包。"
          "若终端对中文文件名支持不佳，把文件重命名为 `main.py` 后运行即可"
          "（`--init` 生成的 README 标题不受影响）。", "",
          "## 结论", "",
          "工程上它跑通了；作为一件产品，它是一次失败——成本远高于收益，"
          "且用途本身就不站得住脚。**愿意花 5 块钱，就不要使用这个。**", "",
          "## 声明", "", DISCLAIMER.strip().replace("\n", "\n\n"), ""]
    return "\n".join(m)


GITIGNORE = """\
# 本地运行产物：含成绩、课程标识、会话凭据与录音，切勿上传
out/
state/
audio/voice/
*.json
*.mp3
*.wav
*.log
.profile/
__pycache__/
*.pyc
.venv/
.DS_Store
Thumbs.db
"""


def cmd_init(root: Path) -> int:
    s = load_stats()
    (root / "README.md").write_text(render_markdown(s), encoding="utf-8")
    (root / ".gitignore").write_text(GITIGNORE, encoding="utf-8")
    print(f"已生成 {root / 'README.md'}")
    print(f"已生成 {root / '.gitignore'}")
    print("提示：.gitignore 已排除 out/、state/、*.json、音频与会话数据，可直接 git init。")
    return 0


def cmd_self_test() -> int:
    s = load_stats()
    checks = [
        ("标题非空", bool(TITLE)),
        ("引言含劝退原句", "愿意花 5 块钱，就不要使用这个" in INTRO),
        ("优点 >= 8 条", len(MERITS) >= 8),
        ("缺点 >= 10 条", len(DEMERITS) >= 10),
        ("缺点含合规风险", any("合规" in t for t, _ in DEMERITS)),
        ("缺点含公开版不可执行", any("公开版" in t for t, _ in DEMERITS)),
        ("架构分层 >= 5", len(ARCHITECTURE) >= 5),
        ("统计可用", s["groups"] > 0 and s["scored"] > 0),
        ("README 可生成", len(render_markdown(s)) > 2000),
        ("纯文本可生成", len(render_plain(s)) > 2000),
    ]
    for name, ok in checks:
        print(("  PASS  " if ok else "  FAIL  ") + name)
    bad = [n for n, ok in checks if not ok]
    print(f"\n{len(checks) - len(bad)}/{len(checks)} 通过")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=f"{TITLE} · 单文件技术复盘")
    ap.add_argument("--init", action="store_true", help="生成 README.md 与 .gitignore")
    ap.add_argument("--stats", nargs="?", const="", help="只打印成绩统计，可指定 verify.json 路径")
    ap.add_argument("--readme", action="store_true", help="把 Markdown 自述打印到标准输出")
    ap.add_argument("--self-test", action="store_true", help="自检")
    ap.add_argument("--version", action="version", version=f"{TITLE} {VERSION}")
    args = ap.parse_args()
    root = Path(__file__).resolve().parent

    if args.self_test:
        return cmd_self_test()
    if args.init:
        return cmd_init(root)
    if args.readme:
        print(render_markdown(load_stats()))
        return 0
    if args.stats is not None:
        print(stats_text(load_stats(args.stats or None)))
        return 0
    print(render_plain(load_stats()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
