#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import numpy as np
# import matplotlib.pyplot as plt
from numpy.lib.index_tricks import ix_


class GA(object):
    # 初始化遗传算法
    def __init__(self, gene_size, cxpb, mupb, popsize, max_gen, travel_time, goods_demand, fixed_cost, loads):
        self.gene_size = gene_size # 遗传算法每个个体的基因size
        self.popsize = popsize # 遗传算法每代种群规模
        self.current_gen = 0 # 记录当前进化的代数
        self.cxpb = cxpb # 交叉的概率
        self.mupb = mupb # 变异的概率
        self.max_gen = max_gen # 进化最大代数
        self.bestind = None # 最好的个体
        self.fitness = None # 种群的适应度向量
        self.tsp = TSP(travel_time) # 计算时间的TSP问题动态规划求解算法
        self.goods_demand = goods_demand # 每个服务点的需求
        self.fixed_cost = fixed_cost # 固定费用
        self.loads = loads # 每辆车的荷载
        self.init()

    def init(self):
        # 初始化种群
        pop = []
        for _ in range(self.popsize):
            # 固定中心数为6个
            x = np.zeros(8, dtype=int)
            tmp = np.arange(8)
            np.random.shuffle(tmp)
            x[tmp[:6]] = 1
            y = np.random.choice([0,1], size=[8, 40], p=[0.85, 0.15]) # 随机生成每辆车需要到达的服务点信息
            tmp = y[x.astype(bool)]
            # 保证每个服务点只有一辆车访问
            for j in range(40):
                if np.sum(tmp[:,j]) != 1:
                    tmp[:,j] = 0
                    tmp[np.random.choice(range(6)),j] = 1
            y[x.astype(bool)] = tmp
            pop.append(np.c_[x, y]) # 将x和y用同一个矩阵存储
        self.pop  = np.array(pop)

    def selection(self, tournament_size):
        # 对种群进行锦标赛选择
        pop = []
        tmp = np.arange(self.popsize)
        for _ in range(self.popsize):
            # 随机选择tournament_size个个体
            ix = np.random.choice(tmp, size=tournament_size)
            # 获取选择几个个体里适应度最高的，并加入选择后的种群
            indix = ix[np.argmin(self.fitness[ix])]
            pop.append(self.pop[indix])
        # 对选择后的个体打乱顺序
        np.random.shuffle(tmp)
        pop = np.array(pop)
        selected_pop = pop[tmp]
        selected_pop[np.random.choice(tmp)] = self.bestind # 将之前的最优个体加入种群
        return selected_pop
    
    def crossover(self, selected_pop):
        offspring = selected_pop.copy()
        cix = np.random.choice([False, True], size=[self.popsize//2]+self.gene_size, p=[1-self.cxpb, self.cxpb]) # 均匀交叉
        for i in range(self.popsize//2):
            offspring[2*i, cix[i]], offspring[2*i+1, cix[i]] = selected_pop[2*i+1, cix[i]], selected_pop[2*i, cix[i]]
        return offspring

    def mutation(self, cxed_pop):
        mix = np.random.choice([False, True], size=self.pop.shape, p=[0.99, 0.01])
        # 当不满足条件，则不进行变异
        for i in range(self.popsize):
            if np.random.random() > self.mupb:
                mix[i,:,:] = False
        offspring = cxed_pop.copy()
        for i in range(self.popsize):
            offspring[i] = np.bitwise_xor(cxed_pop[i], mix[i]).astype(int)
        # 局部搜索
        for i in range(self.popsize):
            # 固定中心数为6个
            if np.sum(offspring[i,:,0]) != 6:
                x = np.zeros(8, dtype=int)
                tmp = np.arange(8)
                np.random.shuffle(tmp)
                x[tmp[:6]] = 1
                offspring[i,:,0] = x
            # 保证每个服务点只有一辆车访问，y矩阵每一列和为1
            if not all(np.sum(offspring[i,:,1:],axis=0)==1):
                x = offspring[i,:,0].astype(bool)
                y = offspring[i,:,1:]
                tmp = y[x]
                for j in range(40):
                    if np.sum(tmp[:,j]) != 1:
                        tmp[:,j] = 0
                        tmp[np.random.choice(range(6)),j] = 1
                y[x] = tmp
                offspring[i,:,1:] = y
        return offspring

    def run(self):
        while self.current_gen < self.max_gen:
            self.fitness = self.objective_function() # 适应度计算
            pop = self.selection(5) # 选择
            self.pop = self.mutation(self.crossover(pop)) # 交叉和变异
            self.current_gen += 1
        # 运行结果显示
        x = self.bestind[:,0].astype(bool)
        y = self.bestind[:, 1:]
        center_ix = np.where(x)[0]
        path =[]
        fit = 0
        for i in range(6):
            loc_num = np.r_[center_ix[i], np.where(y[center_ix[i]]==1)[0]+8]
            dp,p = self.tsp.solve(loc_num, g_p=True)
            fit = fit + dp[0,-1] +self.fixed_cost
            path.append(p)
        print('fitness')
        print(fit)
        print('x:')
        print(self.bestind[:,0])
        print('y:')
        print(self.bestind[:,1:])
        print('path:')
        print(path)

    def objective_function(self):
        Fitness = []
        for ind in self.pop:
            x = ind[:,0].astype(bool)
            y = ind[:, 1:]
            # 判断是否所有服务点都有车经过
            if any(y[x]@self.goods_demand>self.loads):
                Fitness.append(500)
            else :
                fit = 0
                center_ix = np.where(x)[0]
                for i in range(6):
                    loc_num = np.r_[center_ix[i], np.where(y[center_ix[i]]==1)[0]+8]
                    fit = fit + self.tsp.get_time(loc_num)+self.fixed_cost # 物流配送总成本=货车派遣总成本(2*6)+货车旅行时间(tsp返回）×时间价值转换参(1)
                Fitness.append(fit)
        Fitness = np.array(Fitness)
        self.bestind = self.pop[np.argmin(Fitness)]
        return np.array(Fitness)


class TSP(object):
    def __init__(self, travel_time):
        # 初始化传入所有的旅行时间矩阵
        self.travel_time = travel_time

    def solve(self, loc_num, g_p=False):
        '''
        输入中心和对应服务点的时间旅行矩阵的索引loc_num
        返回动态规划矩阵dp，dp[0,-1]为最小的旅行时间
        g_p决定是否返回路线
        '''
        ixgrid = np.ix_(loc_num, loc_num)
        travel_time = self.travel_time[ixgrid]
        row, col = travel_time.shape[0], 2**(travel_time.shape[0]-1)
        dp = np.full([row, col], 100, dtype=float)
        dp[:, 0] = travel_time[:, 0]
        for j in range(1, col):
           for i in range(row):
               if i==0 and j!=col-1:
                   continue
               # 如果集和j(或状态j)中包含结点i,则不符合条件退出
               if i!=0 and j>>(i-1)&1==1:
                   continue
               for k in range(1, row):
                   # 如果集合j中不包含节点k，则不需要计算从k出发的时间
                   if j>>(k-1)&1==0:
                       continue
                   dp[i,j] = min(dp[i,j], travel_time[i, k]+dp[k, j^(1<<(k-1))])
        if g_p:
            return dp, loc_num[self.get_path(dp, travel_time)]
        return dp
   
    def get_path(self, dp, travel_time):
        # 利用矩阵dp推导最短路径
        row, col = dp.shape
        visited = np.full(row,False,dtype=bool)
        visited[0] = True
        s = col-1
        path = [0]
        pioneer = 0
        while not visited.all():
            for i in range(1, row):
                if not visited[i] and (1<<(i-1))&s!=0:
                    if dp[pioneer, s] == travel_time[pioneer][i] + dp[i, (1<<(i-1))^s]:
                        pioneer = i
                        break
            path.append(pioneer)
            visited[pioneer] = True
            s = s^(1<<(pioneer - 1))
        path.append(0)
        return path

    def get_time(self, loc_num):
        return self.solve(loc_num, g_p=False)[0, -1]



if __name__ == '__main__':
    # rng = np.random.default_rng()
    # client_coord = rng.random(size=[40,2])
    # center_coord = rng.random(size=[8,2])
    # travel_time = rng.random(size=[48, 48])
    # travel_time[range(48), range(48)] = 0
    # goods_demand = rng.integers(1, 10, size=[40, 1], endpoint=True)
    # np.savetxt('client.csv', client_coord, delimiter=',', fmt='%.4f')
    # np.savetxt('center.csv', center_coord, delimiter=',', fmt='%.4f')
    # np.savetxt('travel_time.csv', travel_time, delimiter=',', fmt='%.4f')
    # np.savetxt('goods_demand.csv', goods_demand, delimiter=',', fmt='%.4f')
    client_coord = np.loadtxt('client.csv', delimiter=',')
    center_coord = np.loadtxt('center.csv', delimiter=',')
    travel_time = np.loadtxt('travel_time.csv', delimiter=',') # 0-7为服务中心，8-47为客户点
    goods_demand = np.loadtxt('goods_demand.csv', delimiter=',') # 客户点需求
    fixed_cost = 2
    loads = 40
    sol = GA([8, 41], 0.8, 0.01, 30, 100, travel_time, goods_demand, fixed_cost, loads)
    sol.run()
    # ax = plt.figure(figsize=[8,8]).add_axes([0, 0, 1, 1])
    # ax.scatter(client_coord[:, 0], client_coord[:, 1], marker='^', label='client')
    # ax.scatter(center_coord[:, 0], center_coord[:, 1], marker='*', label='center')
    # ax.legend()
    # plt.show()
