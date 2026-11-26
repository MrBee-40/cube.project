import pygame
import sys

pygame.init()

TILE = 48
COLS = 15
ROWS = 11

WIDTH = COLS * TILE
HEIGHT = ROWS * TILE + 110

FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Подземелье сокровищ")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 24, bold=True)
small_font = pygame.font.SysFont("arial", 18, bold=True)
big_font = pygame.font.SysFont("arial", 38, bold=True)

BG = (20, 20, 29)
WALL = (65, 65, 85)
FLOOR = (35, 35, 48)
PLAYER_COLOR = (60, 160, 255)
COIN_COLOR = (255, 205, 40)
TRAP_COLOR = (210, 50, 50)
SAFE_TRAP = (90, 65, 65)
DOOR_COLOR = (140, 90, 45)
EXIT_COLOR = (40, 200, 100)
WHITE = (255, 255, 255)

def create_room(walls, coins, traps):
    grid = [
        [0 for _ in range(COLS)]
        for _ in range(ROWS)
    ]

    for x in range(COLS):
        grid[0][x] = 1
        grid[ROWS - 1][x] = 1

    for y in range(ROWS):
        grid[y][0] = 1
        grid[y][COLS - 1] = 1

    for x, y in walls:
        grid[y][x] = 1

    return {
        "grid": grid,
        "coins": set(coins),
        "traps": set(traps)
    }

rooms = [

    create_room(
        walls=[
            (4, 2), (4, 3), (4, 4),
            (8, 5), (8, 6),
            (10, 2), (10, 3),
            (6, 8), (7, 8)
        ],
        coins=[
            (3, 1), (6, 2), (7, 4),
            (12, 3), (5, 7)
        ],
        traps=[
            (5, 3), (6, 3), (9, 6), (11, 7)
        ]
    ),

    create_room(
        walls=[
            (3, 2), (4, 2), (5, 2),
            (9, 3), (9, 4), (9, 5),
            (5, 7), (6, 7), (7, 7),
            (12, 2)
        ],
        coins=[
            (7, 1), (11, 2), (3, 5),
            (11, 7), (7, 9)
        ],
        traps=[
            (6, 4), (7, 4), (8, 4),
            (3, 8), (10, 8)
        ]
    ),

    create_room(
        walls=[
            (3, 2), (3, 3), (3, 4),
            (6, 5), (7, 5), (8, 5),
            (11, 2), (11, 3),
            (5, 8), (6, 8)
        ],
        coins=[
            (5, 1), (9, 2), (12, 4),
            (2, 7), (9, 8)
        ],
        traps=[
            (4, 5), (5, 5), (9, 5),
            (10, 7), (11, 7), (12, 7)
        ]
    )
]

ROOM_COUNT = len(rooms)
EXIT_COST = 6

player_x = 1
player_y = 1

current_room = 0
total_coins = 0

game_over = False
victory = False
death_time = 0

last_move = 0
MOVE_DELAY = 130

message = ""
message_time = 0


def reset_game():
    global player_x, player_y
    global current_room, total_coins
    global game_over, victory
    global message

    player_x = 1
    player_y = 1

    current_room = 0
    total_coins = 0

    for room in rooms:
        room["coins"] = set(room["original_coins"])

    game_over = False
    victory = False
    message = ""


for room in rooms:
    room["original_coins"] = set(room["coins"])


def show_message(text):
    global message, message_time
    message = text
    message_time = pygame.time.get_ticks()


def die():
    global game_over, death_time

    game_over = True
    death_time = pygame.time.get_ticks()

def move_player(dx, dy):
    global player_x, player_y
    global current_room, total_coins
    global victory

    new_x = player_x + dx
    new_y = player_y + dy

    room = rooms[current_room]
    grid = room["grid"]

    if not (0 <= new_x < COLS and 0 <= new_y < ROWS):
        return

    if grid[new_y][new_x] == 1:
        return

    player_x = new_x
    player_y = new_y

    position = (player_x, player_y)

    if position in room["coins"]:
        room["coins"].remove(position)
        total_coins += 1
        show_message("+1 МОНЕТА!")

    if position in room["traps"] and trap_is_active():
        die()
        return

    if position == (13, 9):

        if current_room < ROOM_COUNT - 1:

            current_room += 1

            player_x = 1
            player_y = 1

            show_message("НОВАЯ КОМНАТА!")

        else:

            if total_coins >= EXIT_COST:
                victory = True
            else:
                show_message(
                    f"Нужно еще {EXIT_COST - total_coins} монет!"
                )


def trap_is_active():
    time = pygame.time.get_ticks()
    return (time % 1400) < 850

