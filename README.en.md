<div align="center">

[中文](./README.md) · **English**

# 🍚 Evie Skills

#### AI agent skills I actually use every day, open-sourced here

[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![Skills](https://img.shields.io/badge/Skills-1-10B981?style=for-the-badge)](#-skills)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-8B5CF6?style=for-the-badge)](https://agentskills.io)

![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-D97706?style=flat-square)
![Codex](https://img.shields.io/badge/Codex-Skill-10B981?style=flat-square)
![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-8B5CF6?style=flat-square)
![40+ Agents](https://img.shields.io/badge/40%2B_Agents-Compatible-3B82F6?style=flat-square)

</div>

Every skill here follows the [Agent Skills](https://agentskills.io) open standard — originally built by
Anthropic and released as an open format. Claude Code, Codex, OpenClaw, Cursor, Gemini CLI, Copilot,
OpenCode and 40+ other agents can install it. **This is not a Claude-Code-only skill.**

---

## 📋 Index

| Name | One line |
|---|---|
| 🍚 [**eat-what**](#-eat-what) | Ask "what's for lunch" and get a combo you can **actually order right now**, plus the exact words to say to the restaurant. Remembers your allergies and dislikes for good. |

---

## 📦 Install

### Easiest: let the agent install it

In any agent that supports Agent Skills (Claude Code, Codex, OpenClaw, Cursor…), just say:

```
Install this skill for me: https://github.com/isa-moon/evie-skills/tree/main/skills/eat-what
```

It clones itself into the right directory. Restart your session afterwards.

### Manual

Copy the whole `skills/eat-what/` directory into wherever your agent reads skills from:

| Agent | Path |
|---|---|
| Codex / Gemini CLI / Copilot / OpenCode / OpenClaw, etc. | `~/.agents/skills/eat-what/` |
| Claude Code (personal / project) | `~/.claude/skills/eat-what/` or `<project>/.claude/skills/` |

### Extra option for Claude Code users: install as a plugin

Claude Code only; the upside is one-command updates:

```bash
claude plugin marketplace add isa-moon/evie-skills
claude plugin install eat-what@evie-skills
# later: claude plugin update eat-what@evie-skills
```

See [INSTALL.md](./skills/eat-what/INSTALL.md) for sharing one profile across agents, sandboxed web
environments, and moving your profile between machines.

---

## ✨ Skills

<a id="-skills"></a>

<table>
<tr><td>

### 🍚 eat-what

> *"What's for lunch" costs you ten minutes a day. Forty hours a year.*

**It does exactly one thing: take the "what to eat" decision out of your head.**

You ask, it gives you a combo you can **order right now** — not a recipe, no cooking. Fits on one screen by default.

```
🍚 Lunch · today's build

Staple    Whole grain, one fist       → multigrain rice, buckwheat noodles, corn
Protein   Fish/shrimp, one palm       → sole, basa, shrimp
Veg       Two fists, half dark        → broccoli, spinach, bell pepper
Fat/salt  Light oil & salt, sauce on the side

💬 Say this when ordering
"Tomato sole + garlic broccoli + multigrain rice, light oil and salt, sauce on the side"

🧠 Why this
· You don't eat cilantro, you're allergic to mango → both avoided
· No fish yet this week → fish it is (China Guideline #4: fish twice a week, 300~500 g)
· Half the veg is dark → China Dietary Guidelines (2022): ≥300 g veg/day, half dark
```

**Why this isn't yet another "healthy eating assistant"**

The usual ones fail on three counts: the dishes need a kitchen you don't have, the numbers come from nowhere, and you can't repeat any of it to an actual restaurant. All three design lines below target exactly that.

**Line 1: nutrition numbers are never improvised**

Every gram and percentage must cite an entry in `references/` that was verified and stamped with its source and check date. A hard rule in SKILL.md: **if it isn't in references, say "I couldn't verify that" — never generate it.**

| Tier | Source | Covers |
|---|---|---|
| Primary | *Dietary Guidelines for Chinese Residents (2022)* — Chinese Nutrition Society | gram targets per food group |
| Secondary | WHO Healthy diet fact sheet | saturated fat, fiber, potassium |
| Secondary | Harvard Healthy Eating Plate | plate proportions |

Where the sources disagree, it says so. Trans fat, for instance: the Chinese guideline gives absolute grams, WHO gives a percentage of energy — **these are not interchangeable**, and references flags it with a ⚠️ so they never get mixed.

**Line 2: allergies are enforced by a script, not by the model's memory**

Before anything is sent, the full text goes through `profile_tool.py check` for a literal string scan. A hit means `exit 2` and the plan **must be rebuilt** — no getting away with "just skip the mango."

A built-in alias table means one entry blocks a whole family of spellings:

```
mango   → 杧果, mango pancake      cilantro → 芫荽
peanut  → peanut butter, satay     milk     → dairy, cheese, butter, whey
seafood → shrimp, crab, clam...    nuts     → walnut, almond, cashew...
```

**Line 3: no invented restaurants, no invented prices**

It connects to no map or review API. So it will say "find a place that does steamed dishes" — never "that spot downstairs from you." Naming restaurants without a data source is just lying.

**Other rules**

| | |
|---|---|
| Asks once | Two rounds up front (allergies/dislikes, then canteen/budget/taste), **then recommends immediately** — you never fill out a form for nothing. Never asks again. |
| 7-day rotation | No repeating a protein source within a week; prioritizes fish if you haven't had it this week |
| Learns | "Give me another" swaps only the rejected slot, not the whole plate; "I don't like X" goes into your profile |
| Medical fallback | Diabetes, hypertension, kidney disease, gout, pregnancy, medication → **stops giving quantitative plans**, refers you to a doctor or registered dietitian |
| No lecturing | Want fried chicken? You get the harm-reduction version (skin off, add a veg, skip the soda) — no talking you out of it. Never mentions weight, BMI, or calorie deficits. |

**Where your data lives**

Allergies and dislikes are stored locally at `~/.agents/eat-what/` (override with `EAT_WHAT_HOME`),
**outside the skill directory and outside any single vendor's config folder**:

- Never committed, never uploaded, never leaves your machine
- Survives skill upgrades
- **Switching agents doesn't cost you a re-entry**: what you told it in Claude Code still applies in Codex
- Move it with `profile_tool.py export` / `import` (the snapshot contains health info — don't paste it anywhere public)

**What it deliberately doesn't do**

No scheduled push notifications (an agent's built-in scheduler generally only fires while a session is open — it can't be an alarm clock), no binding to specific restaurants, no menus or live prices. Reasons are written up in the "边界" section of [SKILL.md](./skills/eat-what/SKILL.md) — if it can't be done properly, it isn't faked.

Zero third-party dependencies, Python stdlib only. Offline at runtime, no API key of any kind. Follows the Agent Skills open standard.

</td></tr>
</table>

---

<div align="center">

MIT License · General dietary guidance. Not a substitute for a doctor or a registered dietitian.

</div>
