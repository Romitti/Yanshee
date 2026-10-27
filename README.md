# Show de Boas-Vindas — Robô Humanoide (YanAPI)

Disciplina de **Robótica Humanoide e Inteligência Artificial**.

> **Nota:** este README descreve a **versão atual** do código. Será atualizado após a refatoração.

## Finalidade

Mantém o robô humanoide UBTech (via API **YanSDK / `YanAPI`**) monitorando o ambiente com **reconhecimento facial**. Ao detectar ao menos um rosto, executa um pequeno show de boas-vindas:

1. **Aceno e saudação** — movimento `wave` com fala de saudação (TTS);
2. **Abertura** — agacha, levanta os braços e anuncia o show;
3. **Dança hip-hop** — sequência de movimentos do catálogo do robô ao som de `hiphop.mp3`; se a música não for encontrada no robô, ele canta trechos via TTS;
4. **Mão levantada = parada** — se alguém fizer o gesto `good` durante o show, o robô interrompe música, movimento e fala, pisca o LED vermelho e pede desculpas;
5. Volta à pose inicial e continua monitorando (loop contínuo, com cooldown entre shows).

Indicação por LED: azul piscando (monitorando) → verde (rosto detectado) → ciano piscando (dançando) → vermelho piscando (pedindo desculpas).

## Estrutura

Script de arquivo único (nome do arquivo principal: *a confirmar*), com constantes de configuração no topo e funções organizadas por responsabilidade:

| Bloco | Funções | Papel |
|---|---|---|
| Conexão | `conectar()`, `checar_bateria()` | Inicializa a YanAPI e alerta bateria < 20% |
| Percepção | `detectar_rostos()`, `contar_rostos_em()`, `mao_levantada()` | Reconhecimento facial (tipo `quantity`) e de gesto (`good`), com leitura defensiva do JSON de retorno |
| Ação | `acenar_falando()`, `abaixar_e_levantar_bracos()`, `dancar_hiphop()`, `tocar_musica()`, `pedir_desculpas()`, `voltar_a_pose()` | Rotinas de movimento, fala, música e LED |
| Controle | `apresentar()`, `main()` | Orquestra o show e o loop de detecção |
| Utilidades | `com_seguranca()`, `led()` | Chamadas à API protegidas contra exceções e controle do LED |

## Ambiente

- **Hardware:** robô humanoide UBTech da família Yan (Alpha Mini ou compatível).
- **Software:** Python 3 com o pacote `YanAPI` (YanSDK da UBTech); além dele, apenas a biblioteca padrão (`time`).
  - Comando de instalação e versões: **a confirmar** (o repositório não possui arquivo de dependências).
- **Rede:** execução apontando `ROBOT_IP` para o robô — o padrão do código é `127.0.0.1`; **a confirmar** se o script roda no próprio robô ou em máquina externa.

## Configuração

| Constante | Padrão | Função |
|---|---|---|
| `ROBOT_IP` | `"127.0.0.1"` | IP do robô |
| `VOLUME` | `100` | Volume do alto-falante |
| `LIMIAR_ROSTOS` | `1` | Mínimo de rostos para disparar o show |
| `COOLDOWN` | `8.0` s | Intervalo mínimo entre shows |
| `INTERVALO` | `0.5` s | Pausa do loop de detecção |
| `MAX_ACENOS` | `0` | 0 = repete indefinidamente |
| `DEBUG` | `False` | Imprime os retornos crus da API |
| `TIPO_RECONHECIMENTO` | `"quantity"` | Modo do reconhecimento facial |
| `RAISE_HAND_STOP` | `True` | Habilita a parada por gesto |
| `VELOCIDADE_MOVIMENTO` / `VELOCIDADE_HIPHOP` | `"slow"` / `"fast"` | Velocidade das rotinas |
| `PAUSA_FALA` / `PAUSA_SEQUENCIA` | `0.7` / `0.5` s | Pausas entre falas e movimentos |
| `REPETIR_HIPHOP` | `1` | Repetições da coreografia |
| `MUSICA_HIPHOP` | `"hiphop.mp3"` | Música buscada no robô |
| `DANCA_HIPHOP` / `LETRA_HIPHOP` | listas | Movimentos da coreografia e trechos cantados (fallback) |

O arquivo `hiphop.mp3` precisa estar na lista de músicas do robô (busca por nome, sem extensão e sem diferenciar maiúsculas).

## Execução

```bash
python <arquivo_principal>.py   # nome do arquivo: a confirmar
```

1. Ajuste `ROBOT_IP` e ligue o robô (bateria e volume são conferidos no início da execução);
2. O loop fica em modo de detecção até um rosto aparecer;
3. Para encerrar: `Ctrl+C` — o robô para a música e o reconhecimento, apaga o LED e retorna à pose inicial;
4. Em caso de dúvida sobre os retornos da API, ativar `DEBUG = True`.

## Rotina crítica e plano de refatoração

A rotina mais difícil de manter é a **parada de emergência por mão levantada** (gesto `good`, via `sync_do_gesture_recognition()`). Foi o ponto mais trabalhoso do desenvolvimento e concentra a lógica mais frágil do programa.

