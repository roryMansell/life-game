import sys
import random
import pygame

# --- Config ---
CELL_SIZE = 12        # pixels per cell
GRID_W, GRID_H = 80, 50  # cells
FPS = 30
BG = (16, 18, 22)
GRID_COLOR = (40, 44, 52)
ALIVE = (0, 200, 130)
DEAD = (28, 31, 38)

# Controls:
#  - Space: play/pause
#  - N: step one generation
#  - R: randomize
#  - C: clear
#  - Left click/drag: toggle cells
#  - Right click/drag: erase cells
#  - Esc or Q: quit

def neighbors(x, y, w, h):
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                yield nx, ny

def step(world):
    w, h = len(world), len(world[0])
    new = [[False]*h for _ in range(w)]
    for x in range(w):
        for y in range(h):
            alive_neighbors = sum(1 for nx, ny in neighbors(x, y, w, h) if world[nx][ny])
            if world[x][y]:
                new[x][y] = alive_neighbors in (2, 3)
            else:
                new[x][y] = alive_neighbors == 3
    return new

def randomize(world, p=0.2):
    for x in range(len(world)):
        for y in range(len(world[0])):
            world[x][y] = random.random() < p

def clear(world):
    for x in range(len(world)):
        for y in range(len(world[0])):
            world[x][y] = False

def draw(screen, world, font, paused, gen):
    screen.fill(BG)
    # grid
    for x in range(GRID_W + 1):
        px = x * CELL_SIZE
        pygame.draw.line(screen, GRID_COLOR, (px, 0), (px, GRID_H * CELL_SIZE), 1)
    for y in range(GRID_H + 1):
        py = y * CELL_SIZE
        pygame.draw.line(screen, GRID_COLOR, (0, py), (GRID_W * CELL_SIZE, py), 1)

    # cells
    for x in range(GRID_W):
        for y in range(GRID_H):
            if world[x][y]:
                rect = pygame.Rect(x * CELL_SIZE + 1, y * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2)
                pygame.draw.rect(screen, ALIVE, rect)

    # HUD
    hud = f"{'PAUSED' if paused else 'RUNNING'} • Gen {gen} • Space=Play/Pause | N=Step | R=Random | C=Clear | LMB/RMB=Paint"
    surf = font.render(hud, True, (200, 210, 220))
    screen.blit(surf, (10, GRID_H * CELL_SIZE + 8))

def cell_from_mouse(pos):
    mx, my = pos
    x = mx // CELL_SIZE
    y = my // CELL_SIZE
    if 0 <= x < GRID_W and 0 <= y < GRID_H:
        return x, y
    return None

def main():
    pygame.init()
    surface_w = GRID_W * CELL_SIZE
    surface_h = GRID_H * CELL_SIZE + 32  # HUD bar
    screen = pygame.display.set_mode((surface_w, surface_h))
    pygame.display.set_caption("Conway's Game of Life — Rory Mansell")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Segoe UI", 16)

    world = [[False]*GRID_H for _ in range(GRID_W)]
    paused = True
    gen = 0
    painting_state = None  # True=paint alive, False=erase, None=not painting

    running = True
    while running:
        # --- input ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_n:   # step once
                    world = step(world)
                    gen += 1
                elif event.key == pygame.K_r:   # random fill
                    randomize(world, p=0.22)
                    gen = 0
                    paused = True
                elif event.key == pygame.K_c:   # clear
                    clear(world)
                    gen = 0
                    paused = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:   # left -> paint alive
                    painting_state = True
                elif event.button == 3: # right -> erase
                    painting_state = False

                cell = cell_from_mouse(event.pos)
                if cell:
                    x, y = cell
                    world[x][y] = painting_state if painting_state is not None else not world[x][y]

            elif event.type == pygame.MOUSEBUTTONUP:
                painting_state = None

        # continuous painting while dragging
        if painting_state is not None and pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
            cell = cell_from_mouse(pygame.mouse.get_pos())
            if cell:
                x, y = cell
                world[x][y] = painting_state

        # --- update ---
        if not paused:
            world = step(world)
            gen += 1

        # --- draw ---
        draw(screen, world, font, paused, gen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
