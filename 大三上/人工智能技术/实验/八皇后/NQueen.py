class NQueen:
    def __init__(self):
        # 用于存储所有解法
        self.solutions = [] 

    # 获取皇后数量
    def get_size(self,size=8):
        if size < 1:
            print("数据过小")
            return False
        elif size > 15:
            print("数据过大，算力不够！")
            return False
        else:
            self.size = size
            # 创建一个包含size个-1的列表，表示棋盘，索引位表示行号，储存值表示列号
            self.board = [-1] * self.size 
            return True
    
    # 判断在指定行和列是否能够放置皇后
    def is_safe(self, row, col): # row行，col列
        for row_now in range(row):
            if (self.board[row_now] == col or # 是否在同一列
                abs(self.board[row_now] - col) == abs(row_now - row)):# 是否处于同一对角线，相距列、行数相同则判定为是
                return False
        return True

    # 递归解决八皇后问题，从指定行开始尝试放置皇后
    def solve(self, row=0):
        if row == self.size:# 当行数达到皇后数量停止递归
            self.solutions.append(self.board[:])# 找到一种结果并添加到solutions中
            return
        for col in range(self.size):
            if self.is_safe(row, col):
                self.board[row] = col
                self.solve(row + 1)
                self.board[row] = -1# 实现回溯，当完成一种解法或此解法不行时进行重置

    # 返回所有找到的解法,用于外部访问
    def get_solutions(self):
        return self.solutions
    
    # 打印结果
    def print_solutions(self):
        print(f"八皇后问题共有 {len(self.solutions)} 种解法")

if __name__ == '__main__':
    n_queen = NQueen()
    while True:
        size = input("请输入皇后数量：")
        if n_queen.get_size(int(size)):
            print("输入成功！")
            n_queen.solve()
            n_queen.print_solutions()
            # # 打印详细结果
            # print("每种解法各行皇后的列坐标如下：")
            # for solution in n_queen.get_solutions():
            #     print(solution)
            break  # 输入有效，退出循环
        else:
            print("请重新输入一个不小于4且不大于15的整数！")

