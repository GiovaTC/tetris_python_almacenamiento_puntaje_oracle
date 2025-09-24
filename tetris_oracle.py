#!/usr/bin/env python3
import pygame
import sys
import os
import oracledb
from datetime import datetime
from dotenv import load_dotenv
import random

# Cargar variables del entorno (.env con ORACLE_USER, ORACLE_PASS, ORACLE_DSN)
load_dotenv()

# ===============================
# 🔹 Constantes del juego
# ===============================
WIDTH, HEIGHT = 300, 600
ROWS, COLUMNS = 20, 10
CELL_SIZE = 30
FPS = 60

COLORS = [
    (0, 255, 255),  # Cyan
    (0, 0, 255),    # Azul
    (255, 165, 0),  # Naranja
    (255, 255, 0),  # Amarillo
    (0, 255, 0),    # Verde
    (128, 0, 128),  # Morado
    (255, 0, 0)     # Rojo
]

# Piezas del Tetris (Tetrominós)
SHAPES = [
    [[1, 1, 1, 1]],                # I
    [[1, 1, 1],
     [0, 1, 0]],                   # T
    [[1, 1, 1],
     [1, 0, 0]],                   # L
    [[1, 1, 1],
     [0, 0, 1]],                   # J
    [[1, 1],
     [1, 1]],                      # O
    [[0, 1, 1],
     [1, 1, 0]],                   # S
    [[1, 1, 0],
     [0, 1, 1]]                    # Z
]

# ===============================
# 🔹 Clases del juego
# ===============================
class Piece:
    def __init__(self, shape):
        self.shape = shape
        self.color = random.choice(COLORS)
        self.x = COLUMNS // 2 - len(shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

class Tetris:
    def __init__(self):
        self.grid = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.fall_speed = 500  # ms entre caídas
        self.game_over = False
        self.current = self.new_piece()

    def new_piece(self):
        return Piece(random.choice(SHAPES))

    def valid(self, shape, x, y):
        for dy, row in enumerate(shape):
            for dx, cell in enumerate(row):
                if cell:
                    new_x = x + dx
                    new_y = y + dy
                    if new_x < 0 or new_x >= COLUMNS or new_y >= ROWS:
                        return False
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return False
        return True

    def lock_piece(self):
        for dy, row in enumerate(self.current.shape):
            for dx, cell in enumerate(row):
                if cell:
                    self.grid[self.current.y + dy][self.current.x + dx] = 1
        self.clear_lines()
        self.current = self.new_piece()
        if not self.valid(self.current.shape, self.current.x, self.current.y):
            self.game_over = True

    def clear_lines(self):
        lines_to_clear = [i for i, row in enumerate(self.grid) if all(row)]
        for i in lines_to_clear:
            del self.grid[i]
            self.grid.insert(0, [0 for _ in range(COLUMNS)])
        if lines_to_clear:
            self.lines += len(lines_to_clear)
            self.score += (len(lines_to_clear) ** 2) * 100
            self.level = 1 + self.lines // 10
            self.fall_speed = max(100, 500 - (self.level - 1) * 20)

    def soft_drop(self):
        if self.valid(self.current.shape, self.current.x, self.current.y + 1):
            self.current.y += 1
        else:
            self.lock_piece()

    def hard_drop(self):
        while self.valid(self.current.shape, self.current.x, self.current.y + 1):
            self.current.y += 1
        self.lock_piece()

# ===============================
# 🔹 Guardado de puntaje en Oracle
# ===============================
# ===============================
# 🔹 Guardado de puntaje en Oracle
# ===============================
def persist_score(player, score, lines, level):
    try:
        user = os.getenv("ORACLE_USER")
        password = os.getenv("ORACLE_PASSWORD")
        dsn = os.getenv("ORACLE_DSN")

        with oracledb.connect(user=user, password=password, dsn=dsn) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO tetris_scores (player_name, score, lines_cleared, game_level, played_at)
                VALUES (:1, :2, :3, :4, SYSTIMESTAMP)
                """,
                (player, score, lines, level),
            )
            connection.commit()
            print(f"✅ Puntaje guardado en Oracle: {player} - {score}")
    except Exception as e:
        print(f"⚠️ Error al guardar en Oracle: {e}")    

# ===============================
# 🔹 Funciones auxiliares de dibujo
# ===============================
def draw_grid(screen, game, font):
    for y in range(ROWS):
        for x in range(COLUMNS):
            val = game.grid[y][x]
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if val:
                color = COLORS[(val - 1) % len(COLORS)]
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)
            else:
                pygame.draw.rect(screen, (30, 30, 30), rect, 1)

    for dy, row in enumerate(game.current.shape):
        for dx, cell in enumerate(row):
            if cell:
                x = (game.current.x + dx) * CELL_SIZE
                y = (game.current.y + dy) * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, game.current.color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)

    text_surface = font.render(f'Score: {game.score}', True, (255, 255, 255))
    screen.blit(text_surface, (10, HEIGHT - 70))
    text_surface = font.render(f'Lines: {game.lines}', True, (255, 255, 255))
    screen.blit(text_surface, (150, HEIGHT - 70))
    text_surface = font.render(f'Level: {game.level}', True, (255, 255, 255))
    screen.blit(text_surface, (220, HEIGHT - 70))

# ===============================
# 🔹 Main
# ===============================
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Tetris - Guarda puntaje en Oracle')
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('dejavusans', 20)

    game = Tetris()

    fall_event = pygame.USEREVENT + 1
    pygame.time.set_timer(fall_event, game.fall_speed)

    player_name = 'Player'

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if game.valid(game.current.shape, game.current.x - 1, game.current.y):
                        game.current.x -= 1
                elif event.key == pygame.K_RIGHT:
                    if game.valid(game.current.shape, game.current.x + 1, game.current.y):
                        game.current.x += 1
                elif event.key == pygame.K_DOWN:
                    game.soft_drop()
                elif event.key == pygame.K_UP:
                    original = [row[:] for row in game.current.shape]
                    game.current.rotate()
                    if not game.valid(game.current.shape, game.current.x, game.current.y):
                        game.current.shape = original
                elif event.key == pygame.K_SPACE:
                    game.hard_drop()
                elif event.key == pygame.K_n:
                    game = Tetris()
                elif event.key == pygame.K_s:
                    try:
                        print('Ingresa nombre del jugador (en la consola): ')
                        name = input().strip()
                        if name:
                            player_name = name
                    except Exception:
                        pass

            elif event.type == fall_event:
                pygame.time.set_timer(fall_event, game.fall_speed)
                if not game.game_over:
                    game.soft_drop()

        screen.fill((10, 10, 10))
        draw_grid(screen, game, font)

        if game.game_over:
            big = pygame.font.SysFont('dejavusans', 24)
            surf = big.render('GAME OVER - Press N to start new game', True, (255, 0, 0))
            screen.blit(surf, (20, HEIGHT // 2 - 20))
            if not getattr(game, '_score_persisted', False):
                persist_score(player_name, game.score, game.lines, game.level)
                game._score_persisted = True

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    print("🎮 Iniciando Tetris con Oracle...")
    main()
