# main.py
# Orquestracao: conexao, loop de deteccao e ciclo de vida do programa.
# As camadas fazem o trabalho; o main decide QUANDO cada coisa acontece.

import time

import YanAPI

from entradas import checar_bateria, detectar_rostos, parar_reconhecimento
from processamento import deve_disparar_show
from saidas import apresentar, configurar_volume, encerrar_sessao, led

ROBOT_IP = "127.0.0.1"
MAX_ACENOS = 0    # 0 = repete para sempre
INTERVALO = 0.5   # pausa do loop de deteccao (segundos)


def conectar():
    print("Conectando ao robo em {} ...".format(ROBOT_IP))
    YanAPI.yan_api_init(ROBOT_IP)
    time.sleep(1)


def main():
    try:
        conectar()
    except Exception:
        print("Nao foi possivel conectar ao robo. Confira o IP.")
        return

    checar_bateria()
    configurar_volume()

    acenos = 0
    ultimo_aceno = 0.0
    try:
        while MAX_ACENOS == 0 or acenos < MAX_ACENOS:
            led("blue", "blink")
            n_rostos = detectar_rostos()
            agora = time.time()
            if deve_disparar_show(n_rostos, agora, ultimo_aceno):
                led("green", "on")
                print("Rosto detectado! Show (mao levantada = para tudo).")
                apresentar()
                acenos += 1
                ultimo_aceno = time.time()
            else:
                time.sleep(INTERVALO)
    except KeyboardInterrupt:
        pass
    finally:
        parar_reconhecimento()
        encerrar_sessao()


if __name__ == "__main__":
    main()
