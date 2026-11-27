#!/usr/bin/env python3
"""Lote de 26-27/11/2026 do Claude do Deck no motor X1 (grimorio-arena), por cima do index.html de 01d0d5e.
Reaplicável: cada seção tem uma marca; se já estiver, pula. Uso: python3 -I patch_x1_27.py ARQUIVO.html"""
import sys
P = []

# ---------- L1. Gatilho atrasado no fim do combate (EndC) e no próximo final de turno de qualquer jogador (EndP) ----------
# Cinder Wall, Fog Elemental, Clockwork Beetle, Windscouter, Wicker Warcrawler...: só quando a cadeia usa a própria carta (sem "lembrado" do gatilho).
P.append(("const fgAtrSemLemb=", "      return nao('gatilho atrasado');}",
"""      {const fgAtrSemLemb=(nm,v)=>{let q=nm,vis=0;while(q&&++vis<12){const l=String((ctx.sv||{})[q]||'');if(!l||/Remembered|Imprinted|Triggered|Targeted|ParentTarget/.test(l))return false;q=fgPP(l).d.SubAbility;}return true;};
       if(d.Mode==='Phase'&&ex.api&&!d.ThisTurn&&!d.NextTurn&&!d.RememberObjects&&!d.DelayedTriggerDefinedPlayer&&(!d.ValidPlayer||d.ValidPlayer==='Player'||d.ValidPlayer==='You')&&fgAtrSemLemb(d.Execute)){
         const ph=d.Phase==='EndCombat'?'EndC':/^(End of Turn|End Of Turn|Cleanup)$/.test(d.Phase||'')&&d.ValidPlayer==='Player'?'EndP':'';
         if(ph){const st=fgCadeia(ex.d,ex.api,ctx);if(st.some(o=>o.op==='nao'))return st;return [{op:'atrasa',ph,st}];}}}
""", 'antes'))
P.append(("tc:it.tc||null});feito.push(", "(e.atr=e.atr||[]).push({ph:s.ph,t0:(X.sala||{}).turno||0,st:s.st,nm:it.nm,k:it.k||'',lemb:it.lemb||null});feito.push(/^Upkeep/.test(s.ph)?(s.ph==='UpkeepP'?'efeito guardado pra próxima manutenção':'efeito guardado pra sua próxima manutenção'):'efeito guardado pro final do turno');",
"(e.atr=e.atr||[]).push({ph:s.ph,t0:(X.sala||{}).turno||0,st:s.st,nm:it.nm,k:it.k||'',lemb:it.lemb||null,tc:it.tc||null});feito.push(/^Upkeep/.test(s.ph)?(s.ph==='UpkeepP'?'efeito guardado pra próxima manutenção':'efeito guardado pra sua próxima manutenção'):s.ph==='EndC'?'efeito guardado pro fim do combate':s.ph==='EndP'?'efeito guardado pro próximo final de turno':'efeito guardado pro final do turno');", 'troca'))
P.append(("ph==='EndC'?a.ph==='EndC'&&a.t0===t", "function xAtrasado(ph){const e=X.eu,s=X.sala||{};if(!e||!e.atr||!e.atr.length)return;const t=s.turno||0,ag=e.atr.filter(a=>(a.ph===ph||(ph==='Upkeep'&&a.ph==='UpkeepP'))&&(ph==='End'?t>=a.t0:t>a.t0));if(!ag.length)return;e.atr=e.atr.filter(a=>!ag.includes(a));\n  for(const a of ag){xLog(`${a.nm}: efeito atrasado (${ph==='Upkeep'?'manutenção':'final do turno'})`);xFazDepois(a.st,{nm:a.nm,k:a.k,al:[],tc:{},sc:{},lemb:a.lemb});}}",
"""/* EndC = fim do combate deste turno; EndP = próximo final de turno de qualquer jogador (sai no seu passa ou na troca de turno: TurnoP) */
function xAtrasado(ph){const e=X.eu,s=X.sala||{};if(!e||!e.atr||!e.atr.length)return;const t=s.turno||0;e.atr=e.atr.filter(a=>!(a.ph==='EndC'&&a.t0<t));
  const ok=a=>ph==='EndC'?a.ph==='EndC'&&a.t0===t:ph==='TurnoP'?a.ph==='EndP'&&t>a.t0:(a.ph===ph||(ph==='Upkeep'&&a.ph==='UpkeepP')||(ph==='End'&&a.ph==='EndP'))&&(ph==='End'?t>=a.t0:t>a.t0);
  const ag=e.atr.filter(ok);if(!ag.length)return;e.atr=e.atr.filter(a=>!ag.includes(a));
  for(const a of ag){xLog(`${a.nm}: efeito atrasado (${/^Upkeep/.test(ph)?'manutenção':ph==='EndC'?'fim do combate':'final do turno'})`);xFazDepois(a.st,{nm:a.nm,k:a.k,al:[],tc:a.tc||{},sc:{},lemb:a.lemb});}}""", 'troca'))
P.append(("X.__cbA&&!cb&&X.__cbT===s.turno", "function xTurno(){const s=X.sala,e=X.eu,me=xUid();if(!s||!e)return;let mud=0;",
"\n  {const cb=s.fase===2||!!s.cb;if(X.__cbA&&!cb&&X.__cbT===s.turno)setTimeout(()=>xAtrasado('EndC'),500);X.__cbA=cb;X.__cbT=s.turno;if(X.__epT!==s.turno){if(X.__epT!=null&&s.turno)setTimeout(()=>xAtrasado('TurnoP'),650);X.__epT=s.turno;}}", 'depois'))

# ---------- L2. Jogador definido pelo Forge perde vida / compra: controlador do alvo, jogador do gatilho, controlador da carta do gatilho ----------
# Hideous End, Liliana's Defeat, Vapor Snag, One Thousand Lashes, Doom Foretold, Curse of Wizardry, Gwafa Hazid, Dream Fracture, Super Intelligence...
P.append(("function fgQuemJ(", "function xDonoK(k){",
"""/* jogador que o Forge definiu (Defined$): alvo = controlador do alvo; tp = jogador do gatilho; tku = controlador da carta do gatilho; td = jogador atingido no gatilho */
function fgQuemJ(df){df=String(df||'');if(/^(Parent)?Targeted(Controller|Owner)$/.test(df))return 'alvo';if(/^Triggered(Player|Activator)$/.test(df))return 'tp';if(/^Triggered(Card|Attacker|Source|Object)(LKICopy)?(Controller|Owner)$/.test(df))return 'tku';if(df==='TriggeredTarget')return 'td';return '';}
function xQuemJ(q,it,ult){const T=it.tc||{},me=xUid();if(q==='tp')return T.tp||T.tku||'';if(q==='tku')return T.tku||'';if(q==='td')return String(T.td||'').startsWith('P:')?String(T.td).slice(2):'';
  if(q==='alvo'){const t0=ult||(it.al||[])[0]||'';if(String(t0).startsWith('S:'))return ((((X.sala||{}).pilha||[]).find(p=>'S:'+p.id===t0))||{}).de||'';if(String(t0).startsWith('P:'))return String(t0).slice(2);if(t0)return (X.eu.campo.some(c=>c.k===t0)?me:(xDonoK(t0)||''));}return '';}
""", 'antes'))
P.append(("const q=fgQuemJ(df);if(q)return [{op:'perdeQ'", "if(!df)return [{op:'perdeEu',n}];return nao('quem perde');}",
"if(!df)return [{op:'perdeEu',n}];{const q=fgQuemJ(df);if(q)return [{op:'perdeQ',n,q}];}return nao('quem perde');}", 'troca'))
P.append(("return [{op:'compraQ',n,q}]", "if(df!=='You'&&!al)return nao('quem compra');",
"if(df!=='You'&&!al){const q=fgQuemJ(d.Defined);if(q)return [{op:'compraQ',n,q}];}", 'antes'))
P.append(("case 'perdeQ':", "      case 'perdeTc':{",
"""      case 'perdeQ':{const u=xQuemJ(s.q,it,ult),q=Math.max(0,+n||0);if(!u){feito.push('sem o jogador que perde vida');break;}if(u===me)e.vida-=q;else ev({op:'vida',d:-q},u);it.perdeu=(it.perdeu||0)+q;feito.push(`${u===me?'você':xNomeU(u)} perdeu ${q} de vida`);break;}
      case 'compraQ':{const u=xQuemJ(s.q,it,ult),q=Math.max(0,+n||0);if(!u){feito.push('sem o jogador que compra');break;}if(u===me){for(let r=0;r<q;r++)if(e.bib.length)e.mao.push(e.bib.shift());}else ev({op:'compra',n:q},u);feito.push(`${u===me?'você':xNomeU(u)} comprou ${q}`);break;}
""", 'antes'))

# ---------- L3. Dono da ficha definido pelo Forge: jogador alvo, cada oponente, cada jogador, jogador do gatilho ----------
# Hunted Dragon/Troll, Gravedig, Emeritus of Truce, Ashling's Command, Grismold, Elephant Resurgence, Questing Phelddagrif, Gonti, Dovescape...
P.append(("const dq=/^(This)?Targeted(Player)?$/", "if(dn==null)return nao('dono da ficha');",
"""if(dn==null){const dq=/^(This)?Targeted(Player)?$/.test(ow)&&/^target (opponent|player)$/.test(al||'')?'ou':ow==='Opponent'||ow==='Player.Opponent'?'ops':ow==='Player'?'todos':fgQuemJ(ow==='TriggeredPlayer'||ow==='TriggeredActivator'?ow:ow==='TriggeredTarget'?ow:'');
        if(dq){const o=fgFicha(d.TokenScript||'',n);if(o){o.forEach(q=>{if(q.op==='ficha'){q.dq=dq;if(d.TokenTapped==='True')q.tap=1;}});if(o.some(q=>q.op==='ficha'))return o;}}}""", 'antes'))
P.append(("if(s.dq){const vv=", "      case 'ficha':if(s.dono==='alvo'&&L0.u&&L0.u!==me){",
"""      case 'ficha':if(s.dq){const vv=Object.keys(X.ops||{}).filter(u=>!xMorto(X.ops[u])),us=s.dq==='ops'?vv:s.dq==='todos'?[me,...vv]:s.dq==='ou'?[ou]:[xQuemJ(s.dq,it,ult)],nm=[];
          for(const u of us){if(!u)continue;if(u===me){xFicha(s.nome,s.p,s.t,s.kw,s.art,s.mana,n,1);xFichaPos(e,n,s);}else ev({op:'fichaD',nome:s.nome,p:s.p,t:s.t,kw:s.kw,art:s.art,mana:s.mana,n},u);nm.push(u===me?'você':xNomeU(u));}
          feito.push(nm.length?`${nm.join(', ')}: ${n} ficha${n>1?'s':''} ${s.nome}${s.p!=null?' '+s.p+'/'+s.t:''}`:'sem o dono da ficha');break;}
        if(s.dono==='alvo'&&L0.u&&L0.u!==me){""", 'troca'))

# ---------- L4. Efeito nas cartas lembradas (Remembered) e nas do gatilho: Pump/PutCounter/Regenerate; regenerar as suas que batem no filtro; ganhar vida: jogador alvo, oponente, cada jogador ----------
# Teysa, Strefan, Savage Order, Giant Regrowth, Fractal Harness, Body of Research, Golgari Charm, Wrap in Vigor, Healing Leaves, Titan of Industry, Soothing Balm...
P.append(("const fgLembT=", "function fgQuemJ(df){",
"""/* passo aplicado em cada carta lembrada (lembT) ou na carta do gatilho (tk); só ops que usam o alvo t */
const fgLembT=(d,api,ctx)=>{const df=String(d.Defined||'');const k=/^Remembered(LKI|Card)?$/.test(df)?'lembT':/^Triggered(Card|Attacker|Object)(LKICopy)?$/.test(df)?'tk':'';if(!k)return null;const d2=Object.assign({},d);delete d2.Defined;delete d2.SubAbility;
  const r=fgPasso(d2,api,ctx);if(r.some(x=>x.op==='nao'))return r;if(!r.length||!r.every(x=>['pump','kt','nDesv','cnt','regen'].includes(x.op)&&!x.al))return null;return r.map(x=>Object.assign(x,{[k]:1}));};
""", 'antes'))
P.append(("fgLembT(d,'Pump',ctx)", "return r.map(x=>Object.assign(x,{anx:1}));}\n      if(!al&&d.Defined&&d.Defined!=='Self')return nao('quem');",
"return r.map(x=>Object.assign(x,{anx:1}));}\n      if(!al&&d.Defined&&d.Defined!=='Self'){const r=fgLembT(d,'Pump',ctx);if(r)return r;return nao('quem');}", 'troca'))
P.append(("{const r=fgLembT(d,'PutCounter',ctx);if(r)return r;}", "ty==='P1P1')return [{op:'cnt',n,al:'',anx:1}];if(!al&&d.Defined&&d.Defined!=='Self')return nao('quem');",
"ty==='P1P1')return [{op:'cnt',n,al:'',anx:1}];if(!al&&d.Defined&&d.Defined!=='Self'){if(ty==='P1P1'||ty==='M1M1'){const r=fgLembT(d,'PutCounter',ctx);if(r)return r;}return nao('quem');}", 'troca'))
P.append(("{const mV=String(d.Defined||'').match(/^Valid (.+YouCtrl.*)$/)", "if(!d.Defined||d.Defined==='Self')return [{op:'regen',al:''}];return nao('quem regenera');",
"if(!d.Defined||d.Defined==='Self')return [{op:'regen',al:''}];{const mV=String(d.Defined||'').match(/^Valid (.+YouCtrl.*)$/);if(mV&&fgSpecOk(mV[1],ctx))return [{op:'regen',al:'',vT:mV[1]}];const r=fgLembT(d,'Regenerate',ctx);if(r)return r;}return nao('quem regenera');", 'troca'))
P.append(("op:'ganhaJ'", "if(((d.Defined==='TriggeredCardController'?'You':d.Defined)||'You')!=='You'||al)return nao('quem ganha');",
"if(!d.Defined&&al==='target player')return [{op:'ganhaJ',n}];if(!d.Defined&&al==='target opponent')return [{op:'ganhaJ',n,so:1}];if(d.Defined==='Player'&&!al)return [{op:'ganhaJ',n,todos:1}];", 'antes'))
# execução: expande lembT/vT numa cópia por carta (fixT = a carta)
P.append(("if(s.lembT||s.vT){", "  let ult=it.ult0||'';for(let s of st){const si=st.indexOf(s);",
"\n    if(s.lembT||s.vT){const L=s.lembT?(it.lemb||[]).filter(c=>xExiste(c.k)):X.eu.campo.filter(c=>{try{return fgValid(c,s.vT,{eu:me,src:it.k||'',sv:{}});}catch(er){return false;}});st.splice(si+1,0,...L.map(c=>Object.assign({},s,{lembT:0,vT:'',al:'',fixT:c.k})));if(!L.length)feito.push(s.lembT?'nenhuma carta lembrada':'nenhuma carta sua');continue;}", 'depois'))
P.append(("t=pa?(it.al||[])[j++]:s.fixT?s.fixT:s.anx?", "const pa=xPrecisaAlvo(s),t=pa?(it.al||[])[j++]:s.anx?",
"const pa=xPrecisaAlvo(s),t=pa?(it.al||[])[j++]:s.fixT?s.fixT:s.anx?", 'troca'))
P.append(("case 'ganhaJ':", "      case 'ganhaDono':",
"""      case 'ganhaJ':{const q=Math.max(0,+n||0),vv=Object.keys(X.ops||{}).filter(u=>!xMorto(X.ops[u])),dar=u=>{if(u===me){X.eu.vida+=q;}else xEvia({op:'vida',d:q,para:u});xLog(`${it.nm}: ${u===me?'você':xNomeU(u)} ganhou ${q} de vida`);};
        if(s.todos){e.vida+=q;ev({op:'vida',d:q});feito.push(`cada jogador ganhou ${q} de vida`);break;}
        if(s.so&&vv.length===1){ev({op:'vida',d:q},vv[0]);feito.push(`${xNomeU(vv[0])} ganhou ${q} de vida`);break;}
        if(!s.so&&(XBOT||!vv.length)){e.vida+=q;feito.push(`você ganhou ${q} de vida`);break;}
        const R=(s.so?[]:[{k:me,rot:'Você',on:1}]).concat(vv.map(u=>({k:u,rot:xNomeU(u),on:0})));setTimeout(async()=>{const v=await xMarca(`${it.nm}: quem ganha ${q} de vida?`,R,1,1);dar((v&&v[0])||R[0].k);xSobe();xTudo();},300);feito.push(`escolha quem ganha ${q} de vida`);break;}
""", 'antes'))

# ---------- L5. Copiar a mágica do gatilho: com escolha de novos alvos, N cópias, sub-habilidade depois; copiar mágica alvo sem TargetType ----------
# Gorion, Ertha Jo, Chandra Hope's Beacon, Thurid, Genesis Storm, Double Stroke, Bygone Marvels, Jaya, Mischievous Quanar, Lutri, Rootha...
P.append(("const subOk=!d.SubAbility||!/Remembered|Copied|Imprinted", "    case 'CopySpellAbility':{if(d.Defined==='TriggeredSpellAbility'&&d.Controller==='You'&&!d.Amount&&!d.SubAbility&&!d.UnlessCost)return [{op:'copiaTS',opc:d.Optional==='True'?1:0}];",
"""    case 'CopySpellAbility':{if(d.Defined==='TriggeredSpellAbility'&&d.Controller==='You'&&!d.Amount&&!d.SubAbility&&!d.UnlessCost)return [{op:'copiaTS',opc:d.Optional==='True'?1:0}];
      {const subOk=!d.SubAbility||!/Remembered|Copied|Imprinted|Defined\\$ Targeted/.test(String((ctx.sv||{})[d.SubAbility]||''));if(d.Defined==='TriggeredSpellAbility'&&(!d.Controller||d.Controller==='You')&&!d.UnlessCost&&subOk&&!(d.Amount==='X'&&String((ctx.sv||{}).X||'').trim()==='Count$xPaid')){const n=d.Amount?N('Amount'):1;if(n!=null)return [{op:'copiaTS',opc:d.Optional==='True'?1:0,n}];}}""", 'troca'))
P.append(("xTempestade(c0,Math.max(1,+n||1)", "const c0=JSON.parse(JSON.stringify(p.c));setTimeout(()=>xTempestade(c0,1,xInfo(c0).tx,0,'cópia'),400);feito.push('copiou '+p.nm);break;}",
"const c0=JSON.parse(JSON.stringify(p.c)),nc=Math.max(1,+n||1);setTimeout(()=>xTempestade(c0,Math.max(1,+n||1),xInfo(c0).tx,0,'cópia'),400);feito.push('copiou '+p.nm+(nc>1?` ${nc} vezes`:''));break;}", 'troca'))
P.append(("(!d.TargetType&&/^(Instant|Sorcery)", "if(d.TargetType!=='Spell'||!d.ValidTgts||d.Defined||d.Amount||d.Controller)return nao('ação CopySpellAbility');",
"if((d.TargetType!=='Spell'&&!(!d.TargetType&&/^(Instant|Sorcery)(\\.YouCtrl)?(,(Instant|Sorcery)(\\.YouCtrl)?)*$/.test(d.ValidTgts||'')))||!d.ValidTgts||d.Defined||d.Amount||d.Controller)return nao('ação CopySpellAbility');", 'troca'))

# ---------- L6. "... a menos que você pague": devolver/sacrificar/virar/descartar/exilar do cemitério/moer, e custo numérico em SVar ----------
# Dromar's Cavern, The Gitrog Monster, Bog Elemental, Treacherous Vampire, Pillaging Horde, Fallow Wurm, Quickling, Rogue Elephant, Fettergeist, Deep Spawn...
P.append(("op:'pagaK',k", "  return nao('custo do oponente');}\n  const A=fgAlvo(d)",
"""  if(d.UnlessPayer==='You'){const uc=String(d.UnlessCost).trim();let k=null,m;
    if(m=uc.match(/^(Return|Sac|tapXType|Discard|ExileFromGrave)<(\\d+)\\/([^/>]+)(?:\\/[^>]*)?>$/)){const t={Return:'volta',Sac:'sac',tapXType:'tap',Discard:'desc',ExileFromGrave:'exiCem'}[m[1]];let v=m[3].replace(/;/g,',');if(t==='desc'&&v==='Random')k={t:'descR',n:+m[2]};else{if(v==='Hand')v='Card';if(/TopGraveyard/.test(v))v=null;if(v&&fgSpecOk(v,ctx))k={t,n:+m[2],v};}}
    else if(m=uc.match(/^Mill<(\\d+)>$/))k={t:'mill',n:+m[1]};
    else if(/^[A-Za-z]\\w*$/.test(uc)&&!/^[WUBRGC]$/.test(uc)){const n=fgConta(uc,ctx);if(typeof n==='number')k={t:'mana',c:'{'+n+'}'};}
    if(k&&(k.n==null||k.n>0)){const d2=Object.assign({},d);delete d2.UnlessCost;delete d2.UnlessPayer;delete d2.UnlessSwitched;const r=fgPasso0(d2,api,ctx);if(r.some(o=>o.op==='nao'))return r;const sw=d.UnlessSwitched==='True'?1:0;return k.t==='mana'?[{op:'pagaOu',c:k.c,sw,st:r}]:[{op:'pagaK',k,sw,st:r}];}}
""", 'antes'))
P.append(("case 'pagaK':", "      case 'escudo':{",
"""      case 'pagaK':{const K=s.k,res=st.slice(si+1),al2=(it.al||[]).slice(j),ok=c=>{try{return fgValid(c,K.v||'Card',{eu:me,src:it.k||'',sv:{}});}catch(er){return false;}};
        const Z=K.t==='desc'?e.mao:K.t==='exiCem'?e.cem:e.campo,C=(K.t==='descR'||K.t==='mill')?[]:Z.filter(c=>ok(c)&&(K.t!=='tap'||!c.tap));
        const pode=K.t==='mill'?e.bib.length>=K.n:K.t==='descR'?e.mao.length>=K.n:C.length>=K.n;
        const rot={volta:'devolver pra mão',sac:'sacrificar',tap:'virar',desc:'descartar',descR:'descartar ao acaso',exiCem:'exilar do cemitério',mill:'moer'}[K.t]+' '+K.n+(K.v&&K.v!=='Card'?' ('+K.v+')':'');
        const quer=pode&&(XBOT||confirm(`${it.nm}: ${rot}? (se não, ${s.sw?'o efeito não acontece':'acontece o efeito'})`));
        setTimeout(async()=>{if(quer){let L=[];if(K.t==='mill'){L=e.bib.splice(0,K.n);e.cem.push(...L);}else if(K.t==='descR'){for(let q=0;q<K.n&&e.mao.length;q++){const c=e.mao.splice(Math.floor(Math.random()*e.mao.length),1)[0];e.cem.push(c);L.push(c);}}
            else{if(C.length===K.n||XBOT)L=C.slice(0,K.n);else{const v=await xMarca(`${it.nm}: ${rot}`,C.map(c=>({k:c.k,rot:c.n,on:0})),K.n,K.n);L=(v||[]).map(k=>C.find(c=>c.k===k)).filter(Boolean);if(L.length<K.n)L=C.slice(0,K.n);}
              for(const c of L){if(K.t==='sac')xSai(c,'cem');else if(K.t==='volta')xSai(c,'mao');else if(K.t==='tap')c.tap=1;else{const Zc=K.t==='desc'?e.mao:e.cem,i=Zc.indexOf(c);if(i>=0){Zc.splice(i,1);(K.t==='desc'?e.cem:e.exi).push(c);}}}}
            xLog(`${it.nm}: ${rot}: ${L.map(c=>c.n).join(', ')||'feito'}`);}else xLog(`${it.nm}: não pagou (${rot})`);
          const r2=(quer===!!s.sw)?[...s.st,...res]:res;if(r2.length)xFazDepois(r2,Object.assign({},it,{al:quer===!!s.sw?al2:al2.slice(s.st.filter(xPrecisaAlvo).length)}));else{xSobe();xPintaEu();}},300);
        feito.push(quer?rot:'não paga: '+rot);xLog(`${it.nm} resolveu: ${feito.join(' · ')}`);return rest;}
""", 'antes'))

