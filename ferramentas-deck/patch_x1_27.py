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
