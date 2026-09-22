<div align="center">

[中文](./README.md) · **English**

# 🍚 Evie Skills

#### Claude Code skills I actually use every day, open-sourced here

[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![Skills](https://img.shields.io/badge/Skills-1-10B981?style=for-the-badge)](#-skills)
[![Plugin](https://img.shields.io/badge/Claude_Code-Plugin-8B5CF6?style=for-the-badge)](#-install)

![No Dependencies](https://img.shields.io/badge/deps-Python_stdlib_only-10B981?style=flat-square)
![Offline](https://img.shields.io/badge/runtime-offline_·_no_API_key-3B82F6?style=flat-square)

</div>

Everything here ran on my own machine for a while and proved useful before it got published.

---

## 📋 Index

| Name | One line |
|---|---|
| 🍚 [**eat-what**](#-eat-what) | Ask "what's for lunch" and get a combo you can **actually order right now**, plus the exact words to say to the restaurant. Remembers your allergies and dislikes for good. |

---

## 📦 Install

### Option 1 — as a plugin (recommended; supports one-command updates)

```bash
claude plugin marketplace add isa-moon/evie-skills
claude plugin install eat-what@evie-skills
```

Restart your session. Later, `claude plugin update eat-what@evie-skills` to upgrade.

### Option 2 — let the agent install it

Just say this in Claude Code:

```
Install this skill for me: https://github.com/isa-moon/evie-skills/tree/main/skills/eat-what
```

### Option 3 — manual

Copy `skills/eat-what/` into `~/.claude/skills/` (personal) or `<project>/.claude/skills/` (checked into your repo).

See [INSTALL.md](./skills/eat-what/INSTALL.md) for claude.ai uploads and moving your profile between machines.

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

Allergies and dislikes are stored locally at `~/.claude/eat-what/` (override with `EAT_WHAT_HOME`), **outside the skill directory**:

- Never committed, never uploaded, never leaves your machine
- Survives skill upgrades
- Move it with `profile_tool.py export` / `import` (the snapshot contains health info — don't paste it anywhere public)

**What it deliberately doesn't do**

No scheduled push notifications (the built-in cron only fires while a session is open and idle — it can't be an alarm clock), no binding to specific restaurants, no menus or live prices. Reasons are written up in the "边界" section of [SKILL.md](./skills/eat-what/SKILL.md) — if it can't be done properly, it isn't faked.

Zero third-party dependencies, Python stdlib only. Offline at runtime, no API key of any kind.

</td></tr>
</table>

---

<div align="center">

MIT License · General dietary guidance. Not a substitute for a doctor or a registered dietitian.

</div>
