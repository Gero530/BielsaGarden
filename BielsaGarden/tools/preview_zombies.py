import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import pygame
from ui.pixel_font import draw_pixel_text

ESCALA = 4
ANCHO_NOMBRE = 360
FONDO, FONDO_ALT = (116, 180, 240), (100, 162, 222)


def main():
    carpeta = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, "assets", "sprites", "zombies_generados")
    salida = sys.argv[2] if len(sys.argv) > 2 else os.path.join(carpeta, "preview.png")
    pygame.init()
    pygame.display.set_mode((1, 1))
    nombres = sorted(f for f in os.listdir(carpeta) if f.endswith(".png") and f != os.path.basename(salida))
    tiras = [(n, pygame.image.load(os.path.join(carpeta, n))) for n in nombres]
    alto = sum(t.get_height() * ESCALA + 12 for _, t in tiras)
    ancho = ANCHO_NOMBRE + max(t.get_width() * ESCALA for _, t in tiras) + 12
    hoja = pygame.Surface((ancho, alto))
    y = 0
    for i, (n, t) in enumerate(tiras):
        h = t.get_height() * ESCALA + 12
        hoja.fill(FONDO if i % 2 == 0 else FONDO_ALT, (0, y, ancho, h))
        draw_pixel_text(hoja, n[:-4].upper().replace("_", " "), (255, 255, 255), 2, outline=(30, 40, 70),
                        midleft=(10, y + h // 2))
        hoja.blit(pygame.transform.scale(t, (t.get_width() * ESCALA, t.get_height() * ESCALA)), (ANCHO_NOMBRE, y + 6))
        y += h
    pygame.image.save(hoja, salida)
    print("vista previa:", salida, hoja.get_size())


if __name__ == "__main__":
    main()
