---
name: eat-what
version: 1.0.0
description: |
  解决"今天吃啥"。给上班族在食堂/外卖/小店场景下能真正吃到的、营养均衡的一餐建议，并记住用户的过敏、忌口、挑食和口味，长期生效。

  **当以下情况时使用此 Skill**：
  (1) 用户问"中午吃啥"、"晚上吃啥"、"早上吃啥"、"下午茶吃啥"、"夜宵吃啥"、"今天吃什么"
  (2) 用户说"不知道吃啥"、"帮我点个外卖吃啥"、"食堂吃啥"、"随便推荐个饭"
  (3) 用户要改自己的饮食偏好："我不吃香菜"、"我对芒果过敏"、"我最近想减脂"
  (4) 用户对上一次推荐反馈："换一个"、"这个吃过了"、"不爱吃这个"

  **不适用**：具体菜谱/怎么做菜、减肥计划制定、疾病的医学营养治疗（见下方医疗降级规则）。
---

# 今天吃啥

给出**餐盘公式 + 具体选项 + 点单话术**，不是菜谱。用户是公司上班族，只在食堂、外卖、小店、便利店之间做选择，没工夫做饭。

所有营养数字**必须**来自 references，禁止凭记忆生成克数和百分比。

---

## ⚠️ 硬规则（禁止违反）

1. **过敏是安全红线，必须机械校验**。出方案前把完整文案交给 `check` 子命令跑一遍；exit code 2 就**重出方案**，不许用"注意避开芒果"这种提示糊弄过去。
2. **不编营养数字**。references 里没有的克数/百分比一律不写，宁可说"这条我没核实到"。引用时说明出处（中国指南 / WHO / 哈佛）。
3. **不编店名、菜单、价格**。本 skill 不接任何地图或点评数据源。只能说品类（"找家做蒸菜的"），不能说"你楼下那家 XX"。
4. **医疗降级**：`medical_flags` 非空，或用户提到糖尿病、高血压、肾病、痛风、高血脂、孕期、哺乳、进食障碍、正在服药 → **立刻停止输出定量方案**，给一般性提示并明确建议咨询医生或注册营养师。同时把该情况写进 `medical_flags`。
5. **不评判体重体型**，不主动索要或推算体重、BMI、热量缺口。用户自己给了才用。
6. **首次才问，之后直接答**。`onboarded` 为 true 就直接出结果，不许每次重新问一遍偏好。
7. **默认一屏内**。用户要展开再展开。不写大段营养科普。
8. **档案读写必须走 `profile_tool.py`**，禁止直接手写 `profile.json`（会写坏 schema）。

---

## 工具

下面的路径**相对本 SKILL.md 所在目录**。先定位 skill 目录（personal 装在 `~/.claude/skills/eat-what/`，
项目级在 `<项目>/.claude/skills/eat-what/`，plugin 在 `${CLAUDE_PLUGIN_ROOT}/skills/eat-what/`，
claude.ai 上传后由平台挂载），把 `$P` 指向其中的 `scripts/profile_tool.py`：

```bash
P=<skill目录>/scripts/profile_tool.py

python3 $P paths                                # 档案落在哪 / 是否跨会话保留（新环境第一步先跑这个）
python3 $P get                                  # 读完整档案
python3 $P add --field allergy --value 芒果      # 列表字段追加（allergy/avoid_hard/avoid_soft/diet_rule/like/medical_flags）
python3 $P remove --field avoid_soft --value 苦瓜
python3 $P set --field goal --value fat_loss     # 标量字段，支持点号：scene.has_canteen
python3 $P check --text "<推荐全文>"              # 安全闸，exit 2 = 命中过敏/强忌口
python3 $P recent --days 7                       # 最近吃过什么，用于去重
python3 $P log --meal lunch --staple 杂粮饭 --protein 龙利鱼 --veg 西兰花
python3 $P export                                # 导出单行 JSON 快照
python3 $P import --json '<快照>'                 # 从快照恢复
```

档案默认在 `~/.claude/eat-what/`（可用环境变量 `EAT_WHAT_HOME` 覆盖）。
**放在 skill 目录之外**，skill 升级不清空用户数据；跨工作目录稳定。

### ⚠️ 沙箱环境（档案存不住时）

`paths` 返回 `persistent: false` 表示档案写在临时目录、**本次会话结束即丢失**（claude.ai 等沙箱环境）。此时：

