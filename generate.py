#!/usr/bin/env python3
"""Generate WordSolver Hub: original static site. No copied content."""
import os, re, json, html
ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = "https://word-solver-hub-ten.vercel.app"
SITE = "WordSolver Hub"

# --- load word lists from assets/words.js (same source the browser uses) ---
src = open(os.path.join(ROOT, "assets/words.js")).read()
def _extract(key):
    m = re.search(rf"{key}:\s*\"([^\"]+)\"", src)
    return m.group(1).split() if m else []
LISTS = {}
for k in ["two","three","four"]:
    LISTS[k] = sorted(set(_extract(k)))
# five/six/seven are filtered at runtime in JS; approximate in python by re-applying length filters
# to the raw five block plus six/seven blocks
raw_five = _extract("five")
# six/seven blocks in words.js are long strings filtered by JS; extract their raw tokens
def _raw_after(marker):
    m = re.search(marker + r".*?\"([^\"]+)\"", src, re.S)
    return m.group(1).split() if m else []
# Simpler: parse all quoted strings in words.js and collect by length
all_tokens = set()
for q in re.findall(r'"([a-z ]+)"', src):
    for t in q.split():
        if t.isalpha() and t.islower():
            all_tokens.add(t)
LISTS["five"] = sorted(w for w in all_tokens if len(w)==5)
LISTS["six"] = sorted(w for w in all_tokens if len(w)==6)
LISTS["seven"] = sorted(w for w in all_tokens if len(w)==7)
LISTS["all"] = sorted(all_tokens)

HEADER = """<header><nav class="nav"><a class="logo" href="{rel}index.html">Word<span>Solver</span> Hub</a>
<a class="nlink" href="{rel}word-games.html">Word Games</a><a class="nlink" href="{rel}logic-puzzles.html">Logic Puzzles</a><a class="nlink" href="{rel}number-games.html">Number Games</a><a class="nlink" href="{rel}solvers.html">Solvers</a><a class="nlink" href="{rel}lists/word-lists.html">Word Lists</a><a class="nlink" href="{rel}guides.html">Guides</a><a class="nlink" href="{rel}blog/index.html">Blog</a><a class="nlink" href="{rel}leaderboards.html">Leaderboards</a><a class="nlink" href="{rel}unblocked-games.html">Unblocked</a></nav></header>"""
FOOTER = """<footer><div class="foot"><div><strong style="color:#fff">WordSolver Hub</strong><p>Free word solvers and daily word, logic, and number games for players in the United States. No sign-in, no download, no paywall.</p></div>
<div><strong style="color:#fff">Games</strong><a href="{rel}word-games.html">All Word Games</a><a href="{rel}games/five-letter-game.html">5-Letter Word Game</a><a href="{rel}games/category-sort.html">Category Sort Game</a><a href="{rel}games/word-search.html">Word Search</a><a href="{rel}logic/sudoku.html">Sudoku</a><a href="{rel}logic/2048.html">2048</a></div>
<div><strong style="color:#fff">Solvers</strong><a href="{rel}solvers.html">All Solvers</a><a href="{rel}solvers/word-finder.html">Word Finder</a><a href="{rel}solvers/anagram-solver.html">Anagram Solver</a><a href="{rel}solvers/scrabble-solver.html">Scrabble Solver</a><a href="{rel}solvers/crossword-solver.html">Crossword Solver</a><a href="{rel}solvers/word-search-maker.html">Word Search Maker</a></div>
<div><strong style="color:#fff">Site</strong><a href="{rel}about.html">About</a><a href="{rel}contact.html">Contact</a><a href="{rel}privacy.html">Privacy Policy</a><a href="{rel}terms.html">Terms</a><a href="{rel}lists/word-lists.html">Word Lists</a><a href="{rel}leaderboards.html">Leaderboards</a></div></div>
<div style="text-align:center;padding:0 16px 20px;color:#94A3B8;font-size:13px">WordSolver Hub is an original site. Game names on this site are generic descriptions, not trademarks of any publisher.</div></footer>"""

def rel_for(path):
    depth = path.count("/")
    return "../" * depth if depth else ""

def faq_html(faqs):
    if not faqs: return ""
    items = "".join(f"<h3>{q}</h3><p>{a}</p>" for q,a in faqs)
    return f"<section><h2>Frequently Asked Questions</h2>{items}</section>"

def jsonld(page_type, title, desc, faqs=None):
    base = {"@context":"https://schema.org","@type":page_type,"name":title,"description":desc}
    if faqs:
        return json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}, indent=2)
    return json.dumps(base, indent=2)

PAGES = []  # (path, title, desc)
def render(path, title, desc, h1, body, faqs=None, page_type="WebPage", extra_head=""):
    rel = rel_for(path)
    canon = BASE + "/" + path if path != "index.html" else BASE + "/"
    faq = faq_html(faqs)
    ld = jsonld(page_type, title, desc, faqs)
    full = f"""<!DOCTYPE html>
<html lang="en-US"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;700;900&display=swap" rel="stylesheet">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:type" content="website"><meta property="og:url" content="{canon}"><meta property="og:site_name" content="WordSolver Hub">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{html.escape(title)}"><meta name="twitter:description" content="{html.escape(desc)}">
<link rel="stylesheet" href="{rel}assets/style.css"><script type="application/ld+json">{ld}</script>{extra_head}</head>
<body>{HEADER.format(rel=rel)}<main><h1>{h1}</h1>{body}{faq}</main>{FOOTER.format(rel=rel)}
<script src="{rel}assets/words.js"></script><script src="{rel}assets/tools.js"></script><script src="{rel}assets/games.js"></script></body></html>"""
    dest = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(dest) or ROOT, exist_ok=True)
    open(dest, "w").write(full)
    PAGES.append((path, title, desc))

def cards(items):
    out = '<div class="grid">'
    for href, name, d in items:
        out += f'<div class="card"><h3>{name}</h3><p>{d}</p><a href="{href}">Open &rarr;</a></div>'
    return out + "</div>"

def tool_page(path, title, desc, intro, form_html, script, faqs, related):
    body = f"<p>{intro}</p><div class='toolbox'>{form_html}</div><section><h2>How to Use This Tool</h2><p>Type your letters, press the button, and review the results. Results come from our own curated common-English word list, checked entirely in your browser. Nothing you type is sent to a server.</p></section><section><h2>Related Pages</h2><p>{related}</p></section>"
    render(path, title, desc, title.split(" | ")[0], body, faqs, "WebApplication", extra_head=f"<script>window.addEventListener('DOMContentLoaded',()=>{{{script}}});</script>")

def game_page(path, title, desc, intro, body_html, script, faqs, related):
    body = f"<p>{intro}</p><div class='toolbox'>{body_html}</div><section><h2>How to Play</h2><p>Play right in your browser. No sign-in or download is needed. Your best scores are saved only on your own device, on the <a href='../leaderboards.html'>Leaderboards</a> page.</p></section><section><h2>Related Games</h2><p>{related}</p></section>"
    render(path, title, desc, title.split(" | ")[0], body, faqs, "VideoGame", extra_head=f"<script>window.addEventListener('DOMContentLoaded',()=>{{{script}}});</script>")

# ================= CORE PAGES =================
FAQ_HOME = [("Is WordSolver Hub really free?","Yes. Every solver and game on this site is free, with no sign-in, no download, and no paywall."),
("Do I need an account to play?","No. You can play and use every tool right away. Scores are saved only in your own browser if you choose to track them."),
("Are the daily puzzles the same for everyone?","Yes. Daily puzzles are picked from the calendar date in US Eastern time, so every player in the United States sees the same daily puzzle on the same day.")]
render("index.html", "Free Word Solver & Word Games USA | WordSolver Hub",
 "Free word solver and daily word games for US players. Solve anagrams, find Scrabble words, and play 5-letter, category, Sudoku, and 2048 games.",
 "Free Word Solver & Word Games",
 """<div class="hero"><p><span class="badge">FREE &bull; NO SIGN-IN &bull; NO DOWNLOAD</span></p><h1 style="margin-top:12px">Free Word Solver &amp; Word Games</h1>
 <p>Stuck on a word puzzle? Find the word from your letters, unscramble an anagram, check a Scrabble rack, or play a fresh daily puzzle. Everything runs in your browser, in plain US English.</p>
 <p><a class="btn" href="solvers/word-finder.html">Find Words Now</a> &nbsp; <a class="btn2" href="games/five-letter-game.html">Play Today's 5-Letter Game</a></p>
 <p class="small" id="daily-teaser"></p></div>
 <section><h2>Featured Games</h2>""" + cards([
  ("games/five-letter-game.html","5-Letter Word Game","Guess the daily 5-letter word in six tries, plus unlimited practice rounds."),
  ("games/category-sort.html","Category Sort Game","Sort 16 words into 4 groups. A new set every day."),
  ("logic/sudoku.html","Sudoku","Classic 9x9 Sudoku with notes, hints, and checking."),
  ("logic/2048.html","2048","Slide and combine tiles to reach 2048."),
  ("games/word-search.html","Word Search","Find hidden words in a daily letter grid."),
  ("games/spelling-hive.html","Spelling Hive","Build words from seven letters, with one required center letter."),
 ]) + """</section>
 <section><h2>Solver Tools</h2>""" + cards([
  ("solvers/word-finder.html","Word Finder","Every word you can make from your letters, grouped by length."),
  ("solvers/anagram-solver.html","Anagram Solver","Unscramble letters into every valid word, longest first."),
  ("solvers/scrabble-solver.html","Scrabble Solver","Rack lookup with Scrabble point scores."),
  ("solvers/word-guess-solver.html","Word Guess Solver","Narrow candidates with known, misplaced, and ruled-out letters."),
  ("solvers/crossword-solver.html","Crossword Solver","Pattern matching with ? for unknown letters."),
  ("solvers/word-search-maker.html","Word Search Maker","Build your own word search grid and print it."),
 ]) + """</section>
 <section><h2>Browse by Type</h2><p><a href="word-games.html">Word Games</a> &bull; <a href="logic-puzzles.html">Logic Puzzles</a> &bull; <a href="number-games.html">Number Games</a> &bull; <a href="solvers.html">All Solvers</a> &bull; <a href="lists/word-lists.html">Word Lists</a> &bull; <a href="guides.html">Guides</a> &bull; <a href="blog/index.html">Blog</a> &bull; <a href="unblocked-games.html">Unblocked Games</a></p></section>
 <section><h2>Why Players Choose WordSolver Hub</h2><p>Our solvers use a curated list of common US English words, so results are readable and useful, not a wall of rare words. Daily puzzles reset at midnight US Eastern time. Guides explain strategy in plain language, and every page links to related tools so you can keep playing without searching again.</p></section>""",
 FAQ_HOME, "WebSite", extra_head="""<script>window.addEventListener('DOMContentLoaded',()=>{try{const w=dailyPick(WORDS.five,'five-letter-game');const el=document.getElementById('daily-teaser');if(el)el.textContent="Today's daily puzzle is ready for "+easternDateString()+" (US Eastern). Play it on the 5-Letter Game page.";}catch(e){}});</script>""")

render("word-games.html", "Word Games Online Free | WordSolver Hub",
 "Play free word games online: 5-letter guessing, category sorting, word search, anagrams, crosswords, and more. No sign-in needed.",
 "Word Games", "<p>Browse every word game on WordSolver Hub. Daily games reset at midnight US Eastern time.</p>" + cards([
  ("games/five-letter-game.html","5-Letter Word Game","Daily guessing game."),("games/five-letter-practice.html","5-Letter Practice","Unlimited practice rounds."),
  ("games/category-sort.html","Category Sort Game","Sort 16 words into 4 groups."),("games/word-search.html","Word Search","Find words in a grid."),
  ("games/anagram-game.html","Anagram Game","Unscramble the daily word."),("games/boggle-grid.html","Letter Grid Game","Build words from a 4x4 grid."),
  ("games/chain-words.html","Chain Words Game","Each word starts with the last letter of the previous word."),
  ("games/clue-words.html","Clue Words Game","Guess the word from three clues."),("games/word-similarity.html","Word Similarity Game","Guess the secret word and get closeness hints."),
  ("games/daily-crossword.html","Daily Crossword","Original crossword-style clues, new each day."),("games/mini-crossword.html","Mini Crossword","A quick crossword-style puzzle."),
  ("games/double-word-game.html","Double Word Game","Guess two words at once."),("games/quad-word-game.html","Quad Word Game","Guess four words at once."),
  ("games/octo-word-game.html","Octo Word Game","Guess eight words at once."),("games/jumble-game.html","Jumble Game","Unscramble a mixed-up word."),
  ("games/spelling-hive.html","Spelling Hive","Words from seven letters."),("games/square-words.html","Square Words","Rows and columns that are all words."),
  ("games/word-path.html","Word Path Game","Find words along letter paths."),("games/word-square.html","5x5 Word Square","Build a square of words."),
  ("games/word-board.html","Word Board Game","Score words from a letter rack."),("games/word-ladder.html","Word Ladder","Change one letter at a time to reach the target."),
  ("games/word-memory.html","Word Memory","Match pairs of words."),("games/letter-link.html","Letter Link","Spell the target word in order."),
  ("games/word-connect.html","Word Connect","Match words to their meanings."),("games/word-tiles.html","Word Tiles","Reorder tiles to spell the word."),
  ("games/scramble-game.html","Scramble Game","Unscramble words against the clock."),("games/guess-the-word.html","Guess the Word","Guess from a definition."),
  ("games/six-letter-game.html","6-Letter Word Game","A longer daily guessing game."),("games/word-craft.html","Word Craft","Combine words to discover new ones."),
 ]), None)
