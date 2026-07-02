import pygame
import sys
from A_star import A_star_search, manhattan, euclidean, chebyshev

pygame.init()

# 常量
GRID_SIZE = 40
COLS = 20
ROWS = 15
# 窗口宽度
WIDTH = COLS * GRID_SIZE + 150
HEIGHT = ROWS * GRID_SIZE + 50
BUTTON_HEIGHT = 50

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("A*算法可视化")
clock = pygame.time.Clock()

# 使用中文字体
try:
    FONT = pygame.font.SysFont('SimHei', 16)
except:
    FONT = pygame.font.SysFont('Arial', 16)

SMALL_FONT = pygame.font.SysFont('Arial', 10)

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)      
RED = (213, 55, 61)        
GREY = (128, 128, 128)     
LIGHT_GREY = (220, 220, 220)
BLUE = (50, 120, 219)      
PURPLE = (128, 0, 128)     
ORANGE = (255, 165, 0)     
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER = (170, 170, 170)
BUTTON_ACTIVE = (100, 150, 255)
LIGHT_BLUE = (173, 216, 230)      
LIGHT_BLUE_HOVER = (135, 206, 250)  

# 初始化状态
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
start = None
end = None
path = []
g_score = {}
f_score = {}
open_set = set()
closed_set = set()
search_done = False
show_no_path_message = False
tool_mode = 'start'

# 启发函数选择
heuristic_mode = 'manhattan'

# 顶部功能按钮
buttons = {
    'start': pygame.Rect(0, 0, 100, BUTTON_HEIGHT),
    'end': pygame.Rect(100, 0, 100, BUTTON_HEIGHT),
    'wall': pygame.Rect(200, 0, 120, BUTTON_HEIGHT),
    'clear_walls': pygame.Rect(320, 0, 150, BUTTON_HEIGHT),
    'run': pygame.Rect(470, 0, 80, BUTTON_HEIGHT),
    'reset': pygame.Rect(550, 0, 100, BUTTON_HEIGHT),
}

button_labels = {
    'start': '选择起点',
    'end': '选择终点',
    'wall': '选择障碍物',
    'clear_walls': '障碍物一键清零',
    'run': '开始',
    'reset': '清除界面',
}

HEURISTIC_BUTTON_WIDTH = 120
HEURISTIC_BUTTON_HEIGHT = 40
HEURISTIC_START_X = COLS * GRID_SIZE + 10  # 网格右侧 + 10px 边距
HEURISTIC_START_Y = 60  # 在顶部按钮下方一点开始

heuristic_buttons = {}
heuristic_labels = {
    'manhattan': '曼哈顿距离',
    'euclidean': '欧氏距离',
    'chebyshev': '切比雪夫距离',
}

# 生成纵向按钮位置
for i, h_type in enumerate(['manhattan', 'euclidean', 'chebyshev']):
    rect = pygame.Rect(
        HEURISTIC_START_X,
        HEURISTIC_START_Y + i * (HEURISTIC_BUTTON_HEIGHT + 10),  # 间距
        HEURISTIC_BUTTON_WIDTH,
        HEURISTIC_BUTTON_HEIGHT
    )
    heuristic_buttons[h_type] = rect


def reset():
    global grid, start, end, path, g_score, f_score, open_set, closed_set, search_done, tool_mode, show_no_path_message
    grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    start = None
    end = None
    path = []
    g_score.clear()
    f_score.clear()
    open_set.clear()
    closed_set.clear()
    search_done = False
    show_no_path_message = False
    tool_mode = 'start'

def clear_walls_only():
    global grid, search_done, show_no_path_message
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] == 1:
                grid[r][c] = 0
    search_done = False
    show_no_path_message = False

