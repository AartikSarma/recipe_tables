# TRN conventions and a worked example

## How the layout is derived (so you can sanity-check output)

- A leaf sits in column 0. An operation sits in column = 1 + the tallest of its
  inputs (its "height").
- A cell's rowspan is the number of leaves beneath it.
- An input shorter than its parent's column gets colspan to reach it. This is
  why a raw ingredient added at the very end (egg wash, garnish) stretches
  across the whole table to meet the final cell.
- The root's cell spans every row and sits in the last column.

Check: every row of the rendered table has exactly the same number of columns
once spans are counted. The script guarantees this; if you read a table that
violates it, the tree was wrong.

## Worked example: prose to tree

Source (typical cookbook prose):

> Heat 2 tablespoons oil in a heavy pot over medium heat. Add 1 teaspoon cumin
> seeds and let them sizzle. Add a finely chopped onion and fry until golden,
> 8 to 10 minutes. Add 4 cloves minced garlic, a tablespoon of grated ginger,
> and 1 or 2 slit green chilies; sauté 1 minute. Stir in 1 teaspoon each ground
> coriander, ground cumin, and Kashmiri chili powder, plus 1/2 teaspoon
> turmeric, and cook 1 minute. Add a 14-oz can of crushed tomatoes and 1
> teaspoon salt; cook until the oil separates from the masala, 8 to 10 minutes.
> Add two drained cans of chickpeas and 1 cup water. Simmer 15 to 20 minutes,
> mashing a few chickpeas to thicken the sauce. Stir in 1 teaspoon each garam
> masala and amchur, and top with chopped cilantro.

Work backward:

- Last step: *stir in; top with cilantro* — consumes the simmered chickpeas,
  garam masala, amchur, and cilantro. The three finishing ingredients are raw
  leaves joining at the very end, so they stretch across the whole table.
- *Simmer 15-20 min* — consumes the cooked masala, chickpeas, and water.
- *Cook until oil separates* — consumes the spiced base, tomatoes, and salt.
- *Stir 1 min* — consumes the aromatic base and the four ground spices.
- *Sauté 1 min* — consumes the fried onion plus garlic, ginger, and chilies.
- *Fry until golden* — consumes the tempered oil and the onion.
- *Heat until seeds sizzle* — consumes oil and cumin seeds. This is a real
  two-input step (a tempering), so it gets its own cell rather than being folded
  into an ingredient.

```json
{
  "title": "Chana Masala",
  "yield": "serves 4",
  "tree": {
    "op": "stir in; top with cilantro",
    "inputs": [
      {
        "op": "simmer 15-20 min; mash a few chickpeas",
        "inputs": [
          {
            "op": "cook until oil separates, 8-10 min",
            "inputs": [
              {
                "op": "stir 1 min",
                "inputs": [
                  {
                    "op": "sauté 1 min",
                    "inputs": [
                      {
                        "op": "fry until golden, 8-10 min",
                        "inputs": [
                          {
                            "op": "heat until seeds sizzle",
                            "inputs": [
                              "2 Tbs. (30 mL) neutral oil",
                              "1 tsp. cumin seeds"
                            ]
                          },
                          "1 large onion, finely chopped"
                        ]
                      },
                      "4 cloves garlic, minced",
                      "1 Tbs. (6 g) fresh ginger, grated",
                      "1-2 green chilies, slit"
                    ]
                  },
                  "1 tsp. ground coriander",
                  "1 tsp. ground cumin",
                  "1/2 tsp. ground turmeric",
                  "1 tsp. Kashmiri chili powder"
                ]
              },
              "14 oz. (400 g) can crushed tomatoes",
              "1 tsp. salt"
            ]
          },
          "2 cans (15 oz. / 425 g each) chickpeas, drained and rinsed",
          "1 cup (240 mL) water"
        ]
      },
      "1 tsp. garam masala",
      "1 tsp. amchur (dried mango powder)",
      "1/4 cup (5 g) cilantro, chopped"
    ]
  }
}
```

Rendered:

