import curses
import random
import time

def main(stdscr):
    # Setup
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    sh, sw = stdscr.getmaxyx()
    height, width = sh - 2, sw - 2

    # Colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # snake
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # food
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # score
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)    # border

    def draw_border():
        stdscr.attron(curses.color_pair(4))
        stdscr.border()
        stdscr.attroff(curses.color_pair(4))

    def place_food(snake):
        while True:
            food = [random.randint(1, height), random.randint(1, width)]
            if food not in snake:
                return food

    # Initial snake (3 segments, moving right)
    snake = [
        [sh // 2, sw // 2],
        [sh // 2, sw // 2 - 1],
        [sh // 2, sw // 2 - 2],
    ]
    direction = curses.KEY_RIGHT
    food = place_food(snake)
    score = 0

    while True:
        stdscr.clear()
        draw_border()

        # Score display
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(0, 2, f" Score: {score} ")
        stdscr.attroff(curses.color_pair(3))

        # Draw food
        stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        stdscr.addch(food[0], food[1], '●')
        stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

        # Draw snake
        for i, seg in enumerate(snake):
            stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
            stdscr.addch(seg[0], seg[1], '■' if i == 0 else '□')
            stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        stdscr.refresh()

        # Input
        key = stdscr.getch()
        opposites = {
            curses.KEY_UP: curses.KEY_DOWN,
            curses.KEY_DOWN: curses.KEY_UP,
            curses.KEY_LEFT: curses.KEY_RIGHT,
            curses.KEY_RIGHT: curses.KEY_LEFT,
        }
        if key in (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT):
            if key != opposites.get(direction):
                direction = key
        elif key == ord('q'):
            break

        # Move head
        head = snake[0][:]
        if direction == curses.KEY_UP:
            head[0] -= 1
        elif direction == curses.KEY_DOWN:
            head[0] += 1
        elif direction == curses.KEY_LEFT:
            head[1] -= 1
        elif direction == curses.KEY_RIGHT:
            head[1] += 1

        # Wall collision
        if head[0] <= 0 or head[0] >= sh - 1 or head[1] <= 0 or head[1] >= sw - 1:
            break

        # Self collision
        if head in snake:
            break

        snake.insert(0, head)

        # Eat food
        if head == food:
            score += 10
            food = place_food(snake)
        else:
            snake.pop()

    # Game over screen
    stdscr.clear()
    draw_border()
    msg = f"Game Over! Final Score: {score}"
    hint = "Press any key to exit"
    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
    stdscr.addstr(sh // 2 - 1, (sw - len(msg)) // 2, msg)
    stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
    stdscr.attron(curses.color_pair(3))
    stdscr.addstr(sh // 2 + 1, (sw - len(hint)) // 2, hint)
    stdscr.attroff(curses.color_pair(3))
    stdscr.nodelay(False)
    stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(main)
