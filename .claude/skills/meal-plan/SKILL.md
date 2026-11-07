---
name: meal-plan
description: Plan meals for a number of days from the recipe collection, let the user review and adjust the plan, then generate a combined shopping list once it's accepted. Use when the user asks for a meal plan, what to cook this week, or a shopping/grocery list.
argument-hint: "<number of days> [start date] [notes, e.g. 'dinners only, no fish']"
---

# Meal Plan

Two phases: **draft a plan for review**, then, after the user accepts it,
**generate the shopping list**. Don't make the shopping list until the user
says the plan is good.

Repo layout and file formats are described in `CLAUDE.md`. The helper script
is `python scripts/recipes.py` (stdlib only).

## Phase 1: Draft the plan

### Settings

- **Days**: from `$ARGUMENTS`. If missing, ask.
- **Start date**: from the arguments; otherwise tomorrow (today is in your
  context). Say which date you used.
- **Household defaults**: read `preferences.md` (meals to plan each day, people
  to feed, dislikes, other rules). If it doesn't exist, ask the user once,
  with AskUserQuestion, which meals to plan (dinner only / lunch + dinner /
  breakfast, lunch + dinner) and how many people, then create
  `preferences.md` with their answers using the format at the bottom of this
  file. Anything stated in this request overrides the file for this plan
  only. If the user says to make it the default, update the file.

### Choose recipes

1. Run `python scripts/recipes.py list --ingredients` to see every recipe with
   its category, servings, tags, and ingredients.
2. Read the two most recent files in `meal-plans/` (if any) and avoid
   repeating those dinners unless the collection is too small.
3. Fill each day's meal slots, using recipes only from the matching category.
   Aim for:
   - **Variety**: don't repeat a main protein or cuisine on back-to-back days.
   - **Leftovers**: when a recipe makes more servings than the people eating,
     use the extra for a later meal (usually the next day's lunch) instead of
     cooking something new. Mark it as `leftovers` with no link.
   - **Shared perishables**: prefer combinations that use up the same fresh
     items (a bunch of cilantro across two recipes beats one recipe that
     wastes most of it).
   - **Sides**: add a `side` recipe to a dinner when the dinner isn't a full
     meal on its own (judge from its ingredients). Sides count as their own
     row.
   - **Effort**: put longer recipes (by total time) on days the user's
     preferences mark as having more time, otherwise spread them out.
4. **Never invent recipes.** If the collection doesn't have enough recipes
   for a category, repeat one, leave the slot as `flexible`, or put
   `eat out`, and tell the user which categories need more recipes
   (they can add them with `/create-recipe`).

### Servings

The Servings column is how many servings to cook, and the shopping list
scales each recipe by `Servings / recipe servings`. Default to the recipe's
own servings (cook the full batch). Only change it to scale a recipe up or
down when the people count calls for it and the leftovers wouldn't be used.

### Write and present

Write `meal-plans/<start-date>.md` in exactly this format:

```markdown
---
status: draft
start: 2026-11-09
days: 3
people: 2
---

# Meal Plan: Nov 9–11, 2026

| Day | Meal | Recipe | Servings |
|---|---|---|---|
| Mon Nov 9 | dinner | [Chicken Tikka Masala](../recipes/dinner/chicken-tikka-masala.md) | 4 |
| Mon Nov 9 | dinner | [Garlic Rice](../recipes/side/garlic-rice.md) | 4 |
| Tue Nov 10 | lunch | leftovers: Chicken Tikka Masala |  |
| Tue Nov 10 | dinner | [Sheet Pan Gnocchi](../recipes/dinner/sheet-pan-gnocchi.md) | 2 |
| Wed Nov 11 | dinner | eat out |  |

## Notes

- Prep ahead: marinate the chicken Sunday night.
```

Rules: one row per dish; links are relative to `meal-plans/`; only linked rows
go on the shopping list. Add `## Notes` only for useful prep-ahead or
leftover tips.

If a plan for that start date already exists, ask before overwriting.

Show the user the table (in chat, not just the file path) with a one-line
reason behind the main choices, then ask if they want any swaps. Then stop
and wait.

### Revisions

When the user asks for changes, update the file and show the revised table.
Repeat until they accept it.

## Phase 2: Shopping list (after the user accepts)

1. Set `status: accepted` in the plan's frontmatter.
2. Run
   `python scripts/recipes.py shopping-list meal-plans/<start-date>.md -o shopping-lists/<start-date>.md`.
   If it reports errors (an ingredient missing from the index, a unit
   mismatch, a broken link), fix the recipe or index the same way
   `/create-recipe` would, then rerun it. Don't hand-write the list.
3. The script groups items by aisle, totals each ingredient across recipes,
   rounds whole items up, and puts staples in a separate "check before you
   shop" section. If the user has extra items to add (paper towels, snacks),
   append them under a `## Extras` heading at the end of the file in the
   same `- [ ] **item**` format.
4. Show the list in chat and give its path. Point out the pantry-staples
   section so they can check what they already have.

## preferences.md format

```markdown
# Household Preferences

Used by /meal-plan. Edit freely.

- **People**: 2
- **Meals to plan**: dinner
- **Leftovers for lunch**: yes
- **Dislikes / avoid**: mushrooms
- **Notes**: Short on time Mon–Thu; bigger cooking projects on weekends.
```
