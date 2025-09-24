#!/usr/bin/env python3
import pygame
import sys
import os
import oracledb
from datetime import datetime
from dotenv import load_dotenv

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

# ===============================
# 🔹 Aquí van tus clases Tetris, Piece y persist_score(...)
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

    # pieza actual
    for dy, row in enumerate(game.current.shape):
        for dx, cell in enumerate(row):
            if cell:
                x = (game.current.x + dx) * CELL_SIZE
                y = (game.current.y + dy) * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, game.current.color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)

    # UI texto
    info_x = 10
    text_surface = font.render(f'Score: {game.score}', True, (255, 255, 255))
    screen.blit(text_surface, (info_x, HEIGHT - 70))
    text_surface = font.render(f'Lines: {game.lines}', True, (255, 255, 255))
    screen.blit(text_surface, (info_x + 150, HEIGHT - 70))
    text_surface = font.render(f'Level: {game.level}', True, (255, 255, 255))
    screen.blit(text_surface, (info_x + 300, HEIGHT - 70))


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
            big = pygame.font.SysFont('dejavusans', 36)
            surf = big.render('GAME OVER - Press N to start new game', True, (255, 0, 0))
            screen.blit(surf, (20, HEIGHT // 2 - 20))
            if not getattr(game, '_score_persisted', False):
                persist_score(player_name, game.score, game.lines, game.level)
                game._score_persisted = True

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


# 🔹 Ejecuta el juego si se llama directamente el script
if __name__ == "__main__":
    print("🎮 Iniciando Tetris con Oracle...")
    main()