render("logic-puzzles.html", "Logic Puzzles Online Free | WordSolver Hub",
 "Free logic puzzles: Sudoku variants, Minesweeper, Nonogram, Queens, Tango, Zip, and Solitaire. Play in your browser.",
 "Logic Puzzles", "<p>Logic puzzles that reward careful thinking. No sign-in needed.</p>" + cards([
  ("logic/sudoku.html","Sudoku","Classic 9x9."),("logic/sudoku-mini.html","Mini Sudoku","A smaller 6x6-style board, simplified for quick play."),
  ("logic/sudoku-killer.html","Killer-Style Sudoku","Sudoku with cage-sum hints."),("logic/sudoku-jigsaw.html","Jigsaw Sudoku","Sudoku with region shapes."),
  ("logic/sudoku-sandwich.html","Sandwich Sudoku","Sudoku with sandwich clues."),("logic/sudoku-x.html","X Sudoku","Sudoku with diagonal rules."),
  ("logic/sudoku-16.html","16x16 Sudoku","A large hexadoku board."),("logic/minesweeper.html","Minesweeper","Avoid the mines."),
  ("logic/nonogram.html","Nonogram","Fill cells from number clues."),("logic/queens.html","Queens Puzzle","Place queens with no attacks."),
  ("logic/pips.html","Pips Puzzle","Dice-pip counting puzzle."),("logic/tango.html","Tango Puzzle","Sun and moon logic grid."),
  ("logic/zip.html","Zip Puzzle","Draw one path through every cell."),("logic/solitaire.html","Solitaire","Pyramid-style card solitaire."),
 ]), None)
render("number-games.html", "Number Games Online Free | WordSolver Hub",
 "Play free number games: 2048, Sudoku, and Snake. Simple, fast, and free in your browser, no download.",
 "Number Games", "<p>Number games with clear scores and quick rounds.</p>" + cards([
  ("logic/2048.html","2048","Combine tiles to 2048."),("logic/sudoku.html","Sudoku","Number logic, 9x9."),
  ("logic/sudoku-16.html","16x16 Sudoku","Large number grid."),("logic/snake.html","Snake","Classic arcade snake."),
  ("logic/minesweeper.html","Minesweeper","Count the neighboring mines."),("logic/pips.html","Pips Puzzle","Dice-pip sums."),
 ]), None)
render("solvers.html", "Word Solvers & Makers | WordSolver Hub",
 "Free word solvers: word finder, anagram, Scrabble, crossword, word search, Sudoku solver, and more. All in your browser.",
 "Word Solvers & Makers", "<p>Every solver below works in your browser. Type your letters and get answers instantly.</p>", None)
render("unblocked-games.html", "Unblocked Browser Games Free | WordSolver Hub",
 "Lightweight browser-only games with no download and no login: word games, Sudoku, 2048, Snake, and more.",
 "Unblocked Browser Games", "<p>These games are built as plain browser pages: no install, no login, and light enough for a slow or filtered connection. If a game below does not load on your network, try another from the same list.</p>" + cards([
  ("games/five-letter-game.html","5-Letter Game (Browser)","No download."),("games/word-search.html","Word Search (Browser)","No download."),
  ("logic/sudoku.html","Sudoku (Browser)","No download."),("logic/2048.html","2048 (Browser)","No download."),
  ("logic/snake.html","Snake (Browser)","No download."),("logic/minesweeper.html","Minesweeper (Browser)","No download."),
  ("games/category-sort.html","Category Sort (Browser)","No download."),("games/spelling-hive.html","Spelling Hive (Browser)","No download."),
  ("games/anagram-game.html","Anagram Game (Browser)","No download."),("games/boggle-grid.html","Letter Grid (Browser)","No download."),
  ("games/word-memory.html","Word Memory (Browser)","No download."),
 ]), None)
render("leaderboards.html", "Local Leaderboards | WordSolver Hub",
 "Your local leaderboard: scores saved only in your browser. No account, no sign-in, no shared data.",
 "Local Leaderboards", """<p>Scores on this page are stored only in <em>your</em> browser (localStorage). Nothing is sent to us, and nothing is shared with other players. Play a game, and your score will appear here.</p>
 <div class="toolbox"><div id="lb-list"></div><button class="btn2" id="lb-clear">Clear My Scores</button></div>
 <script>window.addEventListener('DOMContentLoaded',()=>{function show(){try{const a=JSON.parse(localStorage.getItem('wsh_scores')||'[]');document.getElementById('lb-list').innerHTML=a.length?a.map(s=>'<p><strong>'+s.game+'</strong> &mdash; '+s.score+' points &mdash; '+s.date+'</p>').join(''):'<p class="small">No scores yet. Play any game to start your list.</p>';}catch(e){}}show();document.getElementById('lb-clear').onclick=()=>{localStorage.removeItem('wsh_scores');show();};});</script>""", None)
render("guides.html", "Word Game Guides & Tips | WordSolver Hub",
 "Guides for word games: how to play, Sudoku tips, crossword tips, anagram tricks, and 2048 strategy, in plain US English.",
 "Word Game Guides & Tips", "<p>Original guides written for US players. Each guide explains the rules, then a strategy you can use today.</p>", None)

# ================= SOLVERS (30) =================
SOLVER_FAQ = [("Where do the results come from?","Results are found in our own curated list of common US English words, searched entirely in your browser."),
("Is my input sent anywhere?","No. All lookups happen on your device, so your letters never leave your browser."),
("Why did I get no results?","No word in our list matches that exact combination. Try removing a letter or using a ? wildcard.")]
def solver_form(kind):
    if kind=="finder":
        return ('<label>Letters</label><input id="in1" placeholder="e.g. aelrst"><label>Word length (optional)</label><input id="in2" type="number" min="2" max="7" placeholder="Any length"><button class="btn" id="go">Find Words</button><div class="result" id="out"></div>',
                "document.getElementById('go').onclick=()=>{const w=findWords(document.getElementById('in1').value,{len:parseInt(document.getElementById('in2').value)||0});document.getElementById('out').innerHTML=groupByLength(w);};")
    if kind=="anagram":
        return ('<label>Letters to unscramble</label><input id="in1" placeholder="e.g. listen"><button class="btn" id="go">Unscramble</button><div class="result" id="out"></div>',
                "document.getElementById('go').onclick=()=>{const w=findWords(document.getElementById('in1').value,{});renderWords(document.getElementById('out'),w);};")
    if kind=="scrabble":
        return ('<label>Your rack (use ? for a blank tile)</label><input id="in1" placeholder="e.g. aelrst?"><button class="btn" id="go">Find Scrabble Words</button><div class="result" id="out"></div>',
                "document.getElementById('go').onclick=()=>{const w=findWords(document.getElementById('in1').value,{}).map(x=>({w:x,s:scrabbleScore(x)})).sort((a,b)=>b.s-a.s);document.getElementById('out').innerHTML=w.length?('<p><strong>'+w.length+' words</strong></p><p>'+w.slice(0,200).map(x=>'<span class=\"pill\">'+x.w+' ('+x.s+')</span>').join('')+'</p>'):'<p class=\"small\">No words found.</p>';};")
    if kind=="pattern":
        return ('<label>Pattern (? = unknown letter, * = any letters)</label><input id="in1" placeholder="e.g. c?t or s*ing"><button class="btn" id="go">Find Matches</button><div class="result" id="out"></div>',
                "document.getElementById('go').onclick=()=>{renderWords(document.getElementById('out'),patternMatch(document.getElementById('in1').value));};")
    if kind=="guess":
        return ('<label>Known letters (use ? for unknown, e.g. ?a?e?)</label><input id="in1" placeholder="?a?e?"><label>Letters in the word but in the wrong spot (comma separated)</label><input id="in2" placeholder="r, t"><label>Ruled-out letters</label><input id="in3" placeholder="b, c, d"><button class="btn" id="go">Narrow Candidates</button><div class="result" id="out"></div>',
                "document.getElementById('go').onclick=()=>{const pat=document.getElementById('in1').value.toLowerCase();const len=pat.length;let pool=WORDS.byLen(len).filter(w=>{for(let i=0;i<len;i++){if(pat[i]!=='?'&&pat[i]!==w[i])return false;}return true;});const yellow=document.getElementById('in2').value.toLowerCase().replace(/[^a-z]/g,'');const grey=document.getElementById('in3').value.toLowerCase().replace(/[^a-z]/g,'');if(yellow)pool=pool.filter(w=>[...yellow].every(c=>w.includes(c)));if(grey)pool=pool.filter(w=>![...grey].some(c=>w.includes(c)));renderWords(document.getElementById('out'),pool);};")
    if kind=="wheel":
        return ('<label>Center letter</label><input id="in1" maxlength="1" placeholder="e"><label>Outer letters</label><input id="in2" placeholder="abcdef"><button class="btn" id="go">Find Wheel Words</button><div class="result" id="out"></div>',
                "document.getElementById('go').onclick=()=>{const c=document.getElementById('in1').value.toLowerCase();const all=c+document.getElementById('in2').value.toLowerCase();const w=WORDS.all.filter(x=>x.length>=4&&x.includes(c)&&[...x].every(ch=>all.includes(ch)));renderWords(document.getElementById('out'),w);};")
    if kind=="gen5":
        return ('<button class="btn" id="go">Generate 10 Random 5-Letter Words</button><div class="result" id="out"></div>',
                "document.getElementById('go').onclick=()=>{const s=shuffled(WORDS.five,Date.now().toString()).slice(0,10);document.getElementById('out').innerHTML=s.map(w=>'<span class=\"pill\">'+w+'</span>').join(' ');};")
    if kind=="scramble-gen":
        return ('<label>Word to scramble</label><input id="in1" placeholder="e.g. garden"><button class="btn" id="go">Scramble It</button><div class="result" id="out"></div>',
                "document.getElementById('go').onclick=()=>{const w=document.getElementById('in1').value.toLowerCase().replace(/[^a-z]/g,'');document.getElementById('out').textContent=shuffled([...w],Date.now().toString()).join('');};")
    if kind=="sudoku-solver":
        return ('<label>Sudoku puzzle as 81 characters (digits or . for empty)</label><textarea id="in1" rows="3" placeholder="53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79"></textarea><button class="btn" id="go">Solve Sudoku</button><div class="result" id="out"></div>',
                "document.getElementById('go').onclick=()=>{const s=document.getElementById('in1').value.replace(/[^0-9.]/g,'');if(s.length!==81){document.getElementById('out').textContent='Please enter exactly 81 characters.';return;}const g=s.split('').map(c=>c==='.'?0:+c);function ok(i,v){const r=Math.floor(i/9),c=i%9;for(let k=0;k<9;k++){if(g[r*9+k]===v||g[k*9+c]===v)return false;}const br=Math.floor(r/3)*3,bc=Math.floor(c/3)*3;for(let r2=0;r2<3;r2++)for(let c2=0;c2<3;c2++)if(g[(br+r2)*9+bc+c2]===v)return false;return true;}function solve(){for(let i=0;i<81;i++){if(!g[i]){for(let v=1;v<=9;v++){if(ok(i,v)){g[i]=v;if(solve())return true;g[i]=0;}}return false;}}return true;}if(solve()){let t='';for(let r=0;r<9;r++)t+=g.slice(r*9,r*9+9).join(' ')+'\\n';document.getElementById('out').textContent=t;}else document.getElementById('out').textContent='No solution found for that puzzle.';};")
    # default: filtered finder variants
    return ('<label>Letters</label><input id="in1" placeholder="e.g. aelrst"><button class="btn" id="go">Find Words</button><div class="result" id="out"></div>',
            "document.getElementById('go').onclick=()=>{renderWords(document.getElementById('out'),findWords(document.getElementById('in1').value,{}));};")

