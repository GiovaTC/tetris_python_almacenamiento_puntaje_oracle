#!/usr/bin/env python3

def draw_grid(screen, game, font):
    for y in range(ROWS):
        for x in range(COLUMNS):
            val = game.grid[y][x]
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if val:
                color=COLORS[( val - 1 ) % len(COLORS)]
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)
            else:
                pygame.draw.rect(screen, (30, 30, 30), rect, 1)

    #pieza actual
    for dy, row in enumerate(game.current.shape):
        for dx, cell in enumerate(row):
            if cell:
                x = (game.current.x + dx) * CELL_SIZE
                y = (game.current.y + dy) * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, game.current.color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)    

    #ui texto