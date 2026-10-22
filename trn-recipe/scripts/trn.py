#!/usr/bin/env python3
"""Render a recipe tree as Cooking for Engineers-style Tabular Recipe Notation.

Input: a JSON file describing the recipe as a tree.

  {
    "title": "Chana Masala",
    "yield": "serves 4",                                   (optional)
    "notes": ["Serve with rice or flatbread."],            (optional)
    "tree": {
      "op": "sauté 1 min",
      "inputs": [
        {"op": "fry until golden", "inputs": [
          {"op": "heat until seeds sizzle", "inputs": [
            "2 Tbs. (30 mL) neutral oil",
            "1 tsp. cumin seeds"
          ]},
          "1 large onion, finely chopped"
        ]},
        "4 cloves garlic, minced"
      ]
    }
  }

A leaf (string) is an ingredient. A node ({"op": ..., "inputs": [...]}) is an
operation applied to its inputs, which may be ingredients or other nodes.
Inputs are listed top-to-bottom in the order they appear in the table.

For a dish with several independent components (crust and filling that are
finished separately), use "components": [ {title, tree}, ... ] instead of a
single "tree". Each component renders as its own table.

Usage:
  trn.py recipe.json --html out.html     # standalone HTML page
  trn.py recipe.json --text              # monospace text table to stdout
  trn.py recipe.json --check             # validate only
"""
import argparse
import html
import json
import sys
import textwrap


# --------------------------------------------------------------------------
# Tree analysis
# --------------------------------------------------------------------------

def is_leaf(node):
    return isinstance(node, str)


def height(node):
    """Leaf = 0; node = 1 + tallest input."""
    if is_leaf(node):
        return 0
    return 1 + max(height(c) for c in node["inputs"])


def leaves(node):
    if is_leaf(node):
        return 1
    return sum(leaves(c) for c in node["inputs"])


def validate(node, path="tree"):
    if is_leaf(node):
        if not node.strip():
            raise ValueError(f"{path}: empty ingredient")
        return
    if not isinstance(node, dict) or "op" not in node or "inputs" not in node:
        raise ValueError(f"{path}: node needs 'op' and 'inputs'")
    if not str(node["op"]).strip():
        raise ValueError(f"{path}: empty op")
    if not node["inputs"]:
        raise ValueError(f"{path}: '{node['op']}' has no inputs")
    for i, c in enumerate(node["inputs"]):
        validate(c, f"{path}.inputs[{i}]")


def grid(tree):
    """Return (rows, ncols).

    rows: list of lists of cells, left-to-right; each cell is
      {"text", "colspan", "rowspan", "kind": "ingredient"|"op"|"final"}
    Only the row where a cell *starts* carries it (HTML rowspan semantics).
    A node sits in column = its height; an input shorter than that gets
    colspan to reach it, so raw ingredients added late span left to right.
    """
    ncols = height(tree) + 1
    return _order_rows(tree, ncols), ncols


def _order_rows(tree, ncols):
    rows = [[] for _ in range(leaves(tree))]

    def place(node, parent_height, first_row):
        col = height(node)
        colspan = parent_height - col
        if is_leaf(node):
            rows[first_row].append((col, {"text": node, "colspan": colspan,
                                          "rowspan": 1, "kind": "ingredient"}))
            return 1
        n = leaves(node)
        r = first_row
        for child in node["inputs"]:
            r += place(child, col, r)
        kind = "final" if parent_height == ncols else "op"
        rows[first_row].append((col, {"text": node["op"], "colspan": colspan,
                                      "rowspan": n, "kind": kind}))
        return n

    place(tree, ncols, 0)
    return [[c for _, c in sorted(row, key=lambda t: t[0])] for row in rows]


# --------------------------------------------------------------------------
# HTML rendering
# --------------------------------------------------------------------------

CSS = """
body { font-family: Georgia, 'Times New Roman', serif; max-width: 720px;
       margin: 2em auto; padding: 0 1em; color: #222; }
h1 { font-size: 1.4em; margin-bottom: .2em; }
.yield { color: #555; font-style: italic; margin: 0 0 1em 0; }
h2 { font-size: 1.1em; margin: 1.5em 0 .4em 0; }
table.trn { border-collapse: collapse; width: 100%; font-size: 15px; }
table.trn td { border: 1px solid #999; padding: 4px 8px; vertical-align: middle; }
table.trn td.ingredient { background: #f7f5ef; }
table.trn td.op { background: #fff; text-align: center; }
table.trn td.final { background: #e9e4d5; text-align: center; font-weight: bold; }
ul.notes { margin-top: 1.2em; color: #444; font-size: 14px; }
.credit { margin-top: 2em; font-size: 12px; color: #888; }
"""


def render_table_html(tree):
    rows, _ = grid(tree)
    out = ['<table class="trn">']
    for row in rows:
        out.append("  <tr>")
        for c in row:
            attrs = [f'class="{c["kind"]}"']
            if c["rowspan"] > 1:
                attrs.append(f'rowspan="{c["rowspan"]}"')
            if c["colspan"] > 1:
                attrs.append(f'colspan="{c["colspan"]}"')
            out.append(f'    <td {" ".join(attrs)}>{html.escape(c["text"])}</td>')
        out.append("  </tr>")
    out.append("</table>")
    return "\n".join(out)


