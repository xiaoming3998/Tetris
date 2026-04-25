import pygame
import random

# 初始化 pygame
pygame.init()

# --- 設定參數 ---
BLOCK_SIZE = 30
COLS = 10
ROWS = 20
GAME_WIDTH = COLS * BLOCK_SIZE  # 300
SIDEBAR_WIDTH = 200             # 側邊欄寬度
SCREEN_WIDTH = GAME_WIDTH + SIDEBAR_WIDTH
SCREEN_HEIGHT = ROWS * BLOCK_SIZE # 600

# 設定畫面
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("俄羅斯方塊 - 預覽功能版")

# 定義顏色
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),  # I
    (255, 0, 0),    # Z
    (0, 255, 0),    # S
    (128, 0, 128),  # T
    (255, 255, 0),  # O
    (255, 165, 0),  # L
    (0, 0, 255),    # J
]

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]]
]

class Tetromino:
    def __init__(self):
        self.type = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.type]
        self.color = COLORS[self.type]
        # 初始位置
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

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

def merge(board, shape, offset_x, offset_y, color):
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell and offset_y + y >= 0:
                board[offset_y + y][offset_x + x] = color

def clear_lines(board):
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    cleared = ROWS - len(new_board)
    for _ in range(cleared):
        new_board.insert(0, [0] * COLS)
    return new_board, cleared

# 繪製畫面
def draw_board(screen, board, current, next_piece, score):
    screen.fill(BLACK)
    
    # 1. 畫遊戲區域內的方塊
    for y in range(ROWS):
        for x in range(COLS):
            block_color = board[y][x]
            if block_color:
                pygame.draw.rect(screen, block_color,
                                 (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    
    # 2. 畫當前方塊
    for y, row in enumerate(current.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, current.color,
                                 ((current.x + x) * BLOCK_SIZE, (current.y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    # 3. 畫網格 (只畫在遊戲區)
    for x in range(COLS + 1):
        pygame.draw.line(screen, GRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, SCREEN_HEIGHT))
    for y in range(ROWS + 1):
        pygame.draw.line(screen, GRAY, (0, y * BLOCK_SIZE), (GAME_WIDTH, y * BLOCK_SIZE))

    # 4. 畫側邊欄資訊
    font = pygame.font.SysFont("notosanstc", 30) # 修正部分系統字體問題
    
    # 顯示分數
    score_label = font.render("Score:", True, WHITE)
    score_num = font.render(str(score), True, WHITE)
    screen.blit(score_label, (GAME_WIDTH + 20, 50))
    screen.blit(score_num, (GAME_WIDTH + 20, 80))

    # 顯示「Next」標籤
    next_label = font.render("Next:", True, WHITE)
    screen.blit(next_label, (GAME_WIDTH + 20, 150))

    # 5. 畫預覽方塊
    # 預覽框的基準位置
    preview_x = GAME_WIDTH + 50
    preview_y = 200
    for y, row in enumerate(next_piece.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, next_piece.color,
                                 (preview_x + x * BLOCK_SIZE, preview_y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    pygame.display.flip()

def main():
    clock = pygame.time.Clock()
    board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    
    # 初始化：需要一個當前方塊與一個預覽方塊
    current = Tetromino()
    next_piece = Tetromino()
    
    fall_time = 0
    fall_speed = 0.5
    score = 0

    running = True
    while running:
        fall_time += clock.get_rawtime()
        clock.tick()

        # 下落邏輯
        if fall_time / 1000 > fall_speed:
            if not check_collision(board, current.shape, current.x, current.y + 1):
                current.y += 1
            else:
                merge(board, current.shape, current.x, current.y, current.color)
                board, cleared = clear_lines(board)
                score += cleared * 100
                
                # 方塊落地，交換方塊
                current = next_piece
                next_piece = Tetromino()
                
                # 檢查是否 Game Over
                if check_collision(board, current.shape, current.x, current.y):
                    print(f"Game Over! Final Score: {score}")
                    running = False
            fall_time = 0

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

        draw_board(screen, board, current, next_piece, score)

    pygame.quit()

if __name__ == "__main__":
    main()