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
      if(sb.api==='ChangeZone'&&sd.Defined==='Remembered'&&sd.Origin==='Exile'&&sd.Destination==='Battlefield'&&Object.keys(sd).every(k=>/^(DB|Defined|Origin|Destination|Transformed|Tapped|GainControl|SubAbility|StackDescription|SpellDescription)$/.test(k))){const sb2=sd.SubAbility?fgPP((ctx.sv||{})[sd.SubAbility]||''):null;
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