```
+----------------------------+------------------+------------------------+-------------+------------+---------------------+------------------------+-------------------+
| 2 Tbs. (30 mL) neutral oil | heat until seeds | fry until golden, 8-10 |             |            |                     |                        |                   |
+----------------------------+                  |                        |             |            |                     |                        |                   |
| 1 tsp. cumin seeds         |      sizzle      |          min           |             |            |                     |                        |                   |
+----------------------------+------------------+                        |             |            |                     |                        |                   |
| 1 large onion, finely chopped                 |                        | sauté 1 min |            |                     |                        |                   |
+----------------------------+------------------+------------------------+             |            |                     |                        |                   |
| 4 cloves garlic, minced                                                |             |            |                     |                        |                   |
+----------------------------+------------------+------------------------+             |            |                     |                        |                   |
| 1 Tbs. (6 g) fresh ginger, grated                                      |             | stir 1 min |                     |                        |                   |
+----------------------------+------------------+------------------------+             |            |                     |                        |                   |
| 1-2 green chilies, slit                                                |             |            |    cook until oil   |                        |                   |
+----------------------------+------------------+------------------------+-------------+            |                     |                        |                   |
| 1 tsp. ground coriander                                                              |            | separates, 8-10 min | simmer 15-20 min; mash |                   |
+----------------------------+------------------+------------------------+-------------+            |                     |                        |                   |
| 1 tsp. ground cumin                                                                  |            |                     |    a few chickpeas     | stir in; top with |
+----------------------------+------------------+------------------------+-------------+            |                     |                        |                   |
| 1/2 tsp. ground turmeric                                                             |            |                     |                        |      cilantro     |
+----------------------------+------------------+------------------------+-------------+            |                     |                        |                   |
| 1 tsp. Kashmiri chili powder                                                         |            |                     |                        |                   |
+----------------------------+------------------+------------------------+-------------+------------+                     |                        |                   |
| 14 oz. (400 g) can crushed tomatoes                                                               |                     |                        |                   |
+----------------------------+------------------+------------------------+-------------+------------+                     |                        |                   |
| 1 tsp. salt                                                                                       |                     |                        |                   |
+----------------------------+------------------+------------------------+-------------+------------+---------------------+                        |                   |
| 2 cans (15 oz. / 425 g each) chickpeas, drained and rinsed                                                              |                        |                   |
+----------------------------+------------------+------------------------+-------------+------------+---------------------+                        |                   |
| 1 cup (240 mL) water                                                                                                    |                        |                   |
+----------------------------+------------------+------------------------+-------------+------------+---------------------+------------------------+                   |
| 1 tsp. garam masala                                                                                                                              |                   |
+----------------------------+------------------+------------------------+-------------+------------+---------------------+------------------------+                   |
| 1 tsp. amchur (dried mango powder)                                                                                                               |                   |
+----------------------------+------------------+------------------------+-------------+------------+---------------------+------------------------+                   |
| 1/4 cup (5 g) cilantro, chopped                                                                                                                  |                   |
+----------------------------+------------------+------------------------+-------------+------------+---------------------+------------------------+-------------------+
```

Every step adds something to one pot, so the tree is a single long chain and
the table runs to eight columns. That's correct: the layout shows that nothing
here can happen in parallel. If a recipe has two such chains (a curry and a
separately cooked rice, say), split them with `components`.

## Situations that need a decision

**Ingredient used twice.** Split it: `2 Tbs. butter (for pan)` and
`4 Tbs. butter, melted`. Each leaf appears once.

**Byproduct reused later** (reserved pasta water, bacon fat, pan drippings).
Add it as a separate leaf labeled `reserved …` feeding the later step. Say so
in a note.

**"Meanwhile" / parallel steps.** These are simply sibling subtrees. The table
shows parallelism naturally — two operation cells at the same column that don't
overlap in rows can happen at the same time.

**Repeat-until loops** (fold in egg whites in three additions; add stock a
ladle at a time). Collapse into one op: `fold in, 3 additions`,
`add 1 ladle at a time, stirring, ~20 min`.

**Optional ingredients or variations.** Put them in `notes`, not the table.
The table shows one recipe.

**Resting/chilling with no new ingredient.** A single-input op is fine when
it takes real time: `{"op": "chill 1 hr", "inputs": [ {...} ]}`. Don't make
single-input ops for instant prep like "melt" — fold that into the ingredient.

**Equipment prep** (preheat oven, grease pan). Not ingredients; put the
temperature in the bake cell and any pan prep in notes.

**Serving and plating.** Include a final `serve` / `plate` op only if it joins
something (a garnish, a sauce). If the bake is the last step, the bake cell is
the root.

## Site typography

- Fractions as `1-1/2`, `3/4`, never decimals for volumes.
- `Tbs.` and `tsp.` with periods; `oz.`, `lb.`, `qt.`; `cups`, `g`, `mL`, `L`.
- Temperatures: `350°F (175°C)`. Give both.
- Ingredient prep after a comma in the same cell: `1 onion, diced`.
- Op cells lowercase and short. Time and temperature belong in the op cell.
- Title in Title Case; yield as a short phrase (`serves 4`,
  `about 24 cookies`).

## Credit

The notation is Michael Chu's (Cooking for Engineers). When the output is
published or shared beyond personal use, keep the credit line the script adds.
