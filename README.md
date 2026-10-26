ROBO UBITECH yanshee com 1 GB de memória RAM
Data: 26/10/2026
Mantém o robô humanoide UBTech (via API YanSDK / YanAPI) monitorando o ambiente com reconhecimento facial. Ao detectar ao menos um rosto, executa um pequeno show de boas-vindas:

reconhecimento facial - após reconhecer uma face humana o robo inicia as proximas ações;
Aceno e saudação — movimento wave com fala de saudação (TTS);
Abertura — agacha, levanta os braços e anuncia o show;
Dança hip-hop — sequência de movimentos do catálogo do robô ao som de hiphop.mp3; se a música não for encontrada no robô, ele canta trechos via TTS;
Mão levantada = parada — se alguém fizer o gesto good durante o show, o robô interrompe música, movimento e fala, pisca o LED vermelho e pede desculpas;
Volta à pose inicial e continua monitorando (loop contínuo, com cooldown entre shows).
Indicação por LED: azul piscando (monitorando) → verde (rosto detectado) → ciano piscando (dançando) → vermelho piscando (pedindo desculpas).

Estrutura
Script de arquivo único (nome do arquivo principal: a confirmar), com constantes de configuração no topo e funções organizadas por responsabilidade:

Bloco	Funções	Papel
Conexão	conectar(), checar_bateria()	Inicializa a YanAPI e alerta bateria < 20%
Percepção	detectar_rostos(), contar_rostos_em(), mao_levantada()	Reconhecimento facial (tipo quantity) e de gesto (good), com leitura defensiva do JSON de retorno
Ação	acenar_falando(), abaixar_e_levantar_bracos(), dancar_hiphop(), tocar_musica(), pedir_desculpas(), voltar_a_pose()	Rotinas de movimento, fala, música e LED
Controle	apresentar(), main()	Orquestra o show e o loop de detecção
Utilidades	com_seguranca(), led()	Chamadas à API protegidas contra exceções e controle do LED
Ambiente
Hardware: robô humanoide UBTech da família Yan (Alpha Mini ou compatível).
Software: Python 3 com o pacote YanAPI (YanSDK da UBTech); além dele, apenas a biblioteca padrão (time).
Comando de instalação e versões: a confirmar (o repositório não possui arquivo de dependências).
Rede: execução apontando ROBOT_IP para o robô — o padrão do código é 127.0.0.1; a confirmar se o script roda no próprio robô ou em máquina externa.
Configuração
Constante	Padrão	Função
ROBOT_IP	"127.0.0.1"	IP do robô
VOLUME	100	Volume do alto-falante
LIMIAR_ROSTOS	1	Mínimo de rostos para disparar o show
COOLDOWN	8.0 s	Intervalo mínimo entre shows
INTERVALO	0.5 s	Pausa do loop de detecção
MAX_ACENOS	0	0 = repete indefinidamente
DEBUG	False	Imprime os retornos crus da API
TIPO_RECONHECIMENTO	"quantity"	Modo do reconhecimento facial
RAISE_HAND_STOP	True	Habilita a parada por gesto
VELOCIDADE_MOVIMENTO / VELOCIDADE_HIPHOP	"slow" / "fast"	Velocidade das rotinas
PAUSA_FALA / PAUSA_SEQUENCIA	0.7 / 0.5 s	Pausas entre falas e movimentos
REPETIR_HIPHOP	1	Repetições da coreografia
MUSICA_HIPHOP	"hiphop.mp3"	Música buscada no robô
DANCA_HIPHOP / LETRA_HIPHOP	listas	Movimentos da coreografia e trechos cantados (fallback)
O arquivo hiphop.mp3 precisa estar na lista de músicas do robô (busca por nome, sem extensão e sem diferenciar maiúsculas).

Execução
python <arquivo_principal>.py   # nome do arquivo: a confirmar
Ajuste ROBOT_IP e ligue o robô (bateria e volume são conferidos no início da execução);
O loop fica em modo de detecção até um rosto aparecer;
Para encerrar: Ctrl+C — o robô para a música e o reconhecimento, apaga o LED e retorna à pose inicial;
Em caso de dúvida sobre os retornos da API, ativar DEBUG = True.
Limitações e pontos a confirmar
Formato das respostas da API: a contagem de rostos e a detecção do gesto interpretam o JSON de forma genérica; validar com o retorno real do robô (DEBUG = True).
Catálogo de movimentos: nomes como GangnamStyle, LittleApple e H_RBox dependem do firmware do robô; se algum não existir, a chamada é ignorada e o show continua.
Tolerância a falhas: erros durante o loop são silenciados (com_seguranca); não há reconexão automática nem registro de log.
TTS: as falas usam interrupt=False com pausas fixas — podem se sobrepor em redes lentas. A fala de abertura inclui linguagem forte; ajustar conforme o contexto de apresentação.
Dependências e nome do script: sem requirements.txt; nome do arquivo principal e modelo exato do robô a confirmar.