# ---------- L7. Conjurar da mão sem pagar, com filtro (Valid + ValidSA, valor de mana fixo ou X) ----------
# Sram's/Yahenni's Expertise, Electrodominance, Coveted Prize, West Coast Expansion, Yue, Brazen Bluff, I Am Duskmourn, Maelstrom Archangel...
P.append(("const fgSAv=", "    case 'Play':{if(d.TgtZone==='Graveyard'",
"""    case 'Play':{const fgSAv=x=>String(x||'Spell').split(',').map(a=>{a=a.trim();const j=a.indexOf('.'),t=j<0?a:a.slice(0,j),p=j<0?'':a.slice(j+1);return (t==='Spell'?'Card.nonLand':t)+(p?(t==='Spell'?'+':'.')+p:'');}).join(',');
      if(d.ValidZone==='Hand'&&d.WithoutManaCost==='True'&&d.Valid&&!d.Defined&&(!d.Amount||d.Amount==='1')&&(!d.Controller||d.Controller==='You')&&!Object.keys(d).some(k=>/^(PlayCost|ValidTgts|TgtZone|Condition|RememberPlayed|ReplaceGraveyard|PlayMadness)/.test(k))){const v=d.Valid,vs=fgSAv(d.ValidSA),t=vs.replace(/cmc(LE|LT|EQ|GE)X\\b/g,'cmc$10');
        if(/^Card(\\.[\\w+]+)?$/.test(v)&&fgSpecOk(v,ctx)&&fgSpecOk(t,ctx)&&!/cmc(LE|LT|EQ|GE)[A-WYZ]/.test(vs))return [{op:'maoJogaV',v,vs,opc:d.Optional==='True'?1:0}];}}
    case 'Play':{if(d.TgtZone==='Graveyard'""", 'troca'))
P.append(("case 'maoJogaV':", "      case 'maoJoga':{",
"""      case 'maoJogaV':{const vs=s.vs.replace(/cmc(LE|LT|EQ|GE)X\\b/g,'cmc$1'+(it.x||0)),ok=c=>{try{return fgValid(c,s.v,{eu:me,src:it.k||'',sv:{}})&&fgValid(c,vs,{eu:me,src:it.k||'',sv:{}});}catch(er){return false;}},L=e.mao.filter(ok);
        if(!L.length){feito.push('nenhuma carta da mão serve pra conjurar de graça');break;}
        setTimeout(async()=>{const k=XBOT?L[0].k:await xEscolhe(`${it.nm}: conjurar de graça uma carta da mão? (feche pra não conjurar)`,L.map(c=>({c,lado:'Mão'})));const c=L.find(q=>q.k===k);if(c&&e.mao.includes(c))await xGratis(c,'mao',0,it.nm);},300);
        feito.push('pode conjurar de graça uma carta da mão');break;}
""", 'antes'))

# ---------- L8. Contas: quantas das lembradas batem no filtro (Remembered$Valid), valor de mana do topo do grimório, quantas descartou ----------
# Waste Management, Necron Monolith, Sins of the Father, Selvala's Enforcer, Storm Fleet Negotiator, Interpret the Signs, Judge Unworthy, Book Devourer...
P.append(("function fgConta3(", "function fgQuemJ(df){",
"""function fgConta3(b,ctx,mods){let m;if(fgMods(1,mods||[])==null)return null;const md=mods||[];
  if(m=b.match(/^Remembered\\$Valid (.+)$/)){if(!fgSpecOk(m[1],ctx))return null;return {q:'remV',v:m[1],md};}
  if(b==='Count$TopOfLibraryCMC')return {q:'topoMV',md};
  if(b==='Discarded$Amount')return {q:'rem',md};
  return null;}
""", 'antes'))
P.append(("const n3=fgConta3(base,ctx,mods)", "if(n==null){const n2=fgConta2(base,ctx);if(n2!=null)n=n2;}",
"if(n==null){const n3=fgConta3(base,ctx,mods);if(n3!=null)return n3;}", 'depois'))
P.append(("v.q==='remV'?", ":v.q==='rem'?(it.lemb?it.lemb.length:(it.rem||0))",
":v.q==='remV'?(it.lemb||[]).filter(c=>{try{return fgValid(c,v.v,{eu:me,src:it.k||'',sv:{}});}catch(er){return false;}}).length:v.q==='topoMV'?(X.eu.bib[0]?xMVc(X.eu.bib[0]):0)", 'antes'))

# ---------- L9. Do cemitério pro grimório (topo, fundo, posição N ou embaralhar): a própria carta ou a do gatilho ----------
# Murderous Rider, Lembas, Purity, Hostility, Dark Revenant, Avenging Angel, Moss-Pit Skeleton, Gate Colossus, Vengeful Pharaoh, Bookwurm...
P.append(("op:'cemBib'", "      return nao((og||'?')+' → '+(ds||'?')+(al?' com alvo':''));}",
"""      if(og==='Graveyard'&&ds==='Library'&&!al&&(!d.Defined||/^(Self|TriggeredNewCardLKICopy|TriggeredCard(LKICopy)?)$/.test(d.Defined))&&!d.ChangeType&&!d.Hidden&&!d.Defined0){const pos=d.Shuffle==='True'?'emb':d.LibraryPosition==null?0:+d.LibraryPosition;if(pos==='emb'||Number.isInteger(pos))return [{op:'cemBib',pos,tk:/^Triggered/.test(d.Defined||'')?1:0}];}
""", 'antes'))
P.append(("case 'cemBib':", "      case 'escudo':{",
"""      case 'cemBib':{const k=s.tk?t:(it.k||''),c=e.cem.find(q=>q.k===k)||(s.tk?null:[...e.cem].reverse().find(q=>q.n===it.nm));if(!c){feito.push('a carta não está no cemitério');break;}e.cem.splice(e.cem.indexOf(c),1);
        if(s.pos==='emb'){e.bib.push(c);xEmb(e.bib);}else if(s.pos<0)e.bib.push(c);else e.bib.splice(Math.min(s.pos,e.bib.length),0,c);feito.push(`${c.n} foi ${s.pos==='emb'?'embaralhada no grimório':s.pos<0?'pro fundo do grimório':s.pos===0?'pro topo do grimório':'pra posição '+(s.pos+1)+' do grimório'}`);break;}
""", 'antes'))

# ---------- L10. Explorar (Explore): a própria criatura, a do gatilho ou uma alvo; N vezes ----------
# Ixalli's Diviner, Path of Discovery, Legion Vanguard, Jadelight Ranger, Miner's Guidewing, Over the Edge, Seasoned Dungeoneer...
P.append(("case 'Explore':{", "    case 'Cleanup':case 'StoreSVar':return [];",
"""    case 'Explore':{const n=d.Num?N('Num'):1;if(n==null)return nao('número');if(d.Defined&&!/^(Self|Targeted)$/.test(d.Defined))return nao('quem explora');if(al)return put({op:'explora',n,al},[]);if(d.ValidTgts)return nao('alvo');return [{op:'explora',n,al:'',si:1}];}
""", 'antes'))
P.append(("case 'explora':", "      case 'escudo':{",
"""      case 'explora':{const q=Math.max(0,+n||0),c=e.campo.find(z=>z.k===t),fx=[];for(let r=0;r<q;r++){const top=e.bib[0];if(!top){fx.push('grimório vazio');break;}
          if(xInfo(top).land){e.bib.shift();e.mao.push(top);fx.push(`revelou ${top.n} (terreno, foi pra mão)`);continue;}
          if(c)xEfCarta(c,'cnt',1);const cem=XBOT?true:confirm(`${it.nm}: explorou e revelou ${top.n}. Mandar pro cemitério? (Cancelar = fica no topo)`);if(cem){e.bib.shift();e.cem.push(top);}fx.push(`revelou ${top.n}${c?', +1/+1 em '+c.n:''}, ${cem?'foi pro cemitério':'ficou no topo'}`);}
        feito.push('explorou: '+fx.join(' · '));break;}
""", 'antes'))

# ---------- L11. Cara ou coroa (FlipCoin) com efeito de vitória e/ou derrota, sem alvo dentro ----------
# Tide of War, Planar Chaos, Stitch in Time, Mogg Assassin, Goblin Festival, Zndrsplt, Chaotic Goo...
P.append(("case 'FlipCoin':{", "    case 'Cleanup':case 'StoreSVar':return [];",
"""    case 'FlipCoin':{if(Object.keys(d).some(k=>!/^(DB|SP|AB|Cost|SpellDescription|StackDescription|WinSubAbility|LoseSubAbility|SubAbility|AILogic|Defined)$/.test(k))||(d.Defined&&d.Defined!=='You'))return nao('ação FlipCoin');
      const ld=nm=>{if(!nm)return [];const q=fgPP((ctx.sv||{})[nm]||'');return q.api?fgCadeia(q.d,q.api,ctx):[{op:'nao',d:nm}];},w=ld(d.WinSubAbility),l=ld(d.LoseSubAbility);
      if([...w,...l].some(o=>o.op==='nao'))return [...w,...l].filter(o=>o.op==='nao');if([...w,...l].some(o=>xPrecisaAlvo(o)))return nao('alvo dentro da moeda');return [{op:'moeda',w,l}];}
""", 'antes'))
P.append(("case 'moeda':", "      case 'escudo':{",
"""      case 'moeda':{const g=Math.random()<0.5;st.splice(si+1,0,...(g?s.w:s.l));feito.push(`jogou a moeda e ${g?'ganhou':'perdeu'}`);break;}
""", 'antes'))

# ---------- L12. Prevenir dano do/no alvo da parte anterior (Effect RememberObjects$ Targeted sem alvo próprio) ----------
# Maze of Ith, Maze of Shadows, Elvish Scout, Delirium, Foxfire, Djeru's Resolve, Glyph of Destruction, Energy Arc, Telekinesis...
P.append(("(d.RememberObjects==='Targeted'&&!d.ValidTgts))&&/Targeted/", "return d.RememberObjects==='Self'?'S':(al&&/Targeted/.test(d.RememberObjects||''))?'R':null;",
"return d.RememberObjects==='Self'?'S':((al||(d.RememberObjects==='Targeted'&&!d.ValidTgts))&&/Targeted/.test(d.RememberObjects||''))?'R':null;", 'troca'))
P.append(("mesmo:(a==='R'||b==='R')&&!al?1:0", "al:(a==='R'||b==='R')?al:''});continue;}",
"al:(a==='R'||b==='R')?al:'',mesmo:(a==='R'||b==='R')&&!al?1:0});continue;}", 'troca'))
P.append(("{op:'prevC',al:'',v:'',mesmo:1}", "if(!al||!/Targeted/.test(d.RememberObjects||'')){ok=false;break;}pv.push({op:'prevC',al,v:''});}",
"if(!/Targeted/.test(d.RememberObjects||'')||(!al&&(d.RememberObjects!=='Targeted'||d.ValidTgts))){ok=false;break;}pv.push(al?{op:'prevC',al,v:''}:{op:'prevC',al:'',v:'',mesmo:1});}", 'troca'))
P.append(("k:(s.al||s.mesmo)?(t||''):''", "k:s.al?(t||''):''", "k:(s.al||s.mesmo)?(t||''):''", 'troca'))

P.append(("feito.push((s.al||s.mesmo)?`dano de combate de", "feito.push(s.al?`dano de combate de ${xAlvoNome(t)} prevenido neste turno`", "feito.push((s.al||s.mesmo)?`dano de combate de ${xAlvoNome(t)} prevenido neste turno`", 'troca'))

# ---------- L13. Gatilhos de bloqueio: "Whenever this creature blocks" (ao confirmar os bloqueios), "becomes blocked" (lado do atacante), "attacks or blocks" ----------
# Cinder Wall, Fog Elemental, Clockwork Beetle, Sawtooth Ogre, Wall of Tears, Phantom Whelp, Kaijin..., atacantes com "becomes blocked"
P.append(("function xBlqGat(", "function xFrase(",
"""/* gatilhos de bloqueio. tc.tk = a criatura do outro lado (atacante bloqueado / primeira bloqueadora) */
const XBLQ=/^(?:[A-Za-z ]+ — )?(?:When|Whenever) this (?:card|creature) (?:attacks or )?blocks(?: or becomes blocked)?(?: (?:a|by a) creature)?, ([^\\n]+)$/im,XFBL=/^(?:[A-Za-z ]+ — )?(?:When|Whenever) this (?:card|creature) (?:blocks or )?becomes blocked(?: by (?:a|one or more) creatures?)?, ([^\\n]+)$/im;
function xBlqMeus(at){const e=X.eu,s=X.sala||{};for(const b of e.campo.filter(c=>c.bl&&at.some(q=>q.k===c.bl))){const a=at.find(q=>q.k===b.bl),m=xNorm(xInfo(b).tx||'',b.n).match(XBLQ);if(m)setTimeout(()=>xGatTx(b,m[1],'bloqueou',Object.assign({},xTc(a)||{},{tk:a.k,tku:s.vez})),300);}}
function xBlqGat(){const B=xOpCampos().flatMap(([cp,u])=>cp.filter(c=>c.bl).map(c=>({c,u})));for(const a of X.eu.campo.filter(c=>c.atk)){const bs=B.filter(b=>b.c.bl===a.k);if(!bs.length)continue;const tx=xNorm(xInfo(a).tx||'',a.n),m=tx.match(XFBL)||(/blocks or becomes blocked/i.test(tx)?tx.match(XBLQ):null);if(m)setTimeout(()=>xGatTx(a,m[1],'foi bloqueada',Object.assign({},xTc(bs[0].c)||{},{tk:bs[0].c.k,tku:bs[0].u})),300);}}
""", 'antes'))
P.append(("xBlqMeus(at);", "    const bq=[...(s.bq||[]),me];s.bq=bq;xSala((s.def||[me]).every(",
"    xBlqMeus(at);\n", 'antes'))
P.append(("X.__blqF!==", "  if(s.cb==='blq'&&s.vez===me&&s.def&&s.def.every(u=>(s.bq||[]).includes(u)||xMorto(xPub(u)))&&X.dzF!==s.turno){X.dzF=s.turno;xSala({cb:'dano'});}",
"\n  if(s.cb==='dano'&&s.vez===me&&X.__blqF!==s.turno+'.'+((s.cbX||{}).n||0)){X.__blqF=s.turno+'.'+((s.cbX||{}).n||0);setTimeout(xBlqGat,250);}", 'depois'))
P.append(("(?:When|Whenever) this (?:card|creature) (?:enters(?: the battlefield)? or )?attacks(?: or blocks)?", "Whenever this (?:card|creature) (?:enters(?: the battlefield)? or )?attacks( while saddled)?, ([^\\n]+)$/im", "(?:When|Whenever) this (?:card|creature) (?:enters(?: the battlefield)? or )?attacks(?: or blocks)?( while saddled)?, ([^\\n]+)$/im", 'troca'))

# ---------- L14. SacrificeAll: a própria carta, as lembradas, ou todas as suas que batem no filtro ----------
# Fog Elemental, Mardu Blazebringer, Dorothea, Time Elemental, Doom Foretold, Callous Sell-Sword, Professor Onyx, Rite of Ruin, Death Pit Offering...
P.append(("case 'SacrificeAll':{", "    case 'Cleanup':case 'StoreSVar':return [];",
"""    case 'SacrificeAll':{if(Object.keys(d).some(k=>/^(Remember|Imprint|Condition|Unless)/.test(k)&&k!=='RememberSacrificed'))return nao('ação SacrificeAll');if(d.Controller&&d.Controller!=='You')return nao('quem sacrifica');
      if(d.Defined==='Self'&&!d.ValidCards)return [{op:'sacrEsta'}];if(/^Remembered(LKI)?$/.test(d.Defined||'')&&!d.ValidCards)return [{op:'sacL',v:''}];
      if(!d.Defined&&d.ValidCards){const m=String(d.ValidCards).match(/^(Card|Creature|Artifact|Permanent|Land|Enchantment)\\.IsRemembered$/);if(m)return [{op:'sacL',v:m[1]==='Card'?'':m[1]}];const v=String(d.ValidCards);if(/YouCtrl/.test(v)&&!/OppCtrl|Remembered|Chosen|Targeted|Triggered/.test(v)&&fgSpecOk(v,ctx))return [{op:'sacV',v}];}
      return nao('ação SacrificeAll');}
""", 'antes'))
P.append(("case 'sacL':", "      case 'sacrEsta':{",
"""      case 'sacL':case 'sacV':{const L=s.op==='sacL'?e.campo.filter(c=>(it.lemb||[]).some(q=>q.k===c.k)&&(!s.v||fgValid(c,s.v,{eu:me,src:it.k||'',sv:{}}))):e.campo.filter(c=>{try{return fgValid(c,s.v,{eu:me,src:it.k||'',sv:{}});}catch(er){return false;}});
        L.forEach(c=>xMorre(c));feito.push(L.length?'sacrificou '+L.map(c=>c.n).join(', '):'nada pra sacrificar');break;}
""", 'antes'))

# ---------- L15. Adaptar N (só se não tem +1/+1) e Reforçar N (na sua criatura de menor resistência) ----------
# Pteramander, Zegana, Incubation Druid, Growth-Chamber Guardian, Biogenic Ooze? (Adapt); Abzan Skyarch, Dromoka's Gift, Elite Scaleguard (Bolster)...
P.append(("if(d.Adapt!=null){", "if(!d.CounterType)return nao('tipo de marcador');",
"if(d.Adapt!=null){const m=N('Adapt');if(m==null)return nao('número');if(d.Defined&&d.Defined!=='Self')return nao('quem');return [{op:'adapt',n:m}];}if(d.Bolster!=null){const m=N('Bolster');if(m==null)return nao('número');return [{op:'bolster',n:m}];}", 'antes'))
P.append(("case 'adapt':", "      case 'sacrEsta':{",
"""      case 'adapt':{const c=e.campo.find(q=>q.k===it.k),q=Math.max(0,+n||0);if(!c){feito.push('a criatura saiu');break;}if((c.cnt||0)>0){feito.push(`${c.n} já tem marcador +1/+1, não adaptou`);break;}xEfCarta(c,'cnt',q);feito.push(`${c.n} adaptou ${q}`);break;}
      case 'bolster':{const q=Math.max(0,+n||0),C=e.campo.filter(c=>xCri(c));if(!C.length){feito.push('nenhuma criatura pra reforçar');break;}const mn=Math.min(...C.map(c=>xPT(c).t)),L=C.filter(c=>xPT(c).t===mn);
        if(L.length===1||XBOT){xEfCarta(L[0],'cnt',q);feito.push(`reforçar ${q}: ${L[0].n}`);break;}
        setTimeout(async()=>{const k=await xEscolhe(`${it.nm}: reforçar ${q} em qual (resistência ${mn})?`,L.map(c=>({c,lado:'Campo'})));const c=L.find(z=>z.k===k)||L[0];xEfCarta(c,'cnt',q);xLog(`${it.nm}: reforçar ${q} em ${c.n}`);xSobe();xPintaEu();},300);feito.push(`reforçar ${q}`);break;}
""", 'antes'))

# ---------- L16. Perder habilidade até o fim do turno (Debuff): c.kD = {t: turno, kw: [...]}, tirado no xPT ----------
# Grozoth, Gargoyle Sentinel, Tidewater Minion, Emerald Charm, Vertigo, Gravity Well, Soul Sear, Smite the Deathless, Canopy Dragon, Crash Landing...
P.append(("c.kD&&c.kD.t===", "  return {p,t,kw,pz,mod:p!==i.p||t!==i.t};}",
"  if(c.kD&&c.kD.t===((X.sala||{}).turno||0))for(const x of c.kD.kw)kw.delete(x);\n", 'antes'))
P.append(("op==='debuff'){", "  else if(op==='vira')c.tap=1;else if(op==='desvira')c.tap=0;",
"  else if(op==='debuff'){const tn=(X.sala||{}).turno||0;if(!c.kD||c.kD.t!==tn)c.kD={t:tn,kw:[]};c.kD.kw=[...new Set([...c.kD.kw,...((x||{}).kw||[])])];}\n", 'antes'))
P.append(("case 'Debuff':{", "    case 'Cleanup':case 'StoreSVar':return [];",
"""    case 'Debuff':{if(d.Duration&&d.Duration!=='UntilEndOfTurn')return nao('duração');const ks=String(d.Keywords||'').split(' & ').filter(Boolean),kw=ks.map(k=>FGKW[k]);if(!ks.length||kw.some(x=>!x))return nao('habilidade perdida');
      if(al)return put({op:'debuff',kw,al},[]);if(d.ValidTgts)return nao('alvo');if(d.Defined&&d.Defined!=='Self')return nao('quem');return [d.Defined==='Self'?{op:'debuff',kw,al:'',si:1}:{op:'debuff',kw,al:''}];}
""", 'antes'))
P.append(("case 'debuff':", "      case 'sacrEsta':{",
"""      case 'debuff':{const k=t||it.k;if(!k){feito.push('sem a criatura');break;}xNoAlvo(k,'debuff',0,ev,{kw:s.kw});feito.push(`${xAlvoNome(k)} perdeu ${s.kw.join(', ')} até o fim do turno`);break;}
""", 'antes'))

# ---------- L17. "Não pode ser bloqueada neste turno" via Effect: a própria (RememberObjects Self), o alvo da parte anterior, o atacante do gatilho, todas as suas ----------
# Dreadlight Monstrosity, Creeping Tar Pit, Border Guardian, Agent of Horizons, Blitzball Stadium, Kiora of Salt and Sand, Trygon Prime, Glaring Spotlight, Keeper of Keys...
P.append(("ro==='Self'){o.push({op:'kt',al:'',kw:'unblockable',si:1})", "if(/IsRemembered/.test(va)&&al){o.push({op:'kt',al,kw:'unblockable'});continue;}",
"if(/IsRemembered/.test(va)&&!al){const ro=d.RememberObjects||'';if(ro==='Self'){o.push({op:'kt',al:'',kw:'unblockable',si:1});continue;}if((ro==='Targeted'&&!d.ValidTgts)||ro==='ParentTarget'){o.push({op:'kt',al:'',kw:'unblockable',mesmo:1});continue;}if(/^TriggeredAttacker(LKICopy)?$/.test(ro)){o.push({op:'kt',al:'',kw:'unblockable',tk:1});continue;}}if(va==='Creature.YouCtrl'){o.push({op:'pumpTodos',p:0,t:0,kw:['unblockable'],v:'Creature.YouCtrl'});continue;}", 'depois'))

# ---------- L18. Estáticas de Effect na própria carta até o fim do turno (UntilHostLeavesPlayOrEOT): pode atacar com defensor, não causa dano de combate ----------
# Wall of Wonder, Walking Wall, Mobile Fort, Mirror Wall, Kozilek's Pathfinder, Spin Engine, Laccolith Whelp/Warrior, Farrel's Zealot, Tin Street Dodger...
P.append(("(md==='CanAttackDefender'||md==='AssignNoCombatDamage')", "        if(du&&du!=='UntilEndOfCombat')return nao('duração '+du);",
"""        if((md==='CanAttackDefender'||md==='AssignNoCombatDamage')&&/^(Card|Creature)\\.(Self|EffectSource)$/.test(st.ValidCard||'')&&(!du||du==='UntilHostLeavesPlayOrEOT')&&!al&&Object.keys(st).every(k=>/^(Mode|ValidCard|Description|EffectZone)$/.test(k))){o.push(md==='CanAttackDefender'?{op:'debuff',kw:['defender'],al:'',si:1}:{op:'semDanoC'});continue;}
        if(du==='UntilHostLeavesPlayOrEOT'&&!al&&/EffectSource/.test(st.ValidAttacker||st.ValidCard||st.Affected||'')&&!/IsRemembered|Other/.test(st.ValidAttacker||st.ValidCard||st.Affected||'')){}else
""", 'antes'))
P.append(("c.nCD===(s.turno||0)", "P:pvOk(c,u)?0:Math.max(0,v.p)", "P:(pvOk(c,u)||c.nCD===(s.turno||0))?0:Math.max(0,v.p)", 'troca'))
P.append(("case 'semDanoC':", "      case 'sacrEsta':{",
"""      case 'semDanoC':{const c=e.campo.find(q=>q.k===it.k);if(!c){feito.push('a criatura saiu');break;}c.nCD=(X.sala||{}).turno||0;feito.push(`${c.n} não causa dano de combate neste turno`);break;}
""", 'antes'))

