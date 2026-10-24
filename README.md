# WordSolver Hub

Free, original word solvers and word games for US players. No sign-in, no download, no paywall, no backend.

- Static HTML/CSS/JS — no build step. Open `index.html` or deploy the folder as-is.
- Theme: dark emerald — background #101418, panels #172C26, accent #00D68F.
- Daily puzzles are seeded by the US Eastern calendar date, so every player sees the same daily puzzle.
- 207 pages: solvers, playable games, logic/number games, word lists, guides, blog, hints/archives, leaderboards (local-only), and site info.
- All code, text, puzzles, and word lists were written for this site. Game names are generic descriptions.

## Regenerate pages

`python3 generate.py` rebuilds every HTML page, `sitemap.xml`, and `robots.txt` from the templates and curated word lists in `assets/words.js`.

## Deploy

Static hosting only. Point Vercel (or any static host) at this folder; no build command is needed.
