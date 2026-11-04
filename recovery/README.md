# Recuperação do ambiente experimental

Este é um registo de recuperação, não uma garantia de build reproduzível bit a bit. A documentação anterior em `docs/recompiler-experiment.md` é histórica; consultar `PROJECT_STATUS.md` para o estado mais recente. Os comandos seguintes pressupõem Windows x64, Git, Python, CMake, Ninja e uma consola x64 de desenvolvimento do Visual Studio 2022/MSVC. Usam `E:/Recompille` como raiz e podem necessitar de ajustes locais.

## Framework e alterações

PSXRecomp: https://github.com/RetroPortingToolKit/psxrecomp.git, commit `c1f5cafd4102daa57b7342bec7c432aaca8981ce`. O framework tem licença PolyForm Noncommercial 1.0.0; rever a licença e as licenças das dependências antes de distribuir ou usar comercialmente. Não é submódulo deste repositório. O commit do framework referencia os submódulos públicos `lib/recomp-net` em `e53059306824edf4f0aec4aae5ae65151b18535f` e `lib/retcomm-rbengine` em `b29bdde642bc087f21303b827fadba40496b502d`; no checkout original estavam não inicializados. Inicializar apenas se uma funcionalidade necessitar deles.

Num diretório de trabalho novo, sem substituir um checkout existente:

```powershell
git clone https://github.com/RetroPortingToolKit/psxrecomp.git third_party/psxrecomp
git -C third_party/psxrecomp checkout c1f5cafd4102daa57b7342bec7c432aaca8981ce
git -C third_party/psxrecomp apply --check ../../patches/psxrecomp-c1f5cafd.patch
git -C third_party/psxrecomp apply ../../patches/psxrecomp-c1f5cafd.patch
```

O patch contém alterações de compatibilidade MSVC e instrumentação temporária das investigações de overlays em cinco ficheiros. Foi verificado contra o checkout local por `git apply --reverse --check`. Não se sabe se a build jogável histórica incorpora todas as alterações atuais.

## Dados e configuração

O utilizador fornece a sua própria imagem compatível de Loaded e o executável PS-X extraído em `disc/SLUS_000.76`. Não são fornecidos jogo, assets, código gerado, capturas de memória, DLLs de overlay ou caches. Usar o OpenBIOS disponibilizado pelo checkout do framework, sujeito à respetiva licença, e não publicar BIOS ou dumps de jogo.

`game.toml.example` preserva as opções observadas, inclusive `p1_device = "auto"`; substituir `<WORKSPACE>` pela raiz com barras `/` e `<OWN_CUE>` pelo caminho CUE local. Copiar para `build/loaded-probe/game.toml`. Copiar `seeds.txt` e `CMakeLists.txt` deste diretório para `build/loaded-probe/`; adaptar `PSXRECOMP_ROOT` no CMake se a raiz for diferente. As seeds são endereços heurísticos, não garantem cobertura. A geração anterior produziu avisos de fluxo e pré-passagem não convergente.

O runtime usa SDL3, zlib e libwebp; a configuração observada permite ao CMake obter dependências públicas. A disponibilidade das versões externas e ferramentas pode afetar a reprodução. O projeto de investigação da raiz tem build independente: `cmake -S . -B build/research` e `cmake --build build/research`.

## Geração e build experimental

A partir da raiz e após preparar os dados e ficheiros acima:

```powershell
cmake -S third_party/psxrecomp/recompiler -B build/psxrecomp2 -G Ninja -DCMAKE_BUILD_TYPE=Release -DPSXRECOMP_ENABLE_CHD=OFF
cmake --build build/psxrecomp2 --target psxrecomp-game
& build/psxrecomp2/psxrecomp-game.exe --config build/loaded-probe/game.toml
cmake -S build/loaded-probe -B build/loaded-native -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_SUPPRESS_REGENERATION=ON -DPSX_DEBUG_TOOLS=ON -DPSX_RECOMP_UI=OFF -DPSX_NETPLAY=OFF -DPSX_REWIND=OFF
cmake --build build/loaded-native
```

O CMake original apontava para `E:/Recompille/third_party/psxrecomp`. A build observada usou perfil `ENHANCED`, SDL3 e `/O2 /Ob2`; supressão de regeneração contornava um problema Ninja e obriga a reconfigurar explicitamente após alterar inputs. Estes comandos registam o procedimento e **não foram testados numa instalação limpa**. Dependências concretas, opções adicionais e geração dos overlays precisam de validação.

Exemplo de execução após localizar o executável gerado e preparar OpenBIOS e a cache local:

```powershell
& 'build/loaded-probe/native_62000_isolated/Loaded___experimental.exe' --game 'build/loaded-probe/game.toml' --bios 'build/loaded-probe/native_62000_isolated/bios/openbios.bin' --renderer software
```

Esse caminho é o da cópia jogável histórica, não necessariamente o destino da nova build. As caches isoladas dos overlays não estão versionadas; recriá-las a partir de capturas próprias exige ferramentas e entradas locais, e a respetiva equivalência não está comprovada. Sem essas capturas, a configuração exata da sessão anterior e os dados originais do disco, não é possível prometer reconstrução fiel.
