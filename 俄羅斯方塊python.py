import pygame
import random

# 初始化 pygame
pygame.init()

# --- 設定參數 ---
BLOCK_SIZE = 30
COLS = 10
ROWS = 20
GAME_WIDTH = COLS * BLOCK_SIZE
SIDEBAR_WIDTH = 200
SCREEN_WIDTH = GAME_WIDTH + SIDEBAR_WIDTH
SCREEN_HEIGHT = ROWS * BLOCK_SIZE

# 設定畫面
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("俄羅斯方塊 - 暫停功能版")

# 定義顏色
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
COLORS = [
    (0, 255, 255), (255, 0, 0), (0, 255, 0),
    (128, 0, 128), (255, 255, 0), (255, 165, 0), (0, 0, 255)
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
def draw_board(screen, board, current, next_piece, score, paused):
    screen.fill(BLACK)
    
    # 1. 畫遊戲區域內已固定的方塊
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

    # 3. 畫網格
    for x in range(COLS + 1):
        pygame.draw.line(screen, GRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, SCREEN_HEIGHT))
    for y in range(ROWS + 1):
        pygame.draw.line(screen, GRAY, (0, y * BLOCK_SIZE), (GAME_WIDTH, y * BLOCK_SIZE))

    # 4. 畫側邊欄
    font = pygame.font.SysFont("notosanstc", 30)
    
    score_label = font.render("Score:", True, WHITE)
    score_num = font.render(str(score), True, WHITE)
    screen.blit(score_label, (GAME_WIDTH + 20, 50))
    screen.blit(score_num, (GAME_WIDTH + 20, 80))

    next_label = font.render("Next:", True, WHITE)
    screen.blit(next_label, (GAME_WIDTH + 20, 150))

    preview_x = GAME_WIDTH + 50
    preview_y = 200
    for y, row in enumerate(next_piece.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, next_piece.color,
                                 (preview_x + x * BLOCK_SIZE, preview_y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    # 5. 畫暫停提示
    if paused:
        # 建立一個半透明的遮罩 (Surface)
        overlay = pygame.Surface((GAME_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) # 最後一個參數是透明度 (0-255)
        screen.blit(overlay, (0, 0))
        
        pause_font = pygame.font.SysFont("notosanstc", 50)
        pause_text = pause_font.render("PAUSED", True, RED)
        # 將文字置中於遊戲區
        text_rect = pause_text.get_rect(center=(GAME_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(pause_text, text_rect)

    pygame.display.flip()

def main():
    clock = pygame.time.Clock()
    board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    
    current = Tetromino()
    next_piece = Tetromino()
    
    fall_time = 0
    fall_speed = 0.5
    score = 0
    paused = False # 初始化暫停狀態

    running = True
    while running:
        # 即使暫停也需要更新時鐘，但我們有邏輯判斷是否處理下落
        delta_time = clock.get_rawtime()
        clock.tick()

        if not paused:
            fall_time += delta_time
            # 下落邏輯
            if fall_time / 1000 > fall_speed:
                if not check_collision(board, current.shape, current.x, current.y + 1):
                    current.y += 1
                else:
                    merge(board, current.shape, current.x, current.y, current.color)
                    board, cleared = clear_lines(board)
                    score += cleared * 100
                    current = next_piece
                    next_piece = Tetromino()
                    if check_collision(board, current.shape, current.x, current.y):
                        running = False
                fall_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # 暫停鍵邏輯：無論是否暫停都偵測 P 鍵
                if event.key == pygame.K_p:
                    paused = not paused
                
                # 只有在非暫停狀態下才處理遊戲控制
                if not paused:
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

        draw_board(screen, board, current, next_piece, score, paused)

    pygame.quit()

if __name__ == "__main__":
    main()