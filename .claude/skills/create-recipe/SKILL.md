---
name: create-recipe
description: Add a recipe to the collection. Takes a category (breakfast, lunch, dinner, side), a recipe name, an optional image, an ingredient list, and instructions; normalizes every ingredient against ingredients.md (matching existing entries, converting units, or adding new entries) and writes recipes/<category>/<slug>.md. Use when the user wants to add, save, import, or create a recipe.
argument-hint: "<category> <name> [image] — then paste ingredients and instructions"
---

# Create Recipe

Turn what the user gives you into a recipe file whose ingredients all exist in
`ingredients.md` with matching units, so meal plans can combine them into a
shopping list.

Repo layout and file formats are described in `CLAUDE.md`. The helper script
is `python scripts/recipes.py` (stdlib only).

## 1. Gather the inputs

You need:

| Input | Required | Notes |
|---|---|---|
| category | yes | `breakfast`, `lunch`, `dinner`, or `side` |
| name | yes | Title Case for display |
| ingredients | yes | Any format: pasted list, photo, free text |
| instructions | yes | Any format |
| image | no | Local file path or URL |
| servings | yes, but infer | Use the source's yield. If none is given, estimate from quantities and say so in the summary |
| prep/cook time, tags, source | no | Fill in only when given or obvious (tags: cuisine, main protein, e.g. `mexican, chicken`) |

The user may supply everything in `$ARGUMENTS`, across the message, or as a
link or photo of a recipe. Extract what you can. Ask only for what is missing
and can't be inferred (usually category or name). Ask for all missing items
in one question.

Slug: kebab-case of the name (`Chicken Tikka Masala` → `chicken-tikka-masala`).
If `recipes/<category>/<slug>.md` already exists, ask whether to replace it or
pick a different name.

## 2. Normalize each ingredient

Read `ingredients.md` first. For each raw ingredient line:

1. **Split it** into quantity, unit, the item, and prep.
   `2 cups finely diced yellow onion` → qty 2, unit cup, item "yellow onion", prep "finely diced".
   Prep is anything about how it's cut or handled: chopped, minced, softened,
   room temperature, divided, packed, "plus more for serving", "optional".

2. **Find it in the index.** Look for an exact name match, then an alias match.
   If neither, run `python scripts/recipes.py lookup "<item>" ...` (several
   terms per call) to find near matches. Decide whether a near match is the
   same thing you'd buy:
   - Same purchase → reuse the entry. If the recipe's wording is a new way of
     naming it, add it to that entry's **Aliases**.
     (`onion` → `yellow onion`, `evoo` → `olive oil`, `large eggs` → `egg`.)
   - Different purchase → new entry. Fresh vs. dried herbs, canned vs. dried
     beans, salted vs. unsalted butter, chicken thighs vs. breasts, and
     different cheeses are all different entries.
   - When a recipe is vague ("cheese", "oil", "stock") and nothing marks it as
     a specific item, use the most common match already in the index, or ask
     if it matters to the result.

3. **Convert to the index unit.** The recipe must use the entry's unit
   exactly. Use the entry's **Conversions** column first, then standard
   kitchen conversions (3 tsp = 1 tbsp, 16 tbsp = 1 cup, 16 oz = 1 lb,
   2 cup = 1 pint). If the conversion needs a density or size estimate
   (e.g. `1 cup shredded cheddar` → oz, `2 cups chopped onion` → each),
   estimate from common knowledge and **add that conversion to the entry's
   Conversions column** so future recipes use the same figure.
   Write quantities as decimals or simple fractions (`1.5`, `1/2`, `1 1/2`).
   Keep the original measurement in Prep when it helps cooking
   (`yellow onion | 2 | each | diced (about 2 cups)`).