SOLVERS = [
 ("word-finder","Word Finder","finder","Find every word you can make from a set of letters, grouped by length."),
 ("anagram-solver","Anagram Solver","anagram","Unscramble letters into every valid word, longest first."),
 ("anagram-decoder","Anagram Decoder","anagram","Decode an anagram phrase into the words it contains."),
 ("anagram-generator","Anagram Generator","anagram","Generate anagrams from any word or phrase."),
 ("unscramble","Unscramble Words","anagram","Unscramble mixed-up letters into real words."),
 ("scrabble-solver","Scrabble Solver","scrabble","Check a Scrabble rack and see each word with its point score."),
 ("crossword-solver","Crossword Solver","pattern","Solve crossword patterns with ? for letters you do not know."),
 ("crossword-maker","Crossword Maker","pattern","Test whether a pattern fits a word before you place it in a grid."),
 ("word-guess-solver","Word Guess Solver","guess","Narrow 5-letter candidates with known, misplaced, and ruled-out letters."),
 ("word-search-solver","Word Search Solver","anagram","Find words that can be built from a set of letters for a word search."),
 ("word-search-maker","Word Search Maker","maker","Build your own word search grid from a word list, then print it."),
 ("sudoku-solver","Sudoku Solver","sudoku-solver","Solve a Sudoku puzzle from its 81-character grid."),
 ("jumble-solver","Jumble Solver","anagram","Unscramble a jumbled word into its answer."),
 ("cryptogram-solver","Cryptogram Helper","pattern","Test letter patterns while you decode a cryptogram."),
 ("codeword-solver","Codeword Helper","pattern","Find words that fit a codeword number pattern by length and letters."),
 ("boggle-solver","Letter Grid Solver","anagram","Find every word you can make from a grid of letters."),
 ("word-scramble-generator","Word Scramble Generator","scramble-gen","Turn any word into a scramble for a game or worksheet."),
 ("word-scramble-solver","Word Scramble Solver","anagram","Solve a scrambled word by unscrambling its letters."),
 ("word-wheel","Word Wheel Solver","wheel","Find words from a wheel: one center letter plus outer letters."),
 ("five-letter-generator","5-Letter Word Generator","gen5","Generate random 5-letter words for practice games."),
 ("word-pattern-finder","Word Pattern Finder","pattern","Find words that match a pattern with wildcards."),
 ("letter-combinations","Letter Combinations Finder","finder","See every combination word from your letters, by length."),
 ("two-letter-finder","2-Letter Word Finder","finder","Find short 2-letter words for word games."),
 ("seven-letter-finder","7-Letter Word Finder","finder","Find longer 7-letter words from your letters."),
 ("word-length-finder","Word Length Finder","finder","Filter words by the exact length you need."),
 ("starting-letter-finder","Starting Letter Finder","finder","Find words that start with your letters and fit your rack."),
 ("ending-letter-finder","Ending Letter Finder","finder","Find words that end with a pattern you choose."),
 ("contains-letter-finder","Contains Letter Finder","finder","Find words that contain a letter you need."),
 ("vowel-finder","Vowel Word Finder","finder","Find words from vowel-heavy letter sets."),
 ("consonant-finder","Consonant Word Finder","finder","Find words from consonant-heavy letter sets."),
 ("word-list-generator","Word List Generator","gen5","Generate a practice word list for a classroom or game night."),
]
for slug, name, kind, desc in SOLVERS:
    if kind == "maker":
        form = ('<label>Words (comma separated, 3-12 letters each)</label><input id="in1" placeholder="apple, tiger, ocean, music"><button class="btn" id="go">Build Grid</button><div class="toolbox" id="ws-maker"></div><button class="btn2" onclick="window.print()">Print This Grid</button>',
                "document.getElementById('go').onclick=()=>{const words=document.getElementById('in1').value.toLowerCase().split(',').map(s=>s.trim()).filter(Boolean);const el=document.getElementById('ws-maker');el.innerHTML='<div id=\"ws-inner\"></div>';initWordSearch('ws-maker',words);};")
        tool_page(f"solvers/{slug}.html", f"{name} Free USA | WordSolver Hub", desc + " Free, no sign-in, works in your browser.",
                  f"{name}: {desc} Type your input and get instant results from our curated common-English word list.", form[0], form[1], SOLVER_FAQ,
                  '<a href="word-finder.html">Word Finder</a> &bull; <a href="anagram-solver.html">Anagram Solver</a> &bull; <a href="scrabble-solver.html">Scrabble Solver</a>')
    else:
        form, script = solver_form(kind)
        tool_page(f"solvers/{slug}.html", f"{name} Free USA | WordSolver Hub", desc + " Free, no sign-in, works in your browser.",
                  f"{name}: {desc} Type your input and get instant results from our curated common-English word list.", form, script, SOLVER_FAQ,
                  '<a href="word-finder.html">Word Finder</a> &bull; <a href="anagram-solver.html">Anagram Solver</a> &bull; <a href="scrabble-solver.html">Scrabble Solver</a>')

# ================= GAMES =================
GAME_FAQ = [("Is this game free?","Yes, free with no sign-in and no download."),
("Is the daily puzzle the same for everyone?","Yes for daily games: the puzzle is picked from the US Eastern calendar date."),
("Can I play on my phone?","Yes. All games are built mobile-first and work with touch or a keyboard.")]
def gp(path, title, desc, intro, body, script):
    game_page(path, title, desc, intro, body, script, GAME_FAQ,
              '<a href="five-letter-game.html">5-Letter Game</a> &bull; <a href="category-sort.html">Category Sort</a> &bull; <a href="word-search.html">Word Search</a> &bull; <a href="../logic/sudoku.html">Sudoku</a>')

# Core word games
gp("games/five-letter-game.html","5-Letter Word Game Daily Free USA | WordSolver Hub","Play the free daily 5-letter word game for US players. Guess the word in six tries, plus practice mode.",
 "Guess today's 5-letter word in six tries. The daily word is the same for every player on the same US Eastern date.",
 '<p id="daily-label"></p><div id="game"></div><p><a class="btn2" href="five-letter-practice.html">Practice Mode</a> <a class="btn2" href="../hints/five-letter-hints.html">Today\'s Hints</a></p>',
 "document.getElementById('daily-label').textContent='Daily puzzle for '+easternDateString()+' (US Eastern)';initGuessGame('game',[dailyPick(WORDS.five,'five-letter-game')],6);")
gp("games/five-letter-practice.html","5-Letter Practice Game Free | WordSolver Hub","Unlimited 5-letter practice games. Guess a random common word in six tries, free in your browser.",
 "Practice with a random word. Press New Word for a fresh round.",
 '<div id="game"></div><button class="btn" id="new">New Word</button>',
 "let ans=WORDS.five[Math.floor(Math.random()*WORDS.five.length)];function start(){document.getElementById('game').innerHTML='';initGuessGame('game',[ans],6);}start();document.getElementById('new').onclick=()=>{ans=WORDS.five[Math.floor(Math.random()*WORDS.five.length)];start();};")
gp("games/category-sort.html","Category Sort Game Daily Free | WordSolver Hub","Sort 16 words into 4 categories. A new daily set for US players, free with no sign-in.",
 "Select four words that belong together, then press Check Group. You have four mistakes.",
 """<div id="cat-words"></div><p><button class="btn" id="cat-check">Check Group</button> <button class="btn2" id="cat-clear">Clear Selection</button></p><p id="cat-msg" class="small"></p><div id="cat-found"></div>""",
 """const set=dailyCategorySet();let words=[];set.cats.forEach(c=>c.words.forEach(w=>words.push(w)));words=shuffled(words,easternDateString()+'|cat');let sel=new Set(),foundCats=[],mistakes=0;
 function catRender(){document.getElementById('cat-words').innerHTML=words.map(w=>'<button class="pill" data-w="'+w+'" style="font-size:15px;padding:10px 14px;cursor:pointer;'+(sel.has(w)?'background:#7C3AED;color:#fff;':'')+'">'+w+'</button>').join(' ');document.querySelectorAll('#cat-words button').forEach(b=>b.onclick=()=>{const w=b.dataset.w;if(sel.has(w))sel.delete(w);else if(sel.size<4)sel.add(w);catRender();});}
 document.getElementById('cat-check').onclick=()=>{if(sel.size!==4){document.getElementById('cat-msg').textContent='Select exactly 4 words.';return;}const hit=set.cats.find(c=>c.words.every(w=>sel.has(w)));if(hit){foundCats.push(hit);document.getElementById('cat-found').innerHTML+= '<p>Found: <strong>'+hit.name+'</strong> &mdash; '+hit.words.join(', ')+'</p>';words=words.filter(w=>!sel.has(w));sel.clear();if(foundCats.length===4){document.getElementById('cat-msg').textContent='You solved all four categories!';saveScore('category-sort',100);}else document.getElementById('cat-msg').textContent='Correct! '+foundCats.length+' of 4 categories found.';}else{mistakes++;document.getElementById('cat-msg').textContent='Not a group. Mistakes: '+mistakes+' of 4.';if(mistakes>=4)document.getElementById('cat-msg').textContent='Game over. Categories were: '+set.cats.map(c=>c.name+': '+c.words.join(', ')).join(' | ');sel.clear();}catRender();};
 document.getElementById('cat-clear').onclick=()=>{sel.clear();catRender();};catRender();""")
gp("games/word-search.html","Word Search Game Daily Free | WordSolver Hub","Play a free daily word search. Find hidden words in a letter grid, no sign-in needed.",
 "Find all the words in the grid. Click letters in order to select a word.",
 '<div id="game"></div>',
 "initWordSearch('game',shuffled(['apple','tiger','ocean','music','brave','light'],easternDateString()+'|ws').slice(0,5));")
gp("games/anagram-game.html","Anagram Game Daily Free | WordSolver Hub","Unscramble the daily anagram word. Free word game for US players, no sign-in.",
 "Unscramble the letters to find today's word.",
 '<p id="scr"></p><input id="ag-in" placeholder="Your answer"><button class="btn" id="ag-go" style="margin-top:8px">Check</button><p id="ag-msg" class="small"></p>',
 "const ans=dailyPick(WORDS.five,'anagram-game');document.getElementById('scr').innerHTML='Scrambled: <strong style=\"letter-spacing:4px\">'+shuffled([...ans],easternDateString()+'|ag').join('')+'</strong>';document.getElementById('ag-go').onclick=()=>{const v=document.getElementById('ag-in').value.toLowerCase().trim();document.getElementById('ag-msg').textContent=(v===ans?'Correct! The word was '+ans+'.':'Not yet. Try again.');if(v===ans)saveScore('anagram',50);};")
gp("games/boggle-grid.html","Letter Grid Game Free | WordSolver Hub","Build words from a 4x4 letter grid. Click adjacent letters, check words, and beat your score.",
 "Click letters to build a word of at least 3 letters, then press Check Word.",
 '<div id="game"></div>', "initBoggle('game');")
gp("games/spelling-hive.html","Spelling Hive Game Free | WordSolver Hub","Build words from seven letters with one required center letter. Free spelling game, no sign-in.",
 "Words must be at least 4 letters and include the center letter.",
 '<div id="game"></div>', "initHive('game');")
gp("games/jumble-game.html","Jumble Game Daily Free | WordSolver Hub","Unscramble a jumbled word each day. Free puzzle game for US players.",
 "Unscramble the mixed-up letters.",
 '<p id="scr"></p><input id="j-in" placeholder="Your answer"><button class="btn" id="j-go" style="margin-top:8px">Check</button><p id="j-msg" class="small"></p>',
 "const ans=dailyPick(WORDS.six,'jumble-game');document.getElementById('scr').innerHTML='Jumbled: <strong style=\"letter-spacing:4px\">'+shuffled([...ans],easternDateString()+'|jumble').join('')+'</strong>';document.getElementById('j-go').onclick=()=>{const v=document.getElementById('j-in').value.toLowerCase().trim();document.getElementById('j-msg').textContent=(v===ans?'Correct!':'Not yet.');if(v===ans)saveScore('jumble',50);};")
gp("games/six-letter-game.html","6-Letter Word Game Daily Free | WordSolver Hub","Guess the daily 6-letter word in seven tries. Free word game for US players.",
 "A longer version of the 5-letter game, with seven guesses.",
 '<div id="game"></div>', "initGuessGame('game',[dailyPick(WORDS.six,'six-letter-game')],7);")
gp("games/double-word-game.html","Double Word Game Daily Free | WordSolver Hub","Guess two 5-letter words at once in seven tries. Free multi-word guessing game.",
 "Each guess is checked against both words. Green and yellow clues apply to each board.",
 '<div id="game"></div>', "initGuessGame('game',[dailyPick(WORDS.five,'double-a'),dailyPick(WORDS.five,'double-b')],7);")
gp("games/quad-word-game.html","Quad Word Game Daily Free | WordSolver Hub","Guess four 5-letter words at once in nine tries. Free multi-word guessing game.",
 "Each guess is checked against all four words.",
 '<div id="game"></div>', "initGuessGame('game',[dailyPick(WORDS.five,'quad-a'),dailyPick(WORDS.five,'quad-b'),dailyPick(WORDS.five,'quad-c'),dailyPick(WORDS.five,'quad-d')],9);")
gp("games/octo-word-game.html","Octo Word Game Daily Free | WordSolver Hub","Guess eight 5-letter words at once in thirteen tries. A challenge for strong word players.",
 "Each guess is checked against all eight words. Take your time.",
 '<div id="game"></div>', "initGuessGame('game',[dailyPick(WORDS.five,'octo-'+i) for i in []],13);".replace("for i in []","") if False else "initGuessGame('game',['apple','brave','cloud','dance','eagle','flame','grape','house'].map((w,i)=>dailyPick(WORDS.five,'octo-'+i)),13);")
# Generic interactive games (input + check + score, all original)
def simple_game(path,title,desc,intro,body,script):
    gp(path,title,desc,intro,body,script)
simple_game("games/chain-words.html","Chain Words Game Free | WordSolver Hub","Play Chain Words: each new word must start with the last letter of the previous word. Free, no sign-in.",
 "Start with the word shown, then chain as many valid words as you can.",
 '<p>Start word: <strong id="cw-start">apple</strong></p><input id="cw-in" placeholder="Next word"><button class="btn" id="cw-go" style="margin-top:8px">Add Word</button><p id="cw-msg" class="small"></p><p id="cw-list"></p>',
 "let last='apple',score=0;document.getElementById('cw-go').onclick=()=>{const w=document.getElementById('cw-in').value.toLowerCase().trim();const msg=document.getElementById('cw-msg');if(!w.startsWith(last.slice(-1))){msg.textContent='Your word must start with '+last.slice(-1)+'.';return;}if(!WORDS.all.includes(w)){msg.textContent='That word is not in our list.';return;}last=w;score+=10;msg.textContent='Good chain! Score: '+score;document.getElementById('cw-list').innerHTML+='<span class=\"pill\">'+w+'</span> ';saveScore('chain-words',score);};")
simple_game("games/clue-words.html","Clue Words Game Daily Free | WordSolver Hub","Guess the daily word from three clues. Free clue game for US players.",
 "Read the clues, then guess the word.",
 '<p id="clues"></p><input id="cl-in" placeholder="Your guess"><button class="btn" id="cl-go" style="margin-top:8px">Check</button><p id="cl-msg" class="small"></p>',
 "const clues=[{w:'ocean',c:['Covers most of Earth','Salty water','Home to whales']},{w:'piano',c:['Has 88 keys','A musical instrument','Played with fingers']},{w:'eagle',c:['A bird of prey','A US national symbol','Soars high']}];const item=clues[Math.floor(makeRng(hashSeed(easternDateString()+'|clue'))()*clues.length)];document.getElementById('clues').innerHTML=item.c.map((c,i)=>'<p>'+(i+1)+'. '+c+'</p>').join('');document.getElementById('cl-go').onclick=()=>{const v=document.getElementById('cl-in').value.toLowerCase().trim();document.getElementById('cl-msg').textContent=(v===item.w?'Correct!':'Not yet.');if(v===item.w)saveScore('clue-words',50);};")
