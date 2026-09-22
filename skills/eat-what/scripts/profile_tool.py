#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eat-what 口味档案与历史记录的唯一读写入口。

数据目录按 EAT_WHAT_HOME → 已存在的旧目录 → ~/.agents/eat-what → 临时目录 的顺序解析，
放在 skill 目录之外，skill 升级不会清空用户数据。先跑 `paths` 可知落在哪、是否跨会话保留。
与具体 agent 无关：Claude Code、Codex、OpenClaw 等共用同一份档案。

子命令：
  paths                                 数据落在哪 / 是否持久化（沙箱环境先跑这个）
  init                                  写入默认空档案（已存在则不覆盖）
  get [--field F]                       读档案，默认输出完整 JSON
  set --field F --value V               设值，支持点号嵌套 scene.has_canteen
  add --field F --value V [--value V2]  往列表字段追加（自动去重）
  remove --field F --value V            从列表字段移除
  check --text "推荐文案"                 安全校验：命中过敏/强忌口则 exit 2
  log --meal lunch --protein X ...      记一条推荐
  recent [--days 7]                     最近记录 + 用过的食材汇总（用于去重）
  export                                导出单行 JSON（搬机器 / 沙箱环境做快照）
  import --json '<单行JSON>' [--merge]   从快照恢复
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta


def _resolve_base():
    """按可移植性优先级决定数据目录。

    1. 环境变量 EAT_WHAT_HOME —— 显式指定，优先级最高
    2. 已存在的旧目录 —— 换 agent 或升级后不把用户档案甩掉
    3. ~/.agents/eat-what —— 默认位置。跨 agent 通用，不绑定任何一家厂商，
       Claude Code / Codex / OpenClaw 等装在哪都读同一份档案
    4. 临时目录 —— 家目录不可写时（网页版沙箱等）的兜底，
       仅在当前会话内有效，档案不跨会话保留（见 paths 子命令的 persistent 字段）
    """
    env = os.environ.get("EAT_WHAT_HOME")
    if env:
        return os.path.abspath(os.path.expanduser(env))
    home = os.path.expanduser("~")
    if home and home != "~" and os.path.isdir(home) and os.access(home, os.W_OK):
        default = os.path.join(home, ".agents", "eat-what")
        # 老版本把档案写在 ~/.claude/eat-what，沿用它而不是让用户重新录一遍忌口
        for candidate in (default, os.path.join(home, ".claude", "eat-what")):
            if os.path.exists(os.path.join(candidate, "profile.json")):
                return candidate
        return default
    return os.path.join(tempfile.gettempdir(), "eat-what")


BASE = _resolve_base()
PROFILE = os.path.join(BASE, "profile.json")
HISTORY = os.path.join(BASE, "history.jsonl")
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LIST_FIELDS = ("allergy", "avoid_hard", "avoid_soft", "diet_rule", "like", "medical_flags")

DEFAULT = {
    "version": 1,
    "updated_at": None,
    "allergy": [],          # 安全级：硬过滤，绝不出现
    "avoid_hard": [],       # 强忌口：不出现
    "avoid_soft": [],       # 不爱吃：尽量避开
    "diet_rule": [],        # 宗教/信仰/伦理类约束
    "like": [],
    "goal": "balanced",     # balanced | fat_loss | muscle_gain | 自定义字符串
    "medical_flags": [],    # 非空即触发医疗降级
    "scene": {
        "has_canteen": None,
        "budget_lunch": None,   # [低, 高]，单位元
        "time_budget": None,
        "spice": None,
    },
    "places": [],           # 预留：V2 绑定真实店铺
    "push": {},             # 预留：V2 定时推送配置
    "onboarded": False,
}

# 过敏原的常见别名/同源写法。key 是用户可能录入的词，value 是应一并拦截的写法。
# 只用于扩大拦截范围，宁可误报也不漏报。
ALIAS = {
    "芒果": ["杧果"],
    "花生": ["花生酱", "沙爹", "沙嗲"],
    "牛奶": ["奶制品", "乳制品", "芝士", "奶酪", "黄油", "乳清"],
    "鸡蛋": ["蛋液", "蛋黄", "蛋白", "蛋清", "蛋饼"],
    "虾": ["虾仁", "基围虾", "白灼虾", "虾滑"],
    "蟹": ["蟹柳", "蟹肉", "蟹黄"],
    "海鲜": ["虾", "蟹", "贝", "鱿鱼", "扇贝", "蛤蜊", "生蚝", "牡蛎"],
    "坚果": ["核桃", "杏仁", "腰果", "开心果", "榛子", "夏威夷果", "碧根果"],
    "大豆": ["豆浆", "豆腐", "豆干", "腐竹", "豆皮", "黄豆", "毛豆"],
    "小麦": ["面条", "面包", "馒头", "面筋", "饺子", "包子", "烙饼"],
    "麸质": ["面条", "面包", "馒头", "面筋", "意面"],
    "香菜": ["芫荽"],
    "猪肉": ["排骨", "五花", "里脊", "叉烧", "培根", "火腿", "肉末", "猪"],
    "牛肉": ["牛腩", "肥牛", "牛排", "牛"],
    "羊肉": ["羊排", "羊蝎子", "涮羊", "羊"],
}


