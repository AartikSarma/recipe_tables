# recipe_tables

A [Claude skill](https://support.claude.com/en/articles/12512180-use-skills-in-claude) that rewrites any recipe in **Tabular Recipe Notation (TRN)**, the one-glance recipe card format from [Cooking for Engineers](https://www.cookingforengineers.com).

Give Claude a recipe as a URL, pasted text, or a photo of a cookbook page. It returns a table like this:

<table>
  <tr>
    <td>2 Tbs. (30 mL) neutral oil</td>
    <td rowspan="2">heat until seeds sizzle</td>
    <td rowspan="3">fry until golden, 8-10 min</td>
    <td rowspan="6">sauté 1 min</td>
    <td rowspan="10">stir 1 min</td>
    <td rowspan="12">cook until oil separates, 8-10 min</td>
    <td rowspan="14">simmer 15-20 min; mash a few chickpeas</td>
    <td rowspan="17">stir in; top with cilantro</td>
  </tr>
  <tr>
    <td>1 tsp. cumin seeds</td>
  </tr>
  <tr>
    <td colspan="2">1 large onion, finely chopped</td>
  </tr>
  <tr>
    <td colspan="3">4 cloves garlic, minced</td>
  </tr>
  <tr>
    <td colspan="3">1 Tbs. (6 g) fresh ginger, grated</td>
  </tr>
  <tr>
    <td colspan="3">1-2 green chilies, slit</td>
  </tr>
  <tr>
    <td colspan="4">1 tsp. ground coriander</td>
  </tr>
  <tr>
    <td colspan="4">1 tsp. ground cumin</td>
  </tr>
  <tr>
    <td colspan="4">1/2 tsp. ground turmeric</td>
  </tr>
  <tr>
    <td colspan="4">1 tsp. Kashmiri chili powder</td>
  </tr>
  <tr>
    <td colspan="5">14 oz. (400 g) can crushed tomatoes</td>
  </tr>
  <tr>
    <td colspan="5">1 tsp. salt</td>
  </tr>
  <tr>
    <td colspan="6">2 cans (15 oz. / 425 g each) chickpeas, drained and rinsed</td>
  </tr>
  <tr>
    <td colspan="6">1 cup (240 mL) water</td>
  </tr>
  <tr>
    <td colspan="7">1 tsp. garam masala</td>
  </tr>
  <tr>
    <td colspan="7">1 tsp. amchur (dried mango powder)</td>
  </tr>
  <tr>
    <td colspan="7">1/4 cup (5 g) cilantro, chopped</td>
  </tr>
</table>

Read it left to right. Ingredients sit in the first column. Each operation spans the rows it consumes and sits to the right of its inputs. The columns converge on one cell: the finished dish. You can see every step, every dependency, and which steps can run in parallel without reading a paragraph.

## Install

### Claude app (web, desktop, mobile)

1. Download [`dist/trn-recipe.skill`](dist/trn-recipe.skill).
2. Upload it in Claude's skills settings. Anthropic's [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude) article shows where.
3. Turn on code execution if it is off. The skill runs a small Python script.

On Team and Enterprise plans you can also share an uploaded skill with colleagues from inside Claude; the same article explains how.

### Claude Code

Copy the skill folder into your personal or project skills directory:

```bash
git clone https://github.com/AartikSarma/recipe_tables
cp -r recipe_tables/trn-recipe ~/.claude/skills/        # all projects
# or
cp -r recipe_tables/trn-recipe .claude/skills/          # this project only
```

## Use

Ask in plain language. The skill triggers on mentions of Cooking for Engineers, tabular recipe notation, or requests for a recipe table, grid, or card.

> Turn this into a Cooking for Engineers table: [recipe URL]

> Make a recipe card for my grandmother's lasagna. [pasted text]

Claude builds an operation tree, renders it, and returns a styled HTML page plus a monospace text version. Yield, doneness cues, make-ahead notes, and optional variations go in a list under the table.

## How it works

The skill has three parts:

| File | Role |
| --- | --- |
| [`trn-recipe/SKILL.md`](trn-recipe/SKILL.md) | Instructions Claude follows: how to turn prose into an operation tree, and the site's style for ingredient cells. |
| [`trn-recipe/scripts/trn.py`](trn-recipe/scripts/trn.py) | Renderer. Reads the tree as JSON and computes every rowspan and colspan. Standard library only. |
| [`trn-recipe/references/conventions.md`](trn-recipe/references/conventions.md) | A worked prose-to-tree example and rules for hard cases: reused ingredients, reserved byproducts, parallel steps, repeat-until loops. |

Claude does the judgment (what consumes what); the script does the arithmetic. Hand-built spans go wrong easily, and a mis-spanned cell silently misstates the recipe.

### Recipe JSON

A string is an ingredient. An object with `op` and `inputs` is an operation. Inputs may be ingredients or other operations.

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
      "4 cloves garlic, minced"
    ]
  }
}
```

For dishes with separate sub-recipes, such as a curry and its rice, or a crust and its filling, replace `tree` with `"components": [{"title": "Crust", "tree": {...}}, ...]`. Each component renders as its own table.

### Running the renderer yourself

```bash
python3 trn-recipe/scripts/trn.py recipe.json --check            # validate; report size
python3 trn-recipe/scripts/trn.py recipe.json --text             # monospace table to stdout
python3 trn-recipe/scripts/trn.py recipe.json --html out.html    # standalone styled page
python3 trn-recipe/scripts/trn.py recipe.json --fragment out.html  # bare table for embedding
```

## Example

[`examples/chana-masala.json`](examples/chana-masala.json) holds the recipe shown at the top, with its [HTML](examples/chana-masala.html) and [text](examples/chana-masala.txt) renderings. It is a generic home-style version written for this repo. Its single long chain shows how a one-pot dish lays out: each step adds to the pot, so the table widens to eight columns and the finishing ingredients stretch across to meet the last cell.

GitHub shows the HTML file as source. To see it rendered, download it and open it in a browser.

## Development

After editing anything under `trn-recipe/`, rebuild the uploadable file:

```bash
python3 package.py    # writes dist/trn-recipe.skill
```

## Credit

Michael Chu created Tabular Recipe Notation for [Cooking for Engineers](https://www.cookingforengineers.com). This project is an independent tool for formatting recipes in that style and is not affiliated with Cooking for Engineers.

## License

[MIT](LICENSE). The license covers this code and documentation, not the notation itself.
