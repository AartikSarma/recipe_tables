---
name: trn-recipe
description: Convert any recipe into Cooking for Engineers-style Tabular Recipe Notation (TRN) — the grid where ingredients run down the left column and each cooking operation is a cell to the right that spans the rows it consumes, so the whole recipe collapses into one finished dish at the far right. Use this whenever the user mentions Cooking for Engineers, cookingforengineers.com, Michael Chu, tabular recipe notation, a "recipe table", "recipe grid", "recipe card like the engineers site", or asks to reformat, summarize, or condense a recipe into a table, chart, or one-glance visual — even if they paste a URL, a photo of a cookbook page, or loose prose instead of a structured recipe.
---

# Tabular Recipe Notation (TRN)

TRN is the recipe card format from cookingforengineers.com. It shows a whole
recipe as one table: ingredients in the left column, operations in cells to the
right. An operation cell spans (rowspan) every ingredient or intermediate it
consumes, and sits one column to the right of its tallest input. Reading left to
right you watch the ingredients merge until a single cell — the dish — fills the
last column. A cook can see the entire recipe, its dependencies, and what can be
done in parallel, at a glance.

Example (the opening steps of a chana masala; the full recipe is 8 columns wide):

```
+----------------------------+------------------+------------------------+-------------+
| 2 Tbs. (30 mL) neutral oil | heat until seeds | fry until golden, 8-10 |             |
+----------------------------+                  |                        |             |
| 1 tsp. cumin seeds         |      sizzle      |          min           |             |
+----------------------------+------------------+                        |             |
| 1 large onion, finely chopped                 |                        | sauté 1 min |
+----------------------------+------------------+------------------------+             |
| 4 cloves garlic, minced                                                |             |
+----------------------------+------------------+------------------------+             |
| 1 Tbs. (6 g) fresh ginger, grated                                      |             |
+----------------------------+------------------+------------------------+             |
| 1-2 green chilies, slit                                                |             |
+----------------------------+------------------+------------------------+-------------+
```

The table is a tree drawn sideways: leaves on the left, root on the right.
Building the tree is the real work; drawing it is mechanical, so a script does
that part.

## Workflow

1. **Get the recipe text.** If the user gives a URL, fetch it. If they give a
   photo, transcribe it. If a step is ambiguous, pick the reading a careful cook
   would and note the assumption below the table — don't stall on it.

2. **Build the operation tree.** Work backward from the finished dish. Ask of
   each step: what does it consume? Each answer is either a raw ingredient or an
   earlier step. Write the tree as JSON (schema below). Rules that matter:
   - Every ingredient appears exactly once, as a leaf. If a recipe uses an
     ingredient in two places (butter for the batter and butter for the pan),
     split it into two leaves with the amounts divided.
   - Work done at the same time ("meanwhile", "while that roasts") becomes
     sibling subtrees that meet at the step combining them. Don't force
     parallel work into one chain just to make the table narrower.
   - An operation's inputs are listed top to bottom in the order the cook adds
     them. Ingredients that go in together are adjacent.
   - Ingredients mentioned in a step but not in the ingredient list (salt to
     taste, water for boiling, oil for the pan) still get a leaf.
   - Prep that happens to a single ingredient before it meets anything else
     (melted, diced, room temperature, toasted) goes in the ingredient text, not
     as its own operation. An operation cell needs at least two inputs, or one
     input plus a transformation that takes real time (proof 1 hr, reduce by
     half, chill overnight).
   - Keep operation labels terse and imperative: `whisk`, `sauté 5 min`,
     `bake 350°F (175°C) 25 min`, `fold in`, `simmer until thick`. Put temperature
     and time in the cell; that's what a cook scans for.
   - The root operation is the last thing done before eating (bake, plate,
     serve). Its cell is what the table converges on.

3. **Use `components` for dishes with independent sub-recipes** (crust and
   filling; cake and frosting; sauce and protein) when a single table would be
   more than ~5 columns wide or the sub-recipes are made hours apart. Refer to a
   finished component as a leaf in a later table: `cooled cake (above)`.
   Otherwise prefer one table; the format's whole point is showing how parts
   join.

4. **Render.** Write the JSON to a file and run the script:
   ```bash
   python3 scripts/trn.py recipe.json --check          # validate, show size
   python3 scripts/trn.py recipe.json --text           # monospace table
   python3 scripts/trn.py recipe.json --html out.html  # styled page with rowspan cells
   python3 scripts/trn.py recipe.json --fragment f.html # bare <table> for pasting
   ```
   The script computes all rowspan/colspan values, wraps long op labels, and
   stretches late-joining ingredients across empty columns. Never hand-build
   the table; the span arithmetic is easy to get wrong and a mis-spanned cell
   silently misstates the recipe.

5. **Deliver.** Default to the HTML file (it renders the real merged cells and
   survives being opened on a phone) plus the text table inline in chat so the
   user sees it immediately. Below the table, list anything that doesn't fit a
   cell: yield, make-ahead notes, doneness cues, assumptions you made. Keep the
   notes short; if the recipe needs a paragraph of technique, that's a sign a
   step should be split.

## JSON schema

```json
{
  "title": "Chana Masala",
  "yield": "serves 4",
  "notes": ["If the spices start to scorch, add a splash of water."],
  "tree": {
    "op": "sauté 1 min",
    "inputs": [
      {"op": "fry until golden, 8-10 min", "inputs": [
        {"op": "heat until seeds sizzle", "inputs": ["2 Tbs. (30 mL) neutral oil", "1 tsp. cumin seeds"]},
        "1 large onion, finely chopped"]},
      "4 cloves garlic, minced",
      "1 Tbs. (6 g) fresh ginger, grated"
    ]
  }
}
```

- A string is an ingredient (leaf). An object with `op` and `inputs` is an
  operation. Inputs can mix strings and objects.
- Replace `tree` with `"components": [{"title": "Crust", "tree": {...}}, ...]`
  for multi-part dishes.
- `yield` and `notes` are optional.

## Ingredient cell style

Match the site: quantity first, metric in parentheses, then the ingredient, then
its prep state after a comma. Abbreviate `Tbs.` and `tsp.`; spell out `cups`.

- `1-1/2 cups (190 g) all-purpose flour`
- `14 oz. (400 g) can crushed tomatoes`
- `2 cloves garlic, minced`
- `1 lb. (450 g) chicken thighs, boneless, cut into 1-inch pieces`
- `salt and pepper to taste`

Convert to metric when the source gives only volume; standard densities are
fine (flour 125 g/cup, sugar 200 g/cup, butter 227 g/cup, liquids 240 mL/cup).
When the source already gives weights, keep them.

Read `references/conventions.md` before building your first tree. It has three
worked examples, one for each common shape: a single one-pot chain (chana
masala), parallel branches meeting at assembly (tacos), and separate components
joined at the end (sheet cake). It also covers loops, optional steps, and the
site's typographic conventions.
