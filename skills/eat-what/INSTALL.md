# eat-what 安装说明

零第三方依赖（只用 Python 标准库），不联网，不需要 API key。约 50 KB。

---

## 1. Claude Code — 个人安装

解压后把 `eat-what/` 整个目录放进：

```
~/.claude/skills/eat-what/
```

重开一个会话即生效，问一句"中午吃啥"就会触发。

## 2. Claude Code — 项目级（跟着 git 仓库走）

```
<你的项目>/.claude/skills/eat-what/
```

团队成员 clone 下来自动具备。档案仍存在各人的 `~/.claude/eat-what/`，**不会进仓库**。

## 3. claude.ai / Claude Desktop

Settings → Features → 上传 zip（需 Pro / Max / Team / Enterprise 且已开启代码执行）。

**这个环境有一个重要限制**：沙箱文件系统不保证跨对话保留，忌口档案可能每次新对话都清空。
skill 已内置降级处理：

1. 首次 onboarding 后会额外给你一段**档案快照**（一行 JSON）
2. 把这行存进 claude.ai 的**项目说明 / 自定义指令**
3. 新对话里 skill 会用它 `import` 恢复，不用重新问一遍忌口

安全闸（过敏硬过滤）在该环境下**照常执行**，不因环境降级而跳过。

> 注意：自定义 Skills **不跨平台同步**。claude.ai 上传的不会出现在 Claude Code，反之亦然，要分别装。

## 4. 做成 plugin 分发给别人

```
你的仓库/
├── .claude-plugin/
│   ├── plugin.json        {"name":"eat-what","description":"...","author":{...}}
│   └── marketplace.json   （如果自建 marketplace）
└── skills/
    └── eat-what/          ← 本目录
```

对方执行 `claude plugin install eat-what@<你的marketplace>`。

---

## 验证装好了没

```bash
python3 <skill目录>/scripts/profile_tool.py paths
```

看 `persistent` 字段：`true` = 档案跨会话保留；`false` = 沙箱环境，需要走上面第 3 节的快照流程。

## 搬家（把已有档案带到新环境）

```bash
# 旧环境
python3 .../profile_tool.py export      # 输出一行 JSON

# 新环境
python3 .../profile_tool.py import --json '<粘贴那行>'
```

⚠️ 快照里含过敏、忌口等健康信息，**别随手发给别人或贴进公开渠道**。

## 数据存在哪

| | 路径 |
|---|---|
| 档案 | `~/.claude/eat-what/profile.json` |
| 历史 | `~/.claude/eat-what/history.jsonl` |
| 覆盖位置 | 设环境变量 `EAT_WHAT_HOME` |

**都在 skill 目录之外**，所以：升级 skill 不会清空你的数据；分发这个 zip 也不会带上任何人的个人信息。

## 营养数据来源

`references/` 里的每个数字都标注了出处和核对日期（2026-09-22）：

- 《中国居民膳食指南（2022）》平衡膳食宝塔 / 八准则 — 中国营养学会 `dg.cnsoc.org`（主口径）
- WHO Healthy diet fact sheet — 饱和脂肪、膳食纤维、钾等中国侧缺项
- 哈佛 Healthy Eating Plate — 餐盘比例

SKILL.md 里立了硬规则：**references 里没有的克数和百分比，一律不许生成。**
