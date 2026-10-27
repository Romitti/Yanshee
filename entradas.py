# entradas.py
# Camada de ENTRADA: tudo que o programa LE do robo (cameras, sensor, biblioteca de midia).
# Nenhuma funcao desta camada move o robo, fala ou toca musica.

import YanAPI

DEBUG = False
TIPO_RECONHECIMENTO = "quantity"


def contar_rostos_em(dado):
    """Varre o JSON de retorno da API (recursivo) e estima a quantidade de rostos."""
    if isinstance(dado, list):
        return len(dado)
    if not isinstance(dado, dict):
        return 0
    total = 0
    for chave, valor in dado.items():
        chave_l = str(chave).lower()
        if isinstance(valor, int) and any(
                p in chave_l for p in ("num", "count", "quantity", "total")):
            total = max(total, valor)
        elif isinstance(valor, list) and "face" in chave_l:
            total = max(total, len(valor))
        elif isinstance(valor, dict):
            total = max(total, contar_rostos_em(valor))
    return total


def detectar_rostos():
    """Le a camera e devolve a quantidade de rostos visiveis (0 se falhar)."""
    try:
        retorno = YanAPI.sync_do_face_recognition(type=TIPO_RECONHECIMENTO)
        if DEBUG:
            print(retorno)
        if not isinstance(retorno, dict):
            return 0
        if retorno.get("code", 0) not in (0, "0"):
            return 0
        return contar_rostos_em(retorno.get("data", retorno))
    except Exception:
        return 0


def mao_levantada():
    """Le a camera e devolve True se o gesto de parada ('good') for detectado."""
    try:
        retorno = YanAPI.sync_do_gesture_recognition()
        if DEBUG:
            print(retorno)
    except Exception:
        return False
    if not isinstance(retorno, dict) or retorno.get("code", 0) not in (0, "0"):
        return False
    data = retorno.get("data", retorno)
    valores = []
    if isinstance(data, dict):
        valores = list(data.values())
    elif isinstance(data, list):
        valores = data
    for valor in valores:
        if isinstance(valor, str) and valor.strip().lower() == "good":
            return True
    return False


def checar_bateria():
    """Le o percentual de bateria e avisa no console (nao bloqueia o show)."""
    bateria = YanAPI.get_robot_battery_value()
    if bateria < 20:
        print("Bateria baixa: {}%".format(bateria))
    else:
        print("Bateria OK: {}%".format(bateria))


def listar_musicas():
    """Le a biblioteca de musicas do robo; devolve a lista de itens (ou [])."""
    try:
        retorno = YanAPI.get_media_music_list()
    except Exception:
        return []
    if not (isinstance(retorno, dict) and retorno.get("code", 0) in (0, "0")):
        return []
    data = retorno.get("data", retorno)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if isinstance(data.get("music"), list):
            return data["music"]
        for valor in data.values():
            if isinstance(valor, list):
                return valor
    return []


def parar_reconhecimento():
    """Encerra a sessao de reconhecimento facial (usado na limpeza final)."""
    try:
        YanAPI.stop_face_recognition(type=TIPO_RECONHECIMENTO)
    except Exception:
        pass
