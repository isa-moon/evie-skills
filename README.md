<div align="center">

**中文** · [English](./README.en.md)

# 🍚 Evie Skills

#### 自己每天在用的 Skill，开源在这里

[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![Skills](https://img.shields.io/badge/Skills-1-10B981?style=for-the-badge)](#-skills)
[![Plugin](https://img.shields.io/badge/Claude_Code-Plugin-8B5CF6?style=for-the-badge)](#-安装)

![No Dependencies](https://img.shields.io/badge/依赖-仅_Python_标准库-10B981?style=flat-square)
![Offline](https://img.shields.io/badge/运行时-不联网_·_无需_API_Key-3B82F6?style=flat-square)

</div>


---

## 📋 目录

| 名字 | 一句话 |
|---|---|
| 🍚 [**eat-what（今天吃啥）**](#-eat-what今天吃啥) | 上班族问一句「中午吃啥」，给一份**现在就能点到**的搭配 + 能照着念的点单话术，记住你的过敏和忌口，长期生效 |

---

## 📦 安装

### 方式一：插件

```bash
claude plugin marketplace add isa-moon/evie-skills
claude plugin install eat-what@evie-skills
```

重开一个会话即生效。以后 `claude plugin update eat-what@evie-skills` 就能升级。

### 方式二：直接让 Agent 装

在 Claude Code 里直接说：

```
帮我安装这个 skill：https://github.com/isa-moon/evie-skills/tree/main/skills/eat-what
```

### 方式三：手动

把 `skills/eat-what/` 整个目录拷进 `~/.claude/skills/`（个人）或 `<项目>/.claude/skills/`（跟着仓库走）。

更多细节（claude.ai 上传、跨机器搬档案）见 [INSTALL.md](./skills/eat-what/INSTALL.md)。

---

## ✨ Skills

<a id="-skills"></a>

<table>
<tr><td>

### 🍚 eat-what（今天吃啥）

> *「中午吃啥」这个问题，每天要花掉你十分钟，一年四十个小时。*

**它只解决一件事：把「吃啥」这个决策从你脑子里拿走。**

你问一句，它给一份**现在就能点到**的搭配——不是菜谱，不用你做饭。默认一屏内看完。

```
🍚 午饭 · 今天这么配

主食   杂粮/糙米 一拳大        → 杂粮饭、荞麦面、玉米+红薯
蛋白   鱼虾 一掌心            → 龙利鱼、巴沙鱼、虾仁
蔬菜   两拳，深色占一半        → 西兰花、菠菜、彩椒
油盐   少油少盐，汤汁单放

💬 点单就这么说
"番茄龙利鱼 + 蒜蓉西兰花 + 杂粮饭，少油少盐，汤汁另外装"

🧠 为什么给你这个
· 你不吃香菜、对芒果过敏 → 已避开
· 这周还没吃鱼 → 排了鱼（指南准则四：每周最好吃鱼 2 次或 300~500 g）
· 深色蔬菜占一半 → 《中国居民膳食指南(2022)》：每天蔬菜不少于 300 g，深色占 1/2
```

**为什么不是又一个「健康饮食助手」**

市面上那种东西的问题在于：它推荐的菜你做不出来，它引的数字你不知道哪来的，它说的话你跟外卖店没法复述。这个 skill 的三条设计线都是冲着这个去的。

**第一条：营养数字不许现编**

所有克数和百分比只能引用 `references/` 里已经核对过、逐条标了出处和核对日期的条目。SKILL.md 里立了硬规则：**references 里没有的数字，宁可说「这条我没核实到」，也不许生成。**

| 口径 | 来源 | 管什么 |
|---|---|---|
| 主口径 | 《中国居民膳食指南（2022）》平衡膳食宝塔 / 八准则 — 中国营养学会 | 各类食物的克数 |
| 补充 | WHO Healthy diet fact sheet | 饱和脂肪、膳食纤维、钾等中国侧缺项 |
| 补充 | Harvard Healthy Eating Plate | 餐盘比例 |

有争议的地方会明确标出来。比如反式脂肪，中国指南给的是绝对克数、WHO 给的是供能占比，**两者不能互换**——references 里专门标了 ⚠️，不许混着用。

**第二条：过敏不靠模型记性，靠脚本硬拦**

发出前把整段文案交给 `profile_tool.py check` 跑一遍字符串级校验，命中就 `exit 2`，**必须重出方案**，不许用「注意避开芒果」这种话糊弄过去。

内置别名表，录一个词拦一串写法：

```
芒果 → 杧果、芒果班戟        香菜 → 芫荽
花生 → 花生酱、沙爹、沙嗲     牛奶 → 奶制品、芝士、黄油、乳清
海鲜 → 虾、蟹、贝、鱿鱼…      坚果 → 核桃、杏仁、腰果…
```

**第三条：不编店名、不编价格**

它不接任何地图或点评数据源。所以它只会说「找家做蒸菜的」，不会说「你楼下那家 XX」——没有数据源还报店名，那是骗人。

**别的规矩**

| | |
|---|---|
| 只问一次 | 首次两轮问完（过敏忌口 / 食堂预算口味），问完**当场就给推荐**，不让你填完问卷空手而归；之后不再重复问 |
| 七天去重 | 同一个蛋白来源一周内不重复推；本周还没吃鱼就优先排鱼 |
| 会学 | 「换一个」只换被拒的那一槽，不是整套重摇；「不爱吃 X」自动进档案 |
| 医疗降级 | 提到糖尿病、高血压、肾病、痛风、孕期、服药等 → **立刻停止定量方案**，建议看医生或注册营养师 |
| 不说教 | 你想吃炸鸡就给炸鸡的降级方案（去皮、配菜、别配可乐），不劝退；不提体重、BMI、热量缺口 |

**你的数据在哪**

过敏和忌口存在本机 `~/.claude/eat-what/`（可用环境变量 `EAT_WHAT_HOME` 覆盖），**在 skill 目录之外**：

- 不进仓库、不上传、不出你的电脑
- 升级 skill 不会清空
- 换机器用 `profile_tool.py export` / `import` 搬（快照含健康信息，别贴到公开渠道）

**明确不做的事**

不做定时推送（内置 cron 只在会话开着且空闲时触发，做不到准点闹钟）、不绑定具体店铺、不给菜单和实时价格。理由写在 [SKILL.md](./skills/eat-what/SKILL.md) 的「边界」一节——做不到的事不硬凑。

零第三方依赖，只用 Python 标准库；运行时不联网，不需要任何 API Key。

</td></tr>
</table>

---

<div align="center">

MIT License · 一般性饮食建议，不替代医疗或注册营养师意见

</div>
