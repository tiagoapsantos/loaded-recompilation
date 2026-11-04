# Loaded PS1 → Windows: estado do projeto

Atualizado em 2026-11-04. O objetivo é uma versão Windows jogável do princípio ao fim, preservando a experiência e a velocidade originais da PlayStation. FPS mais altos e melhorias gráficas não são prioridades.

## Estado observado

- Menus, seleção de personagem, entrada no primeiro nível e movimento foram observados. A conclusão do nível e o combate ainda não estão validados.
- O utilizador confirmou o funcionamento do comando Xbox por USB, incluindo A/Cross e direita. DualShock 4 não foi validado fisicamente.
- A execução combina código nativo e interpretação; os testes de overlays não demonstram equivalência funcional completa.
- Foram medidos 150 VBlanks em 8,04 s (18,7 Hz), cerca de 31% dos 59,94 Hz de referência do runtime. Isto não mede o FPS de apresentação original do jogo.
- Perfil da build de diagnóstico no primeiro nível, peso direto das amostras: `raster_shaded_textured_triangle` 18,20%, `texel_fetch` 17,32%, `sw_render_display_hires` 8,14%, `sw_fill_rect` 7,85% e `exec_one_fetched_inner` 7,35%. Rasterização por software e interpretação MIPS são custos importantes; estas amostras não medem ganho de uma alteração.

## Próximo passo

Estudar uma otimização isolada da descodificação da página de textura por triângulo, seguida de comparação de VRAM e imagens no mesmo estado, cobrindo formatos de textura, janela e transparência. Não assumir equivalência gráfica nem melhoria antes de medir.

## Recuperação

Consultar [recovery/README.md](recovery/README.md) para revisão do PSXRecomp, patch, dependências, geração, build e execução. O patch preserva as cinco alterações atuais do checkout local; não garante que a build resultante seja idêntica ao executável jogável histórico. Capturas, código gerado, caches e ficheiros do jogo não são distribuídos; a recuperação exata depende desses dados locais ou da sua recriação.

A build jogável anterior é `build/loaded-probe/native_62000_isolated/Loaded___experimental.exe`; a build de profiling `build/loaded-profile/` é separada, com símbolos e opções de compilação diferentes. Nenhuma está incluída no repositório.
