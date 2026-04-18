import pygame
import random

# 初始化 pygame
pygame.init()

# 定義遊戲畫面大小
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30

# 計算遊戲網格
COLS = SCREEN_WIDTH // BLOCK_SIZE
ROWS = SCREEN_HEIGHT // BLOCK_SIZE

# 設定畫面
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("俄羅斯方塊")

# 定義顏色
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # I
    (255, 0, 0),    # Z
    (0, 255, 0),    # S
    (128, 0, 128),  # T
    (255, 255, 0),  # O
    (255, 165, 0),  # L
    (0, 0, 255),    # J
]

# 所有七種方塊的形狀
SHAPES = [
    [[1, 1, 1, 1]],

    [[1, 1, 0],
     [0, 1, 1]],

    [[0, 1, 1],
     [1, 1, 0]],

    [[0, 1, 0],
     [1, 1, 1]],

    [[1, 1],
     [1, 1]],

    [[1, 0, 0],
     [1, 1, 1]],

    [[0, 0, 1],
     [1, 1, 1]]
]

# 方塊類別
class Tetromino:
    def __init__(self):
        self.type = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.type]
        self.color = COLORS[self.type]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

# 檢查是否碰撞
def check_collision(board, shape, offset_x, offset_y):
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = offset_x + x
                new_y = offset_y + y
                if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                    return True
                if new_y >= 0 and board[new_y][new_x]:
                    return True
    return False

# 合併方塊到版面
def merge(board, shape, offset_x, offset_y, color):
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell and offset_y + y >= 0:
                board[offset_y + y][offset_x + x] = color

# 消行邏輯
def clear_lines(board):
    cleared = 0
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    cleared = ROWS - len(new_board)
    for _ in range(cleared):
        new_board.insert(0, [0] * COLS)
    return new_board, cleared

# 繪製整個畫面
def draw_board(screen, board, shape, offset_x, offset_y, color, score):
    screen.fill(BLACK)
    for y in range(ROWS):
        for x in range(COLS):
            block_color = board[y][x]
            if block_color:
                pygame.draw.rect(screen, block_color,
                                 (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    # 畫當前方塊
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, color,
                                 ((offset_x + x) * BLOCK_SIZE, (offset_y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    # 畫網格
    for x in range(COLS):
        pygame.draw.line(screen, GRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, SCREEN_HEIGHT))
    for y in range(ROWS):
        pygame.draw.line(screen, GRAY, (0, y * BLOCK_SIZE), (SCREEN_WIDTH, y * BLOCK_SIZE))

    # 顯示分數
    font = pygame.font.SysFont(None, 36)
    score_surf = font.render(f"分數: {score}", True, (255, 255, 255))
    screen.blit(score_surf, (10, 10))

    pygame.display.flip()

# 主程式
def main():
    clock = pygame.time.Clock()
    board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    current = Tetromino()
    fall_time = 0
    fall_speed = 0.5
    score = 0

    running = True
    while running:
        fall_time += clock.get_rawtime()
        clock.tick()

        # 下落
        if fall_time / 1000 > fall_speed:
            if not check_collision(board, current.shape, current.x, current.y + 1):
                current.y += 1
            else:
                merge(board, current.shape, current.x, current.y, current.color)
                board, cleared = clear_lines(board)
                score += cleared * 100
                current = Tetromino()
                if check_collision(board, current.shape, current.x, current.y):
                    print("Game Over")
                    running = False
            fall_time = 0

        # 處理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if not check_collision(board, current.shape, current.x - 1, current.y):
                        current.x -= 1
                elif event.key == pygame.K_RIGHT:
                    if not check_collision(board, current.shape, current.x + 1, current.y):
                        current.x += 1
                elif event.key == pygame.K_DOWN:
                    if not check_collision(board, current.shape, current.x, current.y + 1):
                        current.y += 1
                elif event.key == pygame.K_UP:
                    old_shape = current.shape
                    current.rotate()
                    if check_collision(board, current.shape, current.x, current.y):
                        current.shape = old_shape

        draw_board(screen, board, current.shape, current.x, current.y, current.color, score)

    pygame.quit()

if __name__ == "__main__":
    main()