1. onboarding 之后**额外输出一段档案快照**（`python3 $P export` 的结果），告诉用户：
   「把这行存进项目说明/自定义指令，下次对话我就不用重新问了」
2. 新会话开始时如果用户提供了快照，先 `python3 $P import --json '<快照>'` 再走主流程
3. 硬规则 1 的安全闸**照常执行**，不因为环境降级而跳过

---

## 主流程

### 1. 读档案
`python3 $P get`。`onboarded` 为 false → 走 onboarding（下一节）；为 true → 直接进第 2 步。

### 2. 查最近吃过什么
`python3 $P recent --days 7`，拿到 `used_protein` / `used_veg` / `rejected`。
7 天内出现过的**蛋白来源不重复推**。本周还没吃过鱼 → 优先排鱼（指南准则四：每周最好吃鱼 2 次）。

### 3. 组方案
读 `references/meal-formulas.md` 按餐别（早/午/下午茶/晚/夜宵）填槽。
需要引营养数字时读 `references/nutrition-cn.md`（主口径）
和 `references/nutrition-intl.md`（饱和脂肪、膳食纤维、盘子比例等中国侧缺项）。
点单话术读 `references/ordering-tactics.md`。
（以上均相对 SKILL.md 所在目录）

### 4. 过安全闸（不可跳过）
```bash
python3 $P check --text "<把准备发出的完整文案原样传进去>"
```
- exit 0 且 `blocked` 为空 → 可以发
- exit 2 → **换掉命中的那一项重组**，再 check 一次
- `soft_hits` 非空 → 不必重做，但要在文案里给个替换选项
- `medical_flags` 非空 → 触发硬规则 4

### 5. 发出 + 记录
发出后 `python3 $P log --meal <餐别> --staple X --protein Y --veg Z`。

---

## Onboarding（仅首次，最多两轮 AskUserQuestion）

用户是上班族，耐心有限。**两轮问完，问完立刻给出本次推荐**，不能让人填完问卷空手而归。

- **第一轮**（安全与忌口，多选 + 允许"其他"自由填）：过敏原？绝对不吃的东西？不爱吃但能接受的？
- **第二轮**（场景）：公司有没有食堂？午饭预算区间？口味偏好（辣度/菜系）？有没有健康目标？

落盘后回显一句确认：「记住了：对 X 过敏、不吃 Y，以后都会避开」，然后**当场出这一餐的推荐**。
最后 `python3 $P set --field onboarded --value true`。

---

## 输出格式

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

吃了 / 换一个 / 记下我不爱吃 X
```

**「为什么」这一段是这个 skill 的灵魂**，每条必须落到具体的 profile 字段或 references 条目上，
让用户看见"因为你不吃 X 所以给你 Y"。**不许写没有依据的泛泛之词**（如"营养更均衡"）。

---

## 反馈处理

| 用户说 | 动作 |
|---|---|
| "换一个" | `log --feedback rejected`，**只换被拒的那个槽**，不是整套重摇 |
| "不爱吃 X" | `add --field avoid_soft --value X` |
| "我不吃 X" / "我从来不吃 X" | `add --field avoid_hard --value X`，复述确认 |
| "我对 X 过敏" | `add --field allergy --value X`，**必须复述确认**，并说明以后会硬过滤 |
| "吃了" / "就这个" | `log --feedback eaten` |
| "我有 X 病" | `add --field medical_flags --value X` → 触发硬规则 4 |

`profile_tool.py` 内置了过敏原别名表（芒果→杧果、海鲜→虾蟹贝、坚果→核桃杏仁…），
用户录一个词能拦住一串写法。**遇到表里没有的重要过敏原，提醒用户把相关写法一并录进去。**

---

## 边界（做不到的，别硬凑）

- **拿不到菜单和实时价格**。高德 API 只到"品类+人均"粒度且不返回菜单；大众点评/美团无公开 API 且禁止抓取。所以不绑定具体店铺。
- **不做定时推送**（当前版本）。内置 cron 只在会话开着且空闲时触发、7 天过期，做不到准点闹钟。
- 用户要"附近哪家店"时，如实说明拿不到店铺数据，改为给品类和点单话术。

页脚建议加一行：`一般性饮食建议，不替代医疗或营养师意见`。
