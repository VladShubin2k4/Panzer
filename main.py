import sys
from abc import ABC, abstractmethod
from math import cos, sin, pi

import pygame


class Color:
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)


class PG:
    _instance = None

    def __init__(self, width=500, height=400):
        if PG._instance is not None:  # singleton implementation
            raise ReferenceError('Tying to create singleton object twice')
        else:
            PG._instance = self
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((width, height))
        self.width = width
        self.height = height

    @staticmethod
    def get():
        if not PG._instance:
            PG()
        return PG._instance


class PGScene(ABC):
    bgcolor = (0, 0, 0)
    states = []

    def __init__(self):
        self.screen = PG.get().screen
        self.sceneover = False
        self.objects = []
        self.f = pygame.font.Font(None, 64)

    def draw(self):
        self.screen.fill(self.bgcolor)
        for item in self.objects:
            item.draw()
        for state in self.states.values():
            if state[0]:
                txt = self.f.render(state[1], False, Color.GREEN)
                self.screen.blit(txt, (16, 32))

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.sceneover = True
            self.process_event(event)

    def process_event(self, event):
        pass

    @abstractmethod
    def process_logic(self):
        for item in self.objects:
            item.logic()

    def main_loop(self):
        while not self.sceneover:
            self.process_events()
            self.process_logic()
            self.draw()
            pygame.display.flip()
            pygame.time.wait(10)


class Command(ABC):
    def __init__(self, scene):
        self.scene = scene

    @abstractmethod
    def execute_up(self):
        pass

    @abstractmethod
    def execute_down(self):
        pass


class UpCommand(Command):
    def execute_down(self):
        self.scene.panzer.move()
        self.scene.states['not_move'][0] = False
        self.scene.states['up'][0] = True
        self.scene.buttons['up'].set_enabled(True)
        self.scene.buttons['down'].set_enabled(False)

    def execute_up(self):
        self.scene.panzer.stop()
        self.scene.states['up'][0] = False
        self.scene.states['not_move'][0] = True
        self.scene.buttons['up'].set_enabled(False)


class DownCommand(Command):
    def execute_down(self):
        self.scene.panzer.move(fwd=False)
        self.scene.states['not_move'][0] = False
        self.scene.states['down'][0] = True
        self.scene.buttons['down'].set_enabled(True)
        self.scene.buttons['up'].set_enabled(False)

    def execute_up(self):
        self.scene.panzer.stop()
        self.scene.states['down'][0] = False
        self.scene.states['not_move'][0] = True
        self.scene.buttons['down'].set_enabled(False)


class LeftCommand(Command):
    def execute_down(self):
        self.scene.panzer.rotate(-0.1)
        self.scene.states['not_move'][0] = False
        self.scene.states['left'][0] = True
        self.scene.buttons['left'].set_enabled(True)
        self.scene.buttons['right'].set_enabled(False)

    def execute_up(self):
        self.scene.states['left'][0] = False
        self.scene.states['not_move'][0] = True
        self.scene.buttons['left'].set_enabled(False)


class RightCommand(Command):
    def execute_down(self):
        self.scene.panzer.rotate(0.1)
        self.scene.states['not_move'][0] = False
        self.scene.states['right'][0] = True
        self.scene.buttons['right'].set_enabled(True)
        self.scene.buttons['left'].set_enabled(False)

    def execute_up(self):
        self.scene.states['right'][0] = False
        self.scene.states['not_move'][0] = True
        self.scene.buttons['right'].set_enabled(False)


class GameScene(PGScene):
    key_events = {
        pygame.K_w: UpCommand,
        pygame.K_s: DownCommand,
        pygame.K_a: LeftCommand,
        pygame.K_d: RightCommand,
    }

    def __init__(self):
        super().__init__()
        self.panzer = Panzer(200, 200)
        self.buttons = {
            'up': StateRect(100, 500, 20, 20, Color.GREEN, Color.RED),
            'down': StateRect(100, 530, 20, 20, Color.GREEN, Color.RED),
            'left': StateRect(70, 530, 20, 20, Color.GREEN, Color.RED),
            'right': StateRect(130, 530, 20, 20, Color.GREEN, Color.RED),
        }
        self.states = {
            'not_move': [1, 'нет движения'],
            'up': [0, 'движение вперёд'],
            'down': [0, 'движение назад'],
            'left': [0, 'поворот влево'],
            'right': [0, 'поворот вправо'],
        }
        self.objects.append(self.panzer)
        self.objects += self.buttons.values()

    def process_logic(self):
        super().process_logic()

    def process_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in GameScene.key_events.keys():
            GameScene.key_events[event.key](self).execute_down()
        if event.type == pygame.KEYUP and event.key in GameScene.key_events.keys():
            GameScene.key_events[event.key](self).execute_up()


class PGObject(ABC):
    def __init__(self):
        self.screen = PG.get().screen

    @abstractmethod
    def draw(self):
        pass

    def logic(self):
        pass


class Panzer(PGObject):
    def __init__(self, x, y):
        super().__init__()
        self.rotated_image = self.image = pygame.image.load("panzer.png")
        self.rotated_rect = self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.direction = 0
        self.speed = 0
        self.max_speed = 1

    def draw(self):
        self.rect.x = self.x - self.rect.width // 2
        self.rect.y = self.y - self.rect.height // 2
        self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)
        self.screen.blit(self.rotated_image, self.rotated_rect)

    def move(self, fwd=True):
        self.speed = self.max_speed if fwd else -self.max_speed

    def stop(self):
        self.speed = 0

    def step(self):
        self.x += cos(self.direction) * self.speed
        self.y += sin(self.direction) * self.speed

    def rotate(self, angle):
        self.direction += angle
        self.rotated_image = pygame.transform.rotate(self.image, -self.direction / pi * 180)
        self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)

    def logic(self):
        self.step()


class StateRect(PGObject):
    def __init__(self, x, y, width, height, color_enabled, color_disabled):
        super().__init__()
        self.rect = (x, y, width, height)
        self.color_enabled = color_enabled
        self.color_disabled = color_disabled
        self.enabled = False

    def draw(self):
        color = self.color_enabled if self.enabled else self.color_disabled,
        pygame.draw.rect(self.screen, color, self.rect, 0)

    def set_enabled(self, enabled):
        self.enabled = enabled


if __name__ == "__main__":
    PG(800, 600)
    gs = GameScene()
    gs.main_loop()
    sys.exit()
