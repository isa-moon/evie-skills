# evie-skills

个人 Claude Code skill marketplace。

## 安装

```bash
claude plugin marketplace add isa-moon/evie-skills
claude plugin install eat-what@evie-skills
```

装完重开一个会话，问一句「中午吃啥」即可触发。

## 包含的 skill

### eat-what — 今天吃啥

给上班族在**食堂 / 外卖 / 小店 / 便利店**场景下能真正吃到的一餐建议。
输出的是**餐盘公式 + 具体选项 + 点单话术**，不是菜谱。

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
```

**特点**

| | |
|---|---|
| 记住忌口 | 首次问两轮（过敏 / 忌口 / 场景），之后不再重复问 |
| 过敏硬过滤 | 发出前用脚本做字符串级校验，命中即重出方案；内置别名表（芒果→杧果、香菜→芫荽…） |
| 不编数字 | 营养克数/百分比只能引用 `references/` 里已核对的条目 |
| 不编店名 | 不接任何地图/点评数据源，只给品类和话术 |
| 医疗降级 | 提到糖尿病/高血压/肾病/痛风/孕期/服药等 → 停止定量方案，建议就医 |
| 七天去重 | 记录历史，同一蛋白来源一周内不重复推 |

**营养口径**（每个数字都标了出处和核对日期）

- 《中国居民膳食指南（2022）》平衡膳食宝塔 / 八准则 — 中国营养学会（主口径）
- WHO Healthy diet fact sheet — 饱和脂肪、膳食纤维、钾等中国侧缺项
- Harvard Healthy Eating Plate — 餐盘比例

**隐私**：忌口和过敏信息存在本机 `~/.claude/eat-what/`（可用环境变量 `EAT_WHAT_HOME` 覆盖），
**在 skill 目录之外**，不进仓库、不上传、升级 skill 不清空。

**不做的事**：不做定时推送、不绑定具体店铺、不给菜单和价格。原因见 `plugins/eat-what/skills/eat-what/SKILL.md` 的「边界」一节。

零第三方依赖（只用 Python 标准库），不联网，不需要 API key。

## 其他安装方式

不想走 marketplace 的话，见 [INSTALL.md](plugins/eat-what/skills/eat-what/INSTALL.md)：
直接拷进 `~/.claude/skills/`、项目级 `.claude/skills/`、或上传 zip 到 claude.ai。

---

一般性饮食建议，不替代医疗或注册营养师意见。