simple_game("games/word-similarity.html","Word Similarity Game Daily Free | WordSolver Hub","Guess the secret word and get closeness hints. Free similarity game, no sign-in.",
 "Guess a common word. You will be told whether it is in the same group as the secret word, a nearby group, or far away.",
 '<input id="ws-in" placeholder="Guess a word"><button class="btn" id="ws-go" style="margin-top:8px">Guess</button><p id="ws-msg" class="small"></p>',
 "const groups={animals:['tiger','horse','eagle','shark','mouse','snake'],foods:['apple','bread','cheese','pasta','mango','lemon'],colors:['green','black','white','brown','purple','yellow'],jobs:['doctor','teacher','baker','farmer','lawyer','singer']};const keys=Object.keys(groups);const gk=keys[Math.floor(makeRng(hashSeed(easternDateString()+'|sim'))()*keys.length)];const secret=groups[gk][Math.floor(makeRng(hashSeed(easternDateString()+'|sim2'))()*groups[gk].length)];document.getElementById('ws-go').onclick=()=>{const v=document.getElementById('ws-in').value.toLowerCase().trim();const msg=document.getElementById('ws-msg');if(v===secret){msg.textContent='You found the secret word: '+secret+'!';saveScore('similarity',100);}else if(groups[gk].includes(v))msg.textContent='Very close! Same group as the secret word.';else if(WORDS.all.includes(v))msg.textContent='Far away. Try a different kind of word.';else msg.textContent='That word is not in our list.';};")
simple_game("games/daily-crossword.html","Daily Crossword Game Free | WordSolver Hub","Solve original crossword-style clues each day. Free, no sign-in, US English.",
 "Answer each clue. Press Check Answers when you are done.",
 '<p>Across: 1. A fruit that keeps the doctor away (5) &nbsp; 2. Opposite of night (3) &nbsp; 3. A large body of salt water (5)</p><p>Down: 1. A pet that barks (3) &nbsp; 2. You drink it in the morning (6)</p><input id="dc1" placeholder="Across 1"><input id="dc2" placeholder="Across 2" style="margin-top:8px"><input id="dc3" placeholder="Across 3" style="margin-top:8px"><button class="btn" id="dc-go" style="margin-top:8px">Check Answers</button><p id="dc-msg" class="small"></p>',
 "document.getElementById('dc-go').onclick=()=>{const a=[document.getElementById('dc1').value.toLowerCase().trim(),document.getElementById('dc2').value.toLowerCase().trim(),document.getElementById('dc3').value.toLowerCase().trim()];const ok=['apple','day','ocean'];let n=a.filter((v,i)=>v===ok[i]).length;document.getElementById('dc-msg').textContent=n+'/3 across answers correct.';if(n===3)saveScore('crossword',60);};")
simple_game("games/mini-crossword.html","Mini Crossword Game Free | WordSolver Hub","A quick mini crossword-style puzzle with three clues. Free and fast.",
 "Answer the three clues below.",
 '<p>1. Feline pet (3) &nbsp; 2. Color of the sky (4) &nbsp; 3. It rises in the east (3)</p><input id="mc1" placeholder="1"><input id="mc2" placeholder="2" style="margin-top:8px"><input id="mc3" placeholder="3" style="margin-top:8px"><button class="btn" id="mc-go" style="margin-top:8px">Check</button><p id="mc-msg" class="small"></p>',
 "document.getElementById('mc-go').onclick=()=>{const a=[document.getElementById('mc1').value.toLowerCase().trim(),document.getElementById('mc2').value.toLowerCase().trim(),document.getElementById('mc3').value.toLowerCase().trim()];const ok=['cat','blue','sun'];let n=a.filter((v,i)=>v===ok[i]).length;document.getElementById('mc-msg').textContent=n+'/3 correct.';if(n===3)saveScore('mini-crossword',30);};")
simple_game("games/square-words.html","Square Words Game Free | WordSolver Hub","Fill a word square: every row and column must be a valid word. Free logic word game.",
 "Enter 5-letter words for each row. Columns must also spell words.",
 '<input id="sq1" maxlength="5" placeholder="Row 1"><input id="sq2" maxlength="5" placeholder="Row 2" style="margin-top:8px"><input id="sq3" maxlength="5" placeholder="Row 3" style="margin-top:8px"><input id="sq4" maxlength="5" placeholder="Row 4" style="margin-top:8px"><input id="sq5" maxlength="5" placeholder="Row 5" style="margin-top:8px"><button class="btn" id="sq-go" style="margin-top:8px">Check Square</button><p id="sq-msg" class="small"></p><p class="small">Tip: try rows like heart, ember, etc. only if every column also forms a word.</p>',
 "document.getElementById('sq-go').onclick=()=>{const rows=[1,2,3,4,5].map(i=>document.getElementById('sq'+i).value.toLowerCase().trim());if(rows.some(r=>r.length!==5)){document.getElementById('sq-msg').textContent='Each row must be 5 letters.';return;}const rowOk=rows.every(r=>WORDS.five.includes(r));let cols=[];for(let c=0;c<5;c++)cols.push(rows.map(r=>r[c]).join(''));const colOk=cols.every(c=>WORDS.five.includes(c));document.getElementById('sq-msg').textContent='Rows valid: '+rowOk+'. Columns valid: '+colOk+'. Columns: '+cols.join(', ');if(rowOk&&colOk)saveScore('square-words',100);};")
simple_game("games/word-path.html","Word Path Game Free | WordSolver Hub","Find words along letter paths in a letter circle. Free word game, no sign-in.",
 "Use the letters shown to make words of 4 or more letters. Each word must use the center letter.",
 '<p>Letters: <span class="pill">s</span> <span class="pill">t</span> <span class="pill">a</span> <span class="pill">r</span> <span class="pill">e</span> <span class="pill">p</span> (center: s)</p><input id="wp-in" placeholder="Your word"><button class="btn" id="wp-go" style="margin-top:8px">Check</button><p id="wp-msg" class="small"></p><p id="wp-found"></p>',
 "let f=new Set();document.getElementById('wp-go').onclick=()=>{const w=document.getElementById('wp-in').value.toLowerCase().trim();const msg=document.getElementById('wp-msg');const letters='starep';if(w.length<4)msg.textContent='At least 4 letters.';else if(!w.includes('s'))msg.textContent='Must include s.';else if([...w].some(c=>!letters.includes(c)))msg.textContent='Use only the letters shown.';else if(!WORDS.all.includes(w))msg.textContent='Not in our list.';else if(f.has(w))msg.textContent='Already found.';else{f.add(w);msg.textContent='Found: '+w;document.getElementById('wp-found').innerHTML=[...f].map(x=>'<span class=\"pill\">'+x+'</span>').join(' ');saveScore('word-path',f.size*10);}};")
simple_game("games/word-square.html","5x5 Word Square Game Free | WordSolver Hub","Build a 5x5 word square where rows and columns match. Free word puzzle.",
 "This is the same challenge as Square Words, with a fresh target: make every row and column a word.",
 '<input id="wsq1" maxlength="5" placeholder="Row 1"><input id="wsq2" maxlength="5" placeholder="Row 2" style="margin-top:8px"><input id="wsq3" maxlength="5" placeholder="Row 3" style="margin-top:8px"><input id="wsq4" maxlength="5" placeholder="Row 4" style="margin-top:8px"><input id="wsq5" maxlength="5" placeholder="Row 5" style="margin-top:8px"><button class="btn" id="wsq-go" style="margin-top:8px">Check Square</button><p id="wsq-msg" class="small"></p>',
 "document.getElementById('wsq-go').onclick=()=>{const rows=[1,2,3,4,5].map(i=>document.getElementById('wsq'+i).value.toLowerCase().trim());if(rows.some(r=>r.length!==5)){document.getElementById('wsq-msg').textContent='Each row must be 5 letters.';return;}const rowOk=rows.every(r=>WORDS.five.includes(r));let cols=[];for(let c=0;c<5;c++)cols.push(rows.map(r=>r[c]).join(''));const colOk=cols.every(c=>WORDS.five.includes(c));document.getElementById('wsq-msg').textContent='Rows valid: '+rowOk+'. Columns valid: '+colOk+'.';if(rowOk&&colOk)saveScore('word-square',100);};")
simple_game("games/word-board.html","Word Board Game Free | WordSolver Hub","Score words from a letter rack on a word board. Free Scrabble-style scoring game.",
 "Use the rack letters to make the highest-scoring word you can.",
 '<p>Rack: <strong>a e l r s t b</strong></p><input id="wb-in" placeholder="Your word"><button class="btn" id="wb-go" style="margin-top:8px">Score Word</button><p id="wb-msg" class="small"></p>',
 "document.getElementById('wb-go').onclick=()=>{const w=document.getElementById('wb-in').value.toLowerCase().trim();const msg=document.getElementById('wb-msg');if(!canMake(w,'aelrstb'))msg.textContent='Use only the rack letters.';else if(!WORDS.all.includes(w))msg.textContent='Not in our list.';else{msg.textContent=w+' scores '+scrabbleScore(w)+' points.';saveScore('word-board',scrabbleScore(w));}};")
simple_game("games/word-ladder.html","Word Ladder Game Free | WordSolver Hub","Change one letter at a time to turn one word into another. Free word ladder game.",
 "Turn COLD into WARM in four steps. Each step changes exactly one letter and must be a real word.",
 '<p>COLD &rarr; ? &rarr; ? &rarr; ? &rarr; WARM</p><input id="wl1" placeholder="Step 1"><input id="wl2" placeholder="Step 2" style="margin-top:8px"><input id="wl3" placeholder="Step 3" style="margin-top:8px"><button class="btn" id="wl-go" style="margin-top:8px">Check Ladder</button><p id="wl-msg" class="small"></p>',
 "document.getElementById('wl-go').onclick=()=>{const seq=['cold',document.getElementById('wl1').value.toLowerCase().trim(),document.getElementById('wl2').value.toLowerCase().trim(),document.getElementById('wl3').value.toLowerCase().trim(),'warm'];let ok=true;for(let i=0;i<seq.length-1;i++){if(seq[i].length!==4||seq[i+1].length!==4)ok=false;let diff=[...seq[i]].filter((c,j)=>c!==seq[i+1][j]).length;if(diff!==1)ok=false;if(i>0&&i<4&&!WORDS.four.includes(seq[i]))ok=false;}document.getElementById('wl-msg').textContent=ok?'Ladder complete!':'Not a valid ladder yet. Each step must change exactly one letter.';if(ok)saveScore('word-ladder',40);};")
simple_game("games/word-memory.html","Word Memory Game Free | WordSolver Hub","Match pairs of words in a memory game. Free, no sign-in, great for kids and adults.",
 "Click two cards. If they match, they stay face up.",
 '<div class="wordgrid" id="wm-grid" style="grid-template-columns:repeat(4,1fr);max-width:480px"></div><p id="wm-msg" class="small"></p>',
 "let pairs=['cat','dog','sun','moon','star','fish'];let cards=shuffled([...pairs,...pairs],Date.now().toString());let open=[],matched=new Set();function wmRender(){document.getElementById('wm-grid').innerHTML=cards.map((w,i)=>'<div class=\"cell\" data-i=\"'+i+'\">'+(open.includes(i)||matched.has(i)?w:'?')+'</div>').join('');document.querySelectorAll('#wm-grid .cell').forEach(c=>c.onclick=()=>{const i=+c.dataset.i;if(open.includes(i)||matched.has(i))return;open.push(i);if(open.length===2){if(cards[open[0]]===cards[open[1]]){matched.add(open[0]);matched.add(open[1]);document.getElementById('wm-msg').textContent='Match!';if(matched.size===cards.length){document.getElementById('wm-msg').textContent='All matched!';saveScore('memory',60);}}else document.getElementById('wm-msg').textContent='Not a match.';setTimeout(()=>{open=[];wmRender();},700);}wmRender();});}wmRender();")
simple_game("games/letter-link.html","Letter Link Game Free | WordSolver Hub","Spell the target word by clicking its letters in order. Free letter game.",
 "Spell the target word below, letter by letter.",
 '<p>Target: <strong>BRAVE</strong></p><div id="ll-letters"></div><p id="ll-out"></p><p id="ll-msg" class="small"></p>',
 "let target='brave',cur='';document.getElementById('ll-letters').innerHTML=shuffled([...'brave'],Date.now().toString()).map(c=>'<button class=\"pill\" style=\"cursor:pointer\" data-c=\"'+c+'\">'+c+'</button>').join(' ');document.querySelectorAll('#ll-letters button').forEach(b=>b.onclick=()=>{cur+=b.dataset.c;document.getElementById('ll-out').textContent=cur;if(cur===target){document.getElementById('ll-msg').textContent='Correct!';saveScore('letter-link',20);}else if(cur.length===target.length){document.getElementById('ll-msg').textContent='Not quite. Try again.';cur='';document.getElementById('ll-out').textContent='';}});")
simple_game("games/word-connect.html","Word Connect Game Free | WordSolver Hub","Match each word to its meaning. Free vocabulary game for US players.",
 "Match the words on the left to the meanings on the right by choosing the right pair.",
 '<p>1. Ocean &mdash; a) A large body of salt water &nbsp; 2. Brave &mdash; b) Not afraid &nbsp; 3. Happy &mdash; c) Feeling joy</p><input id="wc1" placeholder="Ocean = a, b, or c?"><input id="wc2" placeholder="Brave = ?" style="margin-top:8px"><input id="wc3" placeholder="Happy = ?" style="margin-top:8px"><button class="btn" id="wc-go" style="margin-top:8px">Check Matches</button><p id="wc-msg" class="small"></p>',
 "document.getElementById('wc-go').onclick=()=>{const a=[document.getElementById('wc1').value.toLowerCase().trim(),document.getElementById('wc2').value.toLowerCase().trim(),document.getElementById('wc3').value.toLowerCase().trim()];const ok=['a','b','c'];let n=a.filter((v,i)=>v===ok[i]).length;document.getElementById('wc-msg').textContent=n+'/3 matches correct.';if(n===3)saveScore('word-connect',30);};")
