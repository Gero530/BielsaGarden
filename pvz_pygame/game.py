"""
Bucle principal y gestor de escenas.

Cada pantalla (menú, partida, resultado, opciones) es una Scene con tres métodos:
handle_event, update(dt) y draw(surface). Game solo delega en la escena actual.

Las escenas siempre dibujan sobre self.screen (1000x600). display.present()
se encarga de escalarla a la resolución/pantalla completa elegida.
"""
import pygame
import display
from settings import SCREEN_W, SCREEN_H, FPS, TITLE


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

        # Import aquí para evitar imports circulares (las escenas importan Game)
        from scenes.menu import MenuScene
        self.change_scene(MenuScene(self))

    def change_scene(self, new_scene):
        self.scene = new_scene

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
            self.scene.draw(self.screen)
            display.present(self.screen)

        pygame.quit()
