// Shared helpers: US Eastern date seeding, solvers, scores. All original code.
function easternDateString(d){
  d=d||new Date();
  try{return new Intl.DateTimeFormat('en-CA',{timeZone:'America/New_York',year:'numeric',month:'2-digit',day:'2-digit'}).format(d);}
  catch(e){return d.toISOString().slice(0,10);}
}
function hashSeed(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return h>>>0;}
function makeRng(seed){let a=seed>>>0;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function dailyPick(list,key){const d=easternDateString();const r=makeRng(hashSeed(d+'|'+key));return list[Math.floor(r()*list.length)];}
function shuffled(list,seedStr){const r=makeRng(hashSeed(seedStr));const a=[...list];for(let i=a.length-1;i>0;i--){const j=Math.floor(r()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
function countLetters(s){const m={};for(const c of s.toLowerCase()){if(/[a-z]/.test(c))m[c]=(m[c]||0)+1;}return m;}
function canMake(word,letters){
  const avail=countLetters(letters);let wild=avail['?']||0;delete avail['?'];
  const need=countLetters(word);
  for(const c in need){const have=avail[c]||0;if(need[c]>have){const diff=need[c]-have;if(diff<=wild)wild-=diff;else return false;}}
  return true;
}
function findWords(letters,opts){
  opts=opts||{};const clean=(letters||'').toLowerCase().replace(/[^a-z?]/g,'');
  if(!clean)return[];
  let pool=WORDS.all.filter(w=>canMake(w,clean));
  if(opts.len)pool=pool.filter(w=>w.length===opts.len);
  if(opts.minLen)pool=pool.filter(w=>w.length>=opts.minLen);
  if(opts.pattern){const re=new RegExp('^'+opts.pattern.toLowerCase().replace(/\?/g,'.').replace(/\*/g,'.*')+'$');pool=pool.filter(w=>re.test(w));}
  pool.sort((a,b)=>b.length-a.length||a.localeCompare(b));
  return pool;
}
var SCRABBLE_POINTS={a:1,b:3,c:3,d:2,e:1,f:4,g:2,h:4,i:1,j:8,k:5,l:1,m:3,n:1,o:1,p:3,q:10,r:1,s:1,t:1,u:1,v:4,w:4,x:8,y:4,z:10};
function scrabbleScore(w){return [...w.toLowerCase()].reduce((s,c)=>s+(SCRABBLE_POINTS[c]||0),0);}
function patternMatch(pattern){
  const re=new RegExp('^'+pattern.toLowerCase().replace(/[^a-z?*]/g,'').replace(/\?/g,'.').replace(/\*/g,'.*')+'$');
  return WORDS.all.filter(w=>re.test(w)).sort((a,b)=>a.length-b.length||a.localeCompare(b));
}
function saveScore(game,score){
  try{const k='wsh_scores';const all=JSON.parse(localStorage.getItem(k)||'[]');all.push({game,score,date:easternDateString(),ts:Date.now()});all.sort((a,b)=>b.score-a.score);localStorage.setItem(k,JSON.stringify(all.slice(0,100)));}catch(e){}
}
function renderWords(el,words,limit){
  limit=limit||200;
  if(!words.length){el.innerHTML='<p class="small">No matching words found. Check your letters and try again.</p>';return;}
  const shown=words.slice(0,limit);
  el.innerHTML='<p><strong>'+words.length+' word'+(words.length>1?'s':'')+' found</strong> '+(words.length>limit?' (showing first '+limit+')':'')+'</p><p>'+shown.map(w=>'<span class="pill">'+w+'</span>').join('')+'</p>';
}
function groupByLength(words){
  const g={};words.forEach(w=>{(g[w.length]=g[w.length]||[]).push(w);});
  return Object.keys(g).sort((a,b)=>b-a).map(n=>'<h3>'+n+' letters ('+g[n].length+')</h3><p>'+g[n].map(w=>'<span class="pill">'+w+'</span>').join('')+'</p>').join('');
}
// Category sets for the category-sort game (original groups)
var CATEGORY_SETS=[
 {cats:[{name:'Fruits',words:['apple','peach','mango','lemon']},{name:'Animals',words:['tiger','horse','eagle','shark']},{name:'Colors',words:['green','black','white','brown']},{name:'Sports',words:['soccer','tennis','golf','boxing']}]},
 {cats:[{name:'Kitchen Items',words:['plate','spoon','knife','oven']},{name:'Vehicles',words:['train','truck','plane','boat']},{name:'Body Parts',words:['hand','foot','head','arm']},{name:'Seasons',words:['spring','summer','autumn','winter']}]},
 {cats:[{name:'School Subjects',words:['math','science','history','english']},{name:'Musical Instruments',words:['piano','guitar','violin','drum']},{name:'Weather Words',words:['rain','snow','storm','cloud']},{name:'Jobs',words:['doctor','teacher','baker','farmer']}]},
 {cats:[{name:'Ocean Words',words:['wave','sand','shell','coral']},{name:'Space Words',words:['moon','star','planet','comet']},{name:'Clothing',words:['shirt','pants','dress','coat']},{name:'Drinks',words:['water','juice','coffee','milk']}]},
 {cats:[{name:'Garden Words',words:['flower','leaf','seed','soil']},{name:'Tools',words:['hammer','wrench','screw','drill']},{name:'Shapes',words:['circle','square','triangle','oval']},{name:'Emotions',words:['happy','angry','calm','proud']}]},
 {cats:[{name:'Breakfast Foods',words:['toast','egg','bacon','cereal']},{name:'Buildings',words:['house','school','library','museum']},{name:'Numbers',words:['one','two','three','four']},{name:'Directions',words:['north','south','east','west']}]}
];
function dailyCategorySet(){
  const d=easternDateString();const r=makeRng(hashSeed(d+'|category-sort'));
  return CATEGORY_SETS[Math.floor(r()*CATEGORY_SETS.length)];
}
