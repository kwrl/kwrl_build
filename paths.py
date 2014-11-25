import os

base = os.path.dirname(os.path.abspath(__file__))
template_base = os.path.join(base, "templates")
theme_base = os.path.join(base, "themes")
language_base = os.path.join(base, "languages")
css_assets = os.path.join(template_base,"css")
scratchblocks_filter = os.path.join(base, "pandoc_scratchblocks/filter.py")
rasterize = os.path.join(base, "pandoc_scratchblocks/rasterize.js")
html_assets = [os.path.join(base, "assets",x) for x in ("fonts", "img")]