# ---------- L19. Terrenos adicionais: "play an additional land on each of your turns" (Azusa, Exploration, Oracle of Mul Daya...) e AdjustLandPlays neste turno (Effect) ----------
# Explore, Growth Spiral, Journey of Discovery, Summer Bloom, Azusa's Many Journeys, This World Belongs to Me, Way of the Paradox... + estáticas Azusa, Exploration, Dryad of the Ilysian Grove
P.append(("function xTerMax(", "function xFimJogo(s,me){",
"""/* quantos terrenos pode jogar neste turno: 1 + estáticas "additional land(s) on each of your turns" + efeito deste turno (e.terX) */
function xTerMax(){const e=X.eu,t=(X.sala||{}).turno||0,W={an:1,one:1,two:2,three:3};let n=1+((e&&e.terX&&e.terX.t===t)?e.terX.n:0);for(const c of (e&&e.campo)||[]){if(c.tok&&!c.cp)continue;const m=xNorm(xInfo(c).tx||'',c.n).match(/You may play (an|one|two|three) additional lands? on each of your turns/i);if(m)n+=W[m[1].toLowerCase()];}return n;}
""", 'antes'))
P.append(("if(e.ter>=xTerMax())return xAv('Você já jogou", "if(e.ter>=1)return xAv('Você já jogou um terreno neste turno.')", "if(e.ter>=xTerMax())return xAv('Você já jogou os terrenos que pode neste turno.')", 'troca'))
P.append(("ok=!xPode({inst:0})&&!(e.ter>=xTerMax())", "ok=!xPode({inst:0})&&!(e.ter>=1)", "ok=!xPode({inst:0})&&!(e.ter>=xTerMax())", 'troca'))
P.append(("    if(e.ter<xTerMax()){", "    if(e.ter<1){const ts=e.mao.filter(", "    if(e.ter<xTerMax()){const ts=e.mao.filter(", 'troca'))
P.append(("(st.AdjustLandPlays||'')&&!du", "        if(md==='CantBlockBy'&&st.ValidBlocker==='Creature.withoutHaste'",
"""        if(md==='Continuous'&&st.Affected==='You'&&/^\\d+$/.test(st.AdjustLandPlays||'')&&!du&&Object.keys(st).every(k=>/^(Mode|Affected|AdjustLandPlays|Description|EffectZone)$/.test(k))){o.push({op:'terX',n:+st.AdjustLandPlays});continue;}
""", 'antes'))
P.append(("case 'terX':", "      case 'sacrEsta':{",
"""      case 'terX':{const tn=(X.sala||{}).turno||0;if(!e.terX||e.terX.t!==tn)e.terX={t:tn,n:0};e.terX.n+=s.n;feito.push(`pode jogar ${s.n} terreno${s.n>1?'s':''} adicional${s.n>1?'is':''} neste turno`);break;}
""", 'antes'))

# ---------- L20. "Não pode ser regenerada neste turno" (Effect CantRegenerate): alvo da parte anterior, alvo próprio, a própria ----------
# Carbonize, Disintegrate, Scorching Lava, Gravebind, Orcish Healer, Furnace Brood, Whippoorwill, Engulfing Flames, Clergy/Knight of the Holy Nimbus
P.append(("md==='CantRegenerate'&&", "        if(md==='CantBlockBy'&&st.ValidBlocker==='Creature.withoutHaste'",
"""        if(md==='CantRegenerate'&&/^Card\\.IsRemembered$/.test(st.ValidCard||'')&&!du&&Object.keys(st).every(k=>/^(Mode|ValidCard|Description|EffectZone)$/.test(k))){const ro=d.RememberObjects||'';if(ro==='Self'&&!al){o.push({op:'nRegen',al:'',si:1});continue;}if(ro==='Targeted'&&al){o.push({op:'nRegen',al});continue;}if(!al&&(ro==='ParentTarget'||ro==='Targeted')){o.push({op:'nRegen',al:'',mesmo:1});continue;}}
""", 'antes'))
P.append(("op==='nRegen')", "  else if(op==='vira')c.tap=1;else if(op==='desvira')c.tap=0;",
"  else if(op==='nRegen')c.nRg=(X.sala||{}).turno||0;\n", 'antes'))
P.append(("&&!xUmbra(c)){if(c.regen&&c.nRg!==", "&&!xUmbra(c)){if(c.regen){c.regen=0;", "&&!xUmbra(c)){if(c.regen&&c.nRg!==((X.sala||{}).turno||0)){c.regen=0;", 'troca'))
P.append(("op==='destroiF'){if(c.regen&&c.nRg!==", "op==='destroiF'){if(c.regen){", "op==='destroiF'){if(c.regen&&c.nRg!==((X.sala||{}).turno||0)){", 'troca'))
P.append(("case 'nRegen':", "      case 'sacrEsta':{",
"""      case 'nRegen':{const k=t||it.k;if(!k){feito.push('sem a criatura');break;}xNoAlvo(k,'nRegen',0,ev);feito.push(`${xAlvoNome(k)} não pode ser regenerada neste turno`);break;}
""", 'antes'))

# ---------- L21. Contas: Compare com lado que só se sabe na hora (antes escolhia o "senão" calado) e resultados que são SVar; alvo bate no filtro (Targeted$Valid); vida do jogador-alvo; vida inicial ----------
# Bring Low, Ray of Enfeeblement, Lithomantic Barrage, Cut Propulsion, Twenty-Toed Toad, Blood Lust, Shatterskull Smashing, Crater's Claws, Blood Tribute, Oketra's Last Mercy...
P.append(("(-?\\d+|[A-Za-z]\\w*)\\.(-?\\d+|[A-Za-z]\\w*)\\.(-?\\d+|[A-Za-z]\\w*)$/)){",
"""else if(m=base.match(/^Count\\$Compare (\\w+) (GE|GT|LE|LT|EQ|NE)(\\d+)\\.(\\d+)\\.(\\d+)$/)){const a=fgConta(m[1],ctx,(fundo||0)+1);if(a==null)return null;n=fgCmp(a,m[2]+m[3])?+m[4]:+m[5];}""",
"""else if(m=base.match(/^Count\\$Compare (\\w+) (GE|GT|LE|LT|EQ|NE)(-?\\d+|[A-Za-z]\\w*)\\.(-?\\d+|[A-Za-z]\\w*)\\.(-?\\d+|[A-Za-z]\\w*)$/)){const F=q=>{const r=/^-?\\d+$/.test(q)?+q:fgConta(q,ctx,(fundo||0)+1);return r==='X'?{q:'X'}:r;};const a=F(m[1]),c=F(m[3]),x=F(m[4]),y=F(m[5]);if([a,c,x,y].some(q=>q==null))return null;
    if([a,c,x,y].every(q=>typeof q==='number'))n=fgCmp(a,m[2]+c)?x:y;else{if(fgMods(1,mods)==null)return null;return {q:'cmp',a,o:m[2],c,x,y,md:mods};}}""", 'troca'))
P.append(("b.match(/^Targeted\\$Valid (.+)$/)", "  if(b==='Count$TopOfLibraryCMC')return {q:'topoMV',md};",
"""  if(m=b.match(/^Targeted\\$Valid (.+)$/)){if(!fgSpecOk(m[1],ctx))return null;return {q:'tgV',v:m[1],md};}
  if(b==='TargetedPlayer$LifeTotal')return {q:'tpVida',md};
  if(b==='Count$YourStartingLife')return 20;
""", 'antes'))
P.append(("v.q==='cmp'?", ":v.q==='remV'?",
""":v.q==='cmp'?(()=>{const a=rv(v.a),c=rv(v.c);return fgCmp(a,v.o+c)?rv(v.x):rv(v.y);})():v.q==='tgV'?(()=>{const c=(it.al||[]).map(k=>typeof k==='string'&&xAchaK(k)).find(Boolean);if(!c)return 0;try{return fgValid(c,v.v,{eu:xDonoK(c.k)||me,src:it.k||'',sv:{}})?1:0;}catch(er){return 0;}})():v.q==='tpVida'?(()=>{const P=(it.al||[]).find(a=>String(a).startsWith('P:'));if(!P)return 0;const u=P.slice(2);return u===xUid()?X.eu.vida:(((X.ops||{})[u]||{}).vida||0);})()""", 'antes'))

# ---------- L22. Contas do turno: Landfall (terreno seu entrou neste turno) e "quantas X morreram neste turno" com filtro (lista xTT().morL) ----------
# Rest for the Weary, Tomb Hex, Mysteries of the Deep, Liliana's Standard Bearer, Season of Loss, Body Count, Caller of the Claw, Gadrak, Ember-Fist/Floating-Dream/Dripping-Tongue Zubera
P.append(("(xTT().morL=xTT().morL||[]).push({c,eu:1})", "if(i.cri){xTT().mor++;", "if(i.cri){xTT().mor++;(xTT().morL=xTT().morL||[]).push({c,eu:1});", 'troca'))
P.append(("(xTT().morL=xTT().morL||[]).push({c:(()=>", "else if(v.op==='morreu'&&(xTT().mor++,1))",
"else if(v.op==='morreu'&&(xTT().mor++,(xTT().morL=xTT().morL||[]).push({c:(()=>{try{return Object.assign(xCarta(v.n),{k:v.k,tok:v.tok});}catch(er){return {n:v.n,k:v.k,tok:v.tok};}})(),eu:0}),1))", 'troca'))
P.append(("b.match(/^Count\\$Landfall\\.", "  if(b==='Count$TopOfLibraryCMC')return {q:'topoMV',md};",
"""  if(m=b.match(/^Count\\$Landfall\\.(\\d+)\\.(\\d+)$/))return fgMods(xTT().ent.some(c=>xInfo(c).land)?+m[1]:+m[2],md);
  if(m=b.match(/^Count\\$ThisTurnEntered_Graveyard_from_Battlefield_(.+)$/)){const v=m[1];if(/OppCtrl|Opp|Remembered|Targeted|Triggered|Chosen/.test(v))return null;const so=/YouCtrl|YouOwn/.test(v),v2=v.replace(/[.+](YouCtrl|YouOwn)\\b/g,'');if(!fgSpecOk(v2,ctx))return null;
    const L=(xTT().morL||[]).filter(z=>!so||z.eu);return fgMods(L.filter(z=>{try{return fgValid(z.c,v2,ctx);}catch(er){return false;}}).length,md);}
""", 'antes'))

# ---------- L23. Exilar a própria carta e devolver (pode voltar transformada / virada): Flickering Spirit, Dion, sagas que viram criatura (Fable of the Mirror-Breaker, Era of Enlightenment, Jugan Defends the Temple...) ----------
# self blink com RememberChanged + DBReturn Defined Remembered Exile→Battlefield (Transformed/Tapped/GainControl)
P.append(("/* exila e volta a própria */", "    case 'ChangeZone':{",
"""    case 'ChangeZone':/* exila e volta a própria */if(d.Origin==='Battlefield'&&d.Destination==='Exile'&&!al&&!d.Defined&&!d.ChangeType&&d.RememberChanged==='True'&&d.SubAbility){const sb=fgPP((ctx.sv||{})[d.SubAbility]||'');const sd=sb.d||{};
      if(sb.api==='ChangeZone'&&sd.Defined==='Remembered'&&sd.Origin==='Exile'&&sd.Destination==='Battlefield'&&Object.keys(sd).every(k=>/^(DB|Defined|Origin|Destination|Transformed|Tapped|GainControl|ForgetOtherRemembered|SubAbility|StackDescription|SpellDescription)$/.test(k))){const sb2=sd.SubAbility?fgPP((ctx.sv||{})[sd.SubAbility]||''):null;
        if(!sb2||(sb2.api==='Cleanup'&&!sb2.d.SubAbility)){ctx.pula=[...(Array.isArray(ctx.pula)?ctx.pula:ctx.pula?[ctx.pula]:[]),d.SubAbility,sd.SubAbility].filter(Boolean);return [{op:'piscaS',tf:sd.Transformed==='True'?1:0,tap:sd.Tapped==='True'?1:0}];}}}
""", 'antes'))
P.append(("if(x&&x.tf)c.face=c.face?0:1;", "c.sk=xInfo(c).cri?1:0;e.campo.push(c);xLog(c.n+' foi exilada e voltou pro campo');",
"if(x&&x.tf)c.face=c.face?0:1;if(x&&x.tap)c.tap=1;if(x&&x.tf)delete c.mk;", 'antes'))
P.append(("case 'piscaS':", "      case 'sacrEsta':{",
"""      case 'piscaS':{const c=e.campo.find(q=>q.k===it.k);if(!c){feito.push('a carta já saiu do campo');break;}xEfCarta(c,'pisca',0,{tf:s.tf,tap:s.tap});feito.push(`exilou e devolveu ${c.n}${s.tf?' transformada':''}`);break;}
""", 'antes'))

# ---------- L24. Destroy da criatura do gatilho (TriggeredTarget = quem levou o dano) e NoRegen nos Defined gerais; o gatilho "deals damage to a creature" agora passa a criatura ----------
# Voracious Cobra, Sporogenic Infection, Death Pits of Rath, Toxin Sliver, Phage the Untouchable, Cosmic Horror, Aether Storm, Creepy Doll...
P.append(("/* Destroy: TriggeredTarget e NoRegen */", "    case 'Destroy':if(!al&&!d.__m){",
"""    case 'Destroy':/* Destroy: TriggeredTarget e NoRegen */if(!al&&!d.__m&&!Object.keys(d).some(k=>/^(Unless|Condition|Remember)/.test(k))&&(!d.NoRegen||/^(True|False)$/.test(d.NoRegen))){const df=d.Defined||'';
      const o=df==='Self'?{al:'',si:1}:(df==='Enchanted'||df==='Equipped')?{al:'',anx:1}:/^Triggered(Card|Attacker|Source|Object|Target)(LKICopy)?$/.test(df)?{al:'',tk:1}:(df==='Targeted'||df==='ParentTarget')?{al:'',mesmo:1}:null;
      if(o&&(d.NoRegen==='True'||/^TriggeredTarget/.test(df)))return [...(d.NoRegen==='True'?[Object.assign({op:'nRegen'},o)]:[]),Object.assign({op:'destroi'},o)];}
""", 'antes'))
P.append(("xGatTx(a.c,m[2],'dano em criatura',", "else setTimeout(()=>xGatTx(a.c,m[2],'dano em criatura'),500);}",
"else setTimeout(()=>xGatTx(a.c,m[2],'dano em criatura',Object.assign({},xTc(t.c),{tk:t.c.k,tku:t.u})),500);}", 'troca'))

# ---------- L25. Seek (Alchemy): N cartas aleatórias do grimório que batem no filtro vão pra mão ----------
# Oasis of Renewal, Surge of Acclaim, Gate to Seatower, Soulstealer Axe, Blightwing Whelp, Frenzied Geistblaster, Excogitator Sphinx, Skyshroud Lookout, Hollowhenge Wrangler...
P.append(("case 'Seek':{", "    case 'Cleanup':case 'StoreSVar':return [];",
"""    case 'Seek':{if(d.Destination&&d.Destination!=='Hand')return nao('Seek pra outra zona');if(Object.keys(d).some(k=>/^(Remember|Imprint|Condition|Unless|Defined|Optional)/.test(k)))return nao('ação Seek');
      let v=String(d.Type||'Card'),ok=true;v=v.replace(/(cmc|power|toughness)(EQ|LE|GE|LT|GT|NE)([A-Za-z]\\w*)/g,(m0,a,b,c)=>{const q=fgConta(c,ctx);if(typeof q!=='number'){ok=false;return m0;}return a+b+q;});
      if(!ok||/MostProminent|Chosen|Remembered|Triggered|Targeted/.test(v)||!fgSpecOk(v,ctx))return nao('filtro do Seek');const n=d.Num==null?1:N('Num');if(n==null)return nao('número');return [{op:'seek',v,n}];}
""", 'antes'))
P.append(("case 'seek':", "      case 'sacrEsta':{",
"""      case 'seek':{const q=Math.max(0,+n||0),L=e.bib.filter(c=>{try{return fgValid(c,s.v,{eu:me,src:it.k||'',sv:{}});}catch(er){return false;}}),P=[];
        for(let z=0;z<q&&L.length;z++){const c=L.splice(Math.floor(Math.random()*L.length),1)[0];e.bib.splice(e.bib.indexOf(c),1);e.mao.push(c);P.push(c.n);}
        feito.push(P.length?`buscou (seek) ${P.join(', ')}`:'seek: nenhuma carta assim no grimório');break;}
""", 'antes'))

# ---------- L26. Olhar/revelar o topo (PeekAndReveal) lembrando a carta, e as partes seguintes: "se a lembrada é X" e mover a lembrada do grimório ----------
# Mudbutton Clanger, Kithkin Zephyrnaut, Plane-Merge Elf, Wolf-Skull Shaman, Risen Reef, Skyclave Aerialist, Brutal/Callous/Feral Deceiver, Bucolic Ranch, Squeaking Pie Grubfellows...
P.append(("/* olhar o topo lembrando */", "    case 'PeekAndReveal':{const n=N('PeekAmount')||1,",
"""    case 'PeekAndReveal':/* olhar o topo lembrando */if(!ctx.__pk){ctx.__pk=1;let r0;try{r0=fgPasso0(d,api,ctx);}finally{delete ctx.__pk;}if(!r0.some(o=>o.op==='nao'))return r0;}{const sb=d.SubAbility&&fgPP((ctx.sv||{})[d.SubAbility]||'');if(!ctx.__pk&&(d.RememberRevealed||d.RememberPeeked)&&!(sb&&/^(Repeat|TwoPiles)$/.test(sb.api))&&(!d.Defined||d.Defined==='You')&&Object.keys(d).every(k=>/^(DB|AB|SP|PeekAmount|NoReveal|RememberRevealed|RememberPeeked|RevealValid|RevealOptional|Defined|SubAbility|SpellDescription|StackDescription|AILogic|Cost|ActivationLimit|PrecostDesc|SorcerySpeed)$/.test(k))){
      const n=d.PeekAmount==null?1:N('PeekAmount'),v=d.RevealValid||'';if((typeof n==='number'||n==='X')&&!(v&&(/Chosen|Remembered|Triggered|Targeted/.test(v)||!fgSpecOk(v,ctx)))){ctx.peekL=1;
      return [{op:'peek',n,v,nr:d.NoReveal==='True'&&!d.RememberRevealed?1:0,opc:d.RevealOptional==='True'?1:0}];}}}
""", 'antes'))
P.append(("/* depois de olhar o topo: lembradas */", "o.mesmo=1;return r;}return fgPasso0(d,api,ctx);}",
"""o.mesmo=1;return r;}{const r=fgPasso0(d,api,ctx);if(!ctx.peekL||!r.some(o=>o.op==='nao'))return r;/* depois de olhar o topo: lembradas */
    const ck=Object.keys(d).filter(k=>k.startsWith('Condition'));
    if(ck.length&&d.ConditionDefined==='Remembered'&&ck.every(k=>['ConditionDefined','ConditionPresent','ConditionCompare','ConditionDescription'].includes(k))&&fgSpecOk(d.ConditionPresent||'Card',ctx)&&fgCmp(0,d.ConditionCompare||'GE1')!==null){const d2=Object.assign({},d);for(const k of ck)delete d2[k];delete d2.SubAbility;const r2=fgPasso(d2,api,ctx);if(r2.some(o=>o.op==='nao'))return r2;return [{op:'se',d:'n',q:{q:'remV',v:d.ConditionPresent||'Card',md:[]},cmp:d.ConditionCompare||'GE1',st:r2}];}
    if(!ck.length&&api==='ChangeZone'&&d.Origin==='Library'&&/^(Remembered|TopOfLibrary)$/.test(d.Defined||'')&&{Hand:1,Battlefield:1,Graveyard:1,Exile:1}[d.Destination]&&Object.keys(d).every(k=>/^(DB|Defined|Origin|Destination|Optional|ForgetChanged|Tapped|SubAbility|SpellDescription|StackDescription)$/.test(k)))
      return [{op:'lembZ',z:{Hand:'mao',Battlefield:'campo',Graveyard:'cem',Exile:'exi'}[d.Destination],topo:d.Defined==='TopOfLibrary'?1:0,tap:d.Tapped==='True'?1:0,opc:d.Optional==='True'?1:0,fg:d.ForgetChanged==='True'?1:0}];
    return r;}}""", 'troca'))
P.append(("case 'peek':", "      case 'sacrEsta':{",
"""      case 'peek':{const q=Math.max(0,+n||0),T=e.bib.slice(0,q);let L=T;if(!s.nr){L=s.v?T.filter(c=>{try{return fgValid(c,s.v,{eu:me,src:it.k||'',sv:{}});}catch(er){return false;}}):T;if(L.length&&s.opc&&!XBOT&&!confirm(`${it.nm}: revelar ${L.map(c=>c.n).join(', ')} do topo?`))L=[];}
        it.lemb=L.slice();if(s.nr){if(T.length&&!XBOT)xAv(`${it.nm}: o topo do seu grimório é ${T.map(c=>c.n).join(', ')}`);feito.push(T.length?'olhou o topo do grimório':'grimório vazio');}else feito.push(L.length?`revelou ${L.map(c=>c.n).join(', ')} do topo`:'não revelou nada');break;}
      case 'lembZ':{const L=s.topo?e.bib.slice(0,1):(it.lemb||[]).filter(c=>e.bib.includes(c)),M=[];for(const c of L){if(s.opc&&!XBOT&&!confirm(`${it.nm}: pôr ${c.n} ${{mao:'na mão',campo:'no campo',cem:'no cemitério',exi:'no exílio'}[s.z]}?`))continue;e.bib.splice(e.bib.indexOf(c),1);if(s.z==='campo'){xReset(c);c.tap=s.tap?1:0;c.sk=xInfo(c).cri?1:0;e.campo.push(c);setTimeout(()=>xEntrou(c),300);}else e[s.z].push(c);M.push(c.n);}
        if(s.fg&&M.length)it.lemb=(it.lemb||[]).filter(c=>!L.includes(c)||e.bib.includes(c));feito.push(M.length?`${M.join(', ')} do topo → ${{mao:'mão',campo:'campo',cem:'cemitério',exi:'exílio'}[s.z]}`:'nada mudou de zona');break;}
""", 'antes'))

# ---------- L27. "Você pode pagar <custo>; quando fizer, ..." (ImmediateTrigger): custos de carta (devolver, descartar, exilar do cemitério, virar, moer, sacrificar N) e mana híbrida ----------
# Undead Butler, Doombot Harbinger?, Kroxa and Kunoros, Dokuchi Silencer, Tether Technician, Meanders Guide, Sutina, The Fire Nation Drill, Spider-Man To the Rescue, Rodolf Duskbringer, Slinza, Evereth...
P.append(("function fgCustoK(", "function fgQuemJ(df){",
"""/* custo de carta "pagável" (pagaK): devolver/sacrificar/virar/descartar/exilar do cemitério/moer */
function fgCustoK(uc,ctx){uc=String(uc||'').trim();let m;if(m=uc.match(/^(Return|Sac|tapXType|Discard|ExileFromGrave)<(\\d+)\\/([^/>]+)(?:\\/[^>]*)?>$/)){const t={Return:'volta',Sac:'sac',tapXType:'tap',Discard:'desc',ExileFromGrave:'exiCem'}[m[1]];let v=m[3].replace(/;/g,',');if(t==='desc'&&v==='Random')return {t:'descR',n:+m[2]};if(v==='Hand')v='Card';if(/TopGraveyard|Triggered|Remembered|Chosen/.test(v)||!fgSpecOk(v,ctx))return null;return +m[2]>0?{t,n:+m[2],v}:null;}
  if(m=uc.match(/^Mill<(\\d+)>$/))return {t:'mill',n:+m[1]};return null;}
""", 'antes'))
P.append(("const K=fgCustoK(d.Cost,ctx);", "return [{op:'sacOu',v:mS[1],st}];}const tk=String(d.Cost).trim().split(/\\s+/);if(!tk.every(x=>/^(\\d+|[WUBRGC])$/.test(x)))return nao('custo');",
"""return [{op:'sacOu',v:mS[1],st}];}{const K=fgCustoK(d.Cost,ctx);if(K){const st=fgCadeia(ex.d,ex.api,ctx);if(st.some(o=>o.op==='nao'))return st;return [{op:'pagaK',k:K,sw:1,st}];}}const tk=String(d.Cost).trim().split(/\\s+/);if(!tk.every(x=>/^(\\d+|[WUBRGC]|[WUBRG]{2})$/.test(x)))return nao('custo');""", 'troca'))
P.append(("x.length===2&&!/\\d/.test(x)?'{'", "return [{op:'pagaOu',c:tk.map(x=>'{'+x+'}').join(''),sw:1,st}];}return fgCadeia(ex.d,ex.api,ctx);}",
"return [{op:'pagaOu',c:tk.map(x=>x.length===2&&!/\\d/.test(x)?'{'+x[0]+'/'+x[1]+'}':'{'+x+'}').join(''),sw:1,st}];}return fgCadeia(ex.d,ex.api,ctx);}", 'troca'))

