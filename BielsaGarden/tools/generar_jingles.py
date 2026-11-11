"""
Genera la música de fin de nivel en estilo chiptune (onda cuadrada, sin archivos de afuera):

  assets/musica/victoria.wav   tema alegre de ~7 s que se repite en bucle en la pantalla de victoria
  assets/musica/derrota.wav    "wah wah wah waaah" triste (suena una vez) en la pantalla de derrota

    python tools/generar_jingles.py

Para cambiar las melodías, tocá MELODIA / BAJO / DERROTA (notas MIDI: 60 = do central).
"""
import array
import math
import os
import random
import wave

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUSICA = os.path.join(RAIZ, "assets", "musica")
SR = 22050                      # muestras por segundo
BPM = 140
NEGRA = 60 / BPM                # segundos de un tiempo

# Victoria: 4 compases de 4 tiempos (do - fa - sol - do), cierra justo para que el bucle no se note
MELODIA = [  # (nota MIDI o None = silencio, duración en tiempos)
    (72, .5), (76, .5), (79, .5), (84, 1), (79, .5), (84, 1),
    (77, .5), (81, .5), (84, .5), (89, 1), (84, .5), (89, 1),
    (79, .5), (83, .5), (86, .5), (91, 1), (86, .5), (91, .5), (89, .5),
    (88, .5), (86, .5), (84, 1.5), (None, .5), (84, .5), (79, .5),
]
BAJO = [48, 53, 55, 48]         # raíz de cada compás (do, fa, sol, do)

# Derrota: el trombón triste (sol, fa#, fa y un mi largo que tiembla)
DERROTA = [(67, .62), (66, .62), (65, .62), (64, 1.9)]


def frecuencia(nota):
    return 440.0 * 2 ** ((nota - 69) / 12)


def envolvente(i, n, ataque=0.005, caida=0.08, sostenido=0.65, final=0.04):
    t, total = i / SR, n / SR
    if t < ataque:
        return t / ataque
    if t > total - final:
        return max(0.0, (total - t) / final) * sostenido
    if t < ataque + caida:
        return 1 - (1 - sostenido) * (t - ataque) / caida
    return sostenido


def cuadrada(f, i, duty=0.5):
    return 1.0 if (f * i / SR) % 1.0 < duty else -1.0


def mezclar(pistas, n):
    out = [0.0] * n
    for pista in pistas:
        for i, v in enumerate(pista[:n]):
            out[i] += v
    pico = max(1e-9, max(abs(v) for v in out))
    escala = min(1.0, 0.9 / pico)
    return [v * escala for v in out]


def guardar(nombre, muestras):
    datos = array.array("h", (int(max(-1.0, min(1.0, v)) * 32000) for v in muestras))
    ruta = os.path.join(MUSICA, nombre)
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(datos.tobytes())
    print("creado:", os.path.relpath(ruta, RAIZ), f"({len(muestras) / SR:.1f} s)")


def victoria():
    n = int(16 * NEGRA * SR)
    melodia = [0.0] * n
    pos = 0
    for nota, dur in MELODIA:
        largo = int(dur * NEGRA * SR)
        if nota is not None:
            f = frecuencia(nota)
            for i in range(largo):
                if pos + i < n:
                    melodia[pos + i] = 0.30 * cuadrada(f, i, 0.25) * envolvente(i, largo)
        pos += largo
    bajo = [0.0] * n
    corchea = int(NEGRA / 2 * SR)
    for compas, raiz in enumerate(BAJO):
        for k, salto in enumerate((0, 12, 7, 12, 0, 12, 7, 12)):
            f = frecuencia(raiz + salto)
            inicio = (compas * 8 + k) * corchea
            for i in range(corchea):
                bajo[inicio + i] = 0.22 * cuadrada(f, i, 0.5) * envolvente(i, corchea, caida=0.05, sostenido=0.5)
    bateria = [0.0] * n
    rnd = random.Random(1)
    for tiempo in range(16):
        golpe = int(tiempo * NEGRA * SR)
        largo = int(0.09 * SR) if tiempo % 2 == 0 else int(0.03 * SR)       # bombo en 1 y 3, platillo en 2 y 4
        for i in range(largo):
            if golpe + i < n:
                caer = 1 - i / largo
                if tiempo % 2 == 0:
                    v = math.sin(2 * math.pi * (110 - 70 * i / largo) * i / SR) * 0.35
                else:
                    v = rnd.uniform(-1, 1) * 0.12
                bateria[golpe + i] += v * caer
        medio = golpe + int(NEGRA / 2 * SR)                                   # platillito en la corchea del medio
        for i in range(int(0.02 * SR)):
            if medio + i < n:
                bateria[medio + i] += rnd.uniform(-1, 1) * 0.06 * (1 - i / (0.02 * SR))
    guardar("victoria.wav", mezclar([melodia, bajo, bateria], n))


def derrota():
    total = sum(d for _, d in DERROTA)
    n = int((total + 0.4) * SR)
    voz = [0.0] * n
    pos = 0
    for k, (nota, dur) in enumerate(DERROTA):
        largo = int(dur * SR)
        f0 = frecuencia(nota)
        fase = 0.0
        ultima = k == len(DERROTA) - 1
        for i in range(largo):
            t = i / SR
            f = f0 * (1 - 0.03 * min(1.0, t / 0.08))                         # cada nota se cae un poquito ("wah")
            if ultima:
                f *= 1 + 0.025 * math.sin(2 * math.pi * 6 * t) * min(1.0, t / 0.3)   # vibrato del final
            fase += f / SR
            sierra = 2 * (fase % 1.0) - 1
            cuad = 1.0 if fase % 1.0 < 0.5 else -1.0
            env = envolvente(i, largo, ataque=0.02, caida=0.15, sostenido=0.7, final=0.12 if not ultima else 0.6)
            voz[pos + i] = (0.6 * sierra + 0.4 * cuad) * env * 0.4
        pos += largo
    guardar("derrota.wav", mezclar([voz], n))


if __name__ == "__main__":
    os.makedirs(MUSICA, exist_ok=True)
    victoria()
    derrota()