### O problema: lógica espalhada em 3 pontos

| Local | Contexto | Comportamento atual |
|---|---|---|
| `apresentar()`, início | Antes do show começar | Pede desculpas e cancela o show |
| `apresentar()`, após o aceno | Meio do aceno | Para voz e movimento, pede desculpas |
| `dancar_hiphop()`, no loop | Antes de cada movimento | Para música, movimento e voz; retorna `"parado"` |

**Por quê é difícil de manter:**

- **Duplicação (*shotgun surgery*):** a condição `RAISE_HAND_STOP and mao_levantada()` e a sequência de paradas (`stop_play_music`, `stop_play_motion`, `stop_voice_tts`) repetem-se com ordens diferentes em cada ponto; qualquer ajuste exige editar 2–3 trechos e retestar o show inteiro no robô.
- **Parsing frágil e inconsistente:** `mao_levantada()` olha apenas **um nível** do JSON em busca da string `"good"`. Se a API aninhar o resultado do gesto (ex.: `{"data": {"gesture": [{"type": "good"}]}}`), a função devolve `False` — um **falso negativo numa função de segurança**. `contar_rostos_em()` é recursiva exatamente por causa dessa incerteza de formato; a função gêmea não é.
- **String mágica:** o gesto `"good"` está embutido no corpo da função, sem constante nomeada.
- **Checagens só entre movimentos:** durante um movimento longo o robô não reage ao gesto.

### Mudança proposta (pequena, preserva o comportamento)

Extrair a condição e a sequência de parada para **um único ponto de verdade**:

```python
GESTO_PARADA = "good"   # junto das constantes do topo

def pedido_de_parada():
    """Condicao de parada de emergencia, definida em um unico lugar."""
    return RAISE_HAND_STOP and mao_levantada()

def parar_show(mensagem):
    """Para toda a midia em execucao e pede desculpas."""
    com_seguranca(lambda: YanAPI.stop_play_music())
    com_seguranca(lambda: YanAPI.stop_play_motion(name=""))
    com_seguranca(lambda: YanAPI.stop_voice_tts())
    print(mensagem)
    pedir_desculpas()
```

Chamadas nos mesmos 3 pontos de hoje:

```python
# apresentar() — no inicio (nada esta tocando ainda)
if pedido_de_parada():
    print("Ja comecou com mao levantada! Pedindo desculpas antes de comecar.")
    pedir_desculpas()
    return

# apresentar() — depois do aceno
if pedido_de_parada():
    parar_show("Mao levantada no meio do aceno! Parando.")
    return

# dancar_hiphop() — antes de cada movimento
if pedido_de_parada():
    parar_show("Mao levantada! Parando o show e pedindo desculpas.")
    return "parado"
```

E, dentro de `mao_levantada()`, trocar o literal `== "good"` por `== GESTO_PARADA`.

**O que permanece idêntico:** verificações nos mesmos 3 pontos, mesmas mensagens de console (agora passadas como parâmetro) e mesmo resultado observável — tudo para e o robô pede desculpas.

**Única diferença interna:** a ordem das paradas é unificada numa sequência só; alguns pontos passam a emitir um `stop_play_music` a mais mesmo sem música tocando, e em `apresentar()` movimento/voz são parados na ordem inversa à atual. Como são comandos imediatos de parada e todos passam por `com_seguranca`, o efeito é nulo — nada observável muda.

**Ganho para a refatoração:** melhorias futuras da parada (varredura recursiva do JSON como já faz `contar_rostos_em()`, gesto alternativo, checagem durante o movimento) ficam concentradas em **uma função e uma constante**, em vez de três trechos espalhados pelo fluxo do show.

### Validação no robô (a confirmar)

- [ ] Confirmar com `DEBUG = True` o formato real do retorno de `sync_do_gesture_recognition` (nível de aninhamento e nome exato do campo do gesto).
- [ ] Testar os 3 pontos de disparo: mão levantada antes de começar, durante o aceno e no meio da dança.
- [ ] Confirmar que `stop_play_motion(name="")` interrompe o movimento corrente no firmware usado — se não interromper, a parada só vale entre movimentos.

## Limitações e pontos a confirmar

- **Formato das respostas da API:** a contagem de rostos e a detecção do gesto interpretam o JSON de forma genérica; validar com o retorno real do robô (`DEBUG = True`). Ver também a seção **Rotina crítica e plano de refatoração**.
- **Catálogo de movimentos:** nomes como `GangnamStyle`, `LittleApple` e `H_RBox` dependem do firmware do robô; se algum não existir, a chamada é ignorada e o show continua.
- **Tolerância a falhas:** erros durante o loop são silenciados (`com_seguranca`); não há reconexão automática nem registro de log.
- **TTS:** as falas usam `interrupt=False` com pausas fixas — podem se sobrepor em redes lentas. A fala de abertura inclui linguagem forte; ajustar conforme o contexto de apresentação.
- **Dependências e nome do script:** sem `requirements.txt`; nome do arquivo principal e modelo exato do robô **a confirmar**.
