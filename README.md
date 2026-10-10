# marigold.cash

Holding page for **Marigold** — digital cash in fixed notes. Served via GitHub Pages at [marigold.cash](https://marigold.cash).

Static, no build step. Edit a page, push to `main`, done.

Every page carries the same header (the specimen note, with the page's title on its face and the row of buttons as tabs) and the same footer. Both come from `tools/chrome.py`, which stamps them into each page between the `chrome:header` and `chrome:footer` markers; `chrome.css` holds their styles and `rosette.svg` the flower. To change a tab, a title or the footer, edit the tool and run it:

```
python3 tools/chrome.py          # rewrite every page
python3 tools/chrome.py --check  # exit 1 if a page is stale
```

The litepaper page is copied from `whitepaper/litepaper-web.html` in the marigold repository, where its prose is kept in eight languages; edit it there, copy it here, and run the tool.