def draw_game():

    screen.fill(BG)

    room = rooms[current_room]
    grid = room["grid"]

    traps_active = trap_is_active()

    for y in range(ROWS):
        for x in range(COLS):

            rect = pygame.Rect(
                x * TILE,
                y * TILE,
                TILE,
                TILE
            )

            if grid[y][x] == 1:
                pygame.draw.rect(screen, WALL, rect)
                pygame.draw.rect(
                    screen, (85, 85, 105),
                    rect, 2
                )
            else:
                pygame.draw.rect(screen, FLOOR, rect)
                pygame.draw.rect(
                    screen, (45, 45, 58),
                    rect, 1
                )

    for x, y in room["coins"]:

        center = (
            x * TILE + TILE // 2,
            y * TILE + TILE // 2
        )

        pygame.draw.circle(
            screen, COIN_COLOR, center, 11
        )

        pygame.draw.circle(
            screen, (255, 235, 130), center, 5
        )

    for x, y in room["traps"]:

        rect = pygame.Rect(
            x * TILE + 5,
            y * TILE + 5,
            TILE - 10,
            TILE - 10
        )

        color = TRAP_COLOR if traps_active else SAFE_TRAP

        pygame.draw.rect(
            screen, color, rect, border_radius=7
        )

        if traps_active:
            pygame.draw.line(
                screen, WHITE,
                (rect.left + 8, rect.top + 8),
                (rect.right - 8, rect.bottom - 8), 3
            )

            pygame.draw.line(
                screen, WHITE,
                (rect.right - 8, rect.top + 8),
                (rect.left + 8, rect.bottom - 8), 3
            )

    door_rect = pygame.Rect(
        13 * TILE + 7,
        9 * TILE + 5,
        TILE - 14,
        TILE - 10
    )

    if current_room == ROOM_COUNT - 1:
        door_color = (
            EXIT_COLOR if total_coins >= EXIT_COST
            else (110, 65, 65)
        )
    else:
        door_color = DOOR_COLOR

    pygame.draw.rect(
        screen, door_color,
        door_rect, border_radius=6
    )

    pygame.draw.circle(
        screen, COIN_COLOR,
        (door_rect.right - 6, door_rect.centery), 3
    )

    player_rect = pygame.Rect(
        player_x * TILE + 6,
        player_y * TILE + 6,
        TILE - 12,
        TILE - 12
    )

    pygame.draw.rect(
        screen, PLAYER_COLOR,
        player_rect, border_radius=9
    )

    # Глаза кубика
    pygame.draw.circle(
        screen, WHITE,
        (player_rect.x + 11, player_rect.y + 13), 4
    )

    pygame.draw.circle(
        screen, WHITE,
        (player_rect.x + 25, player_rect.y + 13), 4
    )

    pygame.draw.rect(
        screen, (25, 25, 38),
        (0, ROWS * TILE, WIDTH, 110)
    )

    coins_text = font.render(
        f"Монеты: {total_coins} / {EXIT_COST}",
        True, COIN_COLOR
    )

    room_text = font.render(
        f"Комната: {current_room + 1} / {ROOM_COUNT}",
        True, WHITE
    )

    screen.blit(coins_text, (20, ROWS * TILE + 12))
    screen.blit(room_text, (390, ROWS * TILE + 12))

    controls = small_font.render(
        "WASD / Стрелки - движение",
        True, (180, 180, 190)
    )

    screen.blit(
        controls, (20, ROWS * TILE + 53)
    )

    if message and pygame.time.get_ticks() - message_time < 1600:

        msg = small_font.render(
            message, True, WHITE
        )

        screen.blit(
            msg,
            msg.get_rect(
                center=(WIDTH // 2, HEIGHT - 12)
            )
        )

running = True

while running:

    clock.tick(FPS)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if game_over:

                if pygame.time.get_ticks() - death_time > 900:
                    reset_game()

                continue

            if victory:
                if event.key in (pygame.K_RETURN, pygame.K_r):
                    reset_game()

                continue

            keys = {
                pygame.K_UP: (0, -1),
                pygame.K_w: (0, -1),

                pygame.K_DOWN: (0, 1),
                pygame.K_s: (0, 1),

                pygame.K_LEFT: (-1, 0),
                pygame.K_a: (-1, 0),

                pygame.K_RIGHT: (1, 0),
                pygame.K_d: (1, 0)
            }

            if event.key in keys:

                now = pygame.time.get_ticks()

                if now - last_move >= MOVE_DELAY:

                    dx, dy = keys[event.key]

                    move_player(dx, dy)

                    last_move = now

    if not game_over and not victory:

        if (
            (player_x, player_y)
            in rooms[current_room]["traps"]
            and trap_is_active()
        ):
            die()

    if game_over:

        screen.fill((35, 15, 20))

        title = big_font.render(
            "ВЫ ПОПАЛИ В ЛОВУШКУ!",
            True, (255, 75, 75)
        )

        subtitle = font.render(
            "Подземелье начинается заново...",
            True, WHITE
        )

        screen.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 - 25)
            )
        )

        screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 + 35)
            )
        )

        if pygame.time.get_ticks() - death_time > 1000:
            reset_game()

    elif victory:

        screen.fill((15, 40, 25))

        title = big_font.render(
            "ПОБЕДА!",
            True, EXIT_COLOR
        )

        subtitle = font.render(
            "Вы выбрались из подземелья!",
            True, WHITE
        )

        coins = font.render(
            f"Собрано монет: {total_coins}",
            True, COIN_COLOR
        )

        restart = small_font.render(
            "Нажмите ENTER для новой игры",
            True, WHITE
        )

        screen.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 - 75)
            )
        )

        screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 - 15)
            )
        )

        screen.blit(
            coins,
            coins.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 + 30)
            )
        )

        screen.blit(
            restart,
            restart.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 + 90)
            )
        )

    else:
        draw_game()

    pygame.display.flip()


pygame.quit()
sys.exit()