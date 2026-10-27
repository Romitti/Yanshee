# saidas.py
# Camada de SAIDA: tudo que o programa FAZ no robo (movimento, voz, LED, musica).
# As decisoes vêm de processamento; a leitura de sensores vem de entradas.

import time

import YanAPI

from entradas import listar_musicas
from processamento import com_seguranca, pedido_de_parada, procurar_musica

VOLUME = 100
VELOCIDADE_MOVIMENTO = "slow"
VELOCIDADE_HIPHOP = "fast"
PAUSA_FALA = 0.7
PAUSA_SEQUENCIA = 0.5
REPETIR_HIPHOP = 1

MUSICA_HIPHOP = "hiphop.mp3"
LETRA_HIPHOP = ["Yeah!", "Uh! Vai, vai!", "Boom, boom!", "Bate, bate, bate!"]
DANCA_HIPHOP = ["rightmovestep", "H_RBox", "leftmovestep", "GangnamStyle",
                "H_Wave_R", "H_Wave_L", "LittleApple", "Victory"]


def led(cor, modo):
    com_seguranca(lambda: YanAPI.set_robot_led(type="button", color=cor, mode=modo))


def configurar_volume():
    com_seguranca(lambda: YanAPI.set_robot_volume_value(VOLUME))


def acenar_falando():
    com_seguranca(lambda: YanAPI.start_voice_tts(tts="Ola...", interrupt=False))
    com_seguranca(lambda: YanAPI.sync_play_motion(
        name="wave", direction="right", speed=VELOCIDADE_MOVIMENTO, repeat=1))
    time.sleep(PAUSA_FALA)
    com_seguranca(lambda: YanAPI.start_voice_tts(tts="mestre!", interrupt=False))
    time.sleep(PAUSA_SEQUENCIA)


def abaixar_e_levantar_bracos():
    com_seguranca(lambda: YanAPI.sync_play_motion(
        name="crouch", speed=VELOCIDADE_MOVIMENTO, repeat=1))
    time.sleep(PAUSA_SEQUENCIA)
    com_seguranca(lambda: YanAPI.start_voice_tts(tts="E hora...", interrupt=False))
    com_seguranca(lambda: YanAPI.sync_play_motion(
        name="raise", direction="both", speed=VELOCIDADE_MOVIMENTO, repeat=1))
    time.sleep(PAUSA_FALA)
    com_seguranca(lambda: YanAPI.sync_do_tts(tts="do show...", interrupt=False))
    time.sleep(PAUSA_FALA)
    com_seguranca(lambda: YanAPI.sync_do_tts(tts="porra!", interrupt=False))


def pedir_desculpas():
    led("red", "blink")
    com_seguranca(lambda: YanAPI.sync_play_motion(
        name="bend", direction="both", speed=VELOCIDADE_MOVIMENTO, repeat=1))
    com_seguranca(lambda: YanAPI.sync_do_tts(tts="Desculpa...", interrupt=False))
    time.sleep(PAUSA_FALA)
    com_seguranca(lambda: YanAPI.sync_do_tts(tts="nao vou mais interromper!", interrupt=False))
    com_seguranca(lambda: YanAPI.sync_play_motion(
        name="reset", direction="both", speed=VELOCIDADE_MOVIMENTO, repeat=1))
    led("blue", "off")


def voltar_a_pose():
    com_seguranca(lambda: YanAPI.sync_play_motion(
        name="reset", direction="both", speed=VELOCIDADE_MOVIMENTO, repeat=1))


def tocar_musica(nome_procurado):
    itens = listar_musicas()
    nome = procurar_musica(itens, nome_procurado)
    if nome:
        print("Musica encontrada: {}".format(nome))
        com_seguranca(lambda: YanAPI.start_play_music(name=nome))
        return True
    print("Arquivo {} nao encontrado no robo; cantando pelo TTS.".format(nome_procurado))
    return False


def parar_show(mensagem):
    """Ponto unico de parada de emergencia: para toda a midia e pede desculpas."""
    com_seguranca(lambda: YanAPI.stop_play_music())
    com_seguranca(lambda: YanAPI.stop_play_motion(name=""))
    com_seguranca(lambda: YanAPI.stop_voice_tts())
    print(mensagem)
    pedir_desculpas()


def dancar_hiphop():
    led("cyan", "blink")
    tocando = tocar_musica(MUSICA_HIPHOP)
    for _ in range(REPETIR_HIPHOP):
        for movimento in DANCA_HIPHOP:
            if pedido_de_parada():
                parar_show("Mao levantada! Parando o show e pedindo desculpas.")
                return "parado"
            if not tocando:
                pedaco = LETRA_HIPHOP[DANCA_HIPHOP.index(movimento) % len(LETRA_HIPHOP)]
                com_seguranca(lambda: YanAPI.start_voice_tts(tts=pedaco, interrupt=False))
            com_seguranca(lambda: YanAPI.sync_play_motion(
                name=movimento, direction="both", speed=VELOCIDADE_HIPHOP, repeat=1))
    if tocando:
        com_seguranca(lambda: YanAPI.stop_play_music())
    return "concluido"


def apresentar():
    if pedido_de_parada():
        print("Ja comecou com mao levantada! Pedindo desculpas antes de comecar.")
        pedir_desculpas()
        return
    acenar_falando()
    if pedido_de_parada():
        parar_show("Mao levantada no meio do aceno! Parando.")
        return
    abaixar_e_levantar_bracos()
    if dancar_hiphop() == "parado":
        return
    voltar_a_pose()


def encerrar_sessao():
    """Limpeza final: para a musica, apaga o LED e volta a pose."""
    com_seguranca(lambda: YanAPI.stop_play_music())
    led("blue", "off")
    voltar_a_pose()
