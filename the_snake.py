# Импортируем нужные нам библиотеки.
from random import randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
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

# Цвет границы ячейки.
BORDER_COLOR = (93, 216, 228)

# Цвет яблока.
APPLE_COLOR = (255, 0, 0)

# Цвет змейки.
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс GameObject, от этого класса наследуются другие игровые
    объекты, в нашем случае Apple и Snake.
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
            'Определите метод draw в классе %s.' % (self.__class__.__name__)
        )


class Apple(GameObject):
    """Класс Apple наследуется от GameObject и описывает яблоко."""

    def __init__(self, snake_list=list()):
        """Конструктор класса Apple."""
        super().__init__(APPLE_COLOR)
        # Устнавливаем рандомное положение яблока.
        self.position = self.randomize_position(snake_list)

    def randomize_position(self, positions):
        """Метод randomize_position возвращает рандомную позицию яблока."""
        while True:
            self.position = (
                randint(0, (GRID_WIDTH - 1)) * GRID_SIZE,
                randint(0, (GRID_HEIGHT - 1)) * GRID_SIZE
            )
            if self.position not in positions:
                return self.position
                break

    def draw(self):
        """Метод draw в классе Apple отрисовывет яблоко на поле."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс Snake наследуется от GameObject и описывает змейку
    и ее движения.
    """

    def __init__(self):
        """Конструктор класса Snake."""
        super().__init__(SNAKE_COLOR)
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
        self.current_head_position = self.get_head_position()
        x_position = self.current_head_position[0]
        y_position = self.current_head_position[1]

        # Проверка на границу поля по оси X.
        if x_position >= SCREEN_WIDTH:
            x_position = - GRID_SIZE
        elif x_position < 0:
            x_position = SCREEN_WIDTH

        # Проверка на границу поля по оси Y.
        if y_position >= SCREEN_HEIGHT:
            y_position = - GRID_SIZE
        elif y_position < 0:
            y_position = SCREEN_HEIGHT

        # В зависимости от направления добавляем новую голову.
        if self.direction == RIGHT:
            self.positions.insert(0, (x_position + GRID_SIZE, y_position))
        elif self.direction == LEFT:
            self.positions.insert(0, (x_position - GRID_SIZE, y_position))
        elif self.direction == UP:
            self.positions.insert(0, (x_position, y_position - GRID_SIZE))
        elif self.direction == DOWN:
            self.positions.insert(0, (x_position, y_position + GRID_SIZE))
        self.last = self.positions.pop()

    def draw(self):
        """Метод draw в классе Snake
        отрисовывет нашу змейку, и затирает след.
        """
        for position in self.positions[:-1]:
            self.draw_cell(position)

        # Отрисовка головы змейки.
        self.draw_cell(self.positions[0])

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


def handle_keys(game_object):
    """Функция обработки действий пользователя."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основной цикл программы."""
    pg.init()  # Инициализация pg.
    snake = Snake()  # Создаем змейку.
    # Создаем яблоко, в аргумент передем лист,
    # в котором находятся занятые ячейки.
    apple = Apple(snake.positions)
    while True:
        clock.tick(SPEED)
        pg.display.update()  # Отрисовываем изменения.
        handle_keys(snake)
        snake.update_direction(snake.next_direction)
        apple.draw()  # Рисуем яблоко.
        snake.draw()  # Рисуем змейку.
        snake.move()  # Перемещаем змейку.
        if snake.get_head_position() == apple.position:
            snake.positions.append(snake.last)
            apple = Apple(snake.positions)
        elif snake.get_head_position() in snake.positions[1:]:
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()  # Сбрасываем змейку.


if __name__ == '__main__':
    main()