# ---------- L28. Suspeito (Suspected): c.sspt → ameaça e não pode bloquear, sai quando muda de zona ou "deixa de ser suspeito" ----------
# Repeat Offender, It Doesn't Add Up, Caught Red-Handed, Person of Interest, Rubblebelt Braggart, Frantic Scapegoat, Hot Pursuit, Absolving Lammasu, Incriminating Impetus, Reasonable Doubt, Clandestine Meddler...
P.append(("['fdM','fore','tm','susp','sspt',", "['fdM','fore','tm','susp',", "['fdM','fore','tm','susp','sspt',", 'troca'))
P.append(("if(c.sspt){kw.add('menace')", "  if(c.kD&&c.kD.t===((X.sala||{}).turno||0))for(const x of c.kD.kw)kw.delete(x);",
"  if(c.sspt){kw.add('menace');kw.add('nbloq');}\n", 'antes'))
P.append(("op==='sspt')", "  else if(op==='vira')c.tap=1;else if(op==='desvira')c.tap=0;",
"  else if(op==='sspt'){if((x||{}).v)c.sspt=1;else delete c.sspt;}\n", 'antes'))
P.append(("case 'AlterAttribute':{if(d.Attributes==='Suspected'", "    case 'AlterAttribute':return (d.Attributes==='Harnessed'",
"""    case 'AlterAttribute':{if(d.Attributes==='Suspected'&&(!d.Duration)&&Object.keys(d).every(k=>/^(DB|AB|SP|Attributes|Defined|ValidTgts|TgtPrompt|Activate|SubAbility|SpellDescription|StackDescription|Cost|TargetMin|TargetMax|AILogic|IsCurse)$/.test(k))){const v=d.Activate==='False'?0:1;
      if(al)return put({op:'sspt',v,al},[]);const df=d.Defined||'Self';const o=df==='Self'?{si:1}:(df==='Enchanted'||df==='Equipped')?{anx:1}:(df==='Targeted'||df==='ParentTarget')?{mesmo:1}:/^Triggered(Card|Attacker|Object)(LKICopy)?$/.test(df)?{tk:1}:null;if(o)return [Object.assign({op:'sspt',v,al:''},o)];}}
""", 'antes'))
P.append(("case 'sspt':", "      case 'sacrEsta':{",
"""      case 'sspt':{const k=t||it.k;if(!k){feito.push('sem a criatura');break;}xNoAlvo(k,'sspt',0,ev,{v:s.v});feito.push(`${xAlvoNome(k)} ${s.v?'ficou suspeita (ameaça, não pode bloquear)':'deixou de ser suspeita'}`);break;}
""", 'antes'))

# ---------- L29. Contas: NMinus.K (K menos o número), Count$Random.A.B, conjurada do cemitério, vida e mão do jogador do gatilho (TriggeredTarget) ----------
# The Stone Brain, Lolth, Stroke of Luck, Flametongue Kavu Avatar, Rainbow Knights, Ashuza's Breath, Increasing Savagery, Secrets of the Key, Scytheclaw, Quietus Spike, Sword of War and Peace, Shimian Specter...
P.append(("md.match(/^NMinus\\.(\\d+)$/)", "else if(md==='HalfDown')n=Math.floor(n/2);",
"else if(q=md.match(/^NMinus\\.(\\d+)$/))n=+q[1]-n;else if(md==='HalfDown')n=Math.floor(n/2);", 'troca'))
P.append(("b.match(/^Count\\$Random\\.", "  if(b==='Count$TopOfLibraryCMC')return {q:'topoMV',md};",
"""  if(m=b.match(/^Count\\$Random\\.(\\d+)\\.(\\d+)$/))return {q:'rand',a:+m[1],b:+m[2],md};
  if(m=b.match(/^Count\\$wasCastFromGraveyard\\.(\\d+)\\.(\\d+)$/))return {q:'deCem',a:+m[1],b:+m[2],md};
  if(m=b.match(/^TriggeredTarget\\$(LifeTotal|CardsInHand)$/))return {q:'tdJ',f:m[1]==='LifeTotal'?'vida':'nm',md};
""", 'antes'))
P.append(("v.q==='rand'?", ":v.q==='remV'?",
""":v.q==='rand'?v.a+Math.floor(Math.random()*(v.b-v.a+1)):v.q==='deCem'?(((it.c||xAchaK(it.k)||{}).orig==='cem')?v.a:v.b):v.q==='tdJ'?(()=>{const P=String((it.tc||{}).td||'');if(!P.startsWith('P:'))return 0;const u=P.slice(2);if(u===xUid())return v.f==='vida'?X.eu.vida:X.eu.mao.length;const o=(X.ops||{})[u]||{};return v.f==='vida'?(o.vida||0):(o.nm||0);})()""", 'antes'))

# ---------- L30. TriggeredSource = a criatura que causou o dano (o gatilho "uma criatura sua causa dano de combate a um jogador" passa tk), e Defined "A & Self" vira duas partes ----------
# Stensia, White Widow, Yelena Belova, Vraska Swarm's Eminence, Conclave Sledge-Captain, Necropolis Regent, Quilled Greatwurm, X-23, Juniper Order Ranger, Captain America, Alaborn Zealot, Loyal Sentry
P.append(("Triggered(Card|Attacker|Blocker|Object|NewCardLKICopy|Source)(LKICopy)?$/.test(d.Defined||'')?'tk'", "{const TK=/^Triggered(Card|Attacker|Blocker|Object|NewCardLKICopy)(LKICopy)?$/.test(d.Defined||'')?'tk'",
"{const TK=/^Triggered(Card|Attacker|Blocker|Object|NewCardLKICopy|Source)(LKICopy)?$/.test(d.Defined||'')?'tk'", 'troca'))
P.append(("/* Defined A & Self */", "function fgPasso(d,api,ctx){",
"""function fgPasso(d,api,ctx){/* Defined A & Self */{const m=!d.ValidTgts&&/^(PutCounter|Pump|Untap|Tap|Destroy|Regenerate)$/.test(api)&&String(d.Defined||'').match(/^(Triggered(?:Card|Attacker|Blocker|Source)(?:LKICopy)?) & Self$/);if(m){const a=fgPasso(Object.assign({},d,{Defined:m[1]}),api,ctx);if(a.some(o=>o.op==='nao'))return a;const b=fgPasso(Object.assign({},d,{Defined:'Self'}),api,ctx);if(b.some(o=>o.op==='nao'))return b;return [...a,...b];}}""", 'troca'))
P.append(("xFiltro(m[1],a.c),null,{dano:a.hp,p:xPT(a.c).p,td:'P:'+a.hu,tk:a.c.k", "xFiltro(m[1],a.c),null,{dano:a.hp,p:xPT(a.c).p,td:'P:'+a.hu});",
"xFiltro(m[1],a.c),null,{dano:a.hp,p:xPT(a.c).p,td:'P:'+a.hu,tk:a.c.k,tku:xUid()});", 'troca'))

# ---------- L31. Gatilhos de emblema/efeito "no começo da sua manutenção" e "da sua etapa final" (antes só conjurou e início do combate) ----------
# Liliana, the Last Hope, Kiora, the Crashing Wave, Ajani, Adversary of Tyrants, Chandra, Awakened Inferno, Chandra, Fire of Kaladesh, Teyo, Tezzeret, Artifice Master, Garruk, Unleashed...
P.append(("L.push({m:r.Phase==='Upkeep'?'manut':'fim'", "L.push({m:'combate',ops,desc,uma:r.OneOff==='True'?1:0});else return nao(emb?'gatilho do emblema':'efeito com Triggers');",
"L.push({m:'combate',ops,desc,uma:r.OneOff==='True'?1:0});else if(r.Mode==='Phase'&&/^(End of Turn|Upkeep)$/.test(r.Phase||'')&&(!r.ValidPlayer||r.ValidPlayer==='You'))L.push({m:r.Phase==='Upkeep'?'manut':'fim',ops,desc,uma:r.OneOff==='True'?1:0});else return nao(emb?'gatilho do emblema':'efeito com Triggers');", 'troca'))
P.append(("xAtrasado('End');xEmbDispara('fim');", "e.fimT=s.turno;xAtrasado('End');", "e.fimT=s.turno;xAtrasado('End');xEmbDispara('fim');", 'troca'))
P.append(("setTimeout(()=>xEmbDispara('manut'),820);", "setTimeout(()=>xAtrasado('Upkeep'),760);", "setTimeout(()=>xAtrasado('Upkeep'),760);setTimeout(()=>xEmbDispara('manut'),820);", 'troca'))

# ---------- L32. Gatilho de emblema recalcula as contas na hora que dispara (antes ficava o valor da hora em que ganhou o emblema: Liliana, the Last Hope "2 + zumbis") ----------
P.append(("L.push({re:{d:ex.d,api:ex.api,sv:ctx.sv},m:'cast',", "L.push({m:'cast',", "L.push({re:{d:ex.d,api:ex.api,sv:ctx.sv},m:'cast',", 'troca'))
P.append(("L.push({re:{d:ex.d,api:ex.api,sv:ctx.sv},m:'combate',", "L.push({m:'combate',ops", "L.push({re:{d:ex.d,api:ex.api,sv:ctx.sv},m:'combate',ops", 'troca'))
P.append(("L.push({re:{d:ex.d,api:ex.api,sv:ctx.sv},m:r.Phase", "L.push({m:r.Phase==='Upkeep'?'manut':'fim'", "L.push({re:{d:ex.d,api:ex.api,sv:ctx.sv},m:r.Phase==='Upkeep'?'manut':'fim'", 'troca'))
P.append(("let ops=g.ops;if(g.re)", "function xGatEmb(em,g,c){const al=await xPedeAlvos(g.ops,em.nm,'');",
"function xGatEmb(em,g,c){let ops=g.ops;if(g.re){try{const r=fgCadeia(g.re.d,g.re.api,{eu:xUid(),src:'',sv:g.re.sv||{}});if(!r.some(o=>o.op==='nao'))ops=r;}catch(er){}}const al=await xPedeAlvos(ops,em.nm,'');", 'troca'))
P.append(("nm:em.nm,img:'',k:'',al,ops}", "nm:em.nm,img:'',k:'',al,ops:g.ops}", "nm:em.nm,img:'',k:'',al,ops}", 'troca'))

# ---------- L33. Ficha com P/T = quantos X você controla (TokenScript ..._total_artifacts etc.): antes virava 0/0 e morria. c.tkD guarda o filtro, xPT soma na hora ----------
# Urza's Saga (Construct), Hallowed Haunting, Sai Master Thopterist? (gnome soldier), Ezuri's Predation?, Treefolk total_forests/lands, Sculpture...
P.append(("/* ficha com P/T = quantos X */", "function fgFicha(ts,n){const o=[];for(const t of ts.split(',')){",
"""function fgFicha(ts,n){const o=[];for(const t of ts.split(',')){/* ficha com P/T = quantos X */{const p=t.split('_'),it=p.indexOf('total');if(p.length>=5&&it>3&&it<p.length-1&&/^(\\d+|x)$/.test(p[1])&&/^(\\d+|x)$/.test(p[2])){const tipos=p.slice(it+1).map(w=>w.replace(/s$/,'')).map(w=>w[0].toUpperCase()+w.slice(1)).join(',');const r=fgFicha([p[0],p[1]==='x'?'0':p[1],p[2]==='x'?'0':p[2],...p.slice(3,it)].join('_'),n);if(r&&r.length===1){r[0].tkD=tipos;o.push(r[0]);continue;}}}""", 'troca'))
P.append(("function xFicha(n,p,t,kw,art,mana,q,quieto,xx){", "function xFicha(n,p,t,kw,art,mana,q,quieto){", "function xFicha(n,p,t,kw,art,mana,q,quieto,xx){", 'troca'))
P.append(("sk:p==null?0:1,...(xx&&xx.tkD?{tkD:xx.tkD}:{})}", "mana:mana?1:0,sk:p==null?0:1});e.campo.push(...nov);", "mana:mana?1:0,sk:p==null?0:1,...(xx&&xx.tkD?{tkD:xx.tkD}:{})});e.campo.push(...nov);", 'troca'))
P.append(("if(u===me){xFicha(s.nome,s.p,s.t,s.kw,s.art,s.mana,n,1,s);", "if(u===me){xFicha(s.nome,s.p,s.t,s.kw,s.art,s.mana,n,1);", "if(u===me){xFicha(s.nome,s.p,s.t,s.kw,s.art,s.mana,n,1,s);", 'troca'))
P.append(("ficha saiu');break;}\n        xFicha(s.nome,s.p,s.t,s.kw,s.art,s.mana,n,1,s);", "ficha saiu');break;}\n        xFicha(s.nome,s.p,s.t,s.kw,s.art,s.mana,n,1);", "ficha saiu');break;}\n        xFicha(s.nome,s.p,s.t,s.kw,s.art,s.mana,n,1,s);", 'troca'))
P.append(("else ev({op:'fichaD',nome:s.nome,p:s.p,t:s.t,kw:s.kw,art:s.art,mana:s.mana,n,tkD:s.tkD}", "else ev({op:'fichaD',nome:s.nome,p:s.p,t:s.t,kw:s.kw,art:s.art,mana:s.mana,n}", "else ev({op:'fichaD',nome:s.nome,p:s.p,t:s.t,kw:s.kw,art:s.art,mana:s.mana,n,tkD:s.tkD}", 'troca'))
P.append(("L0.u!==me){ev({op:'fichaD',nome:s.nome,p:s.p,t:s.t,kw:s.kw,art:s.art,mana:s.mana,n,tkD:s.tkD}", "L0.u!==me){ev({op:'fichaD',nome:s.nome,p:s.p,t:s.t,kw:s.kw,art:s.art,mana:s.mana,n}", "L0.u!==me){ev({op:'fichaD',nome:s.nome,p:s.p,t:s.t,kw:s.kw,art:s.art,mana:s.mana,n,tkD:s.tkD}", 'troca'))
P.append(("xFicha(v.nome,v.p,v.t,v.kw,v.art,v.mana,v.n,1,v)", "v.op==='fichaD')xFicha(v.nome,v.p,v.t,v.kw,v.art,v.mana,v.n,1);", "v.op==='fichaD')xFicha(v.nome,v.p,v.t,v.kw,v.art,v.mana,v.n,1,v);", 'troca'))
P.append(("if(c.tkD){const L=xLadoCampo(c)", "  if(c.sspt){kw.add('menace');kw.add('nbloq');}",
"  if(c.tkD){const L=xLadoCampo(c)||[],q=L.filter(l=>{try{return fgValid(l,c.tkD,{eu:'',src:'',sv:{}});}catch(er){return false;}}).length;p+=q;t+=q;}\n", 'antes'))

# ---------- L34. "Ganha {T}: Add X" (habilidade de mana dada por Animate): vai pra gan.mn e o xGanI soma no mana da carta ----------
# Urza's Saga (capítulo I), e quem dá habilidade de mana simples de virar
P.append(("T=[],A=[],tx=[],MN=[],TM=", "const sv=ctx.sv||{},T=[],A=[],tx=[],TM=", "const sv=ctx.sv||{},T=[],A=[],tx=[],MN=[],TM=", 'troca'))
P.append(("/* mana dada */", "for(const nm of String(d.Abilities||'').split(',').map(x=>x.trim()).filter(Boolean)){const q=fgPP(sv[nm]||'');if(q.k!=='AB'||!q.api||q.api==='Mana'",
"for(const nm of String(d.Abilities||'').split(',').map(x=>x.trim()).filter(Boolean)){const q=fgPP(sv[nm]||'');/* mana dada */if(q.k==='AB'&&q.api==='Mana'&&String(q.d.Cost||'').trim()==='T'&&/^[WUBRGC]+$/.test(q.d.Produced||'')&&/^\\d*$/.test(q.d.Amount||'')&&Object.keys(q.d).every(k=>/^(AB|Cost|Produced|Amount|SpellDescription)$/.test(k))){MN.push(q.d.Produced.repeat(+(q.d.Amount||1)));tx.push(fgDescr(q.d,sv));continue;}if(q.k!=='AB'||!q.api||q.api==='Mana'", 'troca'))
P.append(("[...T.concat(A,MN).join('§')]", "const gan={id:'g'+[...T.concat(A).join('§')]", "const gan={id:'g'+[...T.concat(A,MN).join('§')]", 'troca'))
P.append(("T,A,sv:vs,mn:MN}", "tx:tx.join('\\n'),T,A,sv:vs}", "tx:tx.join('\\n'),T,A,sv:vs,mn:MN}", 'troca'))
P.append(("g.mn&&g.mn.length?", "o=Object.assign({},o0,{tx:(o0.tx?o0.tx+'\\n':'')+g.tx.replace(/CARDNAME|NICKNAME/g,c.n)});",
"o=Object.assign({},o0,{tx:(o0.tx?o0.tx+'\\n':'')+g.tx.replace(/CARDNAME|NICKNAME/g,c.n)},g.mn&&g.mn.length?{mana:[...new Set([...(o0.mana||[]),...g.mn])]}:{});", 'troca'))

# ---------- L35. Condições "se {C} foi gasto pra conjurar" (ConditionManaSpent: c.msC guarda as cores gastas) e "se é sua fase principal" (ConditionPhases Main1/Main2, ConditionPlayerTurn, Addendum) ----------
# Boros Fury-Shield, Firespout, Repel Intruders, River's Grasp, Invert the Skies, Torrent of Souls, Moraug, Waves of Aggression, Full Throttle, Precognitive Perception, Arrester's Zeal, Unbreakable Formation...
P.append(("c.msC=ms0?'':(r.cor||[]).join('');", "c.cvg=ms0?0:(r.cor||[]).length;", "c.cvg=ms0?0:(r.cor||[]).length;c.msC=ms0?'':(r.cor||[]).join('');", 'troca'))
P.append(("/* condição: mana gasta / fase principal */", "function fgPasso0(d,api,ctx){const nao=why=>[{op:'nao',d:(d.SpellDescription||d.StackDescription||api)+(why?' ('+why+')':'')}];",
"""function fgPasso0(d,api,ctx){const nao=why=>[{op:'nao',d:(d.SpellDescription||d.StackDescription||api)+(why?' ('+why+')':'')}];
  /* condição: mana gasta / fase principal */if(!d.__cnd&&(d.ConditionManaSpent||d.ConditionPhases)){const ck=Object.keys(d).filter(k=>/^Condition/.test(k)&&k!=='ConditionDescription'),FZ={Main1:1,Main2:3};
    const ok=ck.every(k=>(k==='ConditionManaSpent'&&/^[WUBRG]$/.test(d[k]))||(k==='ConditionPhases'&&String(d[k]).split(',').every(x=>FZ[x.trim()]))||(k==='ConditionPlayerTurn'&&d[k]==='True')||(k==='ConditionDefined'&&d[k]==='Self'&&d.ConditionPresent==='Card.wasCast')||(k==='ConditionPresent'&&d[k]==='Card.wasCast'&&d.ConditionDefined==='Self'));
    if(ok){const d2=Object.assign({},d,{__cnd:1});for(const k of ck)delete d2[k];const r=fgPasso(d2,api,ctx);if(r.some(o=>o.op==='nao'))return r;return [{op:'se',d:'n',q:{q:'cnd',ms:d.ConditionManaSpent||'',ph:d.ConditionPhases?String(d.ConditionPhases).split(',').map(x=>FZ[x.trim()]):null,vz:d.ConditionPlayerTurn==='True'?1:0},cmp:'GE1',st:r}];}}""", 'troca'))
P.append(("v.q==='cnd'?", ":v.q==='remV'?",
""":v.q==='cnd'?(()=>{const S=X.sala||{};if(v.vz&&S.vez!==me)return 0;if(v.ph&&!v.ph.includes(S.fase||0))return 0;if(v.ms){const c=it.c||xAchaK(it.k)||{};if(!String(c.msC||'').includes(v.ms))return 0;}return 1;})()""", 'antes'))

# ---------- L36. Anular "a menos que pague X" com o X da mágica (Power Sink, Overrule, Martyr of Frost, Rethink, Logic Knot...) ----------
P.append(("else if(n==='X')pz={g:'X'};", "if(typeof n==='number')pz={g:n};}else if(uc==='Discard<1/Hand>')pz={mao:1};", "if(typeof n==='number')pz={g:n};else if(n==='X')pz={g:'X'};}else if(uc==='Discard<1/Hand>')pz={mao:1};", 'troca'))
P.append(("s.pz.g==='X'?{g:it.x||0}:{}", "if(s.pz){p.pz=Object.assign({nm:it.nm},s.pz);feito.push(s.pz.mao?", "if(s.pz){p.pz=Object.assign({nm:it.nm},s.pz,s.pz.g==='X'?{g:it.x||0}:{});feito.push(s.pz.mao?", 'troca'))
P.append(("o dono paga {${s.pz.g==='X'?(it.x||0):s.pz.g}}", "`${p.nm}: o dono paga {${s.pz.g}} ou ela é anulada`", "`${p.nm}: o dono paga {${s.pz.g==='X'?(it.x||0):s.pz.g}} ou ela é anulada`", 'troca'))

# ---------- L37. Anexar o Equipamento alvo a esta criatura (Attach Defined Self, Object Targeted) e "anexe esta ao alvo da parte anterior" (Object ParentTarget) ----------
# Sokka Swordmaster, Cloud Ex-SOLDIER, Captain America First Avenger, Armory Automaton, Shagrat, Frodo Determined Hero; Aura Finesse, Magnetic Theft (Object ParentTarget)
P.append(("op:'equipaEsta'", "return put({op:'anexaAlvo',al},[]);return nao('ação Attach');}",
"return put({op:'anexaAlvo',al},[]);if(al&&d.Defined==='Self'&&d.Object==='Targeted'&&/^(Equipment|Aura)\\b/.test(d.ValidTgts||'')&&!d.ConditionDefined)return put({op:'equipaEsta',al},[]);if(al&&d.Object==='ParentTarget'&&!d.Defined&&!d.ConditionDefined)return put({op:'anexaPai',al},[]);return nao('ação Attach');}", 'troca'))
P.append(("case 'equipaEsta':", "      case 'sacrEsta':{",
"""      case 'equipaEsta':{const eq=e.campo.find(q=>q.k===t),cr=e.campo.find(q=>q.k===it.k);if(!eq||!cr){feito.push('não deu pra anexar (precisa ser sua e estar no campo)');break;}eq.an=cr.k;feito.push(`${eq.n} foi anexado a ${cr.n}`);break;}
      case 'anexaPai':{const eq=e.campo.find(q=>q.k===(it.al||[])[0]);if(!eq||!t||eq.k===t||!/\\b(Equipment|Aura)\\b/.test(xInfo(eq).tipo||'')||!xExiste(t)){feito.push('não deu pra anexar');break;}eq.an=t;feito.push(`${eq.n} foi anexado a ${xAlvoNome(t)}`);break;}
""", 'antes'))

# ---------- L38. Virar ou desvirar o alvo (TapOrUntap): lê como Tap e deixa escolher na hora (bot: vira a do oponente, desvira a sua) ----------
# Pestermite, Hidden Strings, Niblis of the Breath, Granite Witness, Twiddle, Trickster Mage, Faerie Dragon, Inverted Iceberg, Sword of the Paruns, Tideforce Elemental...
P.append(("case 'TapOrUntap':{", "    case 'Cleanup':case 'StoreSVar':return [];",
"""    case 'TapOrUntap':{const r=fgPasso0(Object.assign({},d,{AB:'Tap'}),'Tap',ctx);if(r.some(o=>o.op==='nao')||!r.every(o=>o.op==='vira'))return r.some(o=>o.op==='nao')?r:nao('ação TapOrUntap');return r.map(o=>Object.assign({},o,{op:'viraOu'}));}
""", 'antes'))
P.append(("case 'viraOu':", "      case 'sacrEsta':{",
"""      case 'viraOu':{const k=t||(s.anx?'':it.k);const c=k&&xAchaK(k);if(!c){feito.push('sem o permanente');break;}const meu=e.campo.includes(c);const vr=XBOT?(meu?!!0:!c.tap):confirm(`${it.nm}: OK = virar ${c.n}, Cancelar = desvirar`);const op=vr?'vira':'desvira';feito.push(`${vr?'virou':'desvirou'} ${xAlvoNome(k)}`);xNoAlvo(k,op,0,ev);break;}
""", 'antes'))

# ---------- L39. "Seus terrenos/criaturas não desviram na próxima desvirada" (Effect + ReplacementEffect Untap CantHappen em X.YouCtrl) ----------
# Bontu's Last Reckoning, Kefnet's Last Word, Rhonas's Last Stand, Hazoret's Undying Fury, Oketra's Last Mercy...
P.append(("/* não desviram (todas as suas X) */", "/* não desvira: Untap CantHappen no lembrado */",
"""/* não desviram (todas as suas X) */if(d.ReplacementEffects&&!d.Triggers&&!d.StaticAbilities&&!d.Abilities&&!d.RememberObjects&&!String(d.ReplacementEffects).includes(',')&&d.Duration==='UntilTheEndOfYourNextUntap'){const re=String((ctx.sv||{})[d.ReplacementEffects]||''),mv=re.match(/ValidCard\\$ ([A-Za-z]+\\.YouCtrl)\\b/);if(/^\\s*Event\\$ Untap\\b/.test(re)&&/Layer\\$ CantHappen/.test(re)&&mv&&fgSpecOk(mv[1],ctx))return [{op:'nDesvV',v:mv[1]}];}/* não desvira: Untap CantHappen no lembrado */""", 'troca'))
P.append(("case 'nDesvV':", "      case 'sacrEsta':{",
"""      case 'nDesvV':{const L=e.campo.filter(c=>{try{return fgValid(c,s.v,{eu:me,src:it.k||'',sv:{}});}catch(er){return false;}});L.forEach(c=>c.nd=1);feito.push(`${L.length} permanente${L.length===1?'':'s'} seu${L.length===1?'':'s'} (${s.v.replace('.YouCtrl','')}) não desvira${L.length===1?'':'m'} na próxima etapa de desvirar`);break;}
""", 'antes'))

