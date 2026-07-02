import tkinter as tk
import time
import threading
from tkinter import messagebox


class NQueensVisualizer:
    def __init__(self, master):    #构造函数，初始化和创建GUI界面
        self.master = master
        self.master.title("n皇后问题可视化")

        # 画布与状态
        self.canvas = None
        self.board_size = 8
        self.solutions = []          # 全部解（每个解是list）
        self.generated_count = 0     # 已生成解计数（用于进度）
        self.display_index = 0       # 已展示到的解索引（单步或自动模式都递增）
        self.stop_flag = False  #用于标识是否停止求解过程。
        self.pause_flag = False  #用于标识当前是否处于暂停状态
        self.blink_time = 0.05

        #BooleanVar 类型的变量，用于控制是否启用单步模式
        self.single_step = tk.BooleanVar(value=False)
        self.thread = None  #存储求解线程的对象
        self.solver_done = False     # 求解是否完成

        # 互斥保护 确保在生成解和消费解（展示解）时不会发生数据竞争。
        self.lock = threading.Lock()

        self.setup_input()   #设置用户输入界面，包括输入框、按钮

    def setup_input(self):
        self.input_frame = tk.Frame(self.master) #Frame 组件，用于容纳所有输入控件
        self.input_frame.pack(side=tk.RIGHT, padx=10, fill=tk.Y)#将框架放在最右侧，左右间距10，垂直填满空间

        self.label_n = tk.Label(self.input_frame, text="输入棋盘大小 (n):")
        self.label_n.pack()

        self.entry_n = tk.Entry(self.input_frame)  #创建一个输入框
        self.entry_n.insert(0, "8")
        self.entry_n.pack()

        self.label_blink = tk.Label(self.input_frame, text="闪烁时间 (秒):")
        self.label_blink.pack()

        self.entry_blink = tk.Entry(self.input_frame)
        self.entry_blink.insert(0, "0.05")
        self.entry_blink.pack()

        # 单步模式勾选
        #self.step_check = tk.Checkbutton(self.input_frame, text="单步模式", variable=self.single_step)
        #self.step_check.pack(pady=5)

        self.start_button = tk.Button(self.input_frame, text="开始", command=self.start_visualization)
        self.start_button.pack(pady=5, fill=tk.X)

        self.pause_button = tk.Button(self.input_frame, text="暂停", command=self.pause_visualization)
        self.pause_button.pack(pady=5, fill=tk.X)

        self.resume_button = tk.Button(self.input_frame, text="继续", command=self.resume_or_step)
        self.resume_button.pack(pady=5, fill=tk.X)

        self.result_label = tk.Label(self.input_frame, text="")
        self.result_label.pack(pady=5)

        # 去掉进度标签
        # self.progress_label = tk.Label(self.input_frame, text="进度：0/0")
        # self.progress_label.pack(pady=5)

    def start_visualization(self):
        try:
            n = int(self.entry_n.get().strip())
            if n <= 0:
                raise ValueError
            self.board_size = n

            blink_val = float(self.entry_blink.get().strip())
            if blink_val < 0:
                raise ValueError
            self.blink_time = blink_val

            # 初始化画布与状态
            self.setup_board()

            with self.lock:#使用线程锁，确保在多线程环境下的安全性
                self.solutions = []  #存储所有解
                self.generated_count = 0
                self.display_index = 0
                self.solver_done = False

            self.stop_flag = False #停止
            self.pause_flag = False  #暂停
            self.result_label.config(text="")
            # 去掉更新进度
            # self.update_progress()

            # 启动新求解线程
            #确保用户界面的响应性，避免在计算过程中阻塞主线程
            self.thread = threading.Thread(
                target=self.solve_all_then_display,
                args=(self.board_size,),
                daemon=True  #将线程设置为守护线程，意味着它将在主程序退出时自动终止
            )
            self.thread.start()
        except ValueError:
            self.result_label.config(text="请输入有效的数字！")

    #初始化画布，绘制棋盘
    def setup_board(self):
        if self.canvas:          #检查是否存在一个画布canvas
            self.canvas.destroy()
        self.canvas = tk.Canvas(self.master, width=400, height=400)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.draw_board() #绘制方格

    #绘制棋盘的格子
    def draw_board(self):
        self.canvas.delete("all")
        tile_size = 400 // self.board_size if self.board_size > 0 else 50
        for row in range(self.board_size):
            for col in range(self.board_size):
                color = "white" if (row + col) % 2 == 0 else "black"
                self.canvas.create_rectangle( #绘制一个矩形格子，左上角和右下角的坐标
                    col * tile_size, row * tile_size,
                    (col + 1) * tile_size, (row + 1) * tile_size,
                    fill=color, outline="" #不显示边框
                )

    #检查给定棋盘状态下是否可以在指定位置放置一个皇后
    def is_safe(self, board, row, col):
        for i in range(row):
            if (
                board[i] == col or
                board[i] - i == col - row or
                board[i] + i == col + row
            ):
                return False
        return True

    # 后台线程：生成全部解
    def solve_all_then_display(self, n):
        board = [-1] * n
        self.backtrack_collect(0, board)

        # 标记求解完成
        with self.lock:#使用线程锁，确保在多线程环境下对共享变量的安全访问
            self.solver_done = True
            total = len(self.solutions)#解的总数

        # self.update_progress_after()

        # 自动模式：结束后弹窗展示所有解
        self.master.after(0, self.show_all_solutions_popup)

    #求解的算法
    def backtrack_collect(self, row, board):
        if self.stop_flag:#停止
            return
        n = len(board)
        if row == n:
            # 收集解
            with self.lock:
                self.solutions.append(board[:])
                self.generated_count += 1
                total = len(self.solutions)
                idx_to_display = self.generated_count - 1

            # 在主线程调度闪烁并推进 display_index
            self.master.after(0, self.flash_solution_and_advance, idx_to_display)
            return

        for col in range(n):
            if self.stop_flag:
                return


            if not self.single_step.get():
                while self.pause_flag and not self.stop_flag:
                    time.sleep(0.05)

            if self.is_safe(board, row, col):
                board[row] = col
                self.backtrack_collect(row + 1, board)
                board[row] = -1

    # 在主线程中：根据 solutions[index] 绘制并闪烁一次，然后推进 display_index
    def flash_solution_and_advance(self, index):
        if index < 0:
            return
        with self.lock:
            if index >= len(self.solutions):
                return
            board = self.solutions[index][:]

        # 自动模式下，若处于暂停则等待（避免闪烁期间暂停无效）
        if not self.single_step.get():
            while self.pause_flag and not self.stop_flag:
                self.master.update_idletasks()   #同下
                self.master.update()             #更新UI，确保界面能够响应用户操作
                time.sleep(0.05)

        if self.single_step.get() and self.display_index == 0:
            # 单步模式，首次点击只显示第一种解
            self.draw_full_solution_once(board)
        else:
            self.draw_full_solution_once_blink(board)

        with self.lock:
            # 仅当按顺序闪烁时推进 display_index
            if index == self.display_index:
                self.display_index += 1

    #负责绘制给定棋盘状态下的所有皇后
    def draw_full_solution_once(self, board):
        if self.stop_flag:
            return
        tile_size = 400 // self.board_size if self.board_size > 0 else 50
        ovals = []

        # 先重画棋盘，避免前一次残留
        self.draw_board()

        # 画所有皇后
        for row, col in enumerate(board):
            oval = self.canvas.create_oval( #在画布上绘制一个椭圆
                col * tile_size + 10, row * tile_size + 10,
                (col + 1) * tile_size - 10, (row + 1) * tile_size - 10,
                fill="yellow", outline=""
            )
        '''for row, col in enumerate(board):  #圆形
            oval = self.canvas.create_rectangle(
                col * tile_size + 10, row * tile_size + 10,
                (col + 1) * tile_size - 10, (row + 1) * tile_size - 10,
                fill="yellow", outline="blue"
            )'''
        ovals.append(oval)

        self.master.update_idletasks()
        self.master.update()

    #该方法负责在画布上绘制所有皇后，并实现闪烁效果
    def draw_full_solution_once_blink(self, board):
        if self.stop_flag:
            return
        tile_size = 400 // self.board_size if self.board_size > 0 else 50
        ovals = []

        # 先重画棋盘，避免前一次残留
        self.draw_board()

        # 画所有皇后
        for row, col in enumerate(board):
            oval = self.canvas.create_oval(
                col * tile_size + 10, row * tile_size + 10,
                (col + 1) * tile_size - 10, (row + 1) * tile_size - 10,
                fill="red", outline=""
            )
        '''for row, col in enumerate(board):  # 圆形
            oval = self.canvas.create_rectangle(
                col * tile_size + 10, row * tile_size + 10,
                (col + 1) * tile_size - 10, (row + 1) * tile_size - 10,
                fill="yellow", outline="blue"
            )'''
        ovals.append(oval)

        self.master.update_idletasks()
        self.master.update()

        # 等待 blink_time，自动模式下响应暂停；单步模式下不理会暂停
        waited = 0.0
        step = 0.01
        while waited < self.blink_time and not self.stop_flag:
            if not self.single_step.get():#如果没有启动单步模式
                while self.pause_flag and not self.stop_flag:
                    time.sleep(0.05)
            time.sleep(step)
            waited += step

        # 删除所有皇后（实现闪烁一次）
        for oid in ovals:
            self.canvas.delete(oid)
        self.master.update_idletasks()
        self.master.update()

    #继续键
    def resume_or_step(self):
        '''if self.single_step.get():
            # 单步模式：展示下一个未展示的解
            with self.lock:
                next_idx = self.display_index
                total = len(self.solutions)
                done = self.solver_done

            if next_idx < total:
                # 在主线程直接闪烁并推进
                self.flash_solution_and_advance(next_idx)
                # 如果刚好展示完全部解，并且求解也已完成，则弹窗展示所有解
                with self.lock:
                    finished_show = (self.display_index == len(self.solutions))
                    done = self.solver_done
                if finished_show and done:
                    self.show_solution_count_popup()
            else:
                # 还没有新解：若求解已完成，直接提示已完成；若未完成，提示“正在生成”
                if done:
                    messagebox.showinfo("提示", "所有解已展示完成。")
                else:
                    messagebox.showinfo("提示", "解仍在生成中，请稍后再点或等待生成完成。")
        else:'''
        # 自动模式：将暂停状态解除
        self.pause_flag = False

    #暂停键
    def pause_visualization(self):
        # 自动模式有效；单步模式无需暂停
        if not self.single_step.get():
            self.pause_flag = True
            # 显示当前解的棋子
            with self.lock:
                if self.display_index > 0:
                    current_board = self.solutions[self.display_index - 1]
                    self.draw_full_solution_once(current_board)

    '''def update_progress(self):
        with self.lock:
            total = len(self.solutions)
            shown = self.display_index
        # 去掉进度更新
        # self.progress_label.config(text=f"进度：{shown}/{total}")

    def update_progress_after(self):
        self.master.after(0, self.update_progress)

    def show_solution_count_popup(self):
        # 弹窗展示解的数量
        with self.lock:
            total = len(self.solutions)

        messagebox.showinfo("提示", f"解的总数量: {total}")
   '''
    def show_all_solutions_popup(self):
        # 弹窗展示所有解（每行显示为如 [1, 3, 5, 0, ...] 的列坐标）
        with self.lock:
            total = len(self.solutions)
            text_lines = []
            for i, sol in enumerate(self.solutions, 1):
                text_lines.append(f"{i}: {sol}") #将每个解的索引和内容格式化为字符串并添加到列表中

            #将所有解合并为一个字符串，如果没有解，则显示“无解”
            content = "\n".join(text_lines) if text_lines else "无解"

        # 使用顶层窗口展示，避免 messagebox 长文本折叠
        top = tk.Toplevel(self.master)
        top.title(f"全部解（共 {total} 个）")
        top.geometry("480x360")

        txt = tk.Text(top, wrap="none") #创建一个文本框
        txt.pack(fill=tk.BOTH, expand=True) #将文本框填充整个窗口
        txt.insert("1.0", content) #将合并的解内容插入到文本框中
        txt.config(state=tk.DISABLED)  #设置为只读

        btn = tk.Button(top, text="关闭", command=top.destroy)
        btn.pack(pady=5) #垂直间距


if __name__ == "__main__":
    '''
    创建一个 Tkinter 的根窗口。这个窗口是所有其他界面的基础，
    所有的 GUI 元件（如按钮、标签、画布等）都将被添加到这个根窗口中 '''
    root = tk.Tk()

    visualizer = NQueensVisualizer(root)
    root.mainloop()