def draw_buttons():
    # 顶部功能按钮
    for mode, rect in buttons.items():
        color = BUTTON_ACTIVE if tool_mode == mode else BUTTON_COLOR
        mouse_pos = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_pos):
            color = BUTTON_HOVER if tool_mode != mode else BUTTON_ACTIVE
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 1)
        text = FONT.render(button_labels[mode], True, BLACK)
        screen.blit(text, (rect.x + 20, rect.y + 15))

    # 右侧纵向距离按钮
    for h_type, rect in heuristic_buttons.items():
        if h_type == heuristic_mode:
            color = LIGHT_BLUE
        else:
            color = BUTTON_COLOR
        mouse_pos = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_pos):
            if h_type == heuristic_mode:
                color = LIGHT_BLUE_HOVER
            else:
                color = BUTTON_HOVER
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 1)
        text = FONT.render(heuristic_labels[h_type], True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

def draw_grid():
    for r in range(ROWS):
        for c in range(COLS):
            color = LIGHT_GREY
            rect = pygame.Rect(c * GRID_SIZE, r * GRID_SIZE + BUTTON_HEIGHT, GRID_SIZE, GRID_SIZE)
            if grid[r][c] == 1:
                color = GREY
            elif (r, c) == start:
                color = GREEN
            elif (r, c) == end:
                color = RED
            elif (r, c) in path and search_done:
                color = PURPLE
            elif (r, c) in closed_set:
                color = ORANGE
            elif (r, c) in open_set:
                color = BLUE
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

            if search_done:
                node = (r, c)
                if node in g_score:
                    g = g_score[node]
                    if heuristic_mode == 'manhattan':
                        h_val = manhattan(node, end) * 10 if end else 0
                    elif heuristic_mode == 'euclidean':
                        h_val = round(euclidean(node, end) * 10, 1) if end else 0
                    elif heuristic_mode == 'chebyshev':
                        h_val = chebyshev(node, end) * 10 if end else 0
                    else:
                        h_val = 0
                    f = g + h_val
                    text_f = SMALL_FONT.render(str(f), True, BLACK)
                    screen.blit(text_f, (c * GRID_SIZE + 2, r * GRID_SIZE + BUTTON_HEIGHT + 2))
                    text_g = SMALL_FONT.render(str(g), True, BLACK)
                    screen.blit(text_g, (c * GRID_SIZE + 2, r * GRID_SIZE + BUTTON_HEIGHT + GRID_SIZE - 12))
                    text_h = SMALL_FONT.render(str(h_val), True, BLACK)
                    screen.blit(text_h, (c * GRID_SIZE + GRID_SIZE - 18, r * GRID_SIZE + BUTTON_HEIGHT + GRID_SIZE - 12))

def draw_no_path_popup():
    if not show_no_path_message:
        return

    s = pygame.Surface((WIDTH, HEIGHT))
    s.set_alpha(150)
    s.fill(BLACK)
    screen.blit(s, (0, 0))

    popup_width, popup_height = 300, 100
    popup_x = (WIDTH - popup_width) // 2
    popup_y = (HEIGHT - popup_height) // 2
    pygame.draw.rect(screen, WHITE, (popup_x, popup_y, popup_width, popup_height))
    pygame.draw.rect(screen, RED, (popup_x, popup_y, popup_width, popup_height), 3)

    try:
        msg_font = pygame.font.SysFont('SimHei', 18)
    except:
        msg_font = pygame.font.SysFont('Arial', 18)
    text = msg_font.render("未找到路径，请重新规划", True, BLACK)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)

    try:
        hint_font = pygame.font.SysFont('SimHei', 14)
    except:
        hint_font = pygame.font.SysFont('Arial', 14)
    hint = hint_font.render("点击任意位置或按任意键关闭", True, WHITE)
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, popup_y + popup_height + 10))

def run_a_star():
    global path, g_score, f_score, open_set, closed_set, search_done, show_no_path_message
    if not start or not end:
        return
    cost, found_path, g_dict, f_dict = A_star_search(grid, start, end, heuristic_type=heuristic_mode)
    if found_path:
        path = found_path
        g_score = g_dict
        f_score = f_dict
        closed_set = set(g_dict.keys()) - set(path)
        open_set = set()
        search_done = True
        show_no_path_message = False
        print(f"找到路径，总代价: {cost}（使用 {heuristic_mode}）")
    else:
        print("未找到路径")
        show_no_path_message = True

def handle_click_on_grid(pos):
    global start, end, tool_mode
    x, y = pos
    if y < BUTTON_HEIGHT:
        return
    c = x // GRID_SIZE
    r = (y - BUTTON_HEIGHT) // GRID_SIZE
    if r < 0 or r >= ROWS or c < 0 or c >= COLS:
        return

    if tool_mode == 'wall':
        if (start is None or (r, c) != start) and (end is None or (r, c) != end):
            grid[r][c] = 1

    elif tool_mode == 'clear_walls':
        if (r, c) != start and (r, c) != end:
            grid[r][c] = 0

    elif tool_mode == 'start':
        if (end is None or (r, c) != end) and grid[r][c] != 1:
            start = (r, c)
            tool_mode = 'end'

    elif tool_mode == 'end':
        if (start is None or (r, c) != start) and grid[r][c] != 1:
            end = (r, c)
            tool_mode = 'wall'

def main():
    global tool_mode, show_no_path_message, heuristic_mode  
    reset()
    while True:
        screen.fill(WHITE)
        draw_buttons()
        draw_grid()
        if show_no_path_message:
            draw_no_path_popup()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if show_no_path_message:
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                    show_no_path_message = False
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                clicked = False

                # 检查顶部按钮
                for mode, rect in buttons.items():
                    if rect.collidepoint(x, y):
                        if mode == 'run':
                            run_a_star()
                        elif mode == 'reset':
                            reset()
                        elif mode == 'clear_walls':
                            clear_walls_only()
                        else:
                            tool_mode = mode
                        clicked = True
                        break

                if not clicked:
                    for h_type, rect in heuristic_buttons.items():
                        if rect.collidepoint(x, y):
                            heuristic_mode = h_type
                            clicked = True
                            break

                if not clicked:
                    handle_click_on_grid(event.pos)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if start and end:
                        run_a_star()
                elif event.key == pygame.K_r:
                    reset()

        clock.tick(60)

if __name__ == "__main__":
    main()