# ---------- L40. "Moa N; você pode pôr um X dentre elas na mão/no campo" (ChangeZone Hidden, ChangeType X.IsRemembered, origem cemitério/exílio) ----------
# Ainok Wayfarer, Sparring Dummy, First Contact, Scout the City, Oko Lorwyn Liege, Cache Grab, Something Worth Saving, Seed of Hope, Rapid Rescue, Barrowgoyf, Tetzin, Tomakul Scrapsmith, T'Chaka...
P.append(("/* lembradas pra mão */", "    case 'ChangeZone':/* exila e volta a própria */",
"""    case 'ChangeZone':/* lembradas pra mão */if(!al&&!d.Defined&&d.Hidden==='True'&&/^(Graveyard|Graveyard,Exile|Exile,Graveyard)$/.test(d.Origin||'')&&/^(Hand|Battlefield)$/.test(d.Destination||'')&&/IsRemembered/.test(d.ChangeType||'')&&!/EACH|&|IsImprinted|Chosen|Triggered|Targeted/.test(d.ChangeType)&&!Object.keys(d).some(k=>/^(Remember|Imprint|Condition|Unless|DefinedPlayer|Chooser|Forget)/.test(k)&&!/^(RememberChanged|ForgetOtherRemembered)$/.test(k))){
      const v=String(d.ChangeType).replace(/\\.IsRemembered\\+/g,'.').replace(/\\+IsRemembered\\b/g,'').replace(/\\.IsRemembered\\b/g,'');const n=d.ChangeNum==null?1:N('ChangeNum');if(typeof n==='number'&&fgSpecOk(v,ctx))return [{op:'lembEsV',v,n,z:d.Destination==='Hand'?'mao':'campo',tap:d.Tapped==='True'?1:0,lc:d.RememberChanged==='True'?(d.ForgetOtherRemembered==='True'?2:1):0}];}
""", 'antes'))
P.append(("case 'lembEsV':", "      case 'sacrEsta':{",
"""      case 'lembEsV':{const ok=c=>{try{return fgValid(c,s.v,{eu:me,src:it.k||'',sv:{}});}catch(er){return false;}},L=(it.lemb||[]).filter(c=>(e.cem.includes(c)||e.exi.includes(c))&&ok(c)),nm=it.nm,q=Math.max(0,+n||0),res=st.slice(si+1),al2=(it.al||[]).slice(j),s0=s;
        const poe=c=>{const z=e.cem.includes(c)?e.cem:e.exi;z.splice(z.indexOf(c),1);if(s0.z==='campo'){xReset(c);c.tap=s0.tap?1:0;c.sk=xInfo(c).cri?1:0;e.campo.push(c);setTimeout(()=>xEntrou(c),300);}else e.mao.push(c);};
        const fim=P=>{if(P.length)xLog(`${nm}: pôs ${P.map(c=>c.n).join(', ')} ${s0.z==='mao'?'na mão':'no campo'}`);const lb=s0.lc===2?P:s0.lc===1?[...(it.lemb||[]),...P]:(it.lemb||[]);if(res.length)xFazDepois(res,Object.assign({},it,{al:al2,lemb:lb}));else{xSobe();xPintaEu();}};
        setTimeout(async()=>{const P=[];for(let z=0;z<q;z++){const R=L.filter(c=>!P.includes(c));if(!R.length)break;let c;if(XBOT)c=R[0];else{const k=await xEscolhe(`${nm}: pôr qual ${s0.z==='mao'?'na mão':'no campo'}? (feche pra não pôr)`,R.map(c=>({c,lado:'Cemitério'})));c=R.find(x=>x.k===k);}if(!c)break;poe(c);P.push(c);}fim(P);},300);
        feito.push(L.length?'escolhe dentre as cartas':'nenhuma carta assim entre elas');xLog(`${it.nm} resolveu: ${feito.join(' · ')}`);return rest;}
""", 'antes'))

# ---------- L41. Animate nas cartas lembradas / do gatilho (via fgLembT), sem AtEOT ----------
P.append(("fgLembT(d,'Animate',ctx)", "const df=d.Defined||'';if(!al&&df&&df!=='Self')return nao('quem');",
"const df=d.Defined||'';if(!al&&df&&df!=='Self'){if(!d.AtEOT&&!d.Duration){const r=fgLembT(d,'Animate',ctx);if(r)return r;}if(!d.AtEOT&&d.Duration==='Permanent'){const r=fgLembT(d,'Animate',ctx);if(r)return r;}return nao('quem');}", 'troca'))
P.append(("['pump','kt','nDesv','cnt','regen','anima']", "['pump','kt','nDesv','cnt','regen'].includes(x.op)&&!x.al))return null;return r.map(x=>Object.assign(x,{[k]:1}));};",
"['pump','kt','nDesv','cnt','regen','anima'].includes(x.op)&&!x.al))return null;return r.map(x=>Object.assign(x,{[k]:1}));};", 'troca'))

# ---------- L42. TriggeredTarget como carta (quem levou o dano do gatilho "deals damage to a creature") em Pump/Tap/Untap/PutCounter/Animate/Debuff ----------
# Matsu-Tribe Birdstalker, Matsu-Tribe Sniper, Queen of Ice, Ogre Siegebreaker?, Kashi-Tribe Warriors, Hand of Cruelty...
P.append(("|Source)(LKICopy)?$/.test(d.Defined||'')||(/^TriggeredTarget(LKICopy)?$/", "{const TK=/^Triggered(Card|Attacker|Blocker|Object|NewCardLKICopy|Source)(LKICopy)?$/.test(d.Defined||'')?'tk'",
"{const TK=(/^Triggered(Card|Attacker|Blocker|Object|NewCardLKICopy|Source)(LKICopy)?$/.test(d.Defined||'')||(/^TriggeredTarget(LKICopy)?$/.test(d.Defined||'')&&/^(Pump|Tap|Untap|PutCounter|Animate|Debuff)$/.test(api)))?'tk'", 'troca'))

# ---------- L43. Pump nos atacantes do gatilho (Defined TriggeredAttackers, não-maldição) = PumpAll nas suas atacantes ----------
# Frontier Warmonger, Yuriko, Blade of the Mighty?, e gatilhos "sempre que uma ou mais criaturas suas atacam, elas ganham..."
P.append(("d.Defined==='TriggeredAttackers'&&d.IsCurse!=='True'", "if(!al&&d.Defined&&d.Defined!=='Self'){const r=fgLembT(d,'Pump',ctx);if(r)return r;return nao('quem');}",
"if(!al&&d.Defined==='TriggeredAttackers'&&d.IsCurse!=='True'){const d2=Object.assign({},d,{ValidCards:'Creature.attacking+YouCtrl'});delete d2.Defined;delete d2.SubAbility;const r=fgPasso0(d2,'PumpAll',ctx);if(!r.some(o=>o.op==='nao'))return r;}if(!al&&d.Defined&&d.Defined!=='Self'){const r=fgLembT(d,'Pump',ctx);if(r)return r;return nao('quem');}", 'troca'))

# ---------- L44. "Você ganha vida" com alvo jogador (a conta usa o alvo): Gerrard Capashen, Kithkin Zealot, Spoils of Evil ----------
P.append(("d.Defined==='You'&&/^target (opponent|player)$/.test(al||'')", "if(d.Defined==='Player'&&!al)return [{op:'ganhaJ',n,todos:1}];",
"if(d.Defined==='Player'&&!al)return [{op:'ganhaJ',n,todos:1}];if(d.Defined==='You'&&/^target (opponent|player)$/.test(al||''))return put({op:'ganha',n,al},[]);", 'troca'))

# ---------- L45. Quem leva o dano: a própria carta (Defined Self), o jogador do gatilho (TriggeredTarget = td), o controlador da encantada/equipada ----------
# Psionic Entity, Sunflare Shaman, Goblin Kaboomist, Sword of War and Peace, Gremlin Infestation, Power Leak, Errant Minion...
P.append(("/* dano: Self / td / controlador da anexada */", "    case 'DealDamage':{if(d.Defined==='TriggeredTargetController'",
"""    case 'DealDamage':/* dano: Self / td / controlador da anexada */if(!al&&!d.DamageSource&&/^(Self|TriggeredTarget|EnchantedController|EquippedController)$/.test(d.Defined||'')&&!Object.keys(d).some(k=>/^(Remember|Condition|Unless|DamageMap|DividedAsYouChoose|ExcessSVar)/.test(k))){const n=N('NumDmg');if(n!=null)return [d.Defined==='Self'?{op:'dano',n,al:'',si:1}:d.Defined==='TriggeredTarget'?{op:'dano',n,al:'',td:1}:{op:'danoCtl',n}];}
""", 'antes'))
P.append(("case 'danoCtl':", "      case 'sacrEsta':{",
"""      case 'danoCtl':{const a=(e.campo.find(q=>q.k===it.k)||{}).an,u=a&&xDonoK(a);if(!u){feito.push('não está anexada a nada');break;}if(u===me){e.vida-=n;feito.push(`${n} de dano em você`);break;}feito.push(`${n} de dano em ${xNomeU(u)}${xDanoF(it.k,'P:'+u,n,ev)}`);break;}
""", 'antes'))

# ---------- L46. Ganhe o controle de todas até o fim do turno, com habilidades (AllValid + LoseControl EOT + AddKWs) ----------
# Insurrection, Rowan Fearless Sparkmage, Mob Rule, Act of Treason em massa...
P.append(("/* pega todas até o fim do turno */", "    case 'GainControl':{if(d.AllValid&&(!d.NewController",
"""    case 'GainControl':/* pega todas até o fim do turno */if(d.AllValid&&(!d.NewController||d.NewController==='You')&&d.LoseControl==='EOT'&&!al&&!d.Defined&&!Object.keys(d).some(k=>/^(Remember|Condition|Unless)/.test(k))&&fgSpecOk(d.AllValid,ctx)){const kw=(d.AddKWs||'').split(' & ').filter(Boolean);if(kw.every(k=>FGKW[k]))return [{op:'pegaTodos',v:d.AllValid,desv:d.Untap==='True'?1:0,eot:1,kws:kw.map(k=>FGKW[k])}];}
""", 'antes'))
P.append(("ev({op:'daV',v:s.v,pa:me,desv:s.desv,eot:s.eot,kws:s.kws},u)", "for(const u of L)ev({op:'daV',v:s.v,pa:me,desv:s.desv},u);",
"for(const u of L)ev({op:'daV',v:s.v,pa:me,desv:s.desv,eot:s.eot,kws:s.kws},u);", 'troca'))
P.append(("eot:v.eot?1:0,desv:v.desv,kws:v.kws,para:v.pa", "xEvia({op:'recebe',c:JSON.parse(JSON.stringify(c)),dn:c.dono0||xUid(),eot:0,desv:v.desv,para:v.pa});",
"xEvia({op:'recebe',c:JSON.parse(JSON.stringify(c)),dn:c.dono0||xUid(),eot:v.eot?1:0,desv:v.desv,kws:v.kws,para:v.pa});", 'troca'))

# ---------- L47. Efeito com gatilhos "neste turno": quando uma criatura sua entra / morre / ataca ----------
# First Day of Class, Warhost's Frenzy, Waltz of Rage, The Last Ronin?, Song of Blood, Indulge...
P.append(("|OneOff|Phase|ValidPlayer|Origin|Destination)$/", "Execute|TriggerDescription|TriggerZones|OneOff|Phase|ValidPlayer)$/",
"Execute|TriggerDescription|TriggerZones|OneOff|Phase|ValidPlayer|Origin|Destination)$/", 'troca'))
P.append(("m:'entra',v:r.ValidCard", "else return nao(emb?'gatilho do emblema':'efeito com Triggers');",
"""else if(r.Mode==='ChangesZone'&&r.Destination==='Battlefield'&&(!r.Origin||r.Origin==='Any')&&/YouCtrl/.test(r.ValidCard||'')&&fgSpecOk(r.ValidCard,ctx))L.push({re:{d:ex.d,api:ex.api,sv:ctx.sv},m:'entra',v:r.ValidCard,ops,desc,uma:r.OneOff==='True'?1:0});
          else if(r.Mode==='ChangesZone'&&r.Origin==='Battlefield'&&r.Destination==='Graveyard'&&/YouCtrl|YouOwn/.test(r.ValidCard||'')&&fgSpecOk(String(r.ValidCard).replace(/[.+](YouCtrl|YouOwn)\\b/g,''),ctx))L.push({re:{d:ex.d,api:ex.api,sv:ctx.sv},m:'morre',v:String(r.ValidCard).replace(/[.+](YouCtrl|YouOwn)\\b/g,''),ops,desc,uma:r.OneOff==='True'?1:0});
          else if(r.Mode==='Attacks'&&/YouCtrl/.test(r.ValidCard||'')&&fgSpecOk(r.ValidCard,ctx))L.push({re:{d:ex.d,api:ex.api,sv:ctx.sv},m:'ataca',v:r.ValidCard,ops,desc,uma:r.OneOff==='True'?1:0});else return nao(emb?'gatilho do emblema':'efeito com Triggers');""", 'troca'))
P.append(("if(g.v){let ok=false;", "if(m==='cast'){let ok=false;", "if(g.v){let ok=false;", 'troca'))
P.append(("xEmbDispara('entra',c);", "function xEntrou(c){if(!X.eu.campo.includes(c))return;", "function xEntrou(c){if(!X.eu.campo.includes(c))return;xEmbDispara('entra',c);", 'troca'))
P.append(("xEmbDispara('morre',c);", "(xTT().morL=xTT().morL||[]).push({c,eu:1});", "(xTT().morL=xTT().morL||[]).push({c,eu:1});xEmbDispara('morre',c);", 'troca'))
P.append(("xEmbDispara('ataca',c);", "    const tx=xAtqTx(c);if(!tx)continue;let al=[];", "    xEmbDispara('ataca',c);const tx=xAtqTx(c);if(!tx)continue;let al=[];", 'troca'))

# ---------- L48. Sacrificar / veneno pelo jogador do gatilho (TriggeredTarget, TriggeredCardController, TriggeredAttackerController...) ----------
# Demon of Loathing, Killmonger, Destructive Urge, Burning Sands, Funeral March, Necrogen Rotpriest, Marsh Viper, Pit Scorpion...
P.append(("op:'sacrQ'", "if(df==='TriggeredPlayer'&&fgSpecOk(d.SacValid||'Permanent',ctx))return [{op:'sacrTP',n,v:d.SacValid||'Permanent'}];return nao('quem sacrifica');}",
"if(df==='TriggeredPlayer'&&fgSpecOk(d.SacValid||'Permanent',ctx))return [{op:'sacrTP',n,v:d.SacValid||'Permanent'}];{const q=fgQuemJ(df);if(q&&q!=='alvo'&&!al&&!Object.keys(d).some(k=>/^(Unless|Remember|Condition)/.test(k))&&fgSpecOk(d.SacValid||'Permanent',ctx))return [{op:'sacrQ',n,v:d.SacValid||'Permanent',q}];}return nao('quem sacrifica');}", 'troca'))
P.append(("op:'venQ'", "if(al==='target player'||al==='target opponent')return [{op:'veneno',n,quem:'alvo'}];return nao('quem');}",
"if(al==='target player'||al==='target opponent')return [{op:'veneno',n,quem:'alvo'}];{const q=fgQuemJ(df);if(q&&q!=='alvo'&&!al)return [{op:'venQ',n,q}];}return nao('quem');}", 'troca'))
P.append(("case 'sacrQ':", "      case 'sacrEsta':{",
"""      case 'sacrQ':{const u=xQuemJ(s.q,it,ult);if(!u){feito.push('sem jogador pra sacrificar');break;}const o={op:'sacr',n,tipo:'v',v:s.v,nm:it.nm};if(u===me)xSacr(o);else ev(o,u);feito.push(`${u===me?'você':xNomeU(u)} sacrifica ${n} (${s.v})`);break;}
      case 'venQ':{const u=xQuemJ(s.q,it,ult);if(!u){feito.push('sem jogador pro veneno');break;}if(u===me)e.ven=(e.ven||0)+n;else ev({op:'ven',n},u);feito.push(`${u===me?'você':xNomeU(u)} recebe ${n} marcador(es) de veneno`);break;}
""", 'antes'))

# ---------- L49. Shroud como habilidade dada (Pump KW Shroud): o motor de alvos já respeita ----------
# Minotaur Illusionist, Giant Crab, Advanced Hoverguard, Benevolent Bodyguard?...
P.append(("'Shroud':'shroud',", "'Hexproof':'hexproof','HIDDEN Unblockable'", "'Hexproof':'hexproof','Shroud':'shroud','HIDDEN Unblockable'", 'troca'))

# ---------- L50. Mais habilidades dadas que o bloqueio já entende: intimidar, espreitar, equitação, travessias ----------
P.append(("'Landwalk:Forest':'forestwalk',", "'Hexproof':'hexproof','Shroud':'shroud',", "'Hexproof':'hexproof','Shroud':'shroud','Intimidate':'intimidate','Skulk':'skulk','Horsemanship':'horsemanship','Landwalk:Forest':'forestwalk','Landwalk:Island':'islandwalk','Landwalk:Swamp':'swampwalk','Landwalk:Mountain':'mountainwalk','Landwalk:Plains':'plainswalk','Wither':'wither',", 'troca'))

# ---------- L51. Força e resistência trocadas até o fim do turno (KW HIDDEN ... power and toughness are switched) ----------
# Twisted Image, Inside Out, Fluctuator?, Merfolk Thaumaturgist, Strange Inversion, Transmutation...
P.append(("'HIDDEN CARDNAME\\'s power and toughness are switched':'swPT',", "'Hexproof':'hexproof','Shroud':'shroud',", "'Hexproof':'hexproof','Shroud':'shroud','HIDDEN CARDNAME\\'s power and toughness are switched':'swPT',", 'troca'))
P.append(("if(kw.has('swPT'))", "  if(c.kD&&c.kD.t===((X.sala||{}).turno||0))for(const x of c.kD.kw)kw.delete(x);\n  return {p,t,kw,pz,",
"  if(c.kD&&c.kD.t===((X.sala||{}).turno||0))for(const x of c.kD.kw)kw.delete(x);\n  if(kw.has('swPT')){const z=p;p=t;t=z;kw.delete('swPT');}\n  return {p,t,kw,pz,", 'troca'))

P.append(("swPT:'força e resistência trocadas',", "intimidate:'intimidar',", "intimidate:'intimidar',swPT:'força e resistência trocadas',", 'troca'))
# ---------- L52. Anular mágica e/ou habilidade ativada/disparada (TargetType Spell,Activated,Triggered) ----------
# Disallow, Overcharged Amalgam, Sister of Silence, Sublime Epiphany, Spider-Sense, Louisoix's Sacrifice, Subcommander T'Pol, Mirrorshell Crab...
P.append(("ht:{sp:", "return d.TargetType==='Spell'&&!d.ValidTgts?.includes('Activated')?",
"""{const TT=String(d.TargetType||'').split(',');if(TT[0]&&TT.every(x=>/^(Spell(\\.(Instant|Sorcery|nonCreature))?|Instant|Sorcery|Activated|Triggered)$/.test(x))&&TT.some(x=>/^(Activated|Triggered)$/.test(x))&&/^(Card|Emblem|Card,Emblem)$/.test(d.ValidTgts||'')&&!d.Defined&&!Object.keys(d).some(k=>/^(Remember|Condition|TargetValidTargeting|TargetMin|TargetMax|IsPresent)/.test(k))){const sp=TT.filter(x=>!/^(Activated|Triggered)$/.test(x)).map(x=>x.replace(/^Spell\\.?/,'')||'Card');const o={op:'anula',al:'spell',hab:1,ht:{sp:sp.length?1:0,spv:sp.includes('Card')?'':sp.join(',')}};if(d.UnlessCost){if(!/^\\d+$/.test(d.UnlessCost))return nao('custo pra não anular');o.pz={g:+d.UnlessCost};}return [o];}}return d.TargetType==='Spell'&&!d.ValidTgts?.includes('Activated')?""", 'troca'))
P.append(("(s.ht&&p.tipo==='mag'?", "s.op==='anula'&&s.hab?((X.sala&&X.sala.pilha)||[]).filter(p=>p.tipo!=='mag'&&p.de!==xUid())",
"s.op==='anula'&&s.hab?((X.sala&&X.sala.pilha)||[]).filter(p=>(s.ht&&p.tipo==='mag'?!!s.ht.sp&&(!s.ht.spv||!!(p.c&&(()=>{try{return fgValid(p.c,s.ht.spv,{eu:xUid(),src:'',sv:{}});}catch(er){return false;}})())):p.tipo!=='mag')&&p.de!==xUid())", 'troca'))

# ---------- L53. Proteção: na própria carta (cor à escolha) e contra cor(es) fixa(s), na própria ou no alvo ----------
# Cartel Aristocrat, Knight of Dawn, Pristine Skywise, Keeper of Kookus, Grotesque Hybrid, Goblin Wizard, Obsidian Acolyte, Crimson Acolyte...
P.append(("/* proteção fixa / da própria */", "    case 'Protection':{if(d.Gains!=='Choice'",
"""    case 'Protection':/* proteção fixa / da própria */if(!d.Duration&&(!d.Defined||d.Defined==='Self')&&!Object.keys(d).some(k=>/^(Remember|Condition|Defined.+|TargetMin)/.test(k))){const CM={white:'W',blue:'U',black:'B',red:'R',green:'G'},self=!al;
      if(d.Gains==='Choice'&&/^(AnyColor|AnyColor,Colorless|Colorless,AnyColor)$/i.test(d.Choices||'')&&self)return [{op:'protCor',si:1,inc:/Colorless/i.test(d.Choices)?1:0}];
      const g=String(d.Gains||'').split(',').map(x=>x.trim().toLowerCase());if(g[0]&&g.every(x=>CM[x])){const o={op:'protF',cores:g.map(x=>CM[x])};return self?[Object.assign(o,{si:1})]:put(Object.assign(o,{al}),[]);}}
""", 'antes'))
P.append(("if(op==='protF'){", "function xEfCarta(c,op,n,x){const i=xInfo(c);",
"function xEfCarta(c,op,n,x){const i=xInfo(c);if(op==='protF'){c.prT=[...new Set([...(c.prT||[]),...((x||{}).cores||[])])];return;}", 'troca'))
P.append(("case 'protF':", "      case 'sacrEsta':{",
"""      case 'protF':{if(!t){feito.push('sem alvo');break;}const CN={W:'branco',U:'azul',B:'preto',R:'vermelho',G:'verde'};xNoAlvo(t,'protF',0,ev,{cores:s.cores});feito.push(`${xAlvoNome(t)} ganha proteção contra ${s.cores.map(x=>CN[x]).join(' e ')} até o fim do turno`);break;}
""", 'antes'))

# ---------- L54. Contas do jogador do gatilho (TriggeredPlayer$CardsInHand/LifeTotal) e dano em jogador do gatilho (Defined TriggeredPlayer/TriggeredCardController/...) ----------
# Wheel of Torture, Storm World, Dreamborn Muse, Price of Knowledge, Fevered Visions, Antagonism, Mogis, Heat of Battle, Battle Strain, Emberwilde Captain, Meglonoth...
P.append(("b.match(/^TriggeredPlayer\\$(LifeTotal|CardsInHand)$/)", "  if(m=b.match(/^TriggeredTarget\\$(LifeTotal|CardsInHand)$/))return {q:'tdJ',f:m[1]==='LifeTotal'?'vida':'nm',md};",
"  if(m=b.match(/^TriggeredTarget\\$(LifeTotal|CardsInHand)$/))return {q:'tdJ',f:m[1]==='LifeTotal'?'vida':'nm',md};\n  if(m=b.match(/^TriggeredPlayer\\$(LifeTotal|CardsInHand)$/))return {q:'tdJ',f:m[1]==='LifeTotal'?'vida':'nm',tp:1,md};", 'troca'))
P.append(("const P=v.tp?", "v.q==='tdJ'?(()=>{const P=String((it.tc||{}).td||'');",
"v.q==='tdJ'?(()=>{const P=v.tp?((it.tc||{}).tp?'P:'+(it.tc||{}).tp:''):String((it.tc||{}).td||'');", 'troca'))
P.append(("op:'danoQ'", "    case 'DealDamage':/* dano: Self / td / controlador da anexada */",
"""    case 'DealDamage':/* dano no jogador do gatilho */if(!al&&!d.DamageSource&&d.Defined&&!/^(Self|TriggeredTarget|Targeted.*|ParentTarget.*)$/.test(d.Defined)&&!Object.keys(d).some(k=>/^(Remember|Condition|Unless|DamageMap|DividedAsYouChoose|ExcessSVar)/.test(k))){const q=fgQuemJ(d.Defined);if(q&&q!=='alvo'){const n=N('NumDmg');if(n!=null)return [{op:'danoQ',n,q}];}}
""", 'antes'))
P.append(("case 'danoQ':", "      case 'sacrEsta':{",
"""      case 'danoQ':{const u=xQuemJ(s.q,it,ult);if(!u||!(n>0)){feito.push(u?'sem dano':'sem jogador pro dano');break;}xNoAlvo('P:'+u,'dano',n,ev);feito.push(`${n} de dano em ${u===me?'você':xNomeU(u)}`);break;}
""", 'antes'))

