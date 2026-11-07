#!/usr/bin/env python3
"""Helper for the recipe repo. Standard library only.

Commands:
  validate [FILE ...]           Check the ingredient index and recipes (all recipes if none given).
  list [--category C] [--ingredients]
                                List recipes, optionally with their ingredients.
  lookup TERM [TERM ...]        Find ingredients in the index by name, alias, or close match.
  shopping-list PLAN [-o OUT]   Combine a meal plan's recipes into a shopping list.
"""
from __future__ import annotations

import argparse
import difflib
import math
import re
import sys
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "ingredients.md"
RECIPES_DIR = ROOT / "recipes"

CATEGORIES = ["breakfast", "lunch", "dinner", "side"]
AISLES = [
    "produce",
    "meat & seafood",
    "dairy & eggs",
    "bakery",
    "deli",
    "frozen",
    "canned & jarred",
    "pasta & grains",
    "baking",
    "spices",
    "condiments & sauces",
    "oils & vinegars",
    "snacks",
    "beverages",
    "international",
    "other",
]
# Units that are bought whole: shopping list totals round up to a whole number.
COUNT_UNITS = {
    "each", "clove", "head", "bunch", "can", "jar", "bottle", "package",
    "box", "bag", "loaf", "slice", "stalk", "sprig", "sheet", "tortilla",
}
NON_NUMERIC_QTY = {"", "to taste", "as needed"}
UNICODE_FRACTIONS = {
    "½": "1/2", "⅓": "1/3", "⅔": "2/3", "¼": "1/4", "¾": "3/4",
    "⅛": "1/8", "⅜": "3/8", "⅝": "5/8", "⅞": "7/8",
}
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