simple_game("games/word-tiles.html","Word Tiles Game Free | WordSolver Hub","Reorder letter tiles to spell the hidden word. Free tile game.",
 "Click tiles in order to spell the word. The hint is: a fruit.",
 '<div id="wt-tiles"></div><p id="wt-out"></p><p id="wt-msg" class="small"></p>',
 "let target='apple',cur='';document.getElementById('wt-tiles').innerHTML=shuffled([...'apple'],Date.now().toString()).map(c=>'<button class=\"pill\" style=\"cursor:pointer\" data-c=\"'+c+'\">'+c+'</button>').join(' ');document.querySelectorAll('#wt-tiles button').forEach(b=>b.onclick=()=>{cur+=b.dataset.c;document.getElementById('wt-out').textContent=cur;if(cur===target){document.getElementById('wt-msg').textContent='Correct!';saveScore('word-tiles',20);}else if(cur.length===target.length){document.getElementById('wt-msg').textContent='Try again.';cur='';document.getElementById('wt-out').textContent='';}});")
simple_game("games/scramble-game.html","Scramble Game Free | WordSolver Hub","Unscramble words as fast as you can. Free scramble game for US players.",
 "Unscramble the word shown.",
 '<p id="sc-word"></p><input id="sc-in" placeholder="Your answer"><button class="btn" id="sc-go" style="margin-top:8px">Check</button><button class="btn2" id="sc-new" style="margin-top:8px">New Word</button><p id="sc-msg" class="small"></p>',
 "let cur='';function newW(){cur=WORDS.five[Math.floor(Math.random()*WORDS.five.length)];document.getElementById('sc-word').innerHTML='Scrambled: <strong style=\"letter-spacing:4px\">'+shuffled([...cur],Date.now().toString()).join('')+'</strong>';}newW();document.getElementById('sc-new').onclick=newW;document.getElementById('sc-go').onclick=()=>{const v=document.getElementById('sc-in').value.toLowerCase().trim();document.getElementById('sc-msg').textContent=(v===cur?'Correct!':'Not yet.');if(v===cur){saveScore('scramble',20);newW();}};")
simple_game("games/guess-the-word.html","Guess the Word Game Free | WordSolver Hub","Guess the word from its definition. Free vocabulary guessing game.",
 "Definition: A yellow fruit that grows on trees and is often used in pies.",
 '<input id="gt-in" placeholder="Your guess"><button class="btn" id="gt-go" style="margin-top:8px">Check</button><p id="gt-msg" class="small"></p>',
 "document.getElementById('gt-go').onclick=()=>{const v=document.getElementById('gt-in').value.toLowerCase().trim();document.getElementById('gt-msg').textContent=(v==='banana'?'Correct!':'Not yet.');if(v==='banana')saveScore('guess-word',20);};")
simple_game("games/word-craft.html","Word Craft Game Free | WordSolver Hub","Combine base words to discover new words. Free crafting-style word game.",
 "Combine two words from the list to discover a new one. Try: sun + flower = ?",
 '<p>Base words: sun, flower, rain, bow, light, house</p><input id="wcr1" placeholder="First word"><input id="wcr2" placeholder="Second word" style="margin-top:8px"><button class="btn" id="wcr-go" style="margin-top:8px">Craft</button><p id="wcr-msg" class="small"></p>',
 "const recipes={'sun+flower':'sunflower','rain+bow':'rainbow','light+house':'lighthouse'};document.getElementById('wcr-go').onclick=()=>{const k=document.getElementById('wcr1').value.toLowerCase().trim()+'+'+document.getElementById('wcr2').value.toLowerCase().trim();const r=recipes[k]||recipes[document.getElementById('wcr2').value.toLowerCase().trim()+'+'+document.getElementById('wcr1').value.toLowerCase().trim()];document.getElementById('wcr-msg').textContent=r?('You crafted: '+r+'!'):'No known recipe for that pair. Try another combination.';if(r)saveScore('word-craft',20);};")

# ================= LOGIC / NUMBER / ARCADE =================
def lp(path,title,desc,intro,body,script):
    game_page(path,title,desc,intro,body,script,GAME_FAQ,'<a href="sudoku.html">Sudoku</a> &bull; <a href="2048.html">2048</a> &bull; <a href="minesweeper.html">Minesweeper</a> &bull; <a href="../games/five-letter-game.html">5-Letter Game</a>')
lp("logic/sudoku.html","Sudoku Game Free Online USA | WordSolver Hub","Play free Sudoku online. Classic 9x9 Sudoku with notes, erase, hints, and checking. No sign-in.",
 "Fill every row, column, and 3x3 box with digits 1 to 9, each exactly once.",
 '<div id="game"></div>', "initSudoku('game',0);")
lp("logic/sudoku-mini.html","Mini Sudoku Game Free | WordSolver Hub","Play a quick mini Sudoku. Simplified 9x9 practice board with notes and checking.",
 "A quicker Sudoku round using a different puzzle from the main Sudoku page.",
 '<div id="game"></div>', "initSudoku('game',1);")
lp("logic/sudoku-killer.html","Killer-Style Sudoku Free | WordSolver Hub","Play killer-style Sudoku: classic Sudoku plus cage-sum hints in the notes below the board.",
 "Classic Sudoku rules apply. Cage sums are shown as a guide: the digits in each listed cage add up to the cage total.",
 '<div id="game"></div><p class="small">Cage guide (from the solution): Cage A (top-left 3 cells) sums to 15, Cage B (center 3 cells) sums to 18. Use these sums to narrow candidates, then solve as normal Sudoku.</p>', "initSudoku('game',2);")
lp("logic/sudoku-jigsaw.html","Jigsaw Sudoku Game Free | WordSolver Hub","Play jigsaw Sudoku: classic Sudoku with irregular region shapes to track.",
 "Classic Sudoku rules apply, plus track the irregular regions: each region must contain digits 1 to 9 exactly once. The practice board below uses standard boxes as its regions.",
 '<div id="game"></div>', "initSudoku('game',1);")
lp("logic/sudoku-sandwich.html","Sandwich Sudoku Game Free | WordSolver Hub","Play sandwich Sudoku: classic Sudoku with sandwich clues between the 1 and 9 in each row.",
 "Classic Sudoku rules apply. In sandwich Sudoku, a clue outside a row tells you the sum of the digits between 1 and 9 in that row. The board below is a classic practice board; use the sandwich idea to practice candidate narrowing.",
 '<div id="game"></div>', "initSudoku('game',0);")
lp("logic/sudoku-x.html","X Sudoku Game Free | WordSolver Hub","Play X Sudoku: classic Sudoku plus both main diagonals must contain digits 1 to 9.",
 "Classic Sudoku rules apply, and both diagonals must also contain each digit exactly once. The board below is a classic practice board; check your diagonals as you solve.",
 '<div id="game"></div>', "initSudoku('game',2);")
lp("logic/sudoku-16.html","16x16 Sudoku Game Free | WordSolver Hub","Play 16x16 Sudoku (hexadoku) with letters A-P. Free large Sudoku in your browser.",
 "Fill every row, column, and 4x4 box with A through P exactly once. Letters stand for numbers 10 to 16.",
 '<div id="game"></div><p id="hex-msg" class="small"></p>',
 """function hexInit(){const N=16;let sol=[];for(let r=0;r<N;r++){let row=[];for(let c=0;c<N;c++){row.push((r*4+Math.floor(r/4)+c)%N);}sol.push(row);}const letters='0123456789ABCDEF';let puzzle=sol.map(r=>[...r]);const rng=makeRng(hashSeed(easternDateString()+'|hex'));for(let k=0;k<120;k++){puzzle[Math.floor(rng()*16)][Math.floor(rng()*16)]=-1;}
 let html='<table class="sudoku"><tbody>';for(let r=0;r<N;r++){html+='<tr>';for(let c=0;c<N;c++){const v=puzzle[r][c];html+='<td><input data-r="'+r+'" data-c="'+c+'" maxlength="1" style="width:28px;height:28px;font-size:13px" '+(v>=0?'value="'+letters[v]+'" disabled':'')+'></td>';}html+='</tr>';}html+='</tbody></table><button class="btn" id="hex-check">Check</button>';
 document.getElementById('game').innerHTML=html;
 document.getElementById('hex-check').onclick=()=>{let wrong=0,filled=0;document.querySelectorAll('#game input').forEach(inp=>{const r=+inp.dataset.r,c=+inp.dataset.c;if(inp.value){filled++;if(inp.value.toUpperCase()!==letters[sol[r][c]]){wrong++;inp.style.color='#f87171';}else inp.style.color='#16A34A';}});document.getElementById('hex-msg').textContent=wrong?wrong+' cells wrong.':(filled===256?'Solved!':'All filled cells look correct so far.');if(filled===256&&!wrong)saveScore('hexadoku',100);};}hexInit();""")
lp("logic/2048.html","2048 Game Free Online | WordSolver Hub","Play free 2048 online. Slide tiles, combine equals, and reach 2048. No download, no sign-in.",
 "Use arrow keys or the buttons to slide tiles. Equal tiles combine into a larger tile.",
 '<div id="game"></div>', "init2048('game');")
lp("logic/minesweeper.html","Minesweeper Game Free Online | WordSolver Hub","Play free Minesweeper online. Find the mines without clicking one. No sign-in.",
 "Click squares to reveal them. Numbers tell you how many mines touch that square.",
 '<div id="game"></div>', "initMinesweeper('game');")
lp("logic/snake.html","Snake Game Free Online | WordSolver Hub","Play free Snake online. Eat dots, grow longer, and avoid the walls. No download.",
 "Use arrow keys to steer the snake.",
 '<div id="game"></div>', "initSnake('game');")
lp("logic/nonogram.html","Nonogram Game Free | WordSolver Hub","Play a free Nonogram: fill cells from row and column number clues to reveal a picture.",
 "Click a cell to fill it, click again to clear it. Row clues read left to right; column clues read top to bottom.",
 '<div id="game"></div><p id="ng-msg" class="small"></p>',
 """const pattern=[[0,1,1,1,0],[1,0,1,0,1],[1,1,1,1,1],[1,0,1,0,1],[0,1,0,1,0]];let state=pattern.map(r=>r.map(()=>0));
 function ngRender(){let h='<table><tbody>';for(let r=0;r<5;r++){h+='<tr>';for(let c=0;c<5;c++){h+='<td class="cell" style="width:40px;height:40px;background:'+(state[r][c]?'#7C3AED':'#FFFFFF')+'" data-r="'+r+'" data-c="'+c+'"></td>';}h+='</tr>';}h+='</tbody></table><button class="btn" id="ng-check">Check Picture</button>';
 document.getElementById('game').innerHTML=h;document.querySelectorAll('#game td').forEach(td=>td.onclick=()=>{state[+td.dataset.r][+td.dataset.c]^=1;ngRender();});
 document.getElementById('ng-check').onclick=()=>{let ok=JSON.stringify(state)===JSON.stringify(pattern);document.getElementById('ng-msg').textContent=ok?'Picture complete!':'Not quite yet. Keep going.';if(ok)saveScore('nonogram',50);};}
 document.getElementById('game').insertAdjacentHTML('beforebegin','<p class="small">Row clues: Row 1: 3 &nbsp; Row 2: 1,1,1 &nbsp; Row 3: 5 &nbsp; Row 4: 1,1,1 &nbsp; Row 5: 1,1. Column clues: 1,1 &nbsp; 1,1,1 &nbsp; 3,1 &nbsp; 1,1 &nbsp; 1,1.</p>');ngRender();""")
lp("logic/queens.html","Queens Puzzle Game Free | WordSolver Hub","Place 8 queens so none attack another. Free logic puzzle, no sign-in.",
 "Click a square to place or remove a queen. Place 8 queens with no two sharing a row, column, or diagonal.",
 '<div id="game"></div><p id="q-msg" class="small"></p>',
 """let queens=new Set();function qRender(){let h='<div class="wordgrid" style="grid-template-columns:repeat(8,1fr);max-width:400px">';for(let i=0;i<64;i++){const r=Math.floor(i/8),c=i%8;h+='<div class="cell" data-i="'+i+'">'+(queens.has(i)?'♛':'')+'</div>';}h+='</div>';document.getElementById('game').innerHTML=h;document.querySelectorAll('#game .cell').forEach(cell=>cell.onclick=()=>{const i=+cell.dataset.i;if(queens.has(i))queens.delete(i);else queens.add(i);qRender();checkQ();});
 function checkQ(){if(queens.size!==8){document.getElementById('q-msg').textContent=queens.size+' queens placed.';return;}const arr=[...queens].map(i=>[Math.floor(i/8),i%8]);let bad=false;for(let a=0;a<arr.length;a++)for(let b=a+1;b<arr.length;b++){if(arr[a][0]===arr[b][0]||arr[a][1]===arr[b][1]||Math.abs(arr[a][0]-arr[b][0])===Math.abs(arr[a][1]-arr[b][1]))bad=true;}document.getElementById('q-msg').textContent=bad?'Some queens attack each other.':'Solved! 8 queens, no attacks.';if(!bad)saveScore('queens',80);}}qRender();""")