# ---------- L55. PlayerCountOpponents$Highest (CardsInHand / LifeTotal / Valid X.YouCtrl): o maior entre os oponentes ----------
# Beza the Bounding Spring, Teachings of the Archaics, Sunset Revelry, Scholar of New Horizons, Claim Jumper, Emeritus of Truce...
P.append(("b.match(/^PlayerCountOpponents\\$Highest", "  if(m=b.match(/^TriggeredTarget\\$(LifeTotal|CardsInHand)$/))return {q:'tdJ',",
"""  if(b==='PlayerCountOpponents$HighestCardsInHand')return {q:'opMax',f:'nm',md};if(b==='PlayerCountOpponents$HighestLifeTotal')return {q:'opMax',f:'vida',md};
  if(m=b.match(/^PlayerCountOpponents\\$HighestValid (.+)$/)){if(!/YouCtrl/.test(m[1])||/Remembered|Targeted|Triggered|Chosen/.test(m[1])||!fgSpecOk(m[1],ctx))return null;return {q:'opMax',f:'v',v:m[1],md};}
  if(m=b.match(/^TriggeredTarget\\$(LifeTotal|CardsInHand)$/))return {q:'tdJ',""", 'troca'))
P.append(("v.q==='opMax'?", ":v.q==='rand'?",
""":v.q==='opMax'?Math.max(0,...xOpsL().filter(u=>!xMorto(X.ops[u])).map(u=>{const o=X.ops[u]||{};if(v.f==='vida')return o.vida||0;if(v.f==='nm')return o.nm||0;return (o.campo||[]).filter(c=>{try{return fgValid(c,v.v,{eu:u,src:'',sv:{}});}catch(er){return false;}}).length;}))""", 'antes'))

# ---------- L56. BUG: condição comparando com outra SVar (ConditionSVarCompare GTY) descartava o passo calado; e conta só da execução também ----------
# Claim Jumper, Scholar of New Horizons, Knight of the White Orchid, Weathered Wayfarer?, Gift of Estates, Land Tax?...
P.append(("/* compara com outra SVar */", "function fgPasso(d,api,ctx){/* Defined A & Self */",
"""function fgPasso(d,api,ctx){/* compara com outra SVar */if(d.ConditionCheckSVar){const cv=k=>{let r=null;try{r=fgConta(k,ctx);}catch(er){}return r==='X'?{q:'X'}:r;};const a=cv(d.ConditionCheckSVar),m=String(d.ConditionSVarCompare||'GE1').match(/^(LT|LE|EQ|GE|GT|NE)(.+)$/);
    if(m){const nu=/^-?\\d+$/.test(m[2]),c=nu?+m[2]:cv(m[2]);if(c!=null&&c!=='X'&&a!=null&&a!=='X'&&(typeof a==='object'||typeof c==='object')){const d2=Object.assign({},d);delete d2.ConditionCheckSVar;delete d2.ConditionSVarCompare;const r=fgPasso(d2,api,ctx);if(r.some(o=>o.op==='nao'))return r;return [{op:'se',d:'n',q:{q:'cmp',a,o:m[1],c,x:1,y:0,md:[]},cmp:'GE1',st:r}];}
      if(!nu&&typeof c==='number')d=Object.assign({},d,{ConditionSVarCompare:m[1]+c});}}/* Defined A & Self */""", 'troca'))
P.append(("typeof n==='object')return null;const r0=fgCmp(", "if(d.ConditionCheckSVar!=null){const n=fgConta(d.ConditionCheckSVar,ctx);if(n==null||n==='X')return null;if(!fgCmp(n,d.ConditionSVarCompare||'GE1'))return false;}",
"if(d.ConditionCheckSVar!=null){const n=fgConta(d.ConditionCheckSVar,ctx);if(n==null||n==='X'||typeof n==='object')return null;const r0=fgCmp(n,d.ConditionSVarCompare||'GE1');if(r0===null)return null;if(!r0)return false;}", 'troca'))

# ---------- L57. Jace, Vryn's Prodigy e cia: a volta transformada pode ter ForgetOtherRemembered (mudança no L23) ----------
# Jace Vryn's Prodigy, Kytheon Hero of Akros, Liliana Heretical Healer?, Grist Voracious Larva, Sorin of House Markov...

# ---------- L58. BUG: "exile alvo até esta sair do campo" (Duration UntilHostLeavesPlay) na carta do oponente exilava pra sempre ----------
# Banisher Priest, Brutal Cathar, Portable Hole, Skyclave Apparition?, Static Prison?, Ossification, Fiend Hunter (gatilho único)...
P.append(("op:'exAteG'", "      if(og==='Battlefield'&&ds==='Exile'&&d.Duration==='UntilHostLeavesPlay'&&al&&/YouCtrl/.test(d.ValidTgts||'')",
"      if(og==='Battlefield'&&ds==='Exile'&&d.Duration==='UntilHostLeavesPlay'&&al&&!d.Defined&&!/YouCtrl/.test(d.ValidTgts||'')&&!Object.keys(d).some(k=>/^(Remember|Imprint|Condition)/.test(k)))return put({op:'exAteG',al},[]);\n      if(og==='Battlefield'&&ds==='Exile'&&d.Duration==='UntilHostLeavesPlay'&&al&&/YouCtrl/.test(d.ValidTgts||'')", 'troca'))
P.append(("case 'exAteG':", "      case 'sacrEsta':{",
"""      case 'exAteG':{const host=e.campo.find(q=>q.k===it.k);if(!host){feito.push(`não exilou (${it.nm} já saiu do campo)`);break;}if(!t){feito.push('sem alvo');break;}const nm0=xAlvoNome(t),c=e.campo.find(q=>q.k===t);
        if(c){xSai(c,'exi');const q=e.exi.find(z=>z.k===c.k)||e.exi[e.exi.length-1];if(q&&!c.tok){q.exAte=it.k;q.exS=it.k;}}else{host.exO=1;xNoAlvo(t,'exAteO',0,ev,{h:it.k});}feito.push(`exilou ${nm0} até ${it.nm} sair do campo`);break;}
""", 'antes'))
P.append(("if(op==='exAteO'){", "function xEfCarta(c,op,n,x){const i=xInfo(c);",
"function xEfCarta(c,op,n,x){const i=xInfo(c);if(op==='exAteO'){const k=c.k,tk=c.tok;xSai(c,'exi');const q=X.eu.exi.find(z=>z.k===k)||X.eu.exi[X.eu.exi.length-1];if(q&&!tk&&x&&x.h){q.exAte=x.h;q.exS=x.h;}return;}", 'troca'))
P.append(("function xExAteVolta(k,rem){", "function xExAteVolta(k){const e=X.eu;",
"function xExAteVolta(k,rem){if(!rem&&k){const h=X.eu&&X.eu.campo.find(q=>q.k===k);if(h&&h.exO){delete h.exO;xEvia({op:'exAteV',k});}}const e=X.eu;", 'troca'))
P.append(("v.op==='exAteV'", "  else if(v.op==='aniq')xAniq(v);", "  else if(v.op==='aniq')xAniq(v);\n  else if(v.op==='exAteV')xExAteVolta(v.k,1);", 'troca'))

# ---------- L59. BUG: "exile/sacrifique no fim do turno" (AtEOT) era ignorado em fichas e no Pump: a ficha ficava pra sempre ----------
# Geist of Saint Traft, Daring Piracy, War Effort, Angelic Favor, Faerie Aerie, L'Rell, Invocation of Saint Traft, Pyric Salamander, Deathknell Kami, Fatal Frenzy, Lowland Oaf...
P.append(("/* AtEOT em ficha/pump */", "function fgPasso0(d,api,ctx){const nao=why=>[{op:'nao',d:(d.SpellDescription||d.StackDescription||api)+(why?' ('+why+')':'')}];",
"""function fgPasso0(d,api,ctx){const nao=why=>[{op:'nao',d:(d.SpellDescription||d.StackDescription||api)+(why?' ('+why+')':'')}];
  /* AtEOT em ficha/pump */if((api==='Token'||api==='Pump')&&d.AtEOT){const f=/^(Your)?Exile(Combat)?$/.test(d.AtEOT)?'exi':/^(Your)?Sacrifice(Combat|Ctrl)?$/.test(d.AtEOT)?'sac':d.AtEOT==='Destroy'?'des':'';if(!f)return nao('fim do turno');const d2=Object.assign({},d);delete d2.AtEOT;const r=fgPasso0(d2,api,ctx);if(r.some(o=>o.op==='nao'))return r;
    if(api==='Token'){if(!r.some(o=>o.op==='ficha'))return nao('fim do turno');for(const o of r)if(o.op==='ficha')o.fim=f;return r;}const p0=r.find(o=>/^(pump|kt)(Pp)?$/.test(o.op));if(!p0)return nao('fim do turno');return [...r,p0.al?{op:'fimF',f,mesmo:1}:{op:'fimF',f,si:1}];}""", 'troca'))
P.append(("xx&&xx.fim==='sac'?{sacF:1}", "...(xx&&xx.tkD?{tkD:xx.tkD}:{})});e.campo.push(...nov);",
"...(xx&&xx.tkD?{tkD:xx.tkD}:{}),...(xx&&xx.fim==='sac'?{sacF:1}:xx&&xx.fim==='exi'?{exF:1}:xx&&xx.fim==='des'?{desF:1}:{})});e.campo.push(...nov);", 'troca'))
P.append(("if(op==='fimF'){", "function xEfCarta(c,op,n,x){const i=xInfo(c);",
"function xEfCarta(c,op,n,x){const i=xInfo(c);if(op==='fimF'){if(x&&x.f==='sac')c.sacF=1;else if(x&&x.f==='des')c.desF=1;else c.exF=1;return;}", 'troca'))
P.append(("case 'fimF':", "      case 'sacrEsta':{",
"""      case 'fimF':{if(!t){feito.push('sem alvo');break;}xNoAlvo(t,'fimF',0,ev,{f:s.f});feito.push(`${xAlvoNome(t)} vai ser ${s.f==='sac'?'sacrificada':s.f==='des'?'destruída':'exilada'} no fim do turno`);break;}
""", 'antes'))

P.append(("q.desF);", "xLog(`fim do turno: sacrificou ${sf.length} ficha(s) temporária(s)`);xVarre();}",
"xLog(`fim do turno: sacrificou ${sf.length} ficha(s) temporária(s)`);xVarre();}{const df=e.campo.filter(q=>q.desF);if(df.length){df.forEach(q=>{delete q.desF;xEfCarta(q,'destroi',0);});xLog(`fim do turno: destruiu ${df.map(q=>q.n).join(', ')}`);xVarre();}}", 'troca'))
# ---------- L60. BUG: Pump/PumpAll "até o seu próximo turno" (Duration UntilYourNextTurn) acabava no fim do turno ----------
# Liliana the Last Hope, Blue Dragon, Wasp Shrinking Savior, Rootwise Survivor?, For the Common Good, Karvanista, Mouth of the Storm...
P.append(("/* até o seu próximo turno */", "  /* AtEOT em ficha/pump */",
"""  /* até o seu próximo turno */if((api==='Pump'||api==='PumpAll')&&d.Duration==='UntilYourNextTurn'){const d2=Object.assign({},d);delete d2.Duration;const r=fgPasso0(d2,api,ctx);
    if(r.length&&r.every(o=>o.op==='pump'&&!o.dbl||o.op==='kt'||o.op==='pumpTodos'&&!o.dbl&&!o.todasP))return r.map(o=>Object.assign({},o,{op:o.op==='pump'?'pumpN':o.op==='kt'?'ktN':'pumpTodosN'}));}
""", 'antes'))
P.append(("else if(op==='pumpN'){", "else if(op==='pumpProx'){c.tpN=(c.tpN||0)+x.p;c.ateU=x.u;c.ateT=x.tn;}",
"else if(op==='pumpProx'){c.tpN=(c.tpN||0)+x.p;c.ateU=x.u;c.ateT=x.tn;}else if(op==='pumpN'){c.tpN=(c.tpN||0)+(x.p||0);c.ttN=(c.ttN||0)+(x.t||0);c.ateU=x.u;c.ateT=x.tn;}else if(op==='ktN'){c.ktN=[...new Set([...(c.ktN||[]),...(x.kws||[])])];c.ateU=x.u;c.ateT=x.tn;}", 'troca'))
P.append(("+(c.tt||0)+(c.ttN||0)+(c.pT||0)", "+(c.cnt||0)+(c.tt||0)+(c.pT||0)", "+(c.cnt||0)+(c.tt||0)+(c.ttN||0)+(c.pT||0)", 'troca'))
P.append(("c.tpN=0;c.ttN=0;", "c.tpN=0;c.naN=0;c.ateU='';c.gd='';c.ktN=null;", "c.tpN=0;c.ttN=0;c.naN=0;c.ateU='';c.gd='';c.ktN=null;", 'troca'))
P.append(("case 'pumpN':", "      case 'sacrEsta':{",
"""      case 'pumpN':case 'ktN':{const k=t||it.k;if(!k){feito.push('sem alvo');break;}const tn=(X.sala||{}).turno||0;if(s.op==='pumpN')xNoAlvo(k,'pumpN',0,ev,{p:s.p,t:s.t,u:me,tn});else xNoAlvo(k,'ktN',0,ev,{kws:s.kws||[s.kw],u:me,tn});feito.push(`${xAlvoNome(k)} ${s.op==='pumpN'?(s.p>=0?'+':'')+s.p+'/'+(s.t>=0?'+':'')+s.t:'ganha '+(s.kws||[s.kw]).map(x=>KPT[x]||x).join(', ')} até o seu próximo turno`);break;}
      case 'pumpTodosN':{const tn=(X.sala||{}).turno||0;let q=0;e.campo.filter(c=>xCri(c)&&(!s.v||fgValid(c,s.v,{eu:me,src:it.k,sv:{}}))).forEach(c=>{c.tpN=(c.tpN||0)+(s.p||0);c.ttN=(c.ttN||0)+(s.t||0);if(s.kw&&s.kw.length)c.ktN=[...new Set([...(c.ktN||[]),...s.kw])];c.ateU=me;c.ateT=tn;q++;});feito.push(`${q} criatura(s) suas ${s.p||s.t?(s.p>=0?'+':'')+s.p+'/'+(s.t>=0?'+':'')+s.t:''}${s.kw&&s.kw.length?' ganham '+s.kw.map(x=>KPT[x]||x).join(', '):''} até o seu próximo turno`);break;}
""", 'antes'))

# ---------- L61. BUG: "ganhe o controle enquanto esta estiver no campo" (LoseControl LeavesPlay) era controle pra sempre ----------
# Mind Flayer, Vodalian Mindsinger, Roil Elemental, Old Man of the Sea?, Rubinia Soulsinger?, Merieke Ri Berit...
P.append(("h:/LeavesPlay/.test(lc)?1:0,", "{const o={op:'controle',eot:lc==='EOT'?1:0,", "{const o={op:'controle',h:/LeavesPlay/.test(lc)?1:0,eot:lc==='EOT'?1:0,", 'troca'))
P.append(("kws:s.kws,h:s.h?it.k:''},u)", "ev({op:'entrega',k:t,pa:me,eot:s.eot,desv:s.desv,kws:s.kws},u)", "ev({op:'entrega',k:t,pa:me,eot:s.eot,desv:s.desv,kws:s.kws,h:s.h?it.k:''},u)", 'troca'))
P.append(("kws:v.kws,h:v.h||'',para:v.pa});", "xEvia({op:'recebe',c:JSON.parse(JSON.stringify(c)),dn:c.dono0||xUid(),eot:v.eot,desv:v.desv,kws:v.kws,para:v.pa});",
"xEvia({op:'recebe',c:JSON.parse(JSON.stringify(c)),dn:c.dono0||xUid(),eot:v.eot,desv:v.desv,kws:v.kws,h:v.h||'',para:v.pa});", 'troca'))
P.append(("if(v.h)c.ctlH=v.h;else delete c.ctlH;", "if(v.kws&&v.kws.length)c.kt=[...new Set([...(c.kt||[]),...v.kws])];X.eu.campo.push(c);",
"if(v.kws&&v.kws.length)c.kt=[...new Set([...(c.kt||[]),...v.kws])];if(v.h)c.ctlH=v.h;else delete c.ctlH;X.eu.campo.push(c);", 'troca'))
P.append(("q.ctlH===k&&q.dono0", "const e=X.eu;if(!e||!k||!e.exi.some(q=>q.exAte===k))return;",
"const e=X.eu;if(e&&k&&!rem){for(const q of e.campo.filter(q=>q.ctlH===k&&q.dono0)){e.campo.splice(e.campo.indexOf(q),1);const u=q.dono0;delete q.ctlH;xEvia({op:'recebe',c:JSON.parse(JSON.stringify(q)),dn:u,para:u});xLog(`${q.n} voltou pro dono (a carta que tomou o controle saiu)`);}}if(!e||!k||!e.exi.some(q=>q.exAte===k))return;", 'troca'))

# ---------- L62. BUG: dano dividido entre alvos (DividedAsYouChoose) dava o total em CADA alvo (Arc Lightning 3+3+3) ----------
# Arc Lightning, Forked Lightning, Fireball?, Fiery Justice, Cone of Flame?, Ignite Disorder, Rolling Thunder?, Inferno Titan...
P.append(("/* dano dividido */", "  /* AtEOT em ficha/pump */",
"""  /* dano dividido */if(api==='DealDamage'&&d.DividedAsYouChoose!=null){const d2=Object.assign({},d);delete d2.DividedAsYouChoose;const r=fgPasso0(d2,api,ctx);const L=r.filter(o=>o.op==='dano'&&o.al);if(L.length>1&&r.every(o=>o.op==='dano'))return r.map(o=>Object.assign({},o,{op:'danoDiv'}));return r;}
""", 'antes'))
P.append(("if(s.op==='danoDiv'){", "    const pa=xPrecisaAlvo(s),t=pa?(it.al||[])[j++]",
"""    if(s.op==='danoDiv'){if(it.dvR==null)it.dvR=s.n==='X'?(it.x||0):(+(typeof s.n==='object'?rv(s.n):s.n)||0);const rest=st.slice(si+1).filter(o=>o.op==='danoDiv').length,t0=(it.al||[])[j],nx=(it.al||[]).slice(j+1,j+1+rest).filter(Boolean).length;let q=0;
      if(t0&&it.dvR>0){if(!nx)q=it.dvR;else if(XBOT)q=Math.max(1,Math.ceil(it.dvR/(nx+1)));else{const r=prompt(`${it.nm}: quanto dos ${it.dvR} de dano vai em ${xAlvoNome(t0)}? (sobra pelo menos 1 pra cada um dos outros ${nx} alvo(s))`,String(Math.max(1,it.dvR-nx)));q=Math.max(1,Math.min(it.dvR-nx,parseInt(r,10)||1));}}it.dvR-=q;s=Object.assign({},s,{op:'dano',n:q});}
""", 'antes'))

# ---------- L63. BUG: "se a criatura morrer neste turno, exile em vez disso" (ReplaceDyingDefined) era ignorado no dano e no pump ----------
# Reduce to Ashes, Magma Spray, Scorching Dragonfire, Wilt in the Heat, Lava Coil?, Fiery Temper?, Khaaaaaaaaaaaannn!, Pump: Feed the Swarm? ...
P.append(("/* exila se morrer */", "  /* AtEOT em ficha/pump */",
"""  /* exila se morrer */if((api==='DealDamage'||api==='Pump')&&/^(Targeted|ThisTargetedCard)(\\.Creature)?$/.test(d.ReplaceDyingDefined||'')){const d2=Object.assign({},d);delete d2.ReplaceDyingDefined;const r=fgPasso0(d2,api,ctx);if(r.some(o=>o.op==='nao'))return r;const L=r.filter(o=>o.al&&/^(dano|danoDiv|pump)$/.test(o.op));if(!L.length)return r.length?nao('exilar se morrer'):r;return r.map(o=>L.includes(o)?Object.assign({},o,{exM:1}):o);}
""", 'antes'))
P.append(("if(s.exM){const t0=", "    const pa=xPrecisaAlvo(s),t=pa?(it.al||[])[j++]",
"""    if(s.exM){const t0=(it.al||[])[j];if(t0&&!/^[PS]:/.test(t0))xNoAlvo(t0,'exMorre',0,ev);}
""", 'antes'))
P.append(("if(op==='exMorre'){", "function xEfCarta(c,op,n,x){const i=xInfo(c);",
"function xEfCarta(c,op,n,x){const i=xInfo(c);if(op==='exMorre'){c.exM=(X.sala||{}).turno||0;return;}", 'troca'))
P.append(("if(c.exM&&c.exM===", "function xMorre(c){const e=X.eu,ix=e.campo.indexOf(c);if(ix<0)return;",
"function xMorre(c){const e=X.eu,ix=e.campo.indexOf(c);if(ix<0)return;if(c.exM&&c.exM===((X.sala||{}).turno||0)){delete c.exM;xLog(`${c.n} seria morta: foi exilada no lugar`);return xSai(c,'exi');}", 'troca'))

# ---------- L64. BUG: "volta do cemitério com marcador" (WithCountersType) era ignorado: +1/+1, -1/-1, marcador de habilidade, finalidade ----------
# Sand Golem, Generous Revival, Gallia, Persist, Aberrant Return, Metamorphosis Fanatic, Unbreakable Bond, Mirko, Rydia, Admiral Brass, Wolfbat, Season of the Burrow...
P.append(("/* volta com marcador */", "  /* AtEOT em ficha/pump */",
"""  /* volta com marcador */if(api==='ChangeZone'&&d.WithCountersType){const ty=String(d.WithCountersType),ok=/^(P1P1|M1M1|FINALITY|STUN)$/.test(ty)||!!FGKW[ty];let am=d.WithCountersAmount==null?1:/^\\d+$/.test(d.WithCountersAmount)?+d.WithCountersAmount:(()=>{try{return fgConta(d.WithCountersAmount,ctx);}catch(er){return null;}})();const d2=Object.assign({},d);delete d2.WithCountersType;delete d2.WithCountersAmount;const r=fgPasso0(d2,api,ctx);if(r.some(o=>o.op==='nao'))return r;
    const L=r.filter(o=>(o.op==='doCem'||o.op==='doCemAlvo')&&o.dest==='campo');if(!L.length)return r;if(!ok||typeof am!=='number')return r;if(!(am>0))return r;return r.map(o=>L.includes(o)?Object.assign({},o,{wc:{t:ty,n:am}}):o);}
""", 'antes'))
P.append(("function xWc(c,w){", "async function xDoCem(s,nm){",
"""function xWc(c,w){if(!w||!c)return;if(w.t==='P1P1')c.cnt=(c.cnt||0)+w.n;else if(w.t==='M1M1')c.cnt=(c.cnt||0)-w.n;else if(w.t==='FINALITY')c.fin=1;else if(w.t==='STUN')c.stun=(c.stun||0)+w.n;else if(FGKW[w.t])c.kwC=[...new Set([...(c.kwC||[]),FGKW[w.t]])];xLog(`${c.n} entrou com ${w.n} marcador(es) ${w.t==='P1P1'?'+1/+1':w.t==='M1M1'?'-1/-1':w.t==='FINALITY'?'de finalidade':w.t==='STUN'?'de atordoamento':'de '+(KPT[FGKW[w.t]]||w.t)}`);}
async function xDoCem(s,nm){""", 'troca'))
P.append(("if(s.wc)xWc(c,s.wc);if(s.cnt){", "e.campo.push(c);if(s.cnt){", "e.campo.push(c);if(s.wc)xWc(c,s.wc);if(s.cnt){", 'troca'))
P.append(("e.campo.push(c);if(s.wc)xWc(c,s.wc);setTimeout(()=>xEntrou(c),450);}else e.mao.push(c);feito.push(`${c.n} voltou do cemitério pr", "e.campo.push(c);setTimeout(()=>xEntrou(c),450);}else e.mao.push(c);feito.push(`${c.n} voltou do cemitério pr",
"e.campo.push(c);if(s.wc)xWc(c,s.wc);setTimeout(()=>xEntrou(c),450);}else e.mao.push(c);feito.push(`${c.n} voltou do cemitério pr", 'troca'))
P.append(("(c.kwC||[]).forEach(x=>kw.add(x));", "(c.kwM||[]).forEach(x=>kw.add(x));", "(c.kwM||[]).forEach(x=>kw.add(x));(c.kwC||[]).forEach(x=>kw.add(x));", 'troca'))
P.append(("'kwM','kwC','fin','mkN',", "'kwM','mkN',", "'kwM','kwC','fin','mkN',", 'troca'))
P.append(("if(c.fin&&!c.tok){", "function xMorre(c){const e=X.eu,ix=e.campo.indexOf(c);if(ix<0)return;if(c.exM&&c.exM===",
"function xMorre(c){const e=X.eu,ix=e.campo.indexOf(c);if(ix<0)return;if(c.fin&&!c.tok){delete c.fin;xLog(`${c.n} tinha marcador de finalidade: foi exilada em vez de morrer`);return xSai(c,'exi');}if(c.exM&&c.exM===", 'troca'))

