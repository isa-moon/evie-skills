# eat-what 安装说明

遵循 [Agent Skills](https://agentskills.io) 开放标准，**不绑定任何一家 agent**。
零第三方依赖（只用 Python 标准库），运行时不联网，不需要 API Key。约 50 KB。

---

## 最省事的办法：让 agent 自己装

在任何支持 Agent Skills 的 agent 里直接说：

```
帮我安装这个 skill：https://github.com/isa-moon/evie-skills/tree/main/skills/eat-what
```

它会自己 clone 到正确目录，不用你操心路径。

---

## 手动安装

把 `skills/eat-what/` 整个目录放到你的 agent 读取 skill 的位置：

| Agent | 路径 |
|---|---|
| Codex / Gemini CLI / Copilot / OpenCode / OpenClaw 等 | `~/.agents/skills/eat-what/` |
| Claude Code（个人） | `~/.claude/skills/eat-what/` |
| Claude Code（项目级，跟着 git 仓库走） | `<项目>/.claude/skills/eat-what/` |
| 其他 | 查该 agent 文档里的 skills 目录 |

`~/.agents/skills/` 是跨 agent 的通用位置。想让 Claude Code 和别的 agent 共用同一份，
装到 `~/.agents/skills/eat-what/` 然后做个软链：

```bash
mkdir -p ~/.claude/skills
ln -s ~/.agents/skills/eat-what ~/.claude/skills/eat-what
```

装完**重开一个会话**，问一句"中午吃啥"就会触发。

---

## Claude Code 用户的额外选项：装成 plugin

好处是能一键更新（`claude plugin update`）：

```bash
claude plugin marketplace add isa-moon/evie-skills
claude plugin install eat-what@evie-skills
```

这条路只有 Claude Code 支持，别的 agent 用上面的方式装。

---

## 网页版 / 沙箱环境

部分网页版 agent 允许上传 skill 压缩包（可能需要付费档位并开启代码执行）。

**这类环境有一个重要限制**：沙箱文件系统不保证跨对话保留，忌口档案可能每次新对话都清空。
skill 已内置降级处理：

1. 首次 onboarding 后会额外给你一段**档案快照**（一行 JSON）
2. 把这行存进该 agent 的**项目说明 / 自定义指令**
3. 新对话里 skill 会用它 `import` 恢复，不用重新问一遍忌口

安全闸（过敏硬过滤）在该环境下**照常执行**，不因环境降级而跳过。

> 注意：自定义 skill 一般**不跨产品同步**，网页版上传的不会自动出现在命令行版，要分别装。

---

## 验证装好了没

```bash
python3 <skill目录>/scripts/profile_tool.py paths
```

看 `persistent` 字段：`true` = 档案跨会话保留；`false` = 沙箱环境，需要走上面的快照流程。

## 搬家（把已有档案带到新环境或新 agent）

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
| 档案 | `~/.agents/eat-what/profile.json` |
| 历史 | `~/.agents/eat-what/history.jsonl` |
| 覆盖位置 | 设环境变量 `EAT_WHAT_HOME` |
| 老版本位置 | `~/.claude/eat-what/`（若已存在会自动沿用，不用手动迁移） |

**都在 skill 目录之外、也不在任何 agent 的私有目录里**，所以：升级 skill 不会清空你的数据；
换 agent 也不用重新录一遍忌口；分发这个仓库不会带上任何人的个人信息。

## 营养数据来源

`references/` 里的每个数字都标注了出处和核对日期（2026-09-22）：

- 《中国居民膳食指南（2022）》平衡膳食宝塔 / 八准则 — 中国营养学会 `dg.cnsoc.org`（主口径）
- WHO Healthy diet fact sheet — 饱和脂肪、膳食纤维、钾等中国侧缺项
- 哈佛 Healthy Eating Plate — 餐盘比例

SKILL.md 里立了硬规则：**references 里没有的克数和百分比，一律不许生成。**