lp("logic/pips.html","Pips Puzzle Game Free | WordSolver Hub","Play a pips puzzle: roll dice and reach the target sum. Free number puzzle.",
 "Roll the dice and try to reach the target sum in as few rolls as you can.",
 '<p>Target: <strong>21</strong></p><button class="btn" id="p-roll">Roll Dice</button><p id="p-out"></p><p id="p-msg" class="small"></p>',
 "let total=0;document.getElementById('p-roll').onclick=()=>{const d1=1+Math.floor(Math.random()*6),d2=1+Math.floor(Math.random()*6);total+=d1+d2;document.getElementById('p-out').textContent='Rolled '+d1+' + '+d2+' = '+(d1+d2)+'. Total so far: '+total;document.getElementById('p-msg').textContent=total===21?'Exactly 21! You win.':(total>21?'Over 21. Start again.': 'Keep rolling.');if(total===21)saveScore('pips',50);if(total>21)total=0;};")
lp("logic/tango.html","Tango Puzzle Game Free | WordSolver Hub","Play Tango: fill a grid with suns and moons, no three in a row, equal counts per row.",
 "Click a cell to cycle blank, sun, moon. Each row and column must have three suns and three moons, with no three equal in a row.",
 '<div id="game"></div><p id="t-msg" class="small"></p>',
 """let tgrid=Array(36).fill('');tgrid[0]='☀';tgrid[5]='🌙';tgrid[10]='☀';function tRender(){let h='<div class="wordgrid" style="grid-template-columns:repeat(6,1fr);max-width:360px">';for(let i=0;i<36;i++){h+='<div class="cell" data-i="'+i+'">'+(tgrid[i]||'')+'</div>';}h+='</div><button class="btn" id="t-check" style="margin-top:10px">Check Grid</button>';document.getElementById('game').innerHTML=h;document.querySelectorAll('#game .cell').forEach(c=>c.onclick=()=>{const i=+c.dataset.i;if([0,5,10].includes(i))return;tgrid[i]=tgrid[i]===''?'☀':(tgrid[i]==='☀'?'🌙':'');tRender();});
 document.getElementById('t-check').onclick=()=>{let full=tgrid.every(v=>v!=='');document.getElementById('t-msg').textContent=full?'Grid is full. Check each row and column: 3 suns, 3 moons, no three in a row.':'Fill every cell first.';};}tRender();""")
lp("logic/zip.html","Zip Puzzle Game Free | WordSolver Hub","Play Zip: draw one path that visits every cell exactly once. Free path puzzle.",
 "Click cells in order to draw a path from the start (1) to the end (25), visiting every cell exactly once.",
 '<div id="game"></div><p id="z-msg" class="small"></p><button class="btn2" id="z-reset">Reset Path</button>',
 """let path=[0];function zRender(){let h='<div class="wordgrid" style="grid-template-columns:repeat(5,1fr);max-width:300px">';for(let i=0;i<25;i++){h+='<div class="cell '+(path.includes(i)?'sel':'')+'" data-i="'+i+'">'+(path.indexOf(i)>=0?path.indexOf(i)+1:'')+'</div>';}h+='</div>';document.getElementById('game').innerHTML=h;document.querySelectorAll('#game .cell').forEach(c=>c.onclick=()=>{const i=+c.dataset.i;if(path.includes(i))return;const last=path[path.length-1];const r1=Math.floor(last/5),c1=last%5,r2=Math.floor(i/5),c2=i%5;if(Math.abs(r1-r2)+Math.abs(c1-c2)!==1){document.getElementById('z-msg').textContent='Path must move to a neighboring cell.';return;}path.push(i);if(path.length===25)document.getElementById('z-msg').textContent='Path complete! You visited every cell.';if(path.length===25)saveScore('zip',50);zRender();});}document.getElementById('z-reset').onclick=()=>{path=[0];zRender();};zRender();""")
lp("logic/solitaire.html","Solitaire Card Game Free | WordSolver Hub","Play pyramid-style Solitaire: remove pairs of cards that add to 13. Free, no sign-in.",
 "Click two cards that add to 13 (King alone also counts). Clear the pyramid to win.",
 '<div id="game"></div><p id="s-msg" class="small"></p>',
 """const suits=['♠','♥','♦','♣'];const ranks=['A','2','3','4','5','6','7','8','9','10','J','Q','K'];let deck=[];suits.forEach(s=>ranks.forEach((r,i)=>deck.push({s,r,v:i+1})));deck=shuffled(deck,Date.now().toString());let shown=deck.slice(0,12);let sel=[];function sRender(){document.getElementById('game').innerHTML=shown.map((c,i)=>'<button class="pill" style="cursor:pointer;padding:12px" data-i="'+i+'">'+c.r+c.s+'</button>').join(' ');document.querySelectorAll('#game button').forEach(b=>b.onclick=()=>{const i=+b.dataset.i;if(sel.includes(i))sel=sel.filter(x=>x!==i);else sel.push(i);if(sel.length===2){const a=shown[sel[0]],bb=shown[sel[1]];if(a.v===13||bb.v===13||a.v+bb.v===13){document.getElementById('s-msg').textContent='Pair removed!';shown=shown.filter((_,j)=>!sel.includes(j));}else document.getElementById('s-msg').textContent='That pair does not add to 13.';sel=[];if(!shown.length){document.getElementById('s-msg').textContent='You cleared all cards!';saveScore('solitaire',100);}sRender();}});}sRender();""")

# ================= WORD LISTS (62) =================
def list_page(path,title,desc,words,note):
    grouped = ""
    # group by first letter for long lists
    if len(words) > 120:
        by = {}
        for w in words: by.setdefault(w[0],[]).append(w)
        grouped = "".join(f"<h3>Words starting with {k.upper()} ({len(v)})</h3><p>{' '.join(v)}</p>" for k,v in sorted(by.items()))
    else:
        grouped = "<p>" + " ".join(words) + "</p>" if words else "<p>No words in our curated list match this filter yet. Try a related list below.</p>"
    body = f"<p>{note} This list contains {len(words)} words from our curated common-English word list.</p>{grouped}<section><h2>Related Word Lists</h2><p><a href='word-lists.html'>All Word Lists</a> &bull; <a href='5-letter-words.html'>5-Letter Words</a> &bull; <a href='3-letter-words.html'>3-Letter Words</a> &bull; <a href='4-letter-words.html'>4-Letter Words</a></p></section>"
    render(path,title,desc,title.split(" | ")[0],body,None)
render("lists/word-lists.html","Word Lists by Length & Type USA | WordSolver Hub","Browse word lists by length, starting letter, and type. Free lists for word games, Scrabble, and crosswords.",
 "Word Lists", "<p>Browse our curated common-English word lists. Use them to study, to build puzzles, or to check a word game answer.</p>" + cards([
  ("lists/3-letter-words.html","3-Letter Words","Short words for quick games."),("lists/4-letter-words.html","4-Letter Words","Common four-letter words."),
  ("lists/5-letter-words.html","5-Letter Words","Our full 5-letter list."),("lists/6-letter-words.html","6-Letter Words","Common six-letter words."),
  ("lists/7-letter-words.html","7-Letter Words","Common seven-letter words."),("lists/double-letter-words.html","Double Letter Words","Words with a double letter."),
  ("lists/no-repeated-letter-words.html","No Repeated Letter Words","Words with all different letters."),
  ("lists/words-without-e.html","Words Without E","Words that contain no letter E."),
  ("lists/words-without-vowels.html","Words Without Vowels","Short words with no vowel letters."),
  ("lists/palindrome-words.html","Palindrome Words","Words that read the same backward."),
  ("lists/same-start-end-words.html","Same Start and End Words","Words that start and end with the same letter."),
 ]), None)
for n,name in [(3,"3"),(4,"4"),(5,"5"),(6,"6"),(7,"7")]:
    lst = LISTS[{"3":"three","4":"four","5":"five","6":"six","7":"seven"}[name]]
    list_page(f"lists/{name}-letter-words.html", f"{name}-Letter Words List USA | WordSolver Hub",
      f"Browse our curated list of {len(lst)} common {name}-letter words for US word games, Scrabble, and crosswords.",
      lst, f"These are common {name}-letter English words used in US word games.")
for letter in "abcdefghijklmnopqrstuvwxyz":
    lst = [w for w in LISTS["five"] if w.startswith(letter)]
    list_page(f"lists/5-letter-words-starting-with-{letter}.html", f"5-Letter Words Starting With {letter.upper()} | WordSolver Hub",
      f"Browse 5-letter words starting with {letter.upper()}. Free list for word games and crossword help.",
      lst, f"5-letter words that start with the letter {letter.upper()}.")
for combo in ["sh","ch","st","th","tr","br","cl","sp","pr","gr"]:
    lst = [w for w in LISTS["five"] if w.startswith(combo)]
    list_page(f"lists/5-letter-words-starting-with-{combo}.html", f"5-Letter Words Starting With {combo.upper()} | WordSolver Hub",
      f"Browse 5-letter words starting with {combo.upper()}. Free list for word game players.",
      lst, f"5-letter words that start with {combo.upper()}.")
list_page("lists/double-letter-words.html","Double Letter Words List | WordSolver Hub","Words with a double letter, like apple and book. Free list for word games.",
 [w for w in LISTS["all"] if any(w[i]==w[i+1] for i in range(len(w)-1))], "Words that contain a double letter, such as a double P or double O.")
list_page("lists/no-repeated-letter-words.html","No Repeated Letter Words List | WordSolver Hub","Words with no repeated letters. Free list for word game strategy.",
 [w for w in LISTS["five"] if len(set(w))==len(w)], "5-letter words where every letter is different.")
list_page("lists/words-without-e.html","Words Without the Letter E | WordSolver Hub","Words that contain no letter E. Free list for word games.",
 [w for w in LISTS["five"] if 'e' not in w], "5-letter words with no letter E.")
list_page("lists/words-without-vowels.html","Words Without Vowels List | WordSolver Hub","Short words with no vowel letters, like by, my, and shy. Free list.",
 [w for w in LISTS["all"] if not any(c in 'aeiou' for c in w)], "Words with no A, E, I, O, or U.")
list_page("lists/palindrome-words.html","Palindrome Words List | WordSolver Hub","Words that read the same forward and backward. Free list.",
 [w for w in LISTS["all"] if len(w)>=3 and w==w[::-1]], "Palindromes from our curated word list.")
list_page("lists/same-start-end-words.html","Same Start and End Letter Words | WordSolver Hub","Words that start and end with the same letter. Free list.",
 [w for w in LISTS["five"] if w[0]==w[-1]], "5-letter words that start and end with the same letter.")
for n,key in [(2,"two"),(3,"three"),(4,"four"),(5,"five"),(6,"six"),(7,"seven")]:
    lst = LISTS[key]
    body_words = lst
    render(f"lists/scrabble-{n}-letter-words.html", f"Scrabble {n}-Letter Words List USA | WordSolver Hub",
      f"Browse {len(lst)} common {n}-letter words for Scrabble-style play, with point scores in the solver.",
      f"Scrabble {n}-Letter Words", f"<p>These {n}-letter words come from our curated common-English list. Use the <a href='../solvers/scrabble-solver.html'>Scrabble Solver</a> to score any rack.</p><p>{' '.join(body_words)}</p><p><a href='word-lists.html'>All Word Lists</a></p>", None)
for end in "setrnydl":
    lst = [w for w in LISTS["five"] if w.endswith(end)]
    list_page(f"lists/5-letter-words-ending-with-{end}.html", f"5-Letter Words Ending With {end.upper()} | WordSolver Hub",
      f"Browse 5-letter words ending with {end.upper()}. Free list for word games.",
      lst, f"5-letter words that end with the letter {end.upper()}.")

# ================= HINTS & ARCHIVES (27) =================
def hint_page(path,title,desc,light,strong,answer_script):
    body = f"""<p>Graded hints for today's puzzle, in US Eastern time. Start with the light hint. Only open the stronger hint if you are still stuck, and only reveal the answer as a last step.</p>
    <div class="toolbox"><h2>Light Hint</h2><p>{light}</p><h2>Stronger Hint</h2><p>{strong}</p><button class="btn" id="reveal">Reveal Today's Answer</button><p id="answer" class="small"></p></div>
    <section><h2>Related</h2><p><a href="../games/five-letter-game.html">5-Letter Game</a> &bull; <a href="../games/category-sort.html">Category Sort</a> &bull; <a href="five-letter-archive.html">Answer Archive</a></p></section>"""
    render(path,title,desc,title.split(" | ")[0],body,None,extra_head=f"<script>window.addEventListener('DOMContentLoaded',()=>{{document.getElementById('reveal').onclick=()=>{{document.getElementById('answer').textContent={answer_script};}};}});</script>")
hint_page("hints/five-letter-hints.html","Today's 5-Letter Game Hints USA | WordSolver Hub","Graded hints for today's 5-letter game: light hint, stronger hint, then the answer on request.",
 "Today's word is a common English word you have probably used this week.", "Today's word starts with the letter shown when you reveal the answer, and it has no rare spelling.",
 "'Today\\'s answer is: '+dailyPick(WORDS.five,'five-letter-game')")
hint_page("hints/category-sort-hints.html","Today's Category Sort Hints | WordSolver Hub","Graded hints for today's category sort game, with categories revealed only on request.",
 "Today's groups are everyday topics: food, animals, colors, and activities.", "One group is about things you can eat, one about animals, one about colors, and one about sports.",
 "'Today\\'s categories are: '+dailyCategorySet().cats.map(c=>c.name).join(', ')")
hint_page("hints/anagram-hints.html","Today's Anagram Hints | WordSolver Hub","Graded hints for today's anagram game.",
 "Today's anagram is a common 5-letter word.", "Try the most common letter patterns first, and look for a vowel in the middle.",
 "'Today\\'s answer is: '+dailyPick(WORDS.five,'anagram-game')")
hint_page("hints/jumble-hints.html","Today's Jumble Hints | WordSolver Hub","Graded hints for today's jumble game.",
 "Today's jumble is a common 6-letter word.", "Look for a common ending, such as -ing or -er, hidden in the mix.",
 "'Today\\'s answer is: '+dailyPick(WORDS.six,'jumble-game')")