# ---------- L65. BUG: "não pode ser regenerada" (Destroy/DestroyAll NoRegen) era ignorado fora do gatilho ----------
# Fatal Blow, Death Bomb, Grotesque Hybrid, Wrath of God, Damnation, Day of Judgment, Terror, Doom Blade?, Smother, Incinerate (dano)...
P.append(("/* destruir sem regenerar */", "  /* AtEOT em ficha/pump */",
"""  /* destruir sem regenerar */if((api==='Destroy'||api==='DestroyAll')&&d.NoRegen==='True'){const d2=Object.assign({},d);delete d2.NoRegen;const r=fgPasso0(d2,api,ctx);if(r.some(o=>o.op==='nao'))return r;return r.map(o=>o.op==='destroi'&&o.al?Object.assign({},o,{nr:1}):o.op==='todos'?Object.assign({},o,{nr:1}):o);}
""", 'antes'))
P.append(("if(s.nr){const t0=(it.al||[])[j];if(s.al&&t0", "    const pa=xPrecisaAlvo(s),t=pa?(it.al||[])[j++]",
"""    if(s.nr){const t0=(it.al||[])[j];if(s.al&&t0&&!/^[PS]:/.test(t0))xNoAlvo(t0,'nRegen',0,ev);}
""", 'antes'))

P.append(("xTodos(s.tipo,s.nr);", "case 'todos':xTodos(s.tipo);ev({op:'todos',tipo:s.tipo});", "case 'todos':xTodos(s.tipo,s.nr);ev({op:'todos',tipo:s.tipo,nr:s.nr?1:0});", 'troca'))
P.append(("xTodos(v.tipo,v.nr);", "v.op==='todos')xTodos(v.tipo);", "v.op==='todos')xTodos(v.tipo,v.nr);", 'troca'))
P.append(("function xTodos(tipo,nr){", "function xTodos(tipo){", "function xTodos(tipo,nr){", 'troca'))
P.append(("if(ok){if(nr)c.nRg=", "if(ok)xEfCarta(c,'destroi');}}", "if(ok){if(nr)c.nRg=(X.sala||{}).turno||0;xEfCarta(c,'destroi');}}}", 'troca'))
# ---------- L66. Ficha pro jogador-alvo (TokenOwner Targeted/TargetedPlayer) ia pro "outro jogador" e não pro alvo escolhido (multiplayer) ----------
# Hunted Horror, Ox Drover, Forbidden Orchard, Cybernetica Datasmith, Prismari Command, Gravedig?, Brigid's Command...
P.append(("test(al||'')?'alvo':ow==='Opponent'", "&&/^target (opponent|player)$/.test(al||'')?'ou':ow==='Opponent'", "&&/^target (opponent|player)$/.test(al||'')?'alvo':ow==='Opponent'", 'troca'))

# ---------- L67. BUG: "você pode" (Optional) em sacrificar/moer/descartar/comprar era obrigatório; "descarte N a não ser que descarte um X" (UnlessType) descartava N sempre ----------
# Yawgmoth Demon, God-Eternal Bontu, Crawling Sensation, Hedge Shredder, Glacial Dragonhunt, Evie Frye, Sibilant Spirit, Infiltration Lens; Compulsive Research, Thirst for Identity, Practical Research...
P.append(("/* você pode (Optional) */", "  /* AtEOT em ficha/pump */",
"""  /* você pode (Optional) */if(!ctx.__opq&&/^(Sacrifice|Mill|Discard|Draw)$/.test(api)&&(d.Optional==='True'||(api==='Draw'&&d.OptionalDecider==='You'))){ctx.__opq=1;let r;try{r=fgPasso0(d,api,ctx);}finally{delete ctx.__opq;}if(r.some(o=>o.op==='nao'))return r;
    let f=0;return r.map(o=>{if(f)return o;const ok=o.op==='sacrEu'||o.op==='sacrEsta'||o.op==='descarta'||(o.op==='mill'&&o.quem==='eu')||(o.op==='compra'&&o.quem==='eu');if(!ok)return o;f=1;return Object.assign({},o,{opq:1});});}
  /* descarte a não ser */if(!ctx.__dun&&api==='Discard'&&d.UnlessType){ctx.__dun=1;let r;try{r=fgPasso0(d,api,ctx);}finally{delete ctx.__dun;}if(r.length===1&&r[0].op==='descarta'&&fgSpecOk(d.UnlessType,ctx))return [Object.assign({},r[0],{op:'descUn',v:d.UnlessType})];return r;}
""", 'antes'))
P.append(("if(s.opq&&!XBOT){", "    const pa=xPrecisaAlvo(s),t=pa?(it.al||[])[j++]",
"""    if(s.opq&&!XBOT){const tx={sacrEu:'sacrificar '+(s.d||'uma permanente'),sacrEsta:'sacrificar esta carta',mill:'moer',descarta:'descartar',compra:'comprar'}[s.op]||'fazer isso';const nn=typeof s.n==='number'?s.n:null;if(!confirm(`${it.nm}: você quer ${tx}${nn!=null&&s.op!=='sacrEsta'?' ('+nn+')':''}?`)){if(xPrecisaAlvo(s))j++;feito.push('escolheu não '+tx);continue;}}
""", 'antes'))
P.append(("case 'descUn':", "      case 'sacrEsta':{",
"""      case 'descUn':{const L=e.mao.filter(c=>{try{return fgValid(c,s.v,{eu:me,src:'',sv:{}});}catch(er){return false;}}),res=st.slice(si+1),al2=(it.al||[]).slice(j),nm=it.nm,q=n;
        setTimeout(async()=>{let fe=0;if(L.length&&(XBOT||confirm(`${nm}: descartar 1 ${s.v} em vez de ${q} cartas?`))){let c=L[0];if(!XBOT&&L.length>1){const k=await xEscolhe(`${nm}: descarte qual?`,L.map(c=>({c,lado:'Mão'})));c=L.find(x=>x.k===k)||L[0];}xDescarta.ult=[c];e.mao.splice(e.mao.indexOf(c),1);e.cem.push(c);xLog(`${nm}: descartou ${c.n}`);fe=1;}if(!fe)await xDescarta(q,nm);if(res.length)xFazDepois(res,Object.assign({},it,{al:al2}));else{xSobe();xPintaEu();}},300);
        feito.push(`descarta ${q} a não ser que descarte 1 ${s.v}`);xLog(`${it.nm} resolveu: ${feito.join(' · ')}`);return rest;}
""", 'antes'))

# ---------- L68. Descarte pelo jogador do gatilho/alvo (TriggeredTarget/TriggeredPlayer/TargetedController/TriggeredCardController...), inclusive ao acaso ----------
# Skullknocker Ogre, Headless Specter, Urgoros, Necrogen Mists, Doom Foretold, Gloomlance, Dinrova Horror, Recoil, Blightning, Carnival, Oppression, Bereavement...
P.append(("op:'descQ'", "if(df!=='You'&&!/^You$/.test(d.Defined||''))return nao('descarte de outro jogador');",
"{const q=df==='TargetedPlayer'?'alvo':fgQuemJ(df),so=df==='TargetedPlayer'?'P':/^(Parent)?Targeted(Controller|Owner)$/.test(df)?'C':'';if(q&&!al&&!d.RememberDiscarded&&!d.DiscardValid&&(!d.Mode||/^(TgtChoose|Hand|Random)$/.test(d.Mode))){const n=d.Mode==='Hand'?99:(N('NumCards')??1);if(typeof n==='number')return [{op:'descQ',n,q,so,rnd:d.Mode==='Random'?1:0}];}}if(df!=='You'&&!/^You$/.test(d.Defined||''))return nao('descarte de outro jogador');", 'troca'))
P.append(("case 'descQ':", "      case 'sacrEsta':{",
"""      case 'descQ':{if(s.so){const t0=String(ult||(it.al||[])[0]||'');if((s.so==='P')!==t0.startsWith('P:'))break;}const u=xQuemJ(s.q,it,ult);if(!u){feito.push('sem jogador pro descarte');break;}const tx=`${u===me?'você':xNomeU(u)} descarta ${n>=99?'a mão':n}${s.rnd?' ao acaso':''}`;
        if(u!==me){ev({op:'descOp',n,nm:it.nm,rnd:s.rnd},u);feito.push(tx);break;}if(s.rnd||n>=99){const L=[];for(let q=0;q<n&&e.mao.length;q++)L.push(...e.mao.splice(Math.floor(Math.random()*e.mao.length),1));L.forEach(c=>e.cem.push(c));if(L.length)xDescartou(L.length);feito.push(tx+(L.length?': '+L.map(c=>c.n).join(', '):''));break;}setTimeout(()=>xDescarta(n,it.nm).then(()=>{xSobe();xPintaEu();}),300);feito.push(tx);break;}
""", 'antes'))
P.append(("v.op==='descOp'&&v.rnd", "  else if(v.op==='descOp'){if(v.n>=99){",
"  else if(v.op==='descOp'&&v.rnd){const L=[];for(let q=0;q<v.n&&e.mao.length;q++)L.push(...e.mao.splice(Math.floor(Math.random()*e.mao.length),1));L.forEach(c=>e.cem.push(c));if(L.length){xLog(`descartou ao acaso: ${L.map(c=>c.n).join(', ')} (${v.nm})`);xDescartou(L.length);}xSobe();xPintaEu();}\n  else if(v.op==='descOp'){if(v.n>=99){", 'troca'))

# ---------- L69. Comprar: cada oponente (Opponent/Player.Opponent/Player.Other), o jogador-alvo de antes (TargetedPlayer), "você e o do gatilho" ----------
# Words of Wisdom, Archival Whorl, Valiant Batrider, Cut a Deal, Clockwork Fox, Master of the Feast, Memory Worm, Diviner Spirit, Black Widow, Tenuous Truce...
P.append(("op:'compraOps'", "if(df!=='You'&&!al)return nao('quem compra');",
"""if(!al&&/^(Opponent|Player\\.Opponent|Player\\.Other)$/.test(df))return [{op:'compraOps',n}];if(!al&&df==='TargetedPlayer')return [{op:'compraQ',n,q:'alvo'}];{const m2=df.match(/^(?:You & (Triggered\\w+)|(Triggered\\w+) & You)$/);const q2=m2&&fgQuemJ(m2[1]||m2[2]);if(!al&&q2&&q2!=='alvo')return [{op:'compra',n,quem:'eu'},{op:'compraQ',n,q:q2}];}if(df!=='You'&&!al)return nao('quem compra');""", 'troca'))
P.append(("case 'compraOps':", "      case 'sacrEsta':{",
"""      case 'compraOps':ev({op:'compra',n});feito.push(`cada oponente comprou ${n}`);break;
""", 'antes'))

# ---------- L70. "crie uma ficha e anexe este Equipamento a ela" (Attach Defined$ Remembered depois de Token RememberTokens) ----------
# Field-Tested Frying Pan, Midnight Angel Armor, Citizen's Crowbar, Shining Armor?, Kaldra Compleat?...
P.append(("op:'anexaFicha'", "return nao('ação Attach');}",
"if(d.Defined==='Remembered'&&(!d.Object||d.Object==='Self')&&!d.ConditionDefined&&!al)return [{op:'anexaFicha'}];return nao('ação Attach');}", 'troca'))
P.append(("case 'anexaFicha':", "      case 'auraFicha':{",
"""      case 'anexaFicha':{const eq=e.campo.find(q=>q.k===it.k),tk=e.campo.filter(q=>q.tok&&xInfo(q).cri).slice(-1)[0];if(!eq||!tk){feito.push('não deu pra anexar');break;}eq.an=tk.k;feito.push(`${eq.n} foi anexado a ${tk.n}`);break;}
""", 'antes'))

# ---------- L71. BUG: Pump/PumpAll perpétuo ou permanente (Duration Perpetual/Permanent) acabava no fim do turno ----------
# Vladimir and Godfrey, Mace of Disruption, Davriel's Withering, Blighted Nightmare, Mycoid Resurrection, Begin Anew, By Elspeth's Command, Jaheira...
P.append(("/* pump perpétuo */", "  /* AtEOT em ficha/pump */",
"""  /* pump perpétuo */if((api==='Pump'||api==='PumpAll')&&(d.Duration==='Perpetual'||d.Duration==='Permanent')&&!d.PumpZone&&!d.LeaveBattlefield){const d2=Object.assign({},d);delete d2.Duration;const r=fgPasso0(d2,api,ctx);
    if(r.length&&r.every(o=>o.op==='pump'&&!o.dbl||o.op==='kt'||o.op==='pumpTodos'&&!o.dbl&&!o.todasP))return r.map(o=>Object.assign({},o,{op:o.op==='pump'?'pumpPp':o.op==='kt'?'ktPp':'pumpTodosPp'}));}
""", 'antes'))
P.append(("else if(op==='pumpPp'){", "else if(op==='pumpN'){",
"else if(op==='pumpPp'){c.pP=(c.pP||0)+(x.p||0);c.pT=(c.pT||0)+(x.t||0);}else if(op==='ktPp'){c.pK=[...new Set([...(c.pK||[]),...(x.kws||[])])];}else if(op==='pumpN'){", 'troca'))
P.append(("case 'pumpPp':", "      case 'pumpN':case 'ktN':{",
"""      case 'pumpPp':case 'ktPp':{const k=t||it.k;if(!k){feito.push('sem alvo');break;}if(s.op==='pumpPp')xNoAlvo(k,'pumpPp',0,ev,{p:s.p,t:s.t});else xNoAlvo(k,'ktPp',0,ev,{kws:s.kws||[s.kw]});feito.push(`${xAlvoNome(k)} ${s.op==='pumpPp'?(s.p>=0?'+':'')+s.p+'/'+(s.t>=0?'+':'')+s.t:'ganha '+(s.kws||[s.kw]).map(x=>KPT[x]||x).join(', ')} pra sempre`);break;}
      case 'pumpTodosPp':{let q=0;e.campo.filter(c=>xCri(c)&&(!s.v||fgValid(c,s.v,{eu:me,src:it.k,sv:{}}))).forEach(c=>{c.pP=(c.pP||0)+(s.p||0);c.pT=(c.pT||0)+(s.t||0);if(s.kw&&s.kw.length)c.pK=[...new Set([...(c.pK||[]),...s.kw])];q++;});feito.push(`${q} criatura(s) suas ${s.p||s.t?(s.p>=0?'+':'')+s.p+'/'+(s.t>=0?'+':'')+s.t:''}${s.kw&&s.kw.length?' ganham '+s.kw.map(x=>KPT[x]||x).join(', '):''} pra sempre`);break;}
""", 'antes'))

# ---------- L72. BUG: "exile todas ... até esta carta sair do campo" (ChangeZoneAll Duration UntilHostLeavesPlay) exilava pra sempre ----------
# Temporary Lockdown, Consulate Crackdown, Aligned Hedron Network, Planar Guide?...
P.append(("/* exílio em massa temporário */", "  /* AtEOT em ficha/pump */",
"""  /* exílio em massa temporário */if(api==='ChangeZoneAll'&&d.Duration==='UntilHostLeavesPlay'){const d2=Object.assign({},d);delete d2.Duration;const r=fgPasso0(d2,api,ctx);if(r.length===1&&r[0].op==='zonas'&&r[0].og==='campo'&&r[0].ds==='exi')return [Object.assign({},r[0],{ate:1})];if(d.Origin==='Battlefield')return nao('exílio até sair do campo');return r;}
""", 'antes'))
P.append(("case 'zonas':{if(s.ate){", "      case 'zonas':{const os=",
"      case 'zonas':{if(s.ate){s=Object.assign({},s,{h:it.k});const hh=e.campo.find(q=>q.k===it.k);if(hh)hh.exO=1;}const os=", 'troca'))
P.append(("if(v.h&&v.ds==='exi'){", "  if(v.og==='campo'){for(const c of e.campo.slice())if(ok(c)){n++;xSai(c,v.ds);}}",
"  if(v.og==='campo'){for(const c of e.campo.slice())if(ok(c)&&c.k!==v.h){n++;const k0=c.k;xSai(c,v.ds);if(v.h&&v.ds==='exi'){const z=e.exi.find(q=>q.k===k0)||e.exi[e.exi.length-1];if(z)z.exAte=v.h;}}}", 'troca'))

# ---------- L73. BUG: Pump "enquanto você controlar esta" (AsLongAsControl) e "enquanto esta ficar virada" (UntilUntaps) acabava no fim do turno ----------
# Aegis Angel, Kyodai Soul of Kamigawa, Tale of Tinúviel, Ashnod's Battle Gear, Endoskeleton, Spirit Shield, Flamestick/Pearlspear/Frightshroud Courier...
P.append(("/* pump preso à fonte */", "  /* AtEOT em ficha/pump */",
"""  /* pump preso à fonte */if(api==='Pump'&&(d.Duration==='AsLongAsControl'||d.Duration==='UntilUntaps')&&!d.AtEOT){const d2=Object.assign({},d);delete d2.Duration;const r=fgPasso0(d2,api,ctx);if(r.some(o=>o.op==='nao'))return r;
    if(r.length&&r.every(o=>o.op==='pump'&&!o.dbl||o.op==='kt')){const m=d.Duration==='UntilUntaps'?'tap':'ctl';return r.map(o=>Object.assign({},o,{op:'pumpH',m,p:o.op==='pump'?o.p:0,t:o.op==='pump'?o.t:0,kws:o.op==='kt'?(o.kws||[o.kw]):(o.kw||[])}));}return nao('enquanto durar a fonte');}
""", 'antes'))
P.append(("for(const b of xHB(c)){", "(c.kwC||[]).forEach(x=>kw.add(x));",
"(c.kwC||[]).forEach(x=>kw.add(x));for(const b of xHB(c)){p+=b.p||0;t+=b.t||0;(b.kws||[]).forEach(x=>kw.add(x));}", 'troca'))
P.append(("const xHB=c=>", "function xLadoCampo(c){",
"""const xHB=c=>{if(!c.hB||!c.hB.length)return [];const ach=k=>((X.eu||{}).campo||[]).find(x=>x.k===k)||xOpCampos().map(([cp])=>cp.find(x=>x.k===k)).find(Boolean);c.hB=c.hB.filter(b=>{const q=ach(b.s);return q&&(b.m!=='tap'||q.tap);});return c.hB;};
function xLadoCampo(c){""", 'troca'))
P.append(("'kwC','fin','hB',", "'kwC','fin',", "'kwC','fin','hB',", 'troca'))
P.append(("else if(op==='pumpH'){", "else if(op==='pumpN'){",
"else if(op==='pumpH'){c.hB=[...(c.hB||[]),{s:x.s,m:x.m,p:x.p||0,t:x.t||0,kws:x.kws||[]}];}else if(op==='pumpN'){", 'troca'))
P.append(("case 'pumpH':", "      case 'pumpN':case 'ktN':{",
"""      case 'pumpH':{const k=t||it.k;if(!k){feito.push('sem alvo');break;}xNoAlvo(k,'pumpH',0,ev,{s:it.k,m:s.m,p:s.p,t:s.t,kws:s.kws});feito.push(`${xAlvoNome(k)} ${s.p||s.t?(s.p>=0?'+':'')+s.p+'/'+(s.t>=0?'+':'')+s.t+' ':''}${s.kws&&s.kws.length?'ganha '+s.kws.map(x=>KPT[x]||x).join(', ')+' ':''}${s.m==='tap'?'enquanto '+it.nm+' ficar virada':'enquanto você controlar '+it.nm}`);break;}
""", 'antes'))

# ---------- L74. BUG: carta animada não contava como criatura nos filtros (fgTem) nem no "destrua todas as criaturas"; e o Animate ignorava a cor (Colors$/OverwriteColors$): terreno-criatura "verde" continuava incolor pra proteção, "destrua criatura não preta" etc. ----------
# Celestial Colonnade, Raging Ravine, Creeping Tar Pit, Golgari Keyrune, Genju of the Spires, Cave of the Frost Dragon, Mutavault (Colorless)...
P.append(("/* cor no animar */", "  /* AtEOT em ficha/pump */",
"""  /* cor no animar */if(api==='Animate'&&d.Colors&&!ctx.__cor){const cs=String(d.Colors).split(',').map(x=>x.trim());let cor='';for(const x of cs){if(x==='Colorless')continue;if(!FGCOR[x]){cor=null;break;}cor+=FGCOR[x];}if(cor!=null&&(cs.length===1||!cs.includes('Colorless'))){ctx.__cor=1;let r;try{r=fgPasso0(d,api,ctx);}finally{delete ctx.__cor;}if(r.some(o=>o.op==='nao'))return r;return r.map(o=>o.op==='anima'?Object.assign({},o,{cor,ow:d.OverwriteColors==='True'?1:0}):o);}}
""", 'antes'))
P.append(("if(x.cor!=null){c.ani.cor=", "if(x.gan)c.ani.gan=x.gan;}",
"if(x.gan)c.ani.gan=x.gan;if(x.cor!=null){c.ani.cor=x.cor;c.ani.ow=x.ow?1:0;}}", 'troca'))
P.append(("gan:s.gan,cor:s.cor,ow:s.ow});", "rt:s.rt,rc:s.rc,gan:s.gan});", "rt:s.rt,rc:s.rc,gan:s.gan,cor:s.cor,ow:s.ow});", 'troca'))
P.append(("if(c.ani&&c.ani.cor!=null){", "function fgCores(c){if(c.tok&&!c.cp)return new Set(c.cor?String(c.cor).split(''):[]);return new Set(String(xInfo(c).custo||'').match(/[WUBRG]/g)||[]);}",
"function fgCores(c){const b=c.tok&&!c.cp?new Set(c.cor?String(c.cor).split(''):[]):new Set(String(xInfo(c).custo||'').match(/[WUBRG]/g)||[]);if(c.ani&&c.ani.cor!=null){const n=new Set(String(c.ani.cor).split('').filter(Boolean));if(c.ani.ow)return n;n.forEach(x=>b.add(x));}return b;}", 'troca'))

