# Mapeamento do Sistema — Entrada, Processamento, Saída e Estado

Análise do programa do Grau A (show de boas-vindas do robô humanoide via YanAPI).
Sempre que um item depender de confirmação prática com o robô, está marcado como **[a confirmar]**.

## Visão geral do fluxo

```
ENTRADA                    PROCESSAMENTO                     SAÍDA                       ESTADO
-----------------------    ------------------------------    ------------------------    ------------------------
Câmera: rostos          →  contar_rostos_em (parse JSON)  →  show (movimento+voz+LED) →  acenos, ultimo_aceno
Câmera: gesto "good"    →  regra: limiar + cooldown       →  parada + desculpas          (variáveis do loop)
Bateria                 →  mao_levantada (busca "good")   →  música ou TTS de fallback
Lista de músicas        →  sequenciamento do show         →  console (logs)
Ctrl+C                  →  com_seguranca (erros ocultos)  →  limpeza no finally
```

## 1. Entrada

| # | Fonte | Mecanismo (API / função) | Dado obtido | Onde é consumido |
|---|---|---|---|---|
| E1 | Câmera do robô | `YanAPI.sync_do_face_recognition(type="quantity")` | JSON com a quantidade de rostos visíveis | Loop principal em `main()` |
| E2 | Câmera do robô | `YanAPI.sync_do_gesture_recognition()` | Presença do gesto `"good"` (mão levantada) | `apresentar()` e `dancar_hiphop()` |
| E3 | Sensor de bateria | `YanAPI.get_robot_battery_value()` | Percentual de bateria | `checar_bateria()` (uma vez, no início) |
| E4 | Biblioteca de mídia do robô | `YanAPI.get_media_music_list()` | Lista de músicas disponíveis | `tocar_musica()` (verifica se `hiphop.mp3` existe) |
| E5 | Configuração do programa | Constantes no topo do arquivo (`LIMIAR_ROSTOS`, `COOLDOWN`, velocidades etc.) | Parâmetros de comportamento | Todo o programa |
| E6 | Usuário no teclado | `KeyboardInterrupt` (`Ctrl+C`) | Comando de encerramento | `main()` (dispara o `finally`) |

## 2. Processamento

| # | Etapa | Função / local | O que faz |
|---|---|---|---|
| P1 | Interpretação do retorno da API | `contar_rostos_em()` | Varredura **recursiva e defensiva** do JSON: procura inteiros em chaves com `num`/`count`/`quantity`/`total`, listas em chaves com `face` e dicionários aninhados; devolve o maior total encontrado |
| P2 | Decisão de disparo do show | `main()` | Dispara o show se `n_rostos >= LIMIAR_ROSTOS` **e** `agora - ultimo_aceno >= COOLDOWN` |
| P3 | Detecção de gesto | `mao_levantada()` | Percorre os valores do retorno e considera "mão levantada" se algum for a string `"good"` (sem diferenciar maiúsculas) |
| P4 | Casamento de música | `tocar_musica()` | Compara o nome procurado com os itens da lista (sem extensão, sem diferenciar maiúsculas); se não achar, ativa o **fallback** de cantar via TTS |
| P5 | Sequenciamento do show | `apresentar()` | Ordem fixa: checar gesto → acenar/falar → checar gesto → agachar/levantar braços → dançar → voltar à pose |
| P6 | Controle da coreografia | `dancar_hiphop()` | Itera `REPETIR_HIPHOP` × `DANCA_HIPHOP`; **antes de cada movimento** checa `mao_levantada()`; sem música, escolhe o trecho da letra pelo índice (`% len(LETRA_HIPHOP)`) |
| P7 | Temporização | `time.time()` / `time.sleep()` | Cooldown (8 s), intervalo do loop (0,5 s), pausas de fala (0,7 s) e de sequência (0,5 s) |
| P8 | Robustez | `com_seguranca()` | Envolve cada chamada de API em `try/except` que **engole a exceção** — o show continua mesmo se uma chamada falhar |
| P9 | Encerramento limpo | `finally` em `main()` | Para reconhecimento facial, música e TTS; apaga LED; retorna à pose inicial |

## 3. Saída

| # | Canal | API | Efeito produzido |
|---|---|---|---|
| S1 | Movimento | `sync_play_motion` | Aceno (`wave`), abertura (`crouch`, `raise`), desculpas (`bend`), volta à pose (`reset`) e os 8 movimentos de dança (`rightmovestep`, `H_RBox`, `leftmovestep`, `GangnamStyle`, `H_Wave_R`, `H_Wave_L`, `LittleApple`, `Victory`) |
| S2 | Voz (TTS) | `start_voice_tts` / `sync_do_tts` | Saudação ("Ola... mestre!"), anúncio do show, trechos da letra (fallback) e pedido de desculpas |
| S3 | LED do robô | `set_robot_led` | Azul piscando (monitorando) → verde (rosto detectado) → ciano piscando (dançando) → vermelho piscando (desculpas) → azul off (fim) |
| S4 | Áudio | `start_play_music` / `stop_play_music` | Toca/para `hiphop.mp3` |
| S5 | Configuração | `set_robot_volume_value` | Fixa o volume em 100 |
| S6 | Console | `print` | Logs de status: conexão, bateria, música encontrada (ou não), interrupções |
| S7 | Reconhecimento | `stop_face_recognition` | Encerra a sessão de reconhecimento na saída |

## 4. Estado

| # | Estado | Tipo | Onde vive | Papel |
|---|---|---|---|---|
| X1 | `acenos` | Variável local (`int`) | `main()` | Contador de shows já executados; com `MAX_ACENOS = 0` o loop é infinito |
| X2 | `ultimo_aceno` | Variável local (`float`) | `main()` | Timestamp do último show; implementa o cooldown |
| X3 | `tocando` | Variável local (`bool`) | `dancar_hiphop()` | Indica se a música foi encontrada/tocada (define se usa TTS) |
| X4 | `"parado"` / `"concluido"` | Valor retornado | `dancar_hiphop()` → `apresentar()` | Sinaliza se o show foi interrompido (pula a volta à pose) |
| X5 | Constantes de configuração | Globais somente leitura | Topo do arquivo | Definem o comportamento de toda a execução |
| X6 | Máquina de estados implícita | — | Sequência do show + cores do LED | Monitorando → detectado → dançando → (parado/desculpando) → concluído |
| X7 | Estado externo do robô | No firmware do robô | Fora do programa | Bateria real, biblioteca de músicas, conectividade de rede, pose atual do robô, sessão de reconhecimento |

## Observações importantes

1. **Não há estado persistente.** Nada é gravado em disco ou banco: todo estado morre quando o programa termina (contador de acenos volta a zero a cada execução).
2. **O LED funciona como indicador visual do estado** — as cores coincidem com a máquina de estados implícita (X6), o que facilita demonstração e depuração.
3. **O reconhecimento facial nunca é iniciado explicitamente** — o código chama `sync_do_face_recognition` diretamente e só chama `stop_face_recognition` no `finally` (defensivo). O ciclo de vida da sessão é gerenciado pela própria API **[a confirmar]**.
4. **Estado pode ficar inconsistente em silêncio.** Como `com_seguranca()` engole exceções, `tocar_musica()` pode retornar `True` mesmo se `start_play_music` falhar — nesse caso o robô "dança sem música" e sem cantar **[a confirmar]**.
5. **Estado externo (X7) não é controlado pelo programa**: se a música não estiver no robô ou a bateria acabar no meio do show, o comportamento depende apenas dos mecanismos defensivos do código.