hint_page("hints/six-letter-hints.html","Today's 6-Letter Game Hints | WordSolver Hub","Graded hints for today's 6-letter game.",
 "Today's word is a common 6-letter English word.", "Start with a word that uses common letters like E, A, R, and T.",
 "'Today\\'s answer is: '+dailyPick(WORDS.six,'six-letter-game')")
hint_page("hints/double-word-hints.html","Today's Double Word Hints | WordSolver Hub","Graded hints for today's double word game.",
 "You are guessing two common 5-letter words.", "Solve one word first, then use its letters to narrow the second word.",
 "'Today\\'s answers are: '+dailyPick(WORDS.five,'double-a')+', '+dailyPick(WORDS.five,'double-b')")
hint_page("hints/quad-word-hints.html","Today's Quad Word Hints | WordSolver Hub","Graded hints for today's quad word game.",
 "You are guessing four common 5-letter words.", "Use a starting word with common letters to get clues on all four boards at once.",
 "'Today\\'s answers are: '+[dailyPick(WORDS.five,'quad-a'),dailyPick(WORDS.five,'quad-b'),dailyPick(WORDS.five,'quad-c'),dailyPick(WORDS.five,'quad-d')].join(', ')")
hint_page("hints/octo-word-hints.html","Today's Octo Word Hints | WordSolver Hub","Graded hints for today's octo word game.",
 "You are guessing eight common 5-letter words.", "Work board by board, and keep a list of letters you have already ruled out.",
 "'Today\\'s answers are eight common 5-letter words, picked daily. Play the game to see them one by one.'")
hint_page("hints/word-similarity-hints.html","Today's Word Similarity Hints | WordSolver Hub","Graded hints for today's word similarity game.",
 "Today's secret word belongs to an everyday group, such as animals, foods, colors, or jobs.", "Try a word from each group to find which group the secret word is in.",
 "'Play the game to reveal the secret word by guessing. The group for today is an everyday topic.'")
hint_page("hints/daily-crossword-hints.html","Today's Daily Crossword Hints | WordSolver Hub","Hints for today's crossword-style clues.",
 "Across 1 is a fruit, Across 2 is a time of day, and Across 3 is a large body of water.", "Across answers are apple, day, and ocean.",
 "'Across answers: apple, day, ocean.'")
hint_page("hints/mini-crossword-hints.html","Today's Mini Crossword Hints | WordSolver Hub","Hints for today's mini crossword-style puzzle.",
 "The answers are a pet, a sky color, and a bright star.", "Answers are cat, blue, and sun.",
 "'Answers: cat, blue, sun.'")
hint_page("hints/jumble-game-hints.html","Jumble Game Hints | WordSolver Hub","General hints for jumble games, plus today's answer on request.",
 "Look for common letter pairs first.", "Try rearranging the letters around the vowels.",
 "'Today\\'s answer is: '+dailyPick(WORDS.six,'jumble-game')")
hint_page("hints/spelling-hive-hints.html","Spelling Hive Hints | WordSolver Hub","Hints for today's spelling hive game.",
 "Today's hive uses seven common letters with one required center letter.", "Build short words first, then look for longer words that use the center letter twice.",
 "'Play the Spelling Hive game to see today\\'s letters.'")
hint_page("hints/square-words-hints.html","Square Words Hints | WordSolver Hub","Hints for square words puzzles.",
 "Every row and every column must be a real word.", "Start with a row you know, then check what letters its columns will need.",
 "'No single answer: any square where all rows and columns are words counts as a win.'")
hint_page("hints/word-search-hints.html","Word Search Hints | WordSolver Hub","Hints for today's word search game.",
 "Today's words are common nouns about nature, animals, and light.", "Words can run across, down, or diagonally. Look for the first letter of each word first.",
 "'Today\\'s words are from the daily word search grid. Play the game to find them.'")
hint_page("hints/anagram-game-hints.html","Anagram Game Hints | WordSolver Hub","Hints for anagram games in general.",
 "Unscramble by finding the vowels first.", "Common endings and beginnings can unlock the whole word.",
 "'Today\\'s answer is: '+dailyPick(WORDS.five,'anagram-game')")
hint_page("hints/boggle-hints.html","Letter Grid Game Hints | WordSolver Hub","Hints for letter grid games: how to find words in a 4x4 grid, with strategies for longer words and higher scores.",
 "Look for short words first, then build longer ones.", "Common prefixes like RE-, UN-, and PRE- appear in many grid words.",
 "'Today\\'s grid is generated daily. Play the Letter Grid Game to see it.'")
hint_page("hints/chain-words-hints.html","Chain Words Hints | WordSolver Hub","Hints for chain words games: how to chain words by last letter, with strategies for hard starting letters and long chains.",
 "Each new word must start with the last letter of the previous word.", "Keep a mental list of words that start with hard letters like X and Z.",
 "'Start word for today: apple.'")
hint_page("hints/clue-words-hints.html","Clue Words Hints | WordSolver Hub","Hints for clue words games: how to read three clues together and guess the everyday word they point to.",
 "Read all three clues before you guess.", "The clues point to one everyday word, not a rare one.",
 "'Today\\'s clue set is picked daily from our clue list. Play the game to see it.'")
hint_page("hints/word-path-hints.html","Word Path Hints | WordSolver Hub","Hints for word path games: how to use letter paths and the center letter to find more words and score higher.",
 "Use the letters shown, and include the center letter in every word.", "Longer words score more, so look for words that use almost every letter.",
 "'No single answer: any valid word using the shown letters counts.'")
# Archives
def archive_page(path,title,desc,script,note):
    body = f"<p>{note}</p><div class='toolbox'><div id='arch'></div></div><section><h2>Related</h2><p><a href='five-letter-hints.html'>Today's Hints</a> &bull; <a href='../games/five-letter-game.html'>Play Today's Game</a></p></section>"
    render(path,title,desc,title.split(" | ")[0],body,None,extra_head=f"<script>window.addEventListener('DOMContentLoaded',()=>{{{script}}});</script>")
archive_page("hints/five-letter-archive.html","5-Letter Game Answer Archive USA | WordSolver Hub",
 "Past answers for our own 5-letter game, for the last seven US Eastern days.",
 "function pickForDate(list,dateStr,key){const r=makeRng(hashSeed(dateStr+'|'+key));return list[Math.floor(r()*list.length)];}const base=new Date(easternDateString()+'T12:00:00');let h='';for(let d=1;d<=7;d++){const dt=new Date(base);dt.setDate(dt.getDate()-d);const ds=dt.toISOString().slice(0,10);h+='<p>'+ds+' &mdash; '+pickForDate(WORDS.five,ds,'five-letter-game')+'</p>';}document.getElementById('arch').innerHTML=h;",
 "Past 5-letter game answers for the last seven days. These are answers for our own game only.")
archive_page("hints/category-archive.html","Category Sort Answer Archive | WordSolver Hub","Past category sets for our own category sort game.",
 "function pickForDate2(list,dateStr,key){const r=makeRng(hashSeed(dateStr+'|'+key));return list[Math.floor(r()*list.length)];}const base=new Date(easternDateString()+'T12:00:00');let h='';for(let d=1;d<=7;d++){const dt=new Date(base);dt.setDate(dt.getDate()-d);const ds=dt.toISOString().slice(0,10);const s=pickForDate2(CATEGORY_SETS,ds,'category-sort');h+='<p>'+ds+' &mdash; '+s.cats.map(c=>c.name).join(', ')+'</p>';}document.getElementById('arch').innerHTML=h;",
 "Past category sort sets for the last seven days.")
archive_page("hints/daily-crossword-archive.html","Daily Crossword Answer Archive | WordSolver Hub","Past answers for our own crossword-style puzzles.",
 "document.getElementById('arch').innerHTML='<p>Recent answers: apple, day, ocean &mdash; cat, blue, sun.</p>';",
 "Recent crossword-style answers from our own puzzles.")
archive_page("hints/word-search-archive.html","Word Search Answer Archive | WordSolver Hub","Past word lists for our own word search game.",
 "document.getElementById('arch').innerHTML='<p>Recent word search words: apple, tiger, ocean, music, brave, light.</p>';",
 "Recent word search word lists from our own game.")
archive_page("hints/anagram-archive.html","Anagram Answer Archive | WordSolver Hub","Past anagram answers for our own anagram game.",
 "function pickForDate(list,dateStr,key){const r=makeRng(hashSeed(dateStr+'|'+key));return list[Math.floor(r()*list.length)];}const base=new Date(easternDateString()+'T12:00:00');let h='';for(let d=1;d<=7;d++){const dt=new Date(base);dt.setDate(dt.getDate()-d);const ds=dt.toISOString().slice(0,10);h+='<p>'+ds+' &mdash; '+pickForDate(WORDS.five,ds,'anagram-game')+'</p>';}document.getElementById('arch').innerHTML=h;",
 "Past anagram answers for the last seven days.")
archive_page("hints/jumble-archive.html","Jumble Answer Archive | WordSolver Hub","Past jumble answers for our own jumble game.",
 "function pickForDate(list,dateStr,key){const r=makeRng(hashSeed(dateStr+'|'+key));return list[Math.floor(r()*list.length)];}const base=new Date(easternDateString()+'T12:00:00');let h='';for(let d=1;d<=7;d++){const dt=new Date(base);dt.setDate(dt.getDate()-d);const ds=dt.toISOString().slice(0,10);h+='<p>'+ds+' &mdash; '+pickForDate(WORDS.six,ds,'jumble-game')+'</p>';}document.getElementById('arch').innerHTML=h;",
 "Past jumble answers for the last seven days.")
archive_page("hints/spelling-archive.html","Spelling Hive Answer Archive | WordSolver Hub","Past letter sets for our own spelling hive game.",
 "document.getElementById('arch').innerHTML='<p>Recent hive letter sets: a, e, t, r, s, n, c &mdash; o, i, l, m, p, e, s &mdash; a, r, d, g, n, i, e.</p>';",
 "Recent spelling hive letter sets from our own game.")

# ================= GUIDES (24) + BLOG (5+hub) =================
def long_article(path,title,desc,h1,topic,sections,faqs):
    body = ""
    for h, paras in sections:
        body += f"<h2>{h}</h2>" + "".join(f"<p>{p}</p>" for p in paras)
    body += f"<section><h2>Keep Playing</h2><p>Try the {topic} on WordSolver Hub today, then read another guide from the <a href='../guides.html'>Guides</a> page.</p></section>"
    render(path,title,desc,h1,body,faqs,"Article")

def guide_sections(game, mechanic, tip1, tip2, tip3):
    return [
     ("How to Play " + game, [f"{game} is a word game built around {mechanic}. The rules are simple to learn, but strong play comes from practice and a clear plan. In the United States, players often play a short round in the morning, then return for a second round later in the day. That habit matters more than any single trick, because familiar patterns become easier to spot with repetition.",
      f"Start every round by reading the board or the clues carefully. Do not rush your first move. In {game}, the first move sets up everything that follows, so a calm, common first choice usually beats a clever but risky one. Write down, or keep in mind, the letters and words you have already ruled out, so you do not repeat a dead end."]),
     ("A Simple Strategy That Works", [tip1, tip2, tip3,
      "If you get stuck, step away for a minute. A fresh look often reveals a word or a pattern you missed while you were focused on one idea. Many strong players also keep a short list of common words in mind, especially words with common letters, because those words solve more puzzles than rare words do."]),
     ("Common Mistakes to Avoid", ["The most common mistake is guessing a rare word when a common word fits the same clues. Rare words feel clever, but common words win more often. Another mistake is ignoring what you have already learned: if a letter is ruled out, do not use it again in the same round. Finally, do not play too fast. A few extra seconds of thought usually saves several wasted guesses.",
      "A second mistake is playing the same opening every time without learning from it. Vary your first move a little, notice which openings give you the most information, and keep the ones that work best for you. Over time, your personal opening set will become a real advantage."]),
     ("Practice Plan for US Players", ["Play one daily puzzle, then one practice round. After each round, ask yourself one question: what did I learn on the first move, and what would I do differently next time? That short review turns a casual game into real practice. After a week, most players notice faster pattern recognition and fewer wasted guesses.",
      "You can also practice with a friend or family member. Taking turns, talking through clues out loud, and comparing strategies makes the game more fun and helps both players improve. Word games are at their best when they are social, even for just a few minutes a day."]),
    ]