P.append(("if(w==='Creature')return !!i.cri||!!(c.ani&&c.ani.cri);", "if(w==='Creature')return !!i.cri;", "if(w==='Creature')return !!i.cri||!!(c.ani&&c.ani.cri);", 'troca'))
P.append(("const ok=tipo==='creatures'?xCri(c):", "const ok=tipo==='creatures'?i.cri:", "const ok=tipo==='creatures'?xCri(c):", 'troca'))
# ---------- L75. BUG: carta animada (terreno-criatura) não levava dano, não era alvo de "criatura alvo" nos efeitos e ficava fora de "dano em cada criatura" ----------
# Mutavault, Celestial Colonnade, Raging Ravine, Mishra's Factory, Gideon (criatura no turno), Gearhulks animados?... contra Lightning Bolt, Pyroclasm, Murder...
P.append(("else if(i.cri||(c.ani&&c.ani.cri)){c.dn=", "if(i.pw&&!i.cri){c.mk=Object.assign({},c.mk);c.mk.lealdade=(c.mk.lealdade||0)-n;}else if(i.cri){c.dn=",
"if(i.pw&&!i.cri&&!(c.ani&&c.ani.cri)){c.mk=Object.assign({},c.mk);c.mk.lealdade=(c.mk.lealdade||0)-n;}else if(i.cri||(c.ani&&c.ani.cri)){c.dn=", 'troca'))
P.append(("const ok=(c,lado)=>{const i=xInfo(c),cri=xCri(c),", "const ok=(c,lado)=>{const i=xInfo(c),cri=i.cri,", "const ok=(c,lado)=>{const i=xInfo(c),cri=xCri(c),", 'troca'))
P.append(("const ok=tp==='creature'?xCri(c):", "const ok=tp==='creature'?i.cri:tp==='land'", "const ok=tp==='creature'?xCri(c):tp==='land'", 'troca'))
P.append(("if(x==='noncreature')return !xCri(c);", "if(x==='noncreature')return !i.cri;if(x==='creature'||x==='creatures')return i.cri;", "if(x==='noncreature')return !xCri(c);if(x==='creature'||x==='creatures')return xCri(c);", 'troca'))
P.append(("if(c.k!==menos&&xCri(c))xEfCarta", "if(c.k!==menos&&xInfo(c).cri)xEfCarta(c,'dano',n);}", "if(c.k!==menos&&xCri(c))xEfCarta(c,'dano',n);}", 'troca'))
P.append(("xFilV(v.v,v.de,c=>{if(xCri(c))xEfCarta(c,'dano',v.n);});else xTodosDano", "xFilV(v.v,v.de,c=>{if(xInfo(c).cri)xEfCarta(c,'dano',v.n);});else xTodosDano(v.n);X.__dsn='';}else if(v.op==='danoTodos')v.v?xFilV(v.v,v.de,c=>{if(xInfo(c).cri)xEfCarta(c,'dano',v.n);})",
"xFilV(v.v,v.de,c=>{if(xCri(c))xEfCarta(c,'dano',v.n);});else xTodosDano(v.n);X.__dsn='';}else if(v.op==='danoTodos')v.v?xFilV(v.v,v.de,c=>{if(xCri(c))xEfCarta(c,'dano',v.n);})", 'troca'))
P.append(("else if(v.op==='autoDano'){for(const c of e.campo.slice())if(xCri(c)){", "else if(v.op==='autoDano'){for(const c of e.campo.slice())if(xInfo(c).cri){", "else if(v.op==='autoDano'){for(const c of e.campo.slice())if(xCri(c)){", 'troca'))

P.append(('return c?{p:xCri(c)?xPT(c).p:0,t:xCri(c)?xPT(c).t:0,', 'return c?{p:xInfo(c).cri?xPT(c).p:0,t:xInfo(c).cri?xPT(c).t:0,', 'return c?{p:xCri(c)?xPT(c).p:0,t:xCri(c)?xPT(c).t:0,', 'troca'))
P.append(('it.exc=c&&xCri(c)?', 'it.exc=c&&i.cri?', 'it.exc=c&&xCri(c)?', 'troca'))
P.append(("xFilV(s.v,me,c=>{if(xCri(c))xEfCarta(c,'dano',n);});", "xFilV(s.v,me,c=>{if(xInfo(c).cri)xEfCarta(c,'dano',n);});", "xFilV(s.v,me,c=>{if(xCri(c))xEfCarta(c,'dano',n);});", 'troca'))
P.append(('const c0=xAchaK(t||it.k);if(c0&&xCri(c0)){const v0=xPT(c0);', 'const c0=xAchaK(t||it.k);if(c0&&xInfo(c0).cri){const v0=xPT(c0);', 'const c0=xAchaK(t||it.k);if(c0&&xCri(c0)){const v0=xPT(c0);', 'troca'))
P.append(("else if(q.op==='rpPumpVen'){if(u===me){const v=e.ven||0;e.campo.forEach(c=>{if(xCri(c)){", "else if(q.op==='rpPumpVen'){if(u===me){const v=e.ven||0;e.campo.forEach(c=>{if(xInfo(c).cri){", "else if(q.op==='rpPumpVen'){if(u===me){const v=e.ven||0;e.campo.forEach(c=>{if(xCri(c)){", 'troca'))
P.append(("case 'autoDano':{for(const c of e.campo.slice())if(xCri(c)){", "case 'autoDano':{for(const c of e.campo.slice())if(xInfo(c).cri){", "case 'autoDano':{for(const c of e.campo.slice())if(xCri(c)){", 'troca'))
# ---------- L76. Animada = criatura também em: filtro de poder/resistência/habilidade, maior poder, poder da própria carta, vínculo/toque mortal/infectar de quem causa dano, "criatura morreu", shroud/hexproof, sacrifício e P/R na tela ----------
# Mutavault, Hissing Quagmire (toque mortal), Restless Vents, Celestial Colonnade, Mishra's Factory, Lavaclaw Reaches...
P.append(("const n=m[1]==='cmc'?xMVc(c):xCri(c)?xPT(c)[m[1]==='power'?'p':'t']:0;", "const n=m[1]==='cmc'?xMVc(c):xInfo(c).cri?xPT(c)[m[1]==='power'?'p':'t']:0;", "const n=m[1]==='cmc'?xMVc(c):xCri(c)?xPT(c)[m[1]==='power'?'p':'t']:0;", 'troca'))
P.append(('if(m=p.match(/^with(.+)$/))return xCri(c)?xPT(c).kw', 'if(m=p.match(/^with(.+)$/))return xInfo(c).cri?xPT(c).kw', 'if(m=p.match(/^with(.+)$/))return xCri(c)?xPT(c).kw', 'troca'))
P.append(("if(p==='greatestPower'||p==='leastPower'){if(!xCri(c))return false;const P=xPT(c).p,L=fgTodos().filter(q=>xCri(q))", "if(p==='greatestPower'||p==='leastPower'){if(!xInfo(c).cri)return false;const P=xPT(c).p,L=fgTodos().filter(q=>xInfo(q).cri)", "if(p==='greatestPower'||p==='leastPower'){if(!xCri(c))return false;const P=xPT(c).p,L=fgTodos().filter(q=>xCri(q))", 'troca'))
P.append(('const c=xAchaK(ctx.src);n=c&&xCri(c)?xPT(c)', 'const c=xAchaK(ctx.src);n=c&&xInfo(c).cri?xPT(c)', 'const c=xAchaK(ctx.src);n=c&&xCri(c)?xPT(c)', 'troca'))
P.append(('kw=sc&&xCri(sc)?xPT(sc).kw:new Set();', 'kw=sc&&xInfo(sc).cri?xPT(sc).kw:new Set();', 'kw=sc&&xCri(sc)?xPT(sc).kw:new Set();', 'troca'))
P.append(("const cg=xAchaK(t);if(cg&&xCri(cg)){xNoAlvo(t,'cnt',-n,ev);", "const cg=xAchaK(t);if(cg&&xInfo(cg).cri){xNoAlvo(t,'cnt',-n,ev);", "const cg=xAchaK(t);if(cg&&xCri(cg)){xNoAlvo(t,'cnt',-n,ev);", 'troca'))
P.append(('const cnt=c.cnt||0,i=xInfo(c),cr0=!!i.cri||!!(c.ani&&c.ani.cri),tx=xNorm(i.tx,c.n),tok=c.tok&&!c.cp;', 'const cnt=c.cnt||0,i=xInfo(c),tx=xNorm(i.tx,c.n),tok=c.tok&&!c.cp;', 'const cnt=c.cnt||0,i=xInfo(c),cr0=!!i.cri||!!(c.ani&&c.ani.cri),tx=xNorm(i.tx,c.n),tok=c.tok&&!c.cp;', 'troca'))
P.append(('  if(cr0){xTT().mor++;', '  if(i.cri){xTT().mor++;', '  if(cr0){xTT().mor++;', 'troca'))
P.append(("const i=xInfo(c),kw=xCri(c)?xPT(c).kw:i.kws;if(kw.has('shroud'))", "const i=xInfo(c),kw=i.cri?xPT(c).kw:i.kws;if(kw.has('shroud'))", "const i=xInfo(c),kw=xCri(c)?xPT(c).kw:i.kws;if(kw.has('shroud'))", 'troca'))
P.append(("v.tipo==='cp'?(xCri(c)||xInfo(c).pw):v.tipo==='creature'?xCri(c):v.tipo==='permanent'?true:v.tipo==='nc'?!xCri(c)&&!xInfo(c).land:", "v.tipo==='cp'?(xInfo(c).cri||xInfo(c).pw):v.tipo==='creature'?xInfo(c).cri:v.tipo==='permanent'?true:v.tipo==='nc'?!xInfo(c).cri&&!xInfo(c).land:", "v.tipo==='cp'?(xCri(c)||xInfo(c).pw):v.tipo==='creature'?xCri(c):v.tipo==='permanent'?true:v.tipo==='nc'?!xCri(c)&&!xInfo(c).land:", 'troca'))
P.append(('  if(cp){const i=xInfo(c);\n    if(i.cri||xCri(c)){const v=xPT(c);', '  if(cp){const i=xInfo(c);\n    if(i.cri){const v=xPT(c);', '  if(cp){const i=xInfo(c);\n    if(i.cri||xCri(c)){const v=xPT(c);', 'troca'))

# ---------- L77. BUG: "ponha todas as criaturas de todos os cemitérios no campo sob seu controle" (ChangeZoneAll GainControl) devolvia cada uma pro campo do próprio dono ----------
# Grimoire of the Dead, Rise of the Dread Marn?, Liliana's Contract?, Profane Command?...
P.append(("/* zonas sob seu controle */", "  /* AtEOT em ficha/pump */",
"""  /* zonas sob seu controle */if(api==='ChangeZoneAll'&&d.GainControl==='True'&&d.Destination==='Battlefield'&&!ctx.__gcz){ctx.__gcz=1;let r;try{r=fgPasso0(d,api,ctx);}finally{delete ctx.__gcz;}if(r.length===1&&r[0].op==='zonas'&&/^(cem|exi)$/.test(r[0].og)&&r[0].quem==='todos'&&!d.ChangeNum&&!/You|Opp|Ctrl|Own|Remembered|Exiled|Top|Chosen|Targeted|Defender/.test(r[0].v||''))return [Object.assign({},r[0],{gc:1})];return r;}
""", 'antes'))
P.append(("if(s.gc&&s.quem==='todos'){", "      case 'zonas':{if(s.ate){",
"      case 'zonas':{if(s.gc&&s.quem==='todos'){xZonas(s);for(const u of Object.keys(X.ops||{}))ev({op:'daZ',og:s.og,v:s.v,pa:me,nm:it.nm},u);feito.push(`${s.v} de ${s.og==='cem'?'todos os cemitérios':'todos os exílios'} vêm pro seu campo`);break;}if(s.ate){", 'troca'))
P.append(("v.op==='daZ'", "  else if(v.op==='daV'){",
"""  else if(v.op==='daZ'){const cx={eu:xUid(),src:'',sv:{}},z=e[v.og]||[],M=z.filter(c=>{try{return fgValid(c,v.v,cx);}catch(er){return false;}});for(const c of M){z.splice(z.indexOf(c),1);xEvia({op:'recebe',c:JSON.parse(JSON.stringify(xReset(c))),dn:xUid(),para:v.pa});}if(M.length)xLog(`${v.nm} (${xNomeU(v.de)}): ${M.length} carta(s) sua(s) foram pro campo dele`);xSobe();xPintaEu();}
  else if(v.op==='daV'){""", 'troca'))

# ---------- L78. BUG: "ponha todas ... no campo viradas" (ChangeZoneAll Tapped$ True) entravam desviradas ----------
# Planar Birth, Aftermath Analyst, Hedge Shredder, Splendid Reclamation?, Brought Back?, Wake the Dead?...
P.append(("/* zonas virada */", "  /* AtEOT em ficha/pump */",
"""  /* zonas virada */if(api==='ChangeZoneAll'&&d.Tapped==='True'&&d.Destination==='Battlefield'&&!ctx.__tpz){ctx.__tpz=1;let r;try{r=fgPasso0(d,api,ctx);}finally{delete ctx.__tpz;}return r.map(o=>o.op==='zonas'&&o.ds==='campo'?Object.assign({},o,{tap:1}):o);}
""", 'antes'))
P.append(("M.forEach(c=>{c.tap=v.tap?1:0;", "const M=v.emb?xEmb(L):L;if(v.ds==='campo')M.forEach(c=>{c.tap=0;e.campo.push(c);xEntrou(c);});",
"const M=v.emb?xEmb(L):L;if(v.ds==='campo')M.forEach(c=>{c.tap=v.tap?1:0;e.campo.push(c);xEntrou(c);});", 'troca'))

# ---------- L79. BUG: turno extra ignorava o número (NumTurns$ 2/X) e o jogador-alvo ----------
# Time Stretch, Teferi Master of Time (ult), Ral Zarek (X por moedas)?, Sage of Hours (X), Stitch in Time...
P.append(("case 'AddTurn':{", "    case 'AddTurn':return [{op:'extra'}];",
"""    case 'AddTurn':{const n=d.NumTurns==null?1:N('NumTurns');if(n==null)return nao('número de turnos');if(al&&/^(Player|Opponent)$/.test(d.ValidTgts||''))return put({op:'extra',n,al},[]);if(d.Defined&&d.Defined!=='You')return nao('turno extra pra outro');return [{op:'extra',n}];}""", 'troca'))
P.append(("const ux=String(t||'').startsWith('P:')", "      case 'extra':{const sx=X.sala||{};xSala({ext:Object.assign({},sx.ext,{[me]:((sx.ext||{})[me]||0)+1})});feito.push('vai jogar um turno extra');break;}",
"""      case 'extra':{const ux=String(t||'').startsWith('P:')?String(t).slice(2):me,nn=typeof n==='number'?n:1;if(!(nn>0)){feito.push('nenhum turno extra');break;}const sx=X.sala||{};xSala({ext:Object.assign({},sx.ext,{[ux]:((sx.ext||{})[ux]||0)+nn})});feito.push(`${ux===me?'vai jogar':xNomeU(ux)+' vai jogar'} ${nn>1?nn+' turnos extras':'um turno extra'}`);break;}""", 'troca'))

# ---------- L80. BUG: "ponha no campo virada e atacando" (ChangeZone Attacking$ True) entrava parada ----------
# Minion of the Mighty, Arni Metalbrow, Preeminent Captain, Paladin Elizabeth Taggerdy, Warcry Phoenix, Nemesis Phoenix, Phoenix Chick, Grim Reaper?, Alesha...
P.append(("/* entra atacando */", "  /* AtEOT em ficha/pump */",
"""  /* entra atacando */if(api==='ChangeZone'&&d.Attacking==='True'&&d.Destination==='Battlefield'&&!ctx.__atq){ctx.__atq=1;let r;try{r=fgPasso0(d,api,ctx);}finally{delete ctx.__atq;}return r.map(o=>/^(tutor|doCem|doCemAlvo)$/.test(o.op)&&(o.dest==='campo'||o.op!=='tutor'&&!o.dest)?Object.assign({},o,{atq:1}):o);}
""", 'antes'))
P.append(("const xAtq=c=>", "function xLadoCampo(c){",
"""const xAtq=c=>{const s=X.sala||{};c.tap=1;if(s.fase===2&&xVez()){const a=(((X.eu||{}).campo||[]).find(q=>q.atk&&q.alv&&q!==c)||{}).alv;c.atk=2;c.alv=a||('P:'+xOutro());xLog(`${c.n} entrou atacando`);}};
""", 'antes'))
P.append(("e.campo.push(c);if(s.wc)xWc(c,s.wc);if(s.atq)xAtq(c);setTimeout", "e.campo.push(c);if(s.wc)xWc(c,s.wc);setTimeout(()=>xEntrou(c),450);", "e.campo.push(c);if(s.wc)xWc(c,s.wc);if(s.atq)xAtq(c);setTimeout(()=>xEntrou(c),450);", 'troca'))
P.append(("e.campo.push(c);if(s.wc)xWc(c,s.wc);if(s.atq)xAtq(c);if(s.cnt){", "e.campo.push(c);if(s.wc)xWc(c,s.wc);if(s.cnt){", "e.campo.push(c);if(s.wc)xWc(c,s.wc);if(s.atq)xAtq(c);if(s.cnt){", 'troca'))
P.append(("if(d==='campo'){c.tap=s.tap?1:0;e.campo.push(c);if(s.atq)xAtq(c);xEntrou(c);}", "confirm(`${nm}: ${c.n} é artefato. Pôr no campo? (se não, vai pra mão)`))?'campo':'mao'):s.dest;if(d==='campo'){c.tap=s.tap?1:0;e.campo.push(c);xEntrou(c);}",
"confirm(`${nm}: ${c.n} é artefato. Pôr no campo? (se não, vai pra mão)`))?'campo':'mao'):s.dest;if(d==='campo'){c.tap=s.tap?1:0;e.campo.push(c);if(s.atq)xAtq(c);xEntrou(c);}", 'troca'))

# ---------- L81. BUG: condição "CheckSVar$ X | SVarCompare$ GE1" (sem o prefixo Condition) era ignorada em 92 cartas: o efeito acontecia sempre ----------
# Tectonic Edge, Just Fate, Command of Unsummoning, Heavy Fog, Tapestry of the Ages, Endless Atlas, Glistening Sphere, Cult Conscript, Proctor of Potential, Rally the Troops...
P.append(("/* CheckSVar = condição */", "function fgPasso(d,api,ctx){/* compara com outra SVar */",
"function fgPasso(d,api,ctx){/* CheckSVar = condição */if(d.CheckSVar&&!d.ConditionCheckSVar){d=Object.assign({},d,{ConditionCheckSVar:d.CheckSVar,ConditionSVarCompare:d.SVarCompare||'GE1'});delete d.CheckSVar;delete d.SVarCompare;}/* compara com outra SVar */", 'troca'))

P.append(("b==='PlayerCountPropertyYou$HasPropertyBeenAttackedThisCombat'", "  if(b==='PlayerCountOpponents$HighestCardsInHand')return {q:'opMax',f:'nm',md};",
"""  if(b==='PlayerCountPropertyYou$HasPropertyBeenAttackedThisCombat')return {q:'fuiAtk',md};if(b==='PlayerCountOpponents$HighestCounters.Poison')return {q:'opMax',f:'ven',md};if(b==='PlayerCountOpponents$HighestCardsInGraveyard')return {q:'opMax',f:'cem',md};
  if(b==='PlayerCountOpponents$HighestCardsInHand')return {q:'opMax',f:'nm',md};""", 'troca'))
P.append(("if(v.f==='ven')return o.ven||0;", "if(v.f==='vida')return o.vida||0;if(v.f==='nm')return o.nm||0;", "if(v.f==='vida')return o.vida||0;if(v.f==='nm')return o.nm||0;if(v.f==='ven')return o.ven||0;if(v.f==='cem')return (o.cem||[]).length;", 'troca'))
P.append(("v.q==='fuiAtk'?", ":v.q==='rand'?", ":v.q==='fuiAtk'?(xOpCampos().some(([cp])=>cp.some(c=>c.atk&&c.alv==='P:'+xUid()))?1:0)", 'antes'))
# ---------- L82. BUG: ficha "ganha ímpeto até o fim do turno" (Token PumpKeywords) vinha sem; "ganha a sua escolha de X ou Y" (Pump KWChoice) não dava nada; "volta pro campo transformada" (ChangeZone Transformed) voltava pela frente ----------
# Sokenzan, Mardu Monument, Old Hob, Alleycat Blues, Siege-Gang Lieutenant, Legion Warboss; Veteran Warleader, Alchemist's Gift, Assassin Initiate, Urza's Avenger; Startled Awake, Ojer Taq, Radiant Grace, Accursed Witch...
P.append(("/* ficha com habilidade até o fim do turno */", "  /* AtEOT em ficha/pump */",
"""  /* ficha com habilidade até o fim do turno */if(api==='Token'&&d.PumpKeywords&&!ctx.__tpk){const ks=String(d.PumpKeywords).split(' & ').map(x=>FGKW[x.trim()]);const du=d.PumpDuration||'EOT';ctx.__tpk=1;let r;try{r=fgPasso0(d,api,ctx);}finally{delete ctx.__tpk;}if(r.some(o=>o.op==='nao')||ks.some(x=>!x)||!/^(EOT|EndOfTurn|Permanent)$/.test(du))return r;return r.map(o=>o.op==='ficha'?Object.assign({},o,du==='Permanent'?{kw:[...new Set([...(o.kw||[]),...ks])]}:{ktE:ks}):o);}
  /* habilidade à escolha */if(api==='Pump'&&d.KWChoice&&!ctx.__kc){const ks=String(d.KWChoice).split(',').map(x=>FGKW[x.trim()]);ctx.__kc=1;let r;try{r=fgPasso0(d,api,ctx);}finally{delete ctx.__kc;}if(r.some(o=>o.op==='nao')||ks.some(x=>!x)||d.Duration)return r;const p0=r.length===1&&r[0].op==='pump'?r[0]:null;if(p0&&p0.al)return [...r,{op:'ktEsc',ks,mesmo:1}];if(!r.length&&!d.ValidTgts&&(!d.Defined||d.Defined==='Self'))return [{op:'ktEsc',ks,si:1}];return r;}
  /* volta transformada */if(api==='ChangeZone'&&d.Transformed==='True'&&d.Destination==='Battlefield'&&!ctx.__trf){ctx.__trf=1;let r;try{r=fgPasso0(d,api,ctx);}finally{delete ctx.__trf;}return r.map(o=>/^(doCem|doCemAlvo)$/.test(o.op)?Object.assign({},o,{trf:1}):o);}
""", 'antes'))
P.append(("...(xx&&xx.ktE?{kt:xx.ktE}:{}),", "...(xx&&xx.tkD?{tkD:xx.tkD}:{}),", "...(xx&&xx.tkD?{tkD:xx.tkD}:{}),...(xx&&xx.ktE?{kt:xx.ktE}:{}),", 'troca'))
P.append(("case 'ktEsc':", "      case 'pumpN':case 'ktN':{",
"""      case 'ktEsc':{const k=t||it.k;if(!k){feito.push('sem alvo');break;}let kw=s.ks[0];if(!XBOT&&s.ks.length>1){const r=prompt(`${it.nm}: qual habilidade? ${s.ks.map((x,i)=>(i+1)+' = '+(KPT[x]||x)).join(', ')}`,'1');const q=parseInt(r,10);if(q>=1&&q<=s.ks.length)kw=s.ks[q-1];}xNoAlvo(k,'kt',0,ev,{kws:[kw]});feito.push(`${xAlvoNome(k)} ganha ${KPT[kw]||kw} até o fim do turno`);break;}
""", 'antes'))
P.append(("if(s.trf){c.face=1;c.sk=xInfo(c).cri?1:0;}if(s.atq)xAtq(c);setTimeout", "e.campo.push(c);if(s.wc)xWc(c,s.wc);if(s.atq)xAtq(c);setTimeout(()=>xEntrou(c),450);", "e.campo.push(c);if(s.wc)xWc(c,s.wc);if(s.trf){c.face=1;c.sk=xInfo(c).cri?1:0;}if(s.atq)xAtq(c);setTimeout(()=>xEntrou(c),450);", 'troca'))
P.append(("if(s.trf){c.face=1;c.sk=xInfo(c).cri?1:0;}if(s.atq)xAtq(c);if(s.cnt){", "e.campo.push(c);if(s.wc)xWc(c,s.wc);if(s.atq)xAtq(c);if(s.cnt){", "e.campo.push(c);if(s.wc)xWc(c,s.wc);if(s.trf){c.face=1;c.sk=xInfo(c).cri?1:0;}if(s.atq)xAtq(c);if(s.cnt){", 'troca'))


def aplica(s):
    feitos, pulados, falhou = [], [], []
    for marca, anc, novo, modo in P:
        if marca in s:
            if modo == 'troca' and anc in s and anc not in novo:
                falhou.append(('SUSPEITA (marca já existe mas a âncora da troca continua): '+marca, s.count(anc)))
            pulados.append(marca); continue
        if s.count(anc) != 1:
            falhou.append((marca, s.count(anc))); continue
        if modo in ('antes', 'depois') and anc.strip() and anc.strip() in novo:
            falhou.append(('TEXTO NOVO REPETE A ÂNCORA (modo '+modo+'): '+marca, 1)); continue
        if modo == 'antes': s = s.replace(anc, novo + anc)
        elif modo == 'depois': s = s.replace(anc, anc + novo)
        else: s = s.replace(anc, novo)
        feitos.append(marca)
        if marca not in s: falhou.append(('MARCA NÃO APARECE no texto novo: '+marca, 1))
    return s, feitos, pulados, falhou


if __name__ == '__main__':
    f = sys.argv[1]; s = open(f, encoding='utf-8').read()
    s, a, p, x = aplica(s)
    open(f, 'w', encoding='utf-8').write(s)
    print(f'aplicadas {len(a)}, já estavam {len(p)}, falharam {len(x)}')
    for m, c in x: print('  FALHOU (âncora achada', c, 'vezes):', m[:60])