def _now():
    return datetime.now().isoformat(timespec="seconds")


def load():
    if not os.path.exists(PROFILE):
        return json.loads(json.dumps(DEFAULT))
    with open(PROFILE, encoding="utf-8") as f:
        data = json.load(f)
    # 补齐新增字段，老档案不会因为 schema 演进而报错
    merged = json.loads(json.dumps(DEFAULT))
    for k, v in data.items():
        if k == "scene" and isinstance(v, dict):
            merged["scene"].update(v)
        else:
            merged[k] = v
    return merged


def save(data):
    os.makedirs(BASE, exist_ok=True)
    data["updated_at"] = _now()
    tmp = PROFILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, PROFILE)
    return data


def dig(data, path):
    cur = data
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def put(data, path, value):
    parts = path.split(".")
    cur = data
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
    cur[parts[-1]] = value


def coerce(raw):
    """--value 传进来的字符串，尽量还原成 JSON 类型（true / 12 / [15,30]）。"""
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return raw


def expand(term):
    """把一个忌口词展开成需要拦截的全部写法。"""
    out = {term}
    out.update(ALIAS.get(term, []))
    return out


def find_hits(text, terms):
    """在文案里找命中的忌口词。返回 [(用户录入的词, 实际命中的写法)]。"""
    hits = []
    for term in terms:
        if not term:
            continue
        for variant in expand(term):
            if variant and variant in text:
                hits.append((term, variant))
                break
    return hits


# ---------- 子命令 ----------

def cmd_init(args):
    if os.path.exists(PROFILE):
        print(json.dumps({"ok": True, "created": False, "path": PROFILE,
                          "note": "档案已存在，未覆盖"}, ensure_ascii=False))
        return 0
    save(load())
    print(json.dumps({"ok": True, "created": True, "path": PROFILE}, ensure_ascii=False))
    return 0


def cmd_get(args):
    data = load()
    out = dig(data, args.field) if args.field else data
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_set(args):
    data = load()
    put(data, args.field, coerce(args.value[0]) if len(args.value) == 1
        else [coerce(v) for v in args.value])
    save(data)
    print(json.dumps({"ok": True, "field": args.field,
                      "now": dig(data, args.field)}, ensure_ascii=False))
    return 0


def cmd_add(args):
    data = load()
    cur = dig(data, args.field)
    if cur is None:
        cur = []
    if not isinstance(cur, list):
        print(json.dumps({"ok": False, "error": f"{args.field} 不是列表字段，请用 set"},
                         ensure_ascii=False), file=sys.stderr)
        return 1
    added = [v for v in args.value if v not in cur]
    cur.extend(added)
    put(data, args.field, cur)
    save(data)
    print(json.dumps({"ok": True, "field": args.field, "added": added, "now": cur},
                     ensure_ascii=False))
    return 0


def cmd_remove(args):
    data = load()
    cur = dig(data, args.field)
    if not isinstance(cur, list):
        print(json.dumps({"ok": False, "error": f"{args.field} 不是列表字段"},
                         ensure_ascii=False), file=sys.stderr)
        return 1
    removed = [v for v in args.value if v in cur]
    put(data, args.field, [v for v in cur if v not in args.value])
    save(data)
    print(json.dumps({"ok": True, "field": args.field, "removed": removed,
                      "now": dig(data, args.field)}, ensure_ascii=False))
    return 0


