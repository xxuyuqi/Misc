# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt


class Solution(object):
    def __init__(self, arr, num_steps):
        self.arr = arr
        self.num_steps = num_steps
        self.UP = 1
        self.DOWN = 2
        self.LEFT = 3
        self.RIGHT = 4
        [[self.x], [self.y]] = np.nonzero(arr == 0)
        self.move_list = []
        self.final_state = 123456780
        self.state_set = []
        self.move_arr = []
    
    def can_move(self, direction) -> int:
        if direction == self.UP:
            return self.x > 0
        elif direction == self.DOWN:
            return self.x < 2
        elif direction == self.LEFT:
            return self.y > 0
        elif direction == self.RIGHT:
            return self.y < 2
        else:
            return 0
    
    def move(self, direction) -> int:
        if direction == self.UP:
            self.arr[self.x, self.y], self.arr[self.x-1, self.y] = self.arr[self.x-1, self.y], self.arr[self.x, self.y]
            self.x -= 1
        elif direction == self.DOWN:
            self.arr[self.x, self.y], self.arr[self.x+1, self.y] = self.arr[self.x+1, self.y], self.arr[self.x, self.y]
            self.x += 1
        elif direction == self.LEFT:
            self.arr[self.x, self.y], self.arr[self.x, self.y-1] = self.arr[self.x, self.y-1], self.arr[self.x, self.y]
            self.y -= 1
        elif direction == self.RIGHT:
            self.arr[self.x, self.y], self.arr[self.x, self.y+1] = self.arr[self.x, self.y+1], self.arr[self.x, self.y]
            self.y += 1
    
    def move_back(self, direction):
        if direction == self.UP:
            self.arr[self.x, self.y], self.arr[self.x+1, self.y] = self.arr[self.x+1, self.y], self.arr[self.x, self.y]
            self.x += 1
        elif direction == self.DOWN:
            self.arr[self.x, self.y], self.arr[self.x-1, self.y] = self.arr[self.x-1, self.y], self.arr[self.x, self.y]
            self.x -= 1
        elif direction == self.LEFT:
            self.arr[self.x, self.y], self.arr[self.x, self.y+1] = self.arr[self.x, self.y+1], self.arr[self.x, self.y]
            self.y += 1
        elif direction == self.RIGHT:
            self.arr[self.x, self.y], self.arr[self.x, self.y-1] = self.arr[self.x, self.y-1], self.arr[self.x, self.y]
            self.y -= 1
        self.move_arr.pop()

    def get_status(self) -> int:
        return np.sum(self.arr * np.array([[100000000, 10000000, 1000000], [100000, 10000, 1000], [100, 10, 1]]))

    def search(self, direction):
        if self.can_move(direction):
            self.move(direction)
            self.move_arr.append(direction)
            if len(self.move_arr) > self.num_steps:
                self.move_back(direction)
                return 0
            if self.get_status() == self.final_state:
                return 1
            if (self.get_status() in self.state_set):
                self.move_back(direction)
                return 0
            self.state_set.append(self.get_status())
            search4ok = self.search(self.UP) or self.search(self.DOWN) or self.search(self.LEFT) or self.search(self.RIGHT)
            if search4ok:
                return 1
            else:
                self.move_back(direction)
                return 0
        return 0
    
    def solve(self):
        if self.get_status() == self.final_state:
            return 1
        self.state_set.append(self.get_status())
        return self.search(self.UP) or self.search(self.DOWN) or self.search(self.LEFT) or self.search(self.RIGHT)
    '''
    def show_res(self):
        plot_list = np.zeros([9,9], dtype=int)
        for i in range(8):
            plot_list[i, i] = 1
        plot_list = plot_list.reshape([9,3,3])
        plot_arr = plot_list[np.array([3,4,1,5,6,9,8,2,7])-1,:,:].reshape([9, 9])
        plt.imshow(plot_arr)
        plt.show()
        for direction in self.move_arr:
            if direction == self.UP:
                pass
            elif direction == self.DOWN:
                pass
            elif direction == self.LEFT:
                pass
            elif direction == self.RIGHT:
                pass
    '''           


if __name__ == '__main__':
    arr = np.array([[3,4,1],[5,6,0],[8,2,7]])
    for i in range(1, 100):
        ms = Solution(arr, i)
        ms.solve()
        if len(ms.move_arr) != 0:
            break
    print(len(ms.move_arr))
    print(ms.move_arr)