# --------------------------------------------------------------------------- parsing

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Flat `key: value` frontmatter between --- lines."""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    meta: dict[str, str] = {}
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return meta, "\n".join(lines[i + 1:])
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip().lower()] = value.strip()
    return meta, text


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def tables(lines: list[str]) -> list[tuple[list[str], list[list[str]]]]:
    """Return (header, rows) for each markdown table in `lines`."""
    found, block = [], []
    for line in lines + [""]:
        if line.strip().startswith("|"):
            block.append(line)
            continue
        if len(block) >= 2 and set(block[1].replace("|", "").strip()) <= set("-: "):
            header = [h.lower() for h in split_row(block[0])]
            found.append((header, [split_row(r) for r in block[2:]]))
        block = []
    return found


def section(body: str, heading: str) -> list[str]:
    """Lines under `## heading` until the next `## ` heading."""
    out, inside = [], False
    for line in body.splitlines():
        if line.startswith("## "):
            inside = line[3:].strip().lower() == heading.lower()
            continue
        if inside:
            out.append(line)
    return out


def parse_qty(raw: str) -> Fraction | None:
    s = raw.strip().lower()
    for u, f in UNICODE_FRACTIONS.items():
        s = s.replace(u, f" {f}")
    s = s.strip()
    if s in NON_NUMERIC_QTY:
        return None
    total = Fraction(0)
    try:
        for part in s.split():
            total += Fraction(part)
    except (ValueError, ZeroDivisionError):
        raise ValueError(f"unreadable quantity {raw!r}")
    return total


def fmt_qty(q: Fraction, unit: str) -> str:
    if unit in COUNT_UNITS:
        return str(math.ceil(q))
    if unit in {"g", "ml"}:
        return str(round(q))
    # nearest 1/8, shown as a mixed number
    eighths = round(q * 8)
    if eighths == 0:
        return "1/8"
    whole, rem = divmod(eighths, 8)
    frac = Fraction(rem, 8)
    if whole and frac:
        return f"{whole} {frac}"
    return str(whole) if whole else str(frac)


# --------------------------------------------------------------------------- model

@dataclass
class Ingredient:
    name: str
    unit: str
    aisle: str
    staple: bool
    aliases: list[str]
    conversions: str


@dataclass
class RecipeLine:
    qty: Fraction | None
    unit: str
    name: str
    prep: str


@dataclass
class Recipe:
    path: Path
    meta: dict[str, str]
    lines: list[RecipeLine]
    errors: list[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.meta.get("name", self.path.stem)

    @property
    def servings(self) -> int | None:
        try:
            return int(self.meta.get("servings", ""))
        except ValueError:
            return None


def load_index() -> tuple[dict[str, Ingredient], dict[str, str], list[str]]:
    """Return (by_name, alias->name, errors)."""
    errors: list[str] = []
    by_name: dict[str, Ingredient] = {}
    aliases: dict[str, str] = {}
    if not INDEX_PATH.exists():
        return by_name, aliases, [f"{INDEX_PATH.name}: missing"]
    for header, rows in tables(read(INDEX_PATH).splitlines()):
        if "ingredient" not in header:
            continue
        col = {h: i for i, h in enumerate(header)}
        for row in rows:
            get = lambda k: row[col[k]] if k in col and col[k] < len(row) else ""
            name = get("ingredient").strip()
            if not name:
                continue
            key = name.lower()
            ing = Ingredient(
                name=name,
                unit=get("unit").strip().lower(),
                aisle=get("aisle").strip().lower(),
                staple=get("staple").strip().lower() in {"yes", "y", "true"},
                aliases=[a.strip().lower() for a in get("aliases").split(",") if a.strip()],
                conversions=get("conversions").strip(),
            )
            where = f"{INDEX_PATH.name}: '{name}'"
            if name != key:
                errors.append(f"{where}: names must be lowercase")
            if key in by_name:
                errors.append(f"{where}: duplicate entry")
            if not ing.unit:
                errors.append(f"{where}: no unit")
            if ing.aisle not in AISLES:
                errors.append(f"{where}: aisle '{ing.aisle}' is not one of: {', '.join(AISLES)}")
            if get("staple").strip().lower() not in {"yes", "no", "y", "n", "true", "false"}:
                errors.append(f"{where}: staple must be yes or no")
            by_name[key] = ing
    for ing in by_name.values():
        for a in ing.aliases:
            if a in by_name and a != ing.name:
                errors.append(f"{INDEX_PATH.name}: alias '{a}' of '{ing.name}' is also an ingredient name")
            elif a in aliases and aliases[a] != ing.name:
                errors.append(f"{INDEX_PATH.name}: alias '{a}' used by both '{aliases[a]}' and '{ing.name}'")
            aliases[a] = ing.name
    return by_name, aliases, errors


def load_recipe(path: Path) -> Recipe:
    meta, body = parse_frontmatter(read(path))
    recipe = Recipe(path=path, meta=meta, lines=[])
    for header, rows in tables(section(body, "ingredients")):
        col = {h: i for i, h in enumerate(header)}
        if not {"qty", "unit", "ingredient"} <= col.keys():
            recipe.errors.append("ingredient table needs Qty | Unit | Ingredient | Prep columns")
            continue
        for row in rows:
            get = lambda k: row[col[k]] if k in col and col[k] < len(row) else ""
            try:
                qty = parse_qty(get("qty"))
            except ValueError as e:
                recipe.errors.append(str(e))
                qty = None
            recipe.lines.append(RecipeLine(qty, get("unit").lower(), get("ingredient"), get("prep")))
    return recipe


def all_recipe_paths() -> list[Path]:
    return sorted(p for p in RECIPES_DIR.glob("*/*.md") if p.parent.name in CATEGORIES)


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


# --------------------------------------------------------------------------- commands

def check_recipe(recipe: Recipe, by_name, aliases) -> list[str]:
    errs = list(recipe.errors)
    m = recipe.meta
    for key in ("name", "category", "servings"):
        if not m.get(key):
            errs.append(f"frontmatter missing '{key}'")
    cat = m.get("category", "")
    if cat and cat not in CATEGORIES:
        errs.append(f"category '{cat}' must be one of {CATEGORIES}")
    if cat and recipe.path.parent.name != cat:
        errs.append(f"category '{cat}' but file is in recipes/{recipe.path.parent.name}/")
    if m.get("servings") and recipe.servings is None:
        errs.append("servings must be a whole number")
    if m.get("image") and not (recipe.path.parent / m["image"]).exists():
        errs.append(f"image '{m['image']}' not found")
    if not recipe.lines:
        errs.append("no ingredients found under '## Ingredients'")
    _, body = parse_frontmatter(read(recipe.path))
    if not any(l.strip() for l in section(body, "instructions")):
        errs.append("no '## Instructions' section")
    for line in recipe.lines:
        key = line.name.lower()
        ing = by_name.get(key)
        if ing is None:
            if key in aliases:
                errs.append(f"'{line.name}' is an alias; use the index name '{aliases[key]}'")
            else:
                errs.append(f"'{line.name}' is not in {INDEX_PATH.name}")
            continue
        if line.qty is not None and line.unit != ing.unit:
            errs.append(f"'{line.name}' uses unit '{line.unit}' but the index unit is '{ing.unit}'")
        if line.qty is None and line.unit and line.unit != ing.unit:
            errs.append(f"'{line.name}' has unit '{line.unit}' but the index unit is '{ing.unit}'")
    return errs


def cmd_validate(args) -> int:
    by_name, aliases, index_errors = load_index()
    problems = 0
    for e in index_errors:
        print(f"ERROR {e}")
        problems += 1
    paths = [Path(p).resolve() for p in args.files] if args.files else all_recipe_paths()
    for path in paths:
        for e in check_recipe(load_recipe(path), by_name, aliases):
            print(f"ERROR {rel(path)}: {e}")
            problems += 1
    used = {l.name.lower() for p in all_recipe_paths() for l in load_recipe(p).lines}
    unused = sorted(set(by_name) - used)
    if unused and not args.files:
        print(f"note: {len(unused)} index entries not used by any recipe: {', '.join(unused)}")
    print(f"{'OK' if not problems else f'{problems} problem(s)'}: "
          f"{len(by_name)} ingredients, {len(paths)} recipe(s) checked")
    return 1 if problems else 0


def cmd_list(args) -> int:
    for path in all_recipe_paths():
        r = load_recipe(path)
        cat = r.meta.get("category", path.parent.name)
        if args.category and cat != args.category:
            continue
        parts = [cat, r.name, f"serves {r.meta.get('servings', '?')}"]
        for key in ("total_time", "tags"):
            if r.meta.get(key):
                parts.append(r.meta[key])
        parts.append(rel(path))
        print(" | ".join(parts))
        if args.ingredients:
            print("    " + ", ".join(l.name for l in r.lines))
    return 0


def cmd_lookup(args) -> int:
    by_name, aliases, _ = load_index()
    candidates = list(by_name) + list(aliases)

    def show(ing: Ingredient, why: str) -> None:
        extra = f"; conversions: {ing.conversions}" if ing.conversions else ""
        al = f"; aliases: {', '.join(ing.aliases)}" if ing.aliases else ""
        print(f"  {ing.name} [{ing.unit}] ({ing.aisle}{', staple' if ing.staple else ''}){al}{extra}  <- {why}")

    for term in args.terms:
        t = term.lower().strip()
        print(f"{term}:")
        seen: set[str] = set()
        if t in by_name:
            show(by_name[t], "exact"); seen.add(t)
        if t in aliases and aliases[t] not in seen:
            show(by_name[aliases[t]], f"alias '{t}'"); seen.add(aliases[t])
        words = set(re.findall(r"[a-z]+", t))
        for c in candidates:
            target = aliases.get(c, c)
            if target in seen:
                continue
            if t in c or c in t or (words & set(re.findall(r"[a-z]+", c)) - {"of", "and", "or"}):
                show(by_name[target], f"overlaps '{c}'"); seen.add(target)
        for c in difflib.get_close_matches(t, candidates, n=5, cutoff=0.6):
            target = aliases.get(c, c)
            if target not in seen:
                show(by_name[target], f"similar to '{c}'"); seen.add(target)
        if not seen:
            print("  (no match - new ingredient)")
    return 0


def cmd_shopping_list(args) -> int:
    plan_path = Path(args.plan).resolve()
    meta, body = parse_frontmatter(read(plan_path))
    by_name, aliases, index_errors = load_index()
    if index_errors:
        for e in index_errors:
            print(f"ERROR {e}", file=sys.stderr)
        return 1

    totals: dict[str, dict] = {}
    errors: list[str] = []
    cooked = 0
    for header, rows in tables(body.splitlines()):
        if "recipe" not in header:
            continue
        col = {h: i for i, h in enumerate(header)}
        for row in rows:
            cell = row[col["recipe"]] if col["recipe"] < len(row) else ""
            link = LINK_RE.search(cell)
            if not link:
                continue  # leftovers, eating out, etc.
            rpath = (plan_path.parent / link.group(2)).resolve()
            if not rpath.exists():
                errors.append(f"recipe link not found: {link.group(2)}")
                continue
            recipe = load_recipe(rpath)
            problems = check_recipe(recipe, by_name, aliases)
            if problems:
                errors += [f"{rel(rpath)}: {p}" for p in problems]
                continue
            servings_cell = row[col["servings"]] if "servings" in col and col["servings"] < len(row) else ""
            try:
                want = Fraction(servings_cell) if servings_cell else Fraction(recipe.servings)
            except ValueError:
                errors.append(f"bad servings '{servings_cell}' for {recipe.name}")
                continue
            scale = want / recipe.servings
            cooked += 1
            for line in recipe.lines:
                ing = by_name[line.name.lower()]
                t = totals.setdefault(ing.name, {"qty": Fraction(0), "as_needed": False,
                                                 "recipes": [], "optional": True})
                if line.qty is None:
                    t["as_needed"] = True
                else:
                    t["qty"] += line.qty * scale
                if "optional" not in line.prep.lower():
                    t["optional"] = False
                if recipe.name not in t["recipes"]:
                    t["recipes"].append(recipe.name)
    if errors:
        for e in errors:
            print(f"ERROR {e}", file=sys.stderr)
        return 1

    def item(name: str) -> str:
        t, ing = totals[name], by_name[name]
        if t["qty"]:
            amount = fmt_qty(t["qty"], ing.unit)
            amount += "" if ing.unit == "each" else f" {ing.unit}"
            if t["as_needed"]:
                amount += " + more to taste"
        else:
            amount = "as needed"
        opt = " (optional)" if t["optional"] else ""
        return f"- [ ] **{name}** — {amount}{opt} · _{', '.join(t['recipes'])}_"

    start = meta.get("start", plan_path.stem)
    out = [f"# Shopping List — {start}", "",
           f"From [{plan_path.stem} meal plan](../{rel(plan_path)}) · {cooked} recipe(s)", ""]
    buy = [n for n in totals if not by_name[n].staple]
    staples = [n for n in totals if by_name[n].staple]
    for aisle in AISLES:
        names = sorted(n for n in buy if by_name[n].aisle == aisle)
        if names:
            out += [f"## {aisle.title()}", *map(item, names), ""]
    if staples:
        out += ["## Pantry Staples (check before you shop)", *map(item, sorted(staples)), ""]
    text = "\n".join(out)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(text)
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate"); v.add_argument("files", nargs="*"); v.set_defaults(fn=cmd_validate)
    l = sub.add_parser("list"); l.add_argument("--category", choices=CATEGORIES)
    l.add_argument("--ingredients", action="store_true"); l.set_defaults(fn=cmd_list)
    k = sub.add_parser("lookup"); k.add_argument("terms", nargs="+"); k.set_defaults(fn=cmd_lookup)
    s = sub.add_parser("shopping-list"); s.add_argument("plan"); s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_shopping_list)
    args = p.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