4. **Add new entries** when nothing matches:
   - **Name**: lowercase, singular, generic enough to share across recipes,
     specific enough to buy (`boneless skinless chicken thigh`,
     `canned diced tomatoes`, `fresh cilantro`). No brand names, no prep words.
   - **Unit** — choose the unit that both cooking and shopping can count in:

     | Kind of item | Unit |
     |---|---|
     | Whole produce, eggs, tortillas, bread rolls | `each` |
     | Garlic | `clove` |
     | Leafy herbs, green onions, celery | `bunch` |
     | Meat and seafood | `lb` |
     | Cheese by weight, pasta, chocolate | `oz` |
     | Flour, sugar, rice, oats, milk, broth, cream, shredded cheese if the source only gives cups | `cup` |
     | Oils, butter, vinegars, sauces, honey | `tbsp` |
     | Spices, extracts, salt, baking powder | `tsp` |
     | Canned goods | `can` — put the size in the name: `canned diced tomatoes (14.5 oz)` |

   - **Aisle**: one of the aisles listed at the top of `ingredients.md`.
   - **Staple**: `yes` for things usually kept on hand (salt, pepper, oils,
     dried spices, flour, sugar, common condiments); `no` for perishables and
     anything bought for a specific recipe.
   - **Aliases**: other common names, including the one in this recipe if it
     differs.
   - **Conversions**: any you used or know (`1 medium ≈ 1 cup chopped`).
   Keep the table sorted alphabetically by Ingredient. Never use `|` inside a cell.

5. **Quantity-less items** (`salt to taste`, `oil for frying`): Qty `to taste`
   or `as needed`; leave Unit blank or use the index unit.

Ask before writing only when you can't tell what the ingredient is or which
entry it belongs to. Make all other judgment calls yourself and list them in
the summary (step 5).

## 3. Handle the image

If an image was given, save it as `recipes/<category>/images/<slug>.<ext>`
(keep the original extension):
- Local path → copy it.
- URL → download it with `curl -L -o <dest> "<url>"`, then confirm the file is
  an image (check size and extension; delete it and tell the user if it's HTML
  or empty).

## 4. Write the recipe

Create `recipes/<category>/<slug>.md` in exactly this format. Omit frontmatter
lines and sections that have no value (image, times, tags, source, notes).

```markdown
---
name: Chicken Tikka Masala
category: dinner
servings: 4
prep_time: 20 min
cook_time: 40 min
total_time: 1 hr
tags: indian, chicken
source: https://example.com/tikka-masala
image: images/chicken-tikka-masala.jpg
---

# Chicken Tikka Masala

![Chicken Tikka Masala](images/chicken-tikka-masala.jpg)

## Ingredients

| Qty | Unit | Ingredient | Prep |
|---|---|---|---|
| 1.5 | lb | boneless skinless chicken thigh | cut into 1-inch pieces |
| 1 | each | yellow onion | diced (about 1 cup) |
| to taste |  | kosher salt |  |

## Instructions

1. First step.
2. Second step.

## Notes

- Tips, substitutions, storage.
```

- The Ingredient cell must match the index name exactly; Unit must match the
  index unit.
- When the recipe has components ("For the sauce"), put a `### For the sauce`
  heading and its own table under `## Ingredients` for each.
- Instructions: numbered steps in the user's own wording, cleaned up for
  clarity. Don't invent steps, temperatures, or times. Quantities in the
  instructions may stay in the cook-friendly original units.

## 5. Validate and report

Run `python scripts/recipes.py validate recipes/<category>/<slug>.md` and fix
any errors until it passes. Then run `python scripts/recipes.py validate`
(no args) to confirm the index itself is still valid.

Tell the user:
- the file path,
- the **new index entries** (name, unit, aisle, staple),
- **mapped or converted ingredients** where you made a call
  (`"2 cups chopped onion" → 2 each yellow onion`), especially estimates,
- anything inferred (servings, tags).

Keep it short, as a small table if there are more than a few. The user can
correct anything, and you then update both the recipe and the index.
