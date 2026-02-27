import curses
import random

DIRECTIONS = [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]
OPPOSITES = {
    curses.KEY_UP: curses.KEY_DOWN,
    curses.KEY_DOWN: curses.KEY_UP,
    curses.KEY_LEFT: curses.KEY_RIGHT,
    curses.KEY_RIGHT: curses.KEY_LEFT,
}


def move_head(head, direction):
    r, c = head
    if direction == curses.KEY_UP:    return [r - 1, c]
    if direction == curses.KEY_DOWN:  return [r + 1, c]
    if direction == curses.KEY_LEFT:  return [r, c - 1]
    if direction == curses.KEY_RIGHT: return [r, c + 1]


def hits_wall(pos, sh, sw):
    return pos[0] <= 0 or pos[0] >= sh - 1 or pos[1] <= 0 or pos[1] >= sw - 1


def place_food(snake1, snake2, sh, sw):
    occupied = set(map(tuple, snake1 + snake2))
    while True:
        pos = [random.randint(1, sh - 2), random.randint(1, sw - 2)]
        if tuple(pos) not in occupied:
            return pos


def safe_dirs(head, current_dir, snake_self, snake_other, sh, sw):
    """Return directions the enemy can move without immediately dying."""
    result = []
    for d in DIRECTIONS:
        if d == OPPOSITES[current_dir]:
            continue
        nh = move_head(head, d)
        if hits_wall(nh, sh, sw):
            continue
        if nh in snake_self[:-1] or nh in snake_other:
            continue
        result.append(d)
    return result


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    sh, sw = stdscr.getmaxyx()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN,   curses.COLOR_BLACK)  # player
    curses.init_pair(2, curses.COLOR_RED,     curses.COLOR_BLACK)  # food
    curses.init_pair(3, curses.COLOR_YELLOW,  curses.COLOR_BLACK)  # score / ui
    curses.init_pair(4, curses.COLOR_CYAN,    curses.COLOR_BLACK)  # border
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # enemy

    def draw_border():
        stdscr.attron(curses.color_pair(4))
        stdscr.border()
        stdscr.attroff(curses.color_pair(4))

    # ── Initial positions ──────────────────────────────────────────────────────
    mid_r = sh // 2
    player = [[mid_r, sw // 4 + i] for i in range(3, 0, -1)]   # head left, tail right
    player_dir = curses.KEY_RIGHT

    enemy = [[mid_r, 3 * sw // 4 - i] for i in range(3, 0, -1)]  # head right, tail left
    enemy_dir = curses.KEY_LEFT

    food = place_food(player, enemy, sh, sw)
    score = 0

    # Enemy direction-change timer
    change_in = random.randint(5, 15)

    reason = ""

    while True:
        # ── Draw ──────────────────────────────────────────────────────────────
        stdscr.clear()
        draw_border()

        stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
        stdscr.addstr(0, 2, f" Score: {score} ")
        hint = " ↑↓←→ move  q quit "
        stdscr.addstr(0, sw - len(hint) - 1, hint)
        stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)

        stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        stdscr.addch(food[0], food[1], 'O')
        stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

        for i, seg in enumerate(player):
            stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
            stdscr.addch(seg[0], seg[1], '@' if i == 0 else '#')
            stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        for i, seg in enumerate(enemy):
            stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            stdscr.addch(seg[0], seg[1], 'X' if i == 0 else 'x')
            stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)

        stdscr.refresh()

        # ── Player input ──────────────────────────────────────────────────────
        key = stdscr.getch()
        if key == ord('q'):
            reason = "Quit"
            break
        if key in DIRECTIONS and key != OPPOSITES[player_dir]:
            player_dir = key

        # ── Compute next heads ────────────────────────────────────────────────
        new_player = move_head(player[0], player_dir)

        # Enemy: countdown to random direction change
        change_in -= 1
        if change_in <= 0:
            candidates = safe_dirs(enemy[0], enemy_dir, enemy, player, sh, sw)
            if not candidates:
                candidates = [d for d in DIRECTIONS if d != OPPOSITES[enemy_dir]]
            enemy_dir = random.choice(candidates)
            change_in = random.randint(5, 15)

        new_enemy = move_head(enemy[0], enemy_dir)

        # Enemy avoids immediate wall/self-collision if possible
        if hits_wall(new_enemy, sh, sw) or new_enemy in enemy[:-1]:
            candidates = safe_dirs(enemy[0], enemy_dir, enemy, player, sh, sw)
            if candidates:
                enemy_dir = random.choice(candidates)
                new_enemy = move_head(enemy[0], enemy_dir)

        # ── Collision checks ──────────────────────────────────────────────────
        # Player hits wall
        if hits_wall(new_player, sh, sw):
            reason = "You hit the wall!"
            break

        # Player hits itself
        if new_player in player[:-1]:
            reason = "You hit your own tail!"
            break

        # Player head hits enemy body
        if new_player in enemy:
            reason = "You crashed into the enemy snake!"
            break

        # Enemy head hits player body
        if new_enemy in player:
            reason = "The enemy snake hit you!"
            break

        # Head-on collision
        if new_player == new_enemy:
            reason = "Head-on collision!"
            break

        # ── Advance both snakes ───────────────────────────────────────────────
        player.insert(0, new_player)
        if new_player == food:
            score += 10
            food = place_food(player, enemy, sh, sw)
        else:
            player.pop()

        enemy.insert(0, new_enemy)
        if new_enemy == food:
            food = place_food(player, enemy, sh, sw)
        else:
            enemy.pop()

    # ── Game Over screen ──────────────────────────────────────────────────────
    stdscr.clear()
    draw_border()

    lines = [
        ("GAME OVER", curses.color_pair(2) | curses.A_BOLD),
        (reason,      curses.color_pair(3) | curses.A_BOLD),
        ("",          0),
        (f"Final Score: {score}", curses.color_pair(3) | curses.A_BOLD),
        ("",          0),
        ("Press any key to exit", curses.color_pair(4)),
    ]
    start_row = sh // 2 - len(lines) // 2
    for i, (text, attr) in enumerate(lines):
        if text:
            col = max(1, (sw - len(text)) // 2)
            stdscr.attron(attr)
            stdscr.addstr(start_row + i, col, text)
            stdscr.attroff(attr)

    stdscr.nodelay(False)
    stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(main)
