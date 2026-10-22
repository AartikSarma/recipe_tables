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

Read it left to right. Ingredients sit in the first column. Each operation spans the rows it consumes and sits to the right of its inputs. The columns converge on one cell: the finished dish. You can see every step, every dependency, and which steps can run in parallel.

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
| [`trn-recipe/references/conventions.md`](trn-recipe/references/conventions.md) | Three worked examples, one per recipe shape (single chain, parallel branches, separate components), and rules for hard cases: reused ingredients, reserved byproducts, repeat-until loops. |

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

## Examples

Each example in [`examples/`](examples/) has its input JSON and both renderings, HTML and text. All three are generic recipes written for this repo, and each shows one of the common shapes a recipe takes.

| Recipe | Shape |
| --- | --- |
| [Chana Masala](examples/chana-masala.json) | One chain. Every step adds to one pot, so the table widens to eight columns. Shown at the top of this page. |
| [Sweet Potato and Black Bean Tacos](examples/sweet-potato-black-bean-tacos.json) | Parallel branches. Four jobs run at once and meet at assembly. |
| [Vanilla Sheet Cake with Chocolate Frosting](examples/vanilla-sheet-cake.json) | Separate components. Cake and frosting are separate tables, joined in a third. |

### Sweet Potato and Black Bean Tacos

The pickled onions, filling, guacamole, and tortillas are independent until the last step. The filling itself has two parallel parts: the roast and the bean simmer.

<table>
  <tr>
    <td colspan="2">1 red onion, thinly sliced</td>
    <td rowspan="5">pour over; stand 20 min</td>
    <td rowspan="22">fill tortillas; top</td>
  </tr>
  <tr>
    <td>1/2 cup (120 mL) cider vinegar</td>
    <td rowspan="4">heat until dissolved</td>
  </tr>
  <tr>
    <td>1/2 cup (120 mL) water</td>
  </tr>
  <tr>
    <td>1 Tbs. (12 g) sugar</td>
  </tr>
  <tr>
    <td>1 tsp. salt</td>
  </tr>
  <tr>
    <td>2 medium (600 g) sweet potatoes, cut into 1/2-inch cubes</td>
    <td rowspan="5">toss; roast 425°F (220°C) 25 min, turning once</td>
    <td rowspan="9">fold together</td>
  </tr>
  <tr>
    <td>2 Tbs. (30 mL) olive oil</td>
  </tr>
  <tr>
    <td>1 tsp. chili powder</td>
  </tr>
  <tr>
    <td>1 tsp. ground cumin</td>
  </tr>
  <tr>
    <td>1/2 tsp. salt</td>
  </tr>
  <tr>
    <td>2 cans (15 oz. / 425 g each) black beans, drained and rinsed</td>
    <td rowspan="4">simmer 5 min; mash lightly</td>
  </tr>
  <tr>
    <td>2 cloves garlic, minced</td>
  </tr>
  <tr>
    <td>1/4 cup (60 mL) water</td>
  </tr>
  <tr>
    <td>1/4 tsp. salt</td>
  </tr>
  <tr>
    <td>2 ripe avocados</td>
    <td rowspan="4" colspan="2">mash</td>
  </tr>
  <tr>
    <td>2 Tbs. (30 mL) lime juice</td>
  </tr>
  <tr>
    <td>2 Tbs. cilantro, chopped (for guacamole)</td>
  </tr>
  <tr>
    <td>1/2 tsp. salt</td>
  </tr>
  <tr>
    <td>12 small (6-inch) corn tortillas</td>
    <td colspan="2">warm in dry skillet, 30 s per side</td>
  </tr>
  <tr>
    <td colspan="3">1/2 cup (60 g) crumbled feta or cotija</td>
  </tr>
  <tr>
    <td colspan="3">2 Tbs. cilantro, chopped (for topping)</td>
  </tr>
  <tr>
    <td colspan="3">1 lime, cut into wedges</td>
  </tr>
</table>

### Vanilla Sheet Cake with Chocolate Frosting

The cake must cool before frosting, so it gets its own table. Make the frosting while it cools.

**Cake**

<table>
  <tr>
    <td>1 cup (226 g) unsalted butter, softened</td>
    <td rowspan="2">cream on medium-high 3 min</td>
    <td rowspan="4">beat 1 min</td>
    <td rowspan="8">mix on low, adding dry and milk alternately, dry first and last</td>
    <td rowspan="8">spread in greased 9x13-inch pan; bake 350°F (175°C) 30-35 min</td>
    <td rowspan="8">cool completely in pan, 1 hr</td>
  </tr>
  <tr>
    <td>1-1/2 cups (300 g) sugar</td>
  </tr>
  <tr>
    <td colspan="2">3 large eggs</td>
  </tr>
  <tr>
    <td colspan="2">2 tsp. vanilla extract</td>
  </tr>
  <tr>
    <td>2-1/2 cups (315 g) all-purpose flour</td>
    <td rowspan="3" colspan="2">whisk</td>
  </tr>
  <tr>
    <td>2-1/2 tsp. baking powder</td>
  </tr>
  <tr>
    <td>1/2 tsp. salt</td>
  </tr>
  <tr>
    <td colspan="3">1-1/4 cups (300 mL) milk</td>
  </tr>
</table>

**Frosting**

<table>
  <tr>
    <td>1/2 cup (113 g) unsalted butter, softened</td>
    <td rowspan="3">beat on low until combined</td>
    <td rowspan="6">beat until fluffy, 2 min</td>
  </tr>
  <tr>
    <td>2-1/2 cups (300 g) powdered sugar</td>
  </tr>
  <tr>
    <td>1/2 cup (40 g) unsweetened cocoa powder</td>
  </tr>
  <tr>
    <td colspan="2">3-4 Tbs. (45-60 mL) milk</td>
  </tr>
  <tr>
    <td colspan="2">1 tsp. vanilla extract</td>
  </tr>
  <tr>
    <td colspan="2">pinch salt</td>
  </tr>
</table>

**Assembly**

<table>
  <tr>
    <td>cooled cake (above)</td>
    <td rowspan="2">spread over top</td>
  </tr>
  <tr>
    <td>frosting (above)</td>
  </tr>
</table>

GitHub shows the HTML files in `examples/` as source. To see them styled, download one and open it in a browser.

## Development

After editing anything under `trn-recipe/`, rebuild the uploadable file:

```bash
python3 package.py    # writes dist/trn-recipe.skill
```

## Credit

Michael Chu created Tabular Recipe Notation for [Cooking for Engineers](https://www.cookingforengineers.com). This project is an independent tool for formatting recipes in that style and is not affiliated with Cooking for Engineers.

## License

[MIT](LICENSE). The license covers this code and documentation, not the notation itself.
