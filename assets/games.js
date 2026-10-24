// Original playable game engines. No external code.
function guessFeedback(guess,answer){
  const res=Array(guess.length).fill('grey');const counts={};
  for(const c of answer)counts[c]=(counts[c]||0)+1;
  for(let i=0;i<guess.length;i++)if(guess[i]===answer[i]){res[i]='green';counts[guess[i]]--;}
  for(let i=0;i<guess.length;i++)if(res[i]!=='green'&&counts[guess[i]]>0){res[i]='yellow';counts[guess[i]]--;}
  return res;
}
function initGuessGame(rootId,answers,maxGuesses){
  const root=document.getElementById(rootId);if(!root)return;
  const n=answers[0].length;let guesses=[];let done=false;
  root.innerHTML='<div id="gg-board"></div><div style="margin-top:10px"><input id="gg-input" maxlength="'+n+'" placeholder="Type a '+n+'-letter word" aria-label="Guess"><button class="btn" id="gg-go" style="margin-top:8px">Guess</button></div><p id="gg-msg" class="small"></p><div class="kbd" id="gg-kbd"></div>';
  const board=root.querySelector('#gg-board'),msg=root.querySelector('#gg-msg'),input=root.querySelector('#gg-input');
  function render(){
    board.innerHTML=guesses.map(g=>{
      const row=g.feedback.map((f,i)=>'<span class="tile '+f+'">'+g.word[i]+'</span>').join('');
      return '<div>'+row+'</div>';
    }).join('')||'<p class="small">You have '+maxGuesses+' guesses. Green = right letter, right spot. Yellow = right letter, wrong spot. Grey = not in the word.</p>';
  }
  function submit(){
    if(done)return;const w=input.value.toLowerCase().trim();
    if(w.length!==n){msg.textContent='Please enter exactly '+n+' letters.';return;}
    const entry={word:w,feedback:answers.map(a=>guessFeedback(w,a))};
    guesses.push(entry);input.value='';render();
    const solved=answers.every((a,i)=>w===a);
    if(solved){done=true;msg.textContent='You solved it in '+guesses.length+' guesses!';saveScore('word-guess',Math.max(0,100-guesses.length*10));}
    else if(guesses.length>=maxGuesses){done=true;msg.textContent='Game over. The answer'+(answers.length>1?'s were':' was')+': '+answers.join(', ');}
    else msg.textContent='Guess '+(guesses.length+1)+' of '+maxGuesses+'.';
  }
  root.querySelector('#gg-go').onclick=submit;
  input.addEventListener('keydown',e=>{if(e.key==='Enter')submit();});
  const kbd=root.querySelector('#gg-kbd');
  'abcdefghijklmnopqrstuvwxyz'.split('').forEach(c=>{const b=document.createElement('button');b.textContent=c;b.onclick=()=>{if(input.value.length<n)input.value+=c;input.focus();};kbd.appendChild(b);});
  const del=document.createElement('button');del.textContent='⌫';del.onclick=()=>{input.value=input.value.slice(0,-1);};kbd.appendChild(del);
  render();
}
// Sudoku
var SUDOKU_PUZZLES=[
 {puzzle:'53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79',solution:'534678912672195348198342567859761423426853791713924856961537284287419635345286179'},
 {puzzle:'..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..',solution:'483921657967345821251876493548132976729564138136798245372689514814253769695417382'},
 {puzzle:'6.....8.3.4.7.3.61.8..5.....2..7.3...4..6...9.1.4.....3.5..6.8..1.7..2..5.9....7',solution:'619753284254896371783421569926187435475632918831945726392518647547269183168374952'}
];
function initSudoku(rootId,puzzleIndex){
  const root=document.getElementById(rootId);if(!root)return;
  const data=SUDOKU_PUZZLES[puzzleIndex%SUDOKU_PUZZLES.length];
  const puzzle=data.puzzle.split(''),solution=data.solution.split('');
  let notes=false;
  root.innerHTML='<p><button class="btn2" id="sd-notes">Notes: Off</button> <button class="btn2" id="sd-erase">Erase</button> <button class="btn2" id="sd-check">Check</button> <button class="btn2" id="sd-hint">Hint</button></p><table class="sudoku"><tbody>'+Array.from({length:9},(_,r)=>'<tr>'+Array.from({length:9},(_,c)=>{const i=r*9+c;const v=puzzle[i];return '<td><input data-i="'+i+'" maxlength="1" '+(v!=='.'?'value="'+v+'" disabled style="background:#172C26;color:#00D68F"':'')+'></td>';}).join('')+'</tr>').join('')+'</tbody></table><p id="sd-msg" class="small"></p>';
  const msg=root.querySelector('#sd-msg');let selected=null;
  root.querySelectorAll('input').forEach(inp=>{inp.addEventListener('focus',()=>selected=inp);});
  root.querySelector('#sd-notes').onclick=e=>{notes=!notes;e.target.textContent='Notes: '+(notes?'On':'Off');};
  root.querySelector('#sd-erase').onclick=()=>{if(selected&&!selected.disabled)selected.value='';};
  root.querySelector('#sd-check').onclick=()=>{
    let wrong=0,filled=0;
    root.querySelectorAll('input').forEach(inp=>{const i=+inp.dataset.i;if(inp.value){filled++;if(inp.value!==solution[i]){wrong++;inp.style.color='#f87171';}else inp.style.color='#00D68F';}});
    msg.textContent=wrong?wrong+' cell(s) are wrong. Keep going!':(filled===81?'Solved! Great work.':'All filled cells look correct so far.');
    if(filled===81&&!wrong)saveScore('sudoku',100);
  };
  root.querySelector('#sd-hint').onclick=()=>{
    const empties=[...root.querySelectorAll('input')].filter(i=>!i.value&&!i.disabled);
    if(empties.length){const inp=empties[0];inp.value=solution[+inp.dataset.i];inp.style.color='#00D68F';msg.textContent='Hint filled one cell.';}
  };
}
// 2048
function init2048(rootId){
  const root=document.getElementById(rootId);if(!root)return;
  let grid=Array(16).fill(0),score=0,over=false;
  function spawn(){const e=grid.map((v,i)=>v===0?i:-1).filter(i=>i>=0);if(!e.length)return;grid[e[Math.floor(Math.random()*e.length)]]=Math.random()<0.9?2:4;}
  function slide(row){let a=row.filter(v=>v);for(let i=0;i<a.length-1;i++)if(a[i]===a[i+1]){a[i]*=2;score+=a[i];a.splice(i+1,1);}while(a.length<4)a.push(0);return a;}
  function move(dir){
    if(over)return;const old=[...grid];
    for(let k=0;k<4;k++){
      let idx=[];for(let i=0;i<4;i++){let r,c;if(dir==='left'){r=k;c=i;}if(dir==='right'){r=k;c=3-i;}if(dir==='up'){r=i;c=k;}if(dir==='down'){r=3-i;c=k;}idx.push(r*4+c);}
      let row=idx.map(i=>grid[i]);if(dir==='right'||dir==='down')row=slide(row.reverse()).reverse();else row=slide(row);
      idx.forEach((gi,j)=>grid[gi]=row[j]);
    }
    if(JSON.stringify(old)!==JSON.stringify(grid)){spawn();render();if(!grid.includes(0)){over=true;document.getElementById('g2048-msg').textContent='Game over. Final score: '+score;saveScore('2048',score);}}
  }
  function render(){
    document.getElementById('g2048-board').innerHTML=grid.map(v=>'<div class="cell" style="font-size:18px;background:'+(v? '#172C26':'#0f1a17')+';color:'+(v>=64?'#00D68F':'#fff')+'">'+(v||'')+'</div>').join('');
    document.getElementById('g2048-score').textContent='Score: '+score;
  }
  root.innerHTML='<p id="g2048-score">Score: 0</p><div class="wordgrid" id="g2048-board" style="grid-template-columns:repeat(4,1fr)"></div><p><button class="btn2" data-d="up">↑</button> <button class="btn2" data-d="left">←</button> <button class="btn2" data-d="down">↓</button> <button class="btn2" data-d="right">→</button> <button class="btn" id="g2048-new">New Game</button></p><p id="g2048-msg" class="small">Use arrow keys or the buttons. Combine equal tiles to reach 2048.</p>';
  root.querySelectorAll('[data-d]').forEach(b=>b.onclick=()=>move(b.dataset.d));
  document.addEventListener('keydown',e=>{const m={ArrowUp:'up',ArrowDown:'down',ArrowLeft:'left',ArrowRight:'right'}[e.key];if(m){e.preventDefault();move(m);}});
  root.querySelector('#g2048-new').onclick=()=>{grid=Array(16).fill(0);score=0;over=false;spawn();spawn();render();};
  spawn();spawn();render();
}
// Word search
function initWordSearch(rootId,words){
  const root=document.getElementById(rootId);if(!root)return;
  const size=10;let grid=Array.from({length:size},()=>Array(size).fill(''));
  const dirs=[[1,0],[0,1],[1,1],[1,-1]];
  const placed=[];
  const rng=makeRng(hashSeed(easternDateString()+'|wordsearch'));
  words.forEach(w=>{
    for(let attempt=0;attempt<200;attempt++){
      const dir=dirs[Math.floor(rng()*dirs.length)];const r=Math.floor(rng()*size),c=Math.floor(rng()*size);
      const er=r+dir[0]*(w.length-1),ec=c+dir[1]*(w.length-1);
      if(er<0||er>=size||ec<0||ec>=size)continue;
      let ok=true;for(let i=0;i<w.length;i++){const ch=grid[r+dir[0]*i][c+dir[1]*i];if(ch&&ch!==w[i]){ok=false;break;}}
      if(!ok)continue;
      for(let i=0;i<w.length;i++)grid[r+dir[0]*i][c+dir[1]*i]=w[i];
      placed.push(w);break;
    }
  });
  const letters='abcdefghijklmnopqrstuvwxyz';
  for(let r=0;r<size;r++)for(let c=0;c<size;c++)if(!grid[r][c])grid[r][c]=letters[Math.floor(Math.random()*26)];
  let sel=[],found=new Set();
  function render(){
    root.querySelector('#ws-grid').innerHTML=grid.map((row,r)=>row.map((ch,c)=>{
      const key=r+'-'+c;const isSel=sel.includes(key);const isFound=[...found].some(w=>false);
      return '<div class="cell '+(isSel?'sel':'')+'" data-r="'+r+'" data-c="'+c+'">'+ch+'</div>';
    }).join('')).join('');
    root.querySelectorAll('.cell').forEach(cell=>cell.onclick=()=>toggle(cell));
    root.querySelector('#ws-list').innerHTML=placed.map(w=>'<span class="pill" style="'+(found.has(w)?'text-decoration:line-through;color:#00D68F':'')+'">'+w+'</span>').join('');
  }
  function toggle(cell){
    const key=cell.dataset.r+'-'+cell.dataset.c;
    if(sel.includes(key))sel=sel.filter(k=>k!==key);else sel.push(key);
    // check if selection spells a placed word (in any order of cells forming word, use letters in selection order)
    const word=sel.map(k=>{const [r,c]=k.split('-').map(Number);return grid[r][c];}).join('');
    const rev=[...word].reverse().join('');
    const hit=placed.find(w=>w===word||w===rev);
    if(hit){found.add(hit);sel=[];root.querySelector('#ws-msg').textContent='Found: '+hit+' ('+found.size+' of '+placed.length+')';
      if(found.size===placed.length){root.querySelector('#ws-msg').textContent='All words found! Great work.';saveScore('word-search',100);}}
    render();
  }
  root.innerHTML='<div class="wordgrid" id="ws-grid"></div><p id="ws-list"></p><p id="ws-msg" class="small">Click letters in order to select a word. Words can run across, down, or diagonally.</p>';
  render();
}
// Minesweeper 9x9
function initMinesweeper(rootId){
  const root=document.getElementById(rootId);if(!root)return;const n=9,mines=10;
  let cells=Array(n*n).fill(0);let mineSet=new Set();while(mineSet.size<mines)mineSet.add(Math.floor(Math.random()*81));
  function count(r,c){let k=0;for(let dr=-1;dr<=1;dr++)for(let dc=-1;dc<=1;dc++){const rr=r+dr,cc=c+dc;if(rr>=0&&rr<n&&cc>=0&&cc<n&&mineSet.has(rr*n+cc))k++;}return k;}
  let revealed=new Set(),over=false;
  function render(){
    root.querySelector('#ms-grid').innerHTML=Array.from({length:n*n},(_,i)=>{const r=Math.floor(i/n),c=i%n;const rev=revealed.has(i);const isMine=mineSet.has(i);
      return '<div class="cell" style="background:'+(rev?(isMine?'#7f1d1d':'#172C26'):'#0f1a17')+'" data-i="'+i+'">'+(rev?(isMine?'💣':(count(r,c)||'')):'')+'</div>';}).join('');
    root.querySelectorAll('.cell').forEach(cell=>cell.onclick=()=>{
      if(over)return;const i=+cell.dataset.i;if(mineSet.has(i)){revealed=new Set([...Array(81).keys()]);over=true;root.querySelector('#ms-msg').textContent='You hit a mine. Try again!';}
      else{revealed.add(i);if(revealed.size===81-mines){over=true;root.querySelector('#ms-msg').textContent='You cleared the board!';saveScore('minesweeper',100);}}
      render();
    });
  }
  root.innerHTML='<div class="wordgrid" id="ms-grid" style="grid-template-columns:repeat(9,1fr);max-width:450px"></div><p id="ms-msg" class="small">Click a square. Avoid the 10 mines. The number shows how many mines touch that square.</p><button class="btn" id="ms-new">New Game</button>';
  root.querySelector('#ms-new').onclick=()=>{mineSet=new Set();while(mineSet.size<mines)mineSet.add(Math.floor(Math.random()*81));revealed=new Set();over=false;render();};
  render();
}
// Snake on canvas
function initSnake(rootId){
  const root=document.getElementById(rootId);if(!root)return;
  root.innerHTML='<canvas id="snake-canvas" width="400" height="400" style="background:#0f1a17;border:1px solid #2a423a;border-radius:12px;max-width:100%"></canvas><p><button class="btn" id="snake-start">Start</button> <span id="snake-score" class="small">Score: 0</span></p><p class="small">Use arrow keys. Eat the green dots and do not hit yourself or the wall.</p>';
  const cv=root.querySelector('#snake-canvas'),ctx=cv.getContext('2d');let snake,dir,food,score,timer;
  function draw(){
    ctx.clearRect(0,0,400,400);ctx.fillStyle='#00D68F';ctx.fillRect(food.x*20,food.y*20,20,20);
    ctx.fillStyle='#fff';snake.forEach((s,i)=>{ctx.fillStyle=i===0?'#00D68F':'#fff';ctx.fillRect(s.x*20,s.y*20,19,19);});
  }
  function step(){
    const head={x:snake[0].x+dir.x,y:snake[0].y+dir.y};
    if(head.x<0||head.y<0||head.x>=20||head.y>=20||snake.some(s=>s.x===head.x&&s.y===head.y)){clearInterval(timer);root.querySelector('#snake-score').textContent='Game over. Score: '+score;saveScore('snake',score);return;}
    snake.unshift(head);
    if(head.x===food.x&&head.y===food.y){score+=10;food={x:Math.floor(Math.random()*20),y:Math.floor(Math.random()*20)};}else snake.pop();
    root.querySelector('#snake-score').textContent='Score: '+score;draw();
  }
  document.addEventListener('keydown',e=>{const m={ArrowUp:{x:0,y:-1},ArrowDown:{x:0,y:1},ArrowLeft:{x:-1,y:0},ArrowRight:{x:1,y:0}}[e.key];if(m&&!(m.x===-dir.x&&m.y===-dir.y))dir=m;});
  root.querySelector('#snake-start').onclick=()=>{clearInterval(timer);snake=[{x:10,y:10},{x:9,y:10},{x:8,y:10}];dir={x:1,y:0};food={x:15,y:10};score=0;timer=setInterval(step,140);draw();};
}
// Spelling hive
function initHive(rootId){
  const root=document.getElementById(rootId);if(!root)return;
  const sets=[['a','e','t','r','s','n','c'],['o','i','l','m','p','e','s'],['a','r','d','g','n','i','e']];
  const letters=sets[Math.floor(makeRng(hashSeed(easternDateString()+'|hive'))()*sets.length)];
  const center=letters[0];let found=new Set(),score=0;
  root.innerHTML='<p>Letters: '+letters.map((l,i)=>'<span class="pill" style="'+(i===0?'color:#00D68F;border-color:#00D68F':'')+'">'+l+'</span>').join('')+' (center letter <strong>'+center+'</strong> must be used)</p><input id="hive-in" placeholder="Type a word using these letters"><button class="btn" id="hive-go" style="margin-top:8px">Check Word</button><p id="hive-msg" class="small"></p><p id="hive-found"></p>';
  root.querySelector('#hive-go').onclick=()=>{
    const w=root.querySelector('#hive-in').value.toLowerCase().trim();const msg=root.querySelector('#hive-msg');
    if(w.length<4){msg.textContent='Words must be at least 4 letters.';return;}
    if(!w.includes(center)){msg.textContent='The word must include the center letter '+center+'.';return;}
    if([...w].some(c=>!letters.includes(c))){msg.textContent='Use only the letters shown.';return;}
    if(!WORDS.all.includes(w)){msg.textContent='That word is not in our word list.';return;}
    if(found.has(w)){msg.textContent='Already found.';return;}
    found.add(w);score+=w.length;msg.textContent='Nice! +'+w.length+' points. Score: '+score;
    root.querySelector('#hive-found').innerHTML=[...found].map(x=>'<span class="pill">'+x+'</span>').join('');
    saveScore('spelling-hive',score);
  };
}
// Boggle grid
function initBoggle(rootId){
  const root=document.getElementById(rootId);if(!root)return;
  const dice='abcdefghijklmnopqrstuvwxyz';const rng=makeRng(hashSeed(easternDateString()+'|boggle'));
  const grid=Array.from({length:16},()=>dice[Math.floor(rng()*26)]);
  let sel=[],found=new Set();
  root.innerHTML='<div class="wordgrid" id="bg-grid" style="grid-template-columns:repeat(4,1fr);max-width:320px"></div><p><button class="btn" id="bg-check">Check Word</button> <button class="btn2" id="bg-clear">Clear</button></p><p id="bg-msg" class="small">Click adjacent letters to build a word, then check it.</p><p id="bg-found"></p>';
  function render(){
    root.querySelector('#bg-grid').innerHTML=grid.map((ch,i)=>'<div class="cell '+(sel.includes(i)?'sel':'')+'" data-i="'+i+'">'+ch+'</div>').join('');
    root.querySelectorAll('.cell').forEach(c=>c.onclick=()=>{const i=+c.dataset.i;if(sel.includes(i))sel=sel.filter(x=>x!==i);else sel.push(i);render();});
  }
  root.querySelector('#bg-check').onclick=()=>{
    const w=sel.map(i=>grid[i]).join('');const msg=root.querySelector('#bg-msg');
    if(w.length<3){msg.textContent='Words must be at least 3 letters.';return;}
    if(!WORDS.all.includes(w)){msg.textContent=w+' is not in our word list.';}
    else if(found.has(w))msg.textContent='Already found.';
    else{found.add(w);msg.textContent='Found: '+w+'!';root.querySelector('#bg-found').innerHTML=[...found].map(x=>'<span class="pill">'+x+'</span>').join('');saveScore('boggle',found.size*10);}
    sel=[];render();
  };
  root.querySelector('#bg-clear').onclick=()=>{sel=[];render();};
  render();
}
