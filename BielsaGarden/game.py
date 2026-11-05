"""
Bucle principal y gestor de escenas.

Cada pantalla (menú, partida, resultado, opciones) es una Scene con tres métodos:
handle_event, update(dt) y draw(surface). Game solo delega en la escena actual.

Las escenas siempre dibujan sobre self.screen (1000x600). display.present()
se encarga de escalarla a la resolución/pantalla completa elegida.
"""
import pygame
import display
from ui import button
from settings import SCREEN_W, SCREEN_H, FPS, TITLE

CORTINA = 0.3          # segundos que tarda la cortina de cartulina en cruzar la pantalla


class Game:
    def __init__(self):
        display.enable_dpi_awareness()
        pygame.init()
        pygame.display.set_caption(TITLE)
        display.load_config()
        display.apply()
        self.screen = pygame.Surface((SCREEN_W, SCREEN_H)).convert()
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene = None

        self.cortina = None               # transición entre pantallas en curso
        self.intro_done = False     # la intro del menú se ve una sola vez por ejecución
        # Ids de niveles ganados. Solo en memoria: cada vez que se abre el juego arranca vacío
        # (solo el tutorial disponible).
        self.progreso = set()

        # Import aquí para evitar imports circulares (las escenas importan Game)
        from scenes.loading import LoadingScene
        self.change_scene(LoadingScene(self))

    def change_scene(self, new_scene):
        if self.scene is not None:          # la primera escena no tiene transición
            self.cortina = [self.screen.copy(), 0.0]
        self.scene = new_scene

    def dibujar_cortina(self, dt):
        """Cortina de cartulina que cruza la pantalla: adelante se ve la pantalla vieja y atrás la nueva."""
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
        """Aplica la configuración de pantalla actual (la llama el menú de opciones)."""
        display.apply()
        display.save_config()

    def quit(self):
        self.running = False

    def run(self):
        while self.running:
            # dt en segundos, limitado para que un lag no "teletransporte" zombies
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                else:
                    self.scene.handle_event(display.convert_event(event))

            self.scene.update(dt)
            button.actualizar(dt)           # tablones apretados y astillas (tiempo real)
            self.scene.draw(self.screen)
            self.dibujar_cortina(dt)
            button.dibujar_efectos(self.screen)
            display.present(self.screen)

        pygame.quit()
