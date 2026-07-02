import pygame
import sys
import os
import threading
import time
from pygame.locals import *

def resource_path(relative_path):
    """获取资源的绝对路径，支持开发环境和打包后的exe"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class NQueensVisualizer:
    def __init__(self):
        pygame.init()
        # 设置最小窗口大小
        self.min_width, self.min_height = 800, 600
        self.width, self.height = 1100, 700
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("N皇后问题可视化")
        
        # 颜色定义
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.LIGHT_BLUE = (173, 216, 230)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 128, 0)
        self.BLUE = (0, 0, 255)
        self.NANKAI_PURPLE = (155, 36, 132)  # 南开紫
        
        # 字体
        self.font = pygame.font.SysFont('simhei', 18)
        self.title_font = pygame.font.SysFont('simhei', 24, bold=True)
        self.small_font = pygame.font.SysFont('simhei', 14)
        
        # 状态变量
        self.n = 8
        self.solutions = []
        self.current_solution = 0
        self.is_solving = False
        self.is_paused = False
        self.solver_thread = None
        self.auto_playing = False
        self.error_message = ""
        self.error_timer = 0
        
        # 图片资源
        self.background_image = None
        self.queen_image = None
        
        # 布局参数（将在resize方法中计算）
        self.board_size = 500
        self.board_x = 50
        self.board_y = 100
        self.sidebar_width = 550
        self.sidebar_x = 620
        
        self.scroll_offset = 0
        
        self.load_images()
        self.calculate_layout()  # 初始计算布局
        self.create_ui_elements()
    
    def calculate_layout(self):
        """根据窗口大小计算布局参数"""
        # 棋盘大小自适应（保持正方形，最大为窗口高度的70%）
        max_board_size = min(self.width * 0.5, self.height * 0.7)
        self.board_size = int(max_board_size)  # 完全自适应
        
        # 棋盘位置（居中偏左）
        self.board_x = 50
        self.board_y = (self.height - self.board_size) // 2
        if self.board_y < 80:  # 确保有足够空间显示顶部控件
            self.board_y = 80
        
        # 侧边栏宽度和位置
        self.sidebar_width = max(470, self.width * 0.4)  # 最小300，最大窗口宽度的40%
        self.sidebar_x = self.width - self.sidebar_width - 10
        
        # 按钮位置自适应
        self.create_ui_elements()
    
    def create_ui_elements(self):
        """创建UI元素（根据当前窗口大小）"""
        # 输入框
        self.n_input_rect = pygame.Rect(50, 30, 100, 35)
        self.n_input = "8"
        
        # 速度输入框
        self.speed_input_rect = pygame.Rect(200, 30, 100, 35)
        self.speed_input = "0.05"
        
        # 按钮位置根据窗口宽度自适应
        button_y = self.height - 50  # 底部留出空间
        self.start_btn = pygame.Rect(50, button_y, 80, 35)
        self.pause_btn = pygame.Rect(150, button_y, 80, 35)
        self.next_btn = pygame.Rect(250, button_y, 80, 35)
        self.prev_btn = pygame.Rect(350, button_y, 80, 35)
    
    def load_images(self):
        """加载图片"""
        # 尝试加载背景图片
        current_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(current_dir, "background.jpg")
        if os.path.exists(full_path):
            try:
                self.background_image = pygame.image.load(full_path)
                print(f"成功加载背景图片: {full_path}")
            except:
                print(f"加载背景图片失败: {full_path}")
        
        # 尝试加载皇后图片
        queen_paths = os.path.join(current_dir, "queen.jpg")
        if os.path.exists(queen_paths):
            try:
                self.queen_image = pygame.image.load(queen_paths)
                print(f"成功加载皇后图片: {queen_paths}")
            except:
                print(f"加载皇后图片失败: {queen_paths}")
        
        # 如果没找到皇后图片，创建默认的
        if self.queen_image is None:
            self.create_default_queen()
    
    def create_default_queen(self):
        """创建默认皇后图片"""
        size = 60
        queen = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # 绘制一个简单的皇后图形
        pygame.draw.circle(queen, (255, 215, 0), (size//2, size//2), size//3)
        
        # 皇冠
        points = [
            (size//2 - size//3, size//2 - size//6),
            (size//2 - size//6, size//2 - size//3),
            (size//2, size//2 - size//6),
            (size//2 + size//6, size//2 - size//3),
            (size//2 + size//3, size//2 - size//6)
        ]
        pygame.draw.polygon(queen, (255, 255, 100), points)
        
        self.queen_image = queen
    
    def show_error_message(self, message):
        """显示错误消息"""
        self.error_message = message
        self.error_timer = 180
    
    def draw_ui(self):
        """绘制用户界面"""
        # 绘制背景 - 使用导入的图片，并随着窗口大小缩放
        if self.background_image:
            # 调整背景图片大小以适应整个窗口
            scaled_background = pygame.transform.scale(self.background_image, (self.width, self.height))
            self.screen.blit(scaled_background, (0, 0))
        else:
            # 如果没有背景图片，使用纯色背景
            self.screen.fill(self.WHITE)
        
        # 输入标签
        n_label = self.font.render("皇后数量:", True, self.BLACK)
        self.screen.blit(n_label, (50, 10))
        
        # 输入框
        pygame.draw.rect(self.screen, self.WHITE, self.n_input_rect)
        pygame.draw.rect(self.screen, self.BLACK, self.n_input_rect, 2)
        n_text = self.font.render(self.n_input, True, self.BLACK)
        self.screen.blit(n_text, (self.n_input_rect.x + 5, self.n_input_rect.y + 5))
        
        # 速度输入
        speed_label = self.font.render("间隔时间(秒):", True, self.BLACK)
        self.screen.blit(speed_label, (200, 10))
        
        pygame.draw.rect(self.screen, self.WHITE, self.speed_input_rect)
        pygame.draw.rect(self.screen, self.BLACK, self.speed_input_rect, 2)
        speed_text = self.font.render(self.speed_input, True, self.BLACK)
        self.screen.blit(speed_text, (self.speed_input_rect.x + 5, self.speed_input_rect.y + 5))
        
        # 按钮绘制
        self.draw_button(self.start_btn, "开始" if not self.is_solving else "停止", self.NANKAI_PURPLE)
        
        # 暂停按钮状态控制
        pause_enabled = self.is_solving or (self.solutions and not self.is_solving)
        pause_color = self.NANKAI_PURPLE if pause_enabled else self.GRAY
        self.draw_button(self.pause_btn, "暂停" if not self.is_paused else "继续", pause_color)
        
        # 导航按钮状态控制
        nav_enabled = bool(self.solutions)
        nav_color = self.NANKAI_PURPLE if nav_enabled else self.GRAY
        self.draw_button(self.next_btn, "下一个", nav_color)
        self.draw_button(self.prev_btn, "上一个", nav_color)
        
        # 状态信息
        status_x = self.speed_input_rect.right + 40  
        
        # 第一行：状态
        status_text = f"状态: {'求解中...' if self.is_solving else '就绪'}"
        status = self.font.render(status_text, True, self.BLACK)
        self.screen.blit(status, (status_x, 12))
        
        # 第二行：自动播放/当前解信息
        if self.solutions:
            if self.auto_playing:
                play_text = f"自动播放: {self.current_solution + 1}/{len(self.solutions)}"
            else:
                play_text = f"当前解: {self.current_solution + 1}/{len(self.solutions)}"
            play_status = self.font.render(play_text, True, self.BLACK)
            self.screen.blit(play_status, (status_x, 42))
        
        # 显示错误消息
        if self.error_timer > 0:
            error_bg = pygame.Rect(50, 0, 500, 30)
            pygame.draw.rect(self.screen, (255, 200, 200), error_bg, border_radius=5)
            pygame.draw.rect(self.screen, self.RED, error_bg, 2, border_radius=5)
            
            error_text = self.font.render(self.error_message, True, self.RED)
            self.screen.blit(error_text, (60, 5))
            self.error_timer -= 1
    
    def draw_button(self, rect, text, color):
        """绘制按钮"""
        pygame.draw.rect(self.screen, color, rect, border_radius=5)
        pygame.draw.rect(self.screen, self.BLACK, rect, 2, border_radius=5)
        
        text_surf = self.font.render(text, True, self.WHITE)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
    
    def draw_chessboard(self):
        """绘制棋盘和皇后"""
        # 绘制棋盘背景 - 使用默认棋盘样式
        board_surface = pygame.Surface((self.board_size, self.board_size))
        light_color = self.WHITE
        dark_color = self.BLACK
        
        cell_size = self.board_size // self.n
        for row in range(self.n):
            for col in range(self.n):
                x = col * cell_size
                y = row * cell_size
                color = light_color if (row + col) % 2 == 0 else dark_color
                pygame.draw.rect(board_surface, color, (x, y, cell_size, cell_size))
        
        pygame.draw.rect(board_surface, self.BLACK, (0, 0, self.board_size, self.board_size), 2)
        self.screen.blit(board_surface, (self.board_x, self.board_y))
        
        # 绘制坐标标签
        cell_size = self.board_size // self.n
        for i in range(self.n):
            # 行标签 (A, B, C, ...)
            row_label = self.small_font.render(chr(65 + i), True, self.BLACK)
            self.screen.blit(row_label, (self.board_x - 20, self.board_y + i * cell_size + cell_size//2 - 8))
            
            # 列标签 (1, 2, 3, ...)
            col_label = self.small_font.render(str(i + 1), True, self.BLACK)
            self.screen.blit(col_label, (self.board_x + i * cell_size + cell_size//2 - 4, self.board_y - 20))
        
        # 如果有解，绘制皇后
        if self.solutions and self.current_solution < len(self.solutions):
            solution = self.solutions[self.current_solution]
            for row, col in enumerate(solution):
                x = self.board_x + col * cell_size
                y = self.board_y + row * cell_size
                
                # 调整皇后图片大小以适应格子
                queen_size = min(cell_size - 10, 50)
                scaled_queen = pygame.transform.scale(self.queen_image, (queen_size, queen_size))
                
                # 居中放置皇后
                queen_x = x + (cell_size - queen_size) // 2
                queen_y = y + (cell_size - queen_size) // 2
                
                self.screen.blit(scaled_queen, (queen_x, queen_y))
    
    def draw_sidebar(self):
        """绘制侧边栏显示解法数据"""
        # 创建半透明表面
        sidebar_surface = pygame.Surface((self.sidebar_width, self.height-20), pygame.SRCALPHA)
        
        # 绘制半透明背景 (RGBA: 前三个是颜色，第四个是透明度 0-255)
        sidebar_color = (240, 240, 240, 180)  # 浅灰色，半透明
        pygame.draw.rect(sidebar_surface, sidebar_color, (0, 0, self.sidebar_width, self.height-20))
        
        # 绘制边框
        pygame.draw.rect(sidebar_surface, (0, 0, 0, 150), (0, 0, self.sidebar_width, self.height-20), 2)
        
        # 将半透明表面绘制到屏幕上
        self.screen.blit(sidebar_surface, (self.sidebar_x, 10))
        
        # 侧边栏标题
        sidebar_title = self.title_font.render("解法数据", True, self.NANKAI_PURPLE)
        self.screen.blit(sidebar_title, (self.sidebar_x + 20, 20))
        
        # 总解数
        total_text = self.font.render(f"总解数: {len(self.solutions)}", True, self.BLACK)
        self.screen.blit(total_text, (self.sidebar_x + 20, 60))
        
        # 所有解法列表
        if self.solutions:
            all_sols_title = self.font.render("所有解法:", True, self.BLACK)
            self.screen.blit(all_sols_title, (self.sidebar_x + 20, 100))
            
            # 根据侧边栏高度计算显示的解数量
            max_solutions = min(20, (self.height - 150) // 25)
            start_index = max(0, min(self.scroll_offset, len(self.solutions) - max_solutions))
            end_index = min(start_index + max_solutions, len(self.solutions))
            
            for i in range(start_index, end_index):
                y_pos = 130 + (i - start_index) * 25
                sol_text = self.small_font.render(f"解法 {i+1}: {self.solutions[i]}", True, self.BLACK)
                
                # 高亮当前解 - 使用半透明高亮
                if i == self.current_solution:
                    highlight_surface = pygame.Surface((self.sidebar_width - 30, 22), pygame.SRCALPHA)
                    highlight_color = (200, 230, 255, 150)  # 半透明蓝色
                    pygame.draw.rect(highlight_surface, highlight_color, (0, 0, self.sidebar_width - 30, 22))
                    self.screen.blit(highlight_surface, (self.sidebar_x + 15, y_pos - 2))
                
                self.screen.blit(sol_text, (self.sidebar_x + 20, y_pos))
            
            # 滚动提示
            if len(self.solutions) > max_solutions:
                scroll_info = self.small_font.render(f"显示 {start_index+1}-{end_index} / 共 {len(self.solutions)} 个解法", True, (100, 100, 100))
                self.screen.blit(scroll_info, (self.sidebar_x + 20, self.height - 30))
    
    def is_safe(self, board, row, col):
        """检查位置是否安全"""
        for i in range(row):
            if board[i] == col or abs(board[i] - col) == abs(i - row):
                return False
        return True
    
    def solve_n_queens(self):
        """求解N皇后问题"""
        def backtrack(row, board):
            if not self.is_solving:
                return
                
            while self.is_paused and self.is_solving:
                time.sleep(0.1)
                
            if row == self.n:
                self.solutions.append(board[:])
                return
            
            for col in range(self.n):
                if self.is_safe(board, row, col):
                    board[row] = col
                    backtrack(row + 1, board)
                    board[row] = -1
        
        board = [-1] * self.n
        self.solutions = []
        backtrack(0, board)
        self.is_solving = False
        if self.solutions:
            self.auto_playing = True
    
    def start_solving(self):
        """开始求解"""
        if self.is_solving:
            self.is_solving = False
            self.auto_playing = False
            return
            
        try:
            self.n = int(self.n_input) if self.n_input else 8
            self.speed = float(self.speed_input) if self.speed_input else 0.05
            
            if self.n < 1 or self.n > 15:
                self.show_error_message("错误：请重新输入一个不小于1且不大于15的整数！")
                return
                
        except ValueError:
            self.show_error_message("错误：请输入有效的数字！")
            return
        
        self.solutions = []
        self.current_solution = 0
        self.is_solving = True
        self.is_paused = False
        self.auto_playing = False
        self.scroll_offset = 0
        self.error_message = ""
        
        self.solver_thread = threading.Thread(target=self.solve_n_queens, daemon=True)
        self.solver_thread.start()
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == VIDEORESIZE:
                # 处理窗口大小改变事件
                new_width, new_height = event.size
                # 确保窗口不小于最小尺寸
                new_width = max(self.min_width, new_width)
                new_height = max(self.min_height, new_height)
                
                self.width, self.height = new_width, new_height
                self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                self.calculate_layout()  # 重新计算布局
            
            elif event.type == MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)
                if event.button == 4:  # 滚轮上滚
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                elif event.button == 5:  # 滚轮下滚
                    if self.solutions:
                        max_solutions = min(20, (self.height - 150) // 25)
                        self.scroll_offset = min(len(self.solutions) - max_solutions, self.scroll_offset + 1)
            
            elif event.type == KEYDOWN:
                self.handle_key_press(event)
    
    def handle_mouse_click(self, pos):
        """处理鼠标点击"""
        if self.n_input_rect.collidepoint(pos):
            self.n_input = ""
            self.error_message = ""
        elif self.speed_input_rect.collidepoint(pos):
            self.speed_input = ""
            self.error_message = ""
        
        elif self.start_btn.collidepoint(pos):
            self.start_solving()
        
        elif self.pause_btn.collidepoint(pos):
            if self.is_solving or self.solutions:
                self.is_paused = not self.is_paused
                if not self.is_paused and self.auto_playing:
                    self.auto_playing = True
        
        elif self.next_btn.collidepoint(pos) and self.solutions:
            self.auto_playing = False
            if self.current_solution < len(self.solutions) - 1:
                self.current_solution += 1
            max_solutions = min(20, (self.height - 150) // 25)
            if self.current_solution >= self.scroll_offset + max_solutions:
                self.scroll_offset = self.current_solution - max_solutions + 1
        
        elif self.prev_btn.collidepoint(pos) and self.solutions:
            self.auto_playing = False
            if self.current_solution > 0:
                self.current_solution -= 1
            if self.current_solution < self.scroll_offset:
                self.scroll_offset = max(0, self.current_solution)
    
    def handle_key_press(self, event):
        """处理键盘输入"""
        if event.key == K_BACKSPACE:
            if self.n_input_rect.collidepoint(pygame.mouse.get_pos()):
                self.n_input = self.n_input[:-1]
            elif self.speed_input_rect.collidepoint(pygame.mouse.get_pos()):
                self.speed_input = self.speed_input[:-1]
        else:
            if self.n_input_rect.collidepoint(pygame.mouse.get_pos()):
                if event.unicode.isdigit():
                    self.n_input += event.unicode
            elif self.speed_input_rect.collidepoint(pygame.mouse.get_pos()):
                if event.unicode.isdigit() or event.unicode == '.':
                    self.speed_input += event.unicode
    
    def auto_play_solutions(self):
        """自动播放所有解"""
        if (self.auto_playing and self.solutions and 
            not self.is_solving and not self.is_paused):
            
            time.sleep(self.speed)
            
            if self.current_solution < len(self.solutions) - 1:
                self.current_solution += 1
                max_solutions = min(20, (self.height - 150) // 25)
                if self.current_solution >= self.scroll_offset + max_solutions:
                    self.scroll_offset = self.current_solution - max_solutions + 1
            else:
                self.auto_playing = False
    
    def run(self):
        """主循环"""
        clock = pygame.time.Clock()
        
        while True:
            self.screen.fill(self.WHITE)
            
            self.handle_events()
            self.draw_ui()
            self.draw_chessboard()
            self.draw_sidebar()
            
            self.auto_play_solutions()
            
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    visualizer = NQueensVisualizer()
    visualizer.run()