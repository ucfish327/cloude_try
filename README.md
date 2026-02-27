# Snake Game

A terminal-based Snake game written in Python using the built-in `curses` library.

## Requirements

- Python 3.x (no external packages needed)

---

## Version 1 — Classic Snake

```bash
python3 snake.py
```

| Key | Action |
|-----|--------|
| Arrow keys | Move |
| `q` | Quit |

- Eat food (`O`) to grow and score **10 points**
- Avoid walls and your own tail

---

## Version 2 — Enemy Snake

```bash
python3 snake_v2.py
```

| Key | Action |
|-----|--------|
| Arrow keys | Move |
| `q` | Quit |

| Symbol | Meaning |
|--------|---------|
| `@` / `#` | Your snake (head / body) |
| `X` / `x` | Enemy snake (head / body) |
| `O` | Food |

**New in v2:**
- An enemy snake (`X`) roams the board, changing direction randomly
- Game over if: you hit the enemy, the enemy hits you, head-on collision, you hit a wall, or you hit your own tail
- Eat food to grow and earn **10 points**