def render_html(recipe, standalone=True):
    parts = []
    parts.append(f"<h1>{html.escape(recipe['title'])}</h1>")
    if recipe.get("yield"):
        parts.append(f'<p class="yield">Yield: {html.escape(recipe["yield"])}</p>')
    for comp in components(recipe):
        if comp.get("title"):
            parts.append(f"<h2>{html.escape(comp['title'])}</h2>")
        parts.append(render_table_html(comp["tree"]))
    if recipe.get("notes"):
        parts.append('<ul class="notes">')
        for n in recipe["notes"]:
            parts.append(f"  <li>{html.escape(n)}</li>")
        parts.append("</ul>")
    parts.append('<p class="credit">Tabular Recipe Notation after Michael Chu, '
                 'cookingforengineers.com</p>')
    body = "\n".join(parts)
    if not standalone:
        return body
    return (f"<!DOCTYPE html>\n<html><head><meta charset='utf-8'>"
            f"<title>{html.escape(recipe['title'])}</title>"
            f"<style>{CSS}</style></head>\n<body>\n{body}\n</body></html>\n")


# --------------------------------------------------------------------------
# Plain-text rendering (box-drawn, monospace)
# --------------------------------------------------------------------------

def render_table_text(tree):
    rows, ncols = grid(tree)
    nrows = len(rows)
    # Expand into a full occupancy grid: cell id per (row, col).
    occ = [[None] * ncols for _ in range(nrows)]
    cells = []
    for r, row in enumerate(rows):
        for c in row:
            col = 0  # first free column in this row
            while occ[r][col] is not None:
                col += 1
            cid = len(cells)
            cells.append({**c, "row": r, "col": col})
            for rr in range(r, r + c["rowspan"]):
                for cc in range(col, col + c["colspan"]):
                    occ[rr][cc] = cid

    # Column widths: single-column cells set a floor; multi-column cells
    # widen the last column they cover if needed.
    # Wrap op text so tall cells stay narrow; ingredients stay on one line.
    for c in cells:
        if c["kind"] == "ingredient":
            c["lines"] = [c["text"]]
            continue
        w = 22
        while True:
            lines = textwrap.wrap(c["text"], w) or [""]
            if len(lines) <= c["rowspan"] or w >= len(c["text"]):
                break
            w += 6
        c["lines"] = lines

    widths = [1] * ncols
    for c in sorted(cells, key=lambda c: c["colspan"]):
        need = max(len(l) for l in c["lines"]) + 2
        span = list(range(c["col"], c["col"] + c["colspan"]))
        have = sum(widths[i] for i in span) + (len(span) - 1)
        if have < need:
            widths[span[-1]] += need - have

    def cell_at(r, col):
        cid = occ[r][col]
        return cells[cid] if cid is not None else None

    lines = []

    def hline(r):
        """Horizontal rule above row r. A segment inside a spanning cell is
        blank; junctions between two different cells become '|'."""
        def cell_id(rr, col):
            return occ[rr][col] if 0 <= rr < nrows else None
        inside = []
        for col in range(ncols):
            a, b = cell_id(r - 1, col), cell_id(r, col)
            inside.append(a is not None and a == b)
        def junction(i, j):
            if i is None or j is None:
                return "+" if not inside[i if j is None else j] else "|"
            if not inside[i] or not inside[j]:
                return "+"
            return " " if occ[r][i] == occ[r][j] else "|"
        s = junction(None, 0)
        for col in range(ncols):
            s += (" " if inside[col] else "-") * widths[col]
            s += junction(col, col + 1) if col + 1 < ncols else junction(col, None)
        return s

    for r in range(nrows):
        lines.append(hline(r))
        s = "|"
        col = 0
        while col < ncols:
            c = cell_at(r, col)
            if c is None:
                s += " " * widths[col] + "|"
                col += 1
                continue
            span = list(range(c["col"], c["col"] + c["colspan"]))
            w = sum(widths[i] for i in span) + (len(span) - 1)
            first = c["row"] + (c["rowspan"] - len(c["lines"])) // 2
            k = r - first
            text = c["lines"][k] if 0 <= k < len(c["lines"]) else ""
            if c["kind"] == "ingredient":
                s += " " + text.ljust(w - 1)
            else:
                s += text.center(w)
            s += "|"
            col = c["col"] + c["colspan"]
        lines.append(s)
    lines.append(hline(nrows))
    return "\n".join(lines)


def render_text(recipe):
    out = [recipe["title"].upper()]
    if recipe.get("yield"):
        out.append(f"Yield: {recipe['yield']}")
    for comp in components(recipe):
        out.append("")
        if comp.get("title"):
            out.append(comp["title"])
        out.append(render_table_text(comp["tree"]))
    if recipe.get("notes"):
        out.append("")
        for n in recipe["notes"]:
            out.append(f"* {n}")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------

def components(recipe):
    if "components" in recipe:
        return recipe["components"]
    return [{"title": None, "tree": recipe["tree"]}]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("recipe", help="recipe JSON file")
    ap.add_argument("--html", metavar="OUT", help="write standalone HTML page")
    ap.add_argument("--fragment", metavar="OUT",
                    help="write HTML fragment (no <html>/<head>)")
    ap.add_argument("--text", action="store_true", help="print text table")
    ap.add_argument("--check", action="store_true", help="validate only")
    args = ap.parse_args()

    with open(args.recipe) as f:
        recipe = json.load(f)
    if "title" not in recipe:
        sys.exit("recipe needs a 'title'")
    for comp in components(recipe):
        validate(comp["tree"])
    if args.check:
        for comp in components(recipe):
            t = comp["tree"]
            print(f"ok: {comp.get('title') or recipe['title']}: "
                  f"{leaves(t)} ingredients, {height(t)+1} columns")
        return
    if args.html:
        with open(args.html, "w") as f:
            f.write(render_html(recipe))
    if args.fragment:
        with open(args.fragment, "w") as f:
            f.write(render_html(recipe, standalone=False))
    if args.text or not (args.html or args.fragment):
        sys.stdout.write(render_text(recipe))


if __name__ == "__main__":
    main()
