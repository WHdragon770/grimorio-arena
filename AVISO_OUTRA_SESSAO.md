# ⚠ AVISO PRA SESSÃO QUE GERA O index.html (leia antes do próximo build)

**De:** Claude do Steam Deck, a pedido do Edigar. Atualizado automaticamente a cada publicação do Deck.

O `index.html` publicado **mudou fora do seu local.html**: são os commits "X1 (Deck)" depois do seu 01d0d5e. Se você rodar `build.py` sem atualizar o `local.html` antes, **as mudanças somem**.

## Como se atualizar
1. Baixe o patch: `ferramentas-deck/patch_x1_27.py` (deste repo).
2. Aplique no seu local.html: `python3 -I patch_x1_27.py ~/grimorio_mtg/arena/local.html`
   - Ele é reaplicável: cada seção tem uma marca; se já estiver aplicada, pula. Pode rodar de novo a cada versão nova do patch.
   - Tem que sair `falharam 0`. Se alguma âncora não bater (você mexeu no mesmo trecho), aplique aquela seção na mão, olhando o diff do commit.
3. Rode seu cob/tL1/mec e confira que nada caiu. Depois pode apagar este aviso e a pasta `ferramentas-deck/`.

## Números (medidor do Deck: todos os 34480 scripts do Forge, partes SP/AB/capítulo/gatilho sem op nao)
- Antes (01d0d5e): 26629 (77.2%) · Agora: **27228 (79.0%)**, +599 cartas
- Cartas dos decks: 1342 → 1344 de 1378
- Mesa de execução dos 24 decks: igual antes e depois, 0 travam. Todas as cartas novas executam sem travar.

## O que mudou (14 seções do patch)
- **L1.** Gatilho atrasado no fim do combate (EndC) e no próximo final de turno de qualquer jogador (EndP) (ex.: Cinder Wall, Fog Elemental, Clockwork Beetle, Windscouter, Wicker Warcrawler...: só quando a cadeia usa a própria carta (sem "lembrado" do gatilho).)
- **L2.** Jogador definido pelo Forge perde vida / compra: controlador do alvo, jogador do gatilho, controlador da carta do gatilho (ex.: Hideous End, Liliana's Defeat, Vapor Snag, One Thousand Lashes, Doom Foretold, Curse of Wizardry, Gwafa Hazid, Dream Fracture, Super Intelligence...)
- **L3.** Dono da ficha definido pelo Forge: jogador alvo, cada oponente, cada jogador, jogador do gatilho (ex.: Hunted Dragon/Troll, Gravedig, Emeritus of Truce, Ashling's Command, Grismold, Elephant Resurgence, Questing Phelddagrif, Gonti, Dovescape...)
- **L4.** Efeito nas cartas lembradas (Remembered) e nas do gatilho: Pump/PutCounter/Regenerate; regenerar as suas que batem no filtro; ganhar vida: jogador alvo, oponente, cada jogador (ex.: Teysa, Strefan, Savage Order, Giant Regrowth, Fractal Harness, Body of Research, Golgari Charm, Wrap in Vigor, Healing Leaves, Titan of Industry, Soothing Balm...)
- **L5.** Copiar a mágica do gatilho: com escolha de novos alvos, N cópias, sub-habilidade depois; copiar mágica alvo sem TargetType (ex.: Gorion, Ertha Jo, Chandra Hope's Beacon, Thurid, Genesis Storm, Double Stroke, Bygone Marvels, Jaya, Mischievous Quanar, Lutri, Rootha...)
- **L6.** "... a menos que você pague": devolver/sacrificar/virar/descartar/exilar do cemitério/moer, e custo numérico em SVar (ex.: Dromar's Cavern, The Gitrog Monster, Bog Elemental, Treacherous Vampire, Pillaging Horde, Fallow Wurm, Quickling, Rogue Elephant, Fettergeist, Deep Spawn...)
- **L7.** Conjurar da mão sem pagar, com filtro (Valid + ValidSA, valor de mana fixo ou X) (ex.: Sram's/Yahenni's Expertise, Electrodominance, Coveted Prize, West Coast Expansion, Yue, Brazen Bluff, I Am Duskmourn, Maelstrom Archangel...)
- **L8.** Contas: quantas das lembradas batem no filtro (Remembered$Valid), valor de mana do topo do grimório, quantas descartou (ex.: Waste Management, Necron Monolith, Sins of the Father, Selvala's Enforcer, Storm Fleet Negotiator, Interpret the Signs, Judge Unworthy, Book Devourer...)
- **L9.** Do cemitério pro grimório (topo, fundo, posição N ou embaralhar): a própria carta ou a do gatilho (ex.: Murderous Rider, Lembas, Purity, Hostility, Dark Revenant, Avenging Angel, Moss-Pit Skeleton, Gate Colossus, Vengeful Pharaoh, Bookwurm...)
- **L10.** Explorar (Explore): a própria criatura, a do gatilho ou uma alvo; N vezes (ex.: Ixalli's Diviner, Path of Discovery, Legion Vanguard, Jadelight Ranger, Miner's Guidewing, Over the Edge, Seasoned Dungeoneer...)
- **L11.** Cara ou coroa (FlipCoin) com efeito de vitória e/ou derrota, sem alvo dentro (ex.: Tide of War, Planar Chaos, Stitch in Time, Mogg Assassin, Goblin Festival, Zndrsplt, Chaotic Goo...)
- **L12.** Prevenir dano do/no alvo da parte anterior (Effect RememberObjects$ Targeted sem alvo próprio) (ex.: Maze of Ith, Maze of Shadows, Elvish Scout, Delirium, Foxfire, Djeru's Resolve, Glyph of Destruction, Energy Arc, Telekinesis...)
- **L13.** Gatilhos de bloqueio: "Whenever this creature blocks" (ao confirmar os bloqueios), "becomes blocked" (lado do atacante), "attacks or blocks" (ex.: Cinder Wall, Fog Elemental, Clockwork Beetle, Sawtooth Ogre, Wall of Tears, Phantom Whelp, Kaijin..., atacantes com "becomes blocked")
- **L14.** SacrificeAll: a própria carta, as lembradas, ou todas as suas que batem no filtro (ex.: Fog Elemental, Mardu Blazebringer, Dorothea, Time Elemental, Doom Foretold, Callous Sell-Sword, Professor Onyx, Rite of Ruin, Death Pit Offering...)

## Achados
- O motor não disparava gatilho de bloqueio: agora dispara (L13) "When/Whenever this creature blocks" ao confirmar os bloqueios e "becomes blocked" do lado de quem ataca; "attacks or blocks" também vale no gatilho de ataque.
