# Импортируем нужные нам библиотеки.
from random import randint, choice

import pygame as pg
import pygame_menu as pgm

pg.init()  # Инициализация pygame.

pg.font.init()  # Инициализация pygame - работы с текстом.

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Фон меню.
BACKGROUND_MENU_IMG = pg.image.load('image/snake.jpeg')

# Цвет границы ячейки.
BORDER_COLOR = (93, 216, 228)

# Виды еды и цвет (Яблоко, Банан и Апельсин).
EAT = [(255, 0, 0), (255, 255, 0), (255, 165, 0)]

# Цвет змейки.
SNAKE_COLOR = (0, 255, 0)

# Цвет счетчика.
SCORE_COLOR = (250, 235, 215)

# Все возможные направления движения змейки
DIRECTIONS = {
    (pg.K_UP, LEFT): UP,
    (pg.K_UP, RIGHT): UP,
    (pg.K_DOWN, LEFT): DOWN,
    (pg.K_DOWN, RIGHT): DOWN,
    (pg.K_LEFT, UP): LEFT,
    (pg.K_LEFT, DOWN): LEFT,
    (pg.K_RIGHT, UP): RIGHT,
    (pg.K_RIGHT, DOWN): RIGHT,
}

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс GameObject, от этого класса наследуются другие игровые
    объекты, в нашем случае Eat и Snake.
    """

    def __init__(self, color=None):
        """Конструктор класса GameObject."""
        self.position = None  # Позиция объекта (по умолчанию - None).
        self.body_color = color  # Цвет объекта.

    def draw_cell(self, position):
        """Отрисовывает одну ячейку поля."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Метод draw класса GameObject служит для переопределения
        в дочерних классах. Этот метод должен определять, как будет
        рисоваться на экране объект.
        """
        raise NotImplementedError(
            'Определите draw в {error}.'.format(error=self.__class__.__name__)
        )


class Eat(GameObject):
    """Класс Eat наследуется от GameObject и описывает яблоко."""

    def __init__(self, color, occupied_cells=None):
        """Конструктор класса Eat."""
        super().__init__(color)
        if occupied_cells is None:
            occupied_cells = []
        # Устнавливаем рандомное положение яблока.
        self.position = self.randomize_position(occupied_cells)

    def randomize_position(self, occupied_cells):
        """Метод randomize_position возвращает рандомную позицию яблока."""
        while True:
            self.position = (
                randint(0, (GRID_WIDTH - 1)) * GRID_SIZE,
                randint(0, (GRID_HEIGHT - 1)) * GRID_SIZE
            )
            if self.position not in occupied_cells:
                return self.position

    def draw(self):
        """Метод draw в классе Eat отрисовывет яблоко на поле."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс Snake наследуется от GameObject и описывает змейку
    и ее движения.
    """

    def __init__(self, color=SNAKE_COLOR):
        """Конструктор класса Snake."""
        super().__init__(color)
        self.reset()  # В методе reset() указаны начальные параметры.

    def update_direction(self, next_direction=None):
        """Метод обновления направления после нажатия на кнопку."""
        if next_direction:
            self.direction = next_direction

    def get_head_position(self):
        """Метод get_head_position возвращает текущее положение головы
        змейки.
        """
        return self.positions[0]

    def move(self):
        """Метод move отвечает за движение змейки, а именно:
        добавляет новую голову в начало списка и убирает последний элемент.
        """
        x_position, y_position = self.get_head_position()

        x_direction, y_direction = self.direction
        x_coord = (GRID_SIZE * x_direction + x_position) % SCREEN_WIDTH
        y_coord = (GRID_SIZE * y_direction + y_position) % SCREEN_HEIGHT

        self.positions.insert(0, (x_coord, y_coord))
        self.last = (
            self.positions.pop() if len(self.positions) > self.length else None
        )

    def draw(self):
        """Метод draw в классе Snake
        отрисовывет нашу змейку, и затирает след.
        """
        for position in self.positions[:-1]:
            self.draw_cell(position)

        # Отрисовка головы змейки.
        self.draw_cell(self.get_head_position())

        # Затирание последнего сегмента.
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """Сбрасывает змейку в начальное состояние после столкновения
        с собой.
        """
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


class Score(GameObject):
    """Счетчик, увеличивается при съедании еды, сбрасывается при проигрыше."""

    def __init__(self, score):
        self.score = score
        self.font = pg.font.SysFont('robo', 35)

    def draw(self):
        """Метод отрисовывает счетчик."""
        self.score_panel = self.font.render(
            f'Счет: {str(self.score)}',
            True,
            SCORE_COLOR
        )
        score_rect = self.score_panel.get_rect(center=(700, 30))
        screen.blit(self.score_panel, score_rect)


def handle_keys(game_object):
    """Функция обработки действий пользователя."""
    for event in pg.event.get():
        if event.type == pg.QUIT or pg.key.get_pressed()[pg.K_ESCAPE]:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            game_object.next_direction = DIRECTIONS.get(
                (event.key, game_object.direction)
            )


menu = pgm.Menu('Добро пожаловать!', 500, 400, theme=pgm.themes.THEME_DARK)


def start_the_game():
    """Основной цикл программы."""
    snake = Snake()  # Создаем змейку.
    # Создаем еду, в аргумент передем лист,
    # в котором находятся занятые ячейки.
    eat = Eat(choice(EAT), occupied_cells=snake.positions)
    score = Score(0)  # Создаем счетчик.
    screen.fill(BOARD_BACKGROUND_COLOR)  # Закрашиваем экран.
    while True:
        clock.tick(SPEED)
        pg.display.update()  # Отрисовываем изменения.
        handle_keys(snake)
        snake.update_direction(snake.next_direction)
        snake.move()  # Перемещаем змейку.
        if snake.get_head_position() == eat.position:
            score.score += 1
            snake.positions.append(snake.last)
            eat = Eat(choice(EAT), occupied_cells=snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)  # Закрашиваем экран.
        elif snake.get_head_position() in snake.positions[1:]:
            break
        eat.draw()  # Рисуем еду.
        snake.draw()  # Рисуем змейку.
        score.draw()  # Отрисовываем счетчик.

    # Запишем последний результат.
    with open('score.txt', 'w') as f:
        f.write(str(score.score))


if __name__ == '__main__':

    with open('score.txt', 'r') as f:
        score_data = f.read()

    menu.add.text_input('Имя Игрока :', default='Игрок')
    menu.add.label(title=f"Предыдущий результат: {score_data}")
    menu.add.button('Играть', start_the_game)
    menu.add.button('Выход', pgm.events.EXIT)
    menu.add.range_slider(
        'Выберите скорость', 20, (5, 30), 1,
        rangeslider_id='range_slider',
        value_format=lambda x: str(int(x))
    )

    while True:
        """Цикл Меню."""
        screen.blit(BACKGROUND_MENU_IMG, (0, 0))

        dict_event = menu.get_input_data()
        SPEED = dict_event['range_slider']

        events = pg.event.get()

        for event in events:
            if event.type == pg.QUIT:
                exit()

        if menu.is_enabled():
            menu.update(events)
            menu.draw(screen)

        pg.display.update()