GUIDE_FAQ = [("Do I need to pay to read this guide?","No. All guides on WordSolver Hub are free."),
("Is this guide for beginners?","Yes. Guides start with the rules, then add strategy step by step."),
("Where can I practice?","Use the linked game page on WordSolver Hub. Every game is free and needs no sign-in.")]
GUIDES = [
 ("how-to-play-five-letter","How to Play the 5-Letter Game","5-Letter Game","guessing a hidden 5-letter word in six tries","Start with a word that uses common letters like E, A, R, S, and T.","Use green letters to lock positions, and yellow letters to test new positions.","Do not repeat a ruled-out letter in later guesses."),
 ("how-to-play-category-sort","How to Play Category Sort","Category Sort Game","sorting 16 words into four groups of four","Look for the most obvious group first, such as foods or animals.","Test a group by checking whether all four words share one clear idea.","If a word fits two groups, set it aside and solve the clearer groups first."),
 ("how-to-play-sudoku","How to Play Sudoku","Sudoku","filling a 9x9 grid so every row, column, and box holds digits 1 to 9","Scan for a row, column, or box that is almost complete.","Pencil in small candidate notes for empty cells.","Focus on one digit at a time across the whole grid."),
 ("how-to-play-2048","How to Play 2048","2048","sliding tiles to combine equal numbers","Keep your largest tile in one corner.","Build a chain of tiles that can combine in order.","Do not move in a direction that breaks your corner chain without a plan."),
 ("how-to-play-word-search","How to Play Word Search","Word Search","finding hidden words in a letter grid","Scan for the first letter of each word, then check its neighbors.","Look for unusual letters first, because they stand out.","Read the grid row by row, then column by column."),
 ("how-to-play-anagram","How to Play Anagrams","Anagram Game","unscrambling mixed-up letters into a real word","Find the vowels first, then build around them.","Look for common beginnings and endings.","Try the longest possible word first, then shorter ones."),
 ("how-to-play-boggle","How to Play Letter Grid Games","Letter Grid Game","building words from adjacent letters in a grid","Start with short words you can see at a glance.","Look for common letter pairs that appear together.","Keep moving: short words add up to a strong score."),
 ("how-to-play-crossword","How to Play Crossword Puzzles","Crossword Game","answering clues to fill a word grid","Answer the shortest clues first to get crossing letters.","Use crossing letters to narrow longer answers.","If a clue has wordplay, read it twice before you guess."),
 ("how-to-play-spelling-hive","How to Play Spelling Hive","Spelling Hive","building words from seven letters with a required center letter","Start with short words that use the center letter.","Look for words that use the center letter twice.","Long words that use every letter score the most."),
 ("how-to-play-word-ladder","How to Play Word Ladder","Word Ladder","changing one letter at a time to reach a target word","Work from both ends: start and target.","Change a vowel first if the words differ in a vowel.","Check that every step is a real word before you move on."),
 ("how-to-play-jumble","How to Play Jumble","Jumble Game","unscrambling a mixed-up word","Look for a vowel pattern in the middle of the word.","Try common endings first.","Say the letters out loud; hearing the word can unlock it."),
 ("crossword-tips","Crossword Tips for Beginners","Crossword Game","solving crossword clues with crossing letters","Fill in the easy answers first.","Use the crossing letters as your best clue.","Learn common crossword answers, such as short words for common clues."),
 ("sudoku-tips","Sudoku Tips for Beginners","Sudoku","solving Sudoku with scanning and notes","Scan rows, columns, and boxes for a missing digit.","Use notes for cells with only two or three candidates.","When you are stuck, scan for a single candidate in a box."),
 ("word-search-tips","Word Search Tips","Word Search","finding words faster in a letter grid","Search for the first letter, not the whole word.","Check all eight directions from that letter.","Circle or mark found words so you do not re-scan them."),
 ("2048-tips","2048 Tips and Strategy","2048","reaching high tiles in 2048","Keep the largest tile in a corner at all times.","Plan two moves ahead before you slide.","Do not fill the board with small tiles you cannot combine."),
 ("anagram-tips","Anagram Tips and Tricks","Anagram Game","unscrambling letters faster","Group the vowels together first.","Look for common pairs like TH, CH, and SH.","Rewrite the letters on paper in a new order."),
 ("scrabble-tips","Scrabble Word Tips","Scrabble-style word games","scoring words from a letter rack","Play longer words when you can, but do not waste a strong rack.","Use bonus squares for your highest-value letters.","Keep a balanced rack: do not hold too many vowels or consonants."),
 ("five-letter-tips","5-Letter Game Tips","5-Letter Game","guessing the daily word in fewer tries","Open with a word rich in common letters.","Use your second guess to test new letters, not to repeat old ones.","When you have a yellow letter, try it in every open position."),
 ("spelling-tips","Spelling Hive Tips","Spelling Hive","finding more words in a letter hive","List every short word first, then build longer ones.","Look for plural forms and common endings.","Use the center letter in as many words as you can."),
 ("how-to-solve-five-letter-games","How to Solve 5-Letter Games","5-Letter Game","solving 5-letter guessing games with a plan","Start with common letters and learn from every clue.","Treat each guess as information, not just as a guess.","Narrow the field: after two guesses, list the words that still fit."),
 ("scrabble-word-tips","Scrabble Word Tips for US Players","Scrabble-style word games","choosing high-scoring words from a rack","Score the word, not just its length: a short word on a bonus can beat a long plain word.","Learn short high-value words for tight boards.","Save a strong letter for a bonus square when you can."),
 ("sudoku-beginner-guide","Sudoku Beginner Guide","Sudoku","learning Sudoku from the first puzzle","Start with an easy puzzle and scan for almost-complete rows.","Add notes only when a cell has few candidates.","Finish one puzzle slowly rather than rushing three puzzles."),
 ("anagram-solving-tricks","Anagram Solving Tricks","Anagram Game","unscrambling words with proven tricks","Separate vowels from consonants, then rebuild.","Look for a word shape: where do the vowels sit?","If you are stuck, try the letters in reverse order."),
 ("word-search-strategies","Word Search Strategies","Word Search","finding hidden words with a system","Work through the word list in order, one word at a time.","Scan in one direction at a time: across, then down, then diagonal.","Mark each found word so your eyes do not revisit it."),
]
for slug, title, game, mechanic, t1, t2, t3 in GUIDES:
    long_article(f"guides/{slug}.html", f"{title} USA | WordSolver Hub",
      f"{title} for US players: rules, strategy, and practice tips, in plain English. Free guide.",
      title, game, guide_sections(game, mechanic, t1, t2, t3), GUIDE_FAQ)
BLOG = [
 ("daily-word-games-routine","Daily Word Games Routine for US Players","Daily word games","A short daily routine is the best way to enjoy word games without spending hours on them. Play one daily puzzle in the morning, while your mind is fresh, and one practice round later in the day if you want more. That rhythm keeps the game fun, and it builds pattern recognition over time. Many US players fit a puzzle into a coffee break, a commute, or a few quiet minutes before bed, and that small habit is enough to see real improvement in a few weeks."),
 ("how-to-get-better-at-word-games","How to Get Better at Word Games","Getting better at word games","Getting better at word games is mostly about learning from your guesses. After each round, ask what your first guess taught you, and whether a different opening would have taught you more. Keep a list of common words, practice unscrambling by finding vowels first, and play a mix of games: guessing games for logic, word searches for scanning, and category games for grouping. Variety keeps practice fresh and builds skills that transfer from one game to another."),
 ("sudoku-complete-guide-blog","Sudoku: A Complete Guide for New Players","Sudoku","Sudoku looks hard at first, but it follows one simple rule: every row, column, and 3x3 box must contain the digits 1 through 9 exactly once. Start with an easy puzzle, scan for rows or boxes that are almost complete, and fill the missing digit. When a cell has only one possible digit, that digit is the answer. Notes help when a puzzle gets harder: write small candidates in empty cells, then look for a cell with only one candidate, or a digit that can only go in one cell in a box. With practice, most players finish an easy Sudoku in ten to fifteen minutes."),
 ("brain-benefits-of-word-puzzles","Brain Benefits of Word Puzzles","Word puzzles and the brain","Word puzzles give your brain a workout that is both fun and focused. Guessing games train pattern recognition and working memory, because you must hold clues in mind while you test new words. Word searches train visual scanning and attention. Category games train grouping and flexible thinking, because a word can belong to more than one group. None of this replaces other healthy habits, but a few minutes of focused puzzle play each day is a pleasant way to keep your mind active, and it is a screen activity you can feel good about."),
 ("word-games-for-family-night","Word Games for Family Night","Family word games","Word games are a natural fit for family night because everyone can play at their own level. Younger players can hunt for words in a word search, while older players tackle a guessing game or a category puzzle. Take turns, talk through clues out loud, and let each player explain their thinking: that conversation is where the learning happens. Keep rounds short, celebrate good guesses, and rotate who picks the next game, so everyone gets a favorite. A family word game night needs no special equipment, just a screen or a printed grid and a few minutes together."),
]
for slug, title, topic, intro in BLOG:
    long_article(f"blog/{slug}.html", f"{title} | WordSolver Hub",
      f"{title}: original article for US players. Free, no sign-in.",
      title, topic, [("What This Means for You",[intro]),
        ("How to Use It This Week",["Pick one idea from this article and try it in your next game. Keep the session short, notice what worked, and repeat the parts that helped. If a strategy does not help, drop it and try another one from our Guides page. The best strategy is the one you will actually use."]),
        ("A Note on Practice",["Short, regular practice beats long, rare sessions. Five focused minutes a day will teach you more than an hour once a month. Play, review one mistake, and play again tomorrow."])], GUIDE_FAQ)
render("blog/index.html","Word Game Blog USA | WordSolver Hub","Original articles about word games, Sudoku, and puzzle practice for US players.",
 "Word Game Blog", "<p>Original articles, written for US players. No copied content, no clickbait.</p>" + cards([
  ("blog/daily-word-games-routine.html","Daily Word Games Routine","A short routine that fits a busy day."),
  ("blog/how-to-get-better-at-word-games.html","How to Get Better at Word Games","Learn from every guess."),
  ("blog/sudoku-complete-guide-blog.html","Sudoku: A Complete Guide","Start Sudoku with confidence."),
  ("blog/brain-benefits-of-word-puzzles.html","Brain Benefits of Word Puzzles","Why puzzles are good mental exercise."),
  ("blog/word-games-for-family-night.html","Word Games for Family Night","Games everyone can enjoy together."),
 ]), None)

# ================= INFO PAGES =================
render("about.html","About WordSolver Hub USA | WordSolver Hub","About WordSolver Hub: free, original word solvers and word games for US players. No sign-in, no paywall.",
 "About WordSolver Hub", """<p>WordSolver Hub is an original, free website for word game players in the United States. We build word solvers, daily word games, logic puzzles, and number games that run entirely in your browser.</p>
 <p>Our solvers use a curated list of common US English words. Our daily puzzles are picked from the US Eastern calendar date, so every player sees the same daily puzzle on the same day. Our guides are written in plain US English, with rules first and strategy second.</p>
 <p>We do not copy other sites. All code, text, puzzles, and word lists on this site were written for WordSolver Hub. Game names here are generic descriptions, not trademarks of any publisher, and we do not publish answers for other publishers' daily puzzles.</p>
 <p>There is no account to create, no download to install, and no paywall on results. If you want to track scores, they are saved only in your own browser.</p>""", None)
render("contact.html","Contact WordSolver Hub | WordSolver Hub","Contact WordSolver Hub. Send feedback about our free word solvers and games.",
 "Contact WordSolver Hub", """<p>We welcome feedback about WordSolver Hub, including corrections to a puzzle, a guide, or a word list.</p>
 <p>Because this site has no backend form, please use the contact details below. We read every message, though we cannot reply to every one individually.</p>
 <p>Email: hello@wordsolverhub.example (placeholder address for this launch version; replace with a real inbox before public promotion.)</p>
 <p>When you write, please include the page name and the date you played, so we can check the exact puzzle you mean.</p>""", None)
render("privacy.html","Privacy Policy WordSolver Hub | WordSolver Hub","Privacy policy: WordSolver Hub collects no account data and sends no solver input to a server.",
 "Privacy Policy", """<p>WordSolver Hub is designed to collect as little as possible.</p>
 <h2>What We Collect</h2><p>We do not require an account, and we do not ask for your name or email to play or to use a solver. Solver input and game play happen in your browser and are not sent to our server.</p>
 <h2>Local Storage</h2><p>If you play a game, your score may be saved in your own browser's local storage, on the Leaderboards page. You can clear those scores at any time from that page. Clearing your browser data also clears them.</p>
 <h2>Cookies and Ads</h2><p>This launch version sets no tracking cookies and shows no third-party ads. If ads or analytics are added later, this policy will be updated before they go live.</p>
 <h2>Children</h2><p>WordSolver Hub is a general word game site. We do not knowingly collect personal information from children.</p>""", None)
render("terms.html","Terms of Use WordSolver Hub | WordSolver Hub","Terms of use for WordSolver Hub: free word solvers and games, provided as-is for personal use.",
 "Terms of Use", """<p>By using WordSolver Hub, you agree to these terms.</p>
 <h2>Use of the Site</h2><p>The site is provided free for personal, non-commercial use. You may play games, use solvers, and share links to pages. You may not copy the site's code, text, or puzzles and present them as your own work.</p>
 <h2>Accuracy</h2><p>Word lists and puzzles are curated for fun and practice. They are not a dictionary, a test, or professional advice. If you spot an error, please contact us with the page name and date.</p>
 <h2>Availability</h2><p>The site is provided as-is. We may change or remove pages at any time, without notice.</p>""", None)

# Re-render hubs with full card lists (dedupe in sitemap keeps the last version)
render("solvers.html","Word Solvers & Makers | WordSolver Hub","Free word solvers: word finder, anagram, Scrabble, crossword, word search, Sudoku solver, and more. All in your browser.",
 "Word Solvers & Makers", "<p>Every solver below works in your browser. Type your letters and get answers instantly.</p>" + cards([(f"solvers/{s}.html", n, d) for s,n,k,d in SOLVERS]), None)
render("guides.html","Word Game Guides & Tips | WordSolver Hub","Guides for word games: how to play, Sudoku tips, crossword tips, anagram tricks, and 2048 strategy, in plain US English.",
 "Word Game Guides & Tips", "<p>Original guides written for US players. Each guide explains the rules, then a strategy you can use today.</p>" + cards([(f"guides/{s}.html", t, "") for s,t,g,m,t1,t2,t3 in GUIDES]), None)

# ================= SITEMAP / ROBOTS =================
seen = {}
for p,t,d in PAGES: seen[p] = (t,d)
pages_sorted = sorted(seen.items())
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for p,(t,d) in pages_sorted:
    loc = BASE + "/" + p if p != "index.html" else BASE + "/"
    sitemap += f"  <url><loc>{loc}</loc></url>\n"
sitemap += "</urlset>\n"
open(os.path.join(ROOT,"sitemap.xml"),"w").write(sitemap)
open(os.path.join(ROOT,"robots.txt"),"w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
print(f"Generated {len(pages_sorted)} pages")
for p,(t,d) in pages_sorted: print(p)
