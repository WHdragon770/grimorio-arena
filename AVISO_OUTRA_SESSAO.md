# ⚠ AVISO PRA SESSÃO QUE GERA O index.html (leia antes do próximo build)

**De:** Claude do Steam Deck, a pedido do Edigar (27/11/2026)

O `index.html` publicado **mudou fora do seu local.html**. São 4 commits do Deck em cima do seu 01d0d5e:
`e117c8b`, `0025347`, `2dc7de3` (motor) e `79b557d` (patch). Se você rodar `build.py` sem atualizar o `local.html` antes, **as mudanças somem**.

## Como se atualizar
1. Baixe o patch: `ferramentas-deck/patch_x1_27.py` (deste repo).
2. Aplique no seu local.html: `python3 -I patch_x1_27.py ~/grimorio_mtg/arena/local.html`
   - Ele é reaplicável: cada seção tem uma marca; se já estiver aplicada, pula.
   - Tem que sair `falharam 0`. Se alguma âncora não bater (você mexeu no mesmo trecho), aplique aquela seção na mão, olhando o diff do commit.
3. Rode seu cob/tL1/mec e confira que nada caiu. Depois pode apagar este aviso e a pasta `ferramentas-deck/`.

## O que mudou (15 regras gerais, +590 cartas sem ⚠ no medidor do Deck, 77,2% → 78,9%)
- Gatilho atrasado no fim do combate (EndC) e no próximo final de turno de qualquer jogador (EndP), e o atrasado guarda o tc
- perdeQ/compraQ: jogador definido perde vida ou compra (controlador do alvo, jogador do gatilho...) com fgQuemJ/xQuemJ
- Dono da ficha: jogador alvo, cada oponente, cada jogador, jogador do gatilho (campo dq na op ficha)
- fgLembT: Pump/PutCounter/Regenerate nas cartas lembradas (lembT) ou na do gatilho (tk); no xFaz, lembT/vT viram uma cópia por carta com fixT
- Regenerar as suas que batem no filtro; ganhaJ: ganhar vida com jogador alvo, oponente alvo, cada jogador
- copiaTS com N cópias, Controller ausente e sub-habilidade; CopySpellAbility alvo sem TargetType
- pagaK: "a menos que você pague" com devolver/sacrificar/virar/descartar/descartar ao acaso/exilar do cemitério/moer; UnlessCost numérico em SVar vira pagaOu
- maoJogaV: conjurar da mão sem pagar com filtro Valid + ValidSA (cmcLE N ou X)
- fgConta3: Remembered$Valid (q remV), Count$TopOfLibraryCMC (topoMV), Discarded$Amount
- cemBib: do cemitério pro grimório (topo, fundo, posição, embaralhar)
- Explore (op explora), FlipCoin (op moeda)
- Prevenção de dano no/do alvo da parte anterior (Effect RememberObjects$ Targeted sem ValidTgts: prevC/prevD com mesmo)

Testes no Deck: mesa de execução dos 24 decks igual antes e depois (1940 ok, 30 parciais, 0 travam). As 570+ cartas novas executam sem travar. Conferi o resultado de Hideous End, Healing Leaves, Hunted Dragon, Cinder Wall, Murderous Rider, Ixalli's Diviner, Bog Elemental, Sram's Expertise e Maze of Ith.

Achado: o motor não dispara gatilho de bloqueio (Mode$ Blocks / AttackerBlocked). Cinder Wall, Aether Membrane e Sawtooth Ogre dependem disso pra funcionar na partida.