def cmd_check(args):
    """输出推荐前的机械安全闸。命中过敏或强忌口 → exit 2，必须重出方案。"""
    data = load()
    text = args.text
    blocked = ([{"term": t, "matched": m, "level": "allergy"}
                for t, m in find_hits(text, data["allergy"])]
               + [{"term": t, "matched": m, "level": "avoid_hard"}
                  for t, m in find_hits(text, data["avoid_hard"])]
               + [{"term": t, "matched": m, "level": "diet_rule"}
                  for t, m in find_hits(text, data["diet_rule"])])
    soft = [{"term": t, "matched": m, "level": "avoid_soft"}
            for t, m in find_hits(text, data["avoid_soft"])]
    result = {
        "ok": not blocked,
        "blocked": blocked,
        "soft_hits": soft,
        "medical_flags": data["medical_flags"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if blocked else 0


def cmd_log(args):
    os.makedirs(BASE, exist_ok=True)
    entry = {
        "ts": _now(),
        "meal": args.meal,
        "staple": args.staple,
        "protein": args.protein,
        "veg": args.veg,
        "note": args.note,
        "feedback": args.feedback,
    }
    with open(HISTORY, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(json.dumps({"ok": True, "logged": entry}, ensure_ascii=False))
    return 0


def cmd_recent(args):
    if not os.path.exists(HISTORY):
        print(json.dumps({"entries": [], "used_protein": [], "used_veg": [],
                          "used_staple": [], "rejected": []}, ensure_ascii=False, indent=2))
        return 0
    cutoff = datetime.now() - timedelta(days=args.days)
    entries = []
    with open(HISTORY, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
                if datetime.fromisoformat(e["ts"]) >= cutoff:
                    entries.append(e)
            except (ValueError, KeyError):
                continue  # 坏行跳过，不让历史文件毁掉整次调用

    def collect(key):
        seen = []
        for e in entries:
            v = e.get(key)
            if v and v not in seen:
                seen.append(v)
        return seen

    print(json.dumps({
        "days": args.days,
        "count": len(entries),
        "entries": entries[-20:],
        "used_protein": collect("protein"),
        "used_veg": collect("veg"),
        "used_staple": collect("staple"),
        "rejected": [e for e in entries if e.get("feedback") == "rejected"],
    }, ensure_ascii=False, indent=2))
    return 0


def cmd_paths(args):
    """告诉调用方档案落在哪、是否跨会话保留。在网页版等沙箱环境里先跑这个。"""
    ephemeral = BASE.startswith(tempfile.gettempdir())
    print(json.dumps({
        "skill_dir": SKILL_DIR,
        "data_dir": BASE,
        "profile": PROFILE,
        "history": HISTORY,
        "exists": os.path.exists(PROFILE),
        "persistent": not ephemeral,
        "note": ("档案写在临时目录，本次会话结束即丢失：请在回答末尾输出档案快照，"
                 "让用户存进项目说明，下次用 import 恢复"
                 if ephemeral else "档案跨会话保留"),
    }, ensure_ascii=False, indent=2))
    return 0


def cmd_export(args):
    """导出成单行 JSON，便于粘贴进 agent 的项目说明/自定义指令，或搬到另一台机器。"""
    data = load()
    data.pop("updated_at", None)
    print(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    return 0


def cmd_import(args):
    """从 export 出来的单行 JSON 恢复档案。"""
    try:
        incoming = json.loads(args.json)
    except ValueError as e:
        print(json.dumps({"ok": False, "error": f"不是合法 JSON: {e}"},
                         ensure_ascii=False), file=sys.stderr)
        return 1
    if not isinstance(incoming, dict):
        print(json.dumps({"ok": False, "error": "顶层必须是 JSON 对象"},
                         ensure_ascii=False), file=sys.stderr)
        return 1
    data = load() if args.merge else json.loads(json.dumps(DEFAULT))
    for k, v in incoming.items():
        if k == "scene" and isinstance(v, dict):
            data["scene"].update(v)
        elif k in LIST_FIELDS and isinstance(v, list) and args.merge:
            data[k] = data.get(k, []) + [x for x in v if x not in data.get(k, [])]
        else:
            data[k] = v
    save(data)
    print(json.dumps({"ok": True, "mode": "merge" if args.merge else "replace",
                      "profile": PROFILE}, ensure_ascii=False))
    return 0


def main():
    p = argparse.ArgumentParser(description="eat-what 档案与历史工具")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init").set_defaults(func=cmd_init)

    g = sub.add_parser("get")
    g.add_argument("--field", help="点号路径，如 scene.has_canteen")
    g.set_defaults(func=cmd_get)

    s = sub.add_parser("set")
    s.add_argument("--field", required=True)
    s.add_argument("--value", required=True, nargs="+")
    s.set_defaults(func=cmd_set)

    a = sub.add_parser("add")
    a.add_argument("--field", required=True, choices=LIST_FIELDS)
    a.add_argument("--value", required=True, nargs="+")
    a.set_defaults(func=cmd_add)

    r = sub.add_parser("remove")
    r.add_argument("--field", required=True, choices=LIST_FIELDS)
    r.add_argument("--value", required=True, nargs="+")
    r.set_defaults(func=cmd_remove)

    c = sub.add_parser("check")
    c.add_argument("--text", required=True, help="待发出的推荐全文")
    c.set_defaults(func=cmd_check)

    l = sub.add_parser("log")
    l.add_argument("--meal", required=True,
                   choices=["breakfast", "lunch", "tea", "dinner", "supper"])
    l.add_argument("--staple")
    l.add_argument("--protein")
    l.add_argument("--veg")
    l.add_argument("--note")
    l.add_argument("--feedback", choices=["ok", "rejected", "eaten"])
    l.set_defaults(func=cmd_log)

    rc = sub.add_parser("recent")
    rc.add_argument("--days", type=int, default=7)
    rc.set_defaults(func=cmd_recent)

    sub.add_parser("paths").set_defaults(func=cmd_paths)
    sub.add_parser("export").set_defaults(func=cmd_export)

    im = sub.add_parser("import")
    im.add_argument("--json", required=True, help="export 输出的单行 JSON")
    im.add_argument("--merge", action="store_true",
                    help="与现有档案合并（列表字段取并集），默认整体替换")
    im.set_defaults(func=cmd_import)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
