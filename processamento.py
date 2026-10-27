# processamento.py
# Camada de PROCESSAMENTO: interpretacao dos dados de entrada e regras de decisao.
# Nao conversa com o robo diretamente: interpreta, decide e guarda as constantes
# de decisao (limiar, cooldown, gesto de parada).

from entradas import mao_levantada

LIMIAR_ROSTOS = 1      # minimo de rostos para disparar o show
COOLDOWN = 8.0         # intervalo minimo entre shows (segundos)
RAISE_HAND_STOP = True # habilita a parada por gesto
GESTO_PARADA = "good"  # gesto reconhecido como "mao levantada"


def com_seguranca(funcao):
    """Executa uma chamada de API sem deixar que uma falha derrube o show."""
    try:
        funcao()
    except Exception:
        pass


def deve_disparar_show(n_rostos, agora, ultimo_aceno):
    """Regra de disparo: rosto suficiente E cooldown vencido."""
    return n_rostos >= LIMIAR_ROSTOS and (agora - ultimo_aceno) >= COOLDOWN


def pedido_de_parada():
    """Condicao de parada de emergencia, definida em um unico lugar."""
    return RAISE_HAND_STOP and mao_levantada()


def procurar_musica(itens, nome_procurado):
    """Procura a musica na lista (sem extensao, ignorando maiusculas).

    Devolve o nome exato do item encontrado, ou None se nao achar.
    """
    alvo_base = nome_procurado.rsplit(".", 1)[0].lower()
    for item in itens:
        if isinstance(item, dict):
            nome_item = str(item.get("name", item.get("fileName", "")))
        else:
            nome_item = str(item)
        if nome_item.rsplit(".", 1)[0].lower() == alvo_base:
            return nome_item
    return None
