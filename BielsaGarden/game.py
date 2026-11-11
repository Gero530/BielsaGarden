import pygame
import display
import cuentas
import ajustes
import logros
from ui import button, audio, aviso_logro
from settings import SCREEN_W, SCREEN_H, FPS, TITLE

CORTINA = 0.3


class Game:
    def __init__(self):
        display.enable_dpi_awareness()
        pygame.init()
        pygame.display.set_caption(TITLE)
        display.load_config()
        audio.cargar()
        ajustes.cargar()
        display.apply()
        self.screen = pygame.Surface((SCREEN_W, SCREEN_H)).convert()
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene = None

        self.cortina = None
        self.intro_done = False
        self.progreso = set()
        cuentas.cargar_en(self)

        from scenes.loading import LoadingScene
        self.change_scene(LoadingScene(self))

    def change_scene(self, new_scene):
        logros.guardar()
        if self.scene is not None:
            self.cortina = [self.screen.copy(), 0.0]
        self.scene = new_scene

    def dibujar_cortina(self, dt):
        if not self.cortina:
            return
        from ui.intro_art import build_cortina, CORTINA_ESC
        vieja, t = self.cortina
        t += dt
        u = min(1.0, t / CORTINA)
        hoja = build_cortina()
        x = int(-hoja.get_width() + u * (SCREEN_W + hoja.get_width())) // CORTINA_ESC * CORTINA_ESC
        frente = x + hoja.get_width()
        if frente < SCREEN_W:
            self.screen.blit(vieja, (frente, 0), pygame.Rect(frente, 0, SCREEN_W - frente, SCREEN_H))
        self.screen.blit(hoja, (x, 0))
        self.cortina = None if u >= 1.0 else [vieja, t]

    def apply_display(self):
        display.apply()
        display.save_config()

    def quit(self):
        self.running = False

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type in (pygame.WINDOWFOCUSLOST, pygame.WINDOWMINIMIZED):
                    audio.set_foco(False)
                elif event.type == pygame.WINDOWFOCUSGAINED:
                    audio.set_foco(True)
                else:
                    self.scene.handle_event(display.convert_event(event))

            self.scene.update(dt)
            button.actualizar(dt)
            self.scene.draw(self.screen)
            self.dibujar_cortina(dt)
            button.dibujar_efectos(self.screen)
            aviso_logro.dibujar(self.screen, dt)
            display.present(self.screen)

        cuentas.guardar_desde(self)
        logros.guardar()
        pygame.quit()
