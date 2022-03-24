# -*- coding: utf-8 -*-
# 5节点电网优化
import numpy as np
import cplex

CU = np.array([40,170,520,200,600],dtype=float)
PU = np.array([20,50,150,100,200],dtype=float)
CG = np.array([14,15,30,40,20],dtype=float)
CR = np.array([7,7.5,15,20,10],dtype=float)
GSF = np.array([[0.1939,-0.4759,-0.3490,0,0.1595],
       [0.4376,0.2583,0.1895,0,0.3600],
       [0.3685,0.2176,0.1595,0,-0.5195],
       [0.1939,0.5241,-0.3490,0,0.1595],
       [0.1939,0.5241,0.6510,0,0.1595],
       [-0.3685,-0.2176,-0.1595,0,-0.4805]])
Init_power = np.array([40,170,0,0,300],dtype=float)
Fl = 230.0
D = 50.0
npdm = np.array([550.0, 670.0, 800.0, 630.0], dtype=float)


if __name__ == '__main__':
    # 优化变量为 x = [pg1t,pg2t,pg3t,pg4t,pg5t,dpg1t,dpg2t,dpg3t,dpg4t,dpg5t]
    # pg1t表示1发电机在4个时间段的功率pg1t=[pg11,pg12,pg13,pg14] dpg1t为备用功率
    my_obj = np.r_[np.repeat(CG, 4), np.repeat(CR, 4)]
    my_ub = np.tile(np.repeat(CU, 4),2)
    c = cplex.Cplex()
    c.variables.add(obj=my_obj, ub=my_ub)
    # 2a
    # list(range(0,20,4))表示第一个时间段的发电机功率
    # list(range(1,20,4))表示第二个时间段的发电机功率，下同
    cons = [[list(range(0,20,4)),[1.0]*5], # 第一个时间段的功率乘系数1就是直接相加
            [list(range(1,20,4)),[1.0]*5],
            [list(range(2,20,4)),[1.0]*5],
            [list(range(3,20,4)),[1.0]*5]]
    mrhs = npdm
    msense = 'EEEE'
    c.linear_constraints.add(lin_expr=cons, senses=msense, rhs=mrhs, names=["lambda_bt"]*4)
    # 2b,2c是上下界，前面已经加入模型，这里不再给出
    # 2d, 2e
    cons =[[[0,1],[-1.0,1.0]],[[1,2],[-1.0,1.0]],[[2,3],[-1.0,1.0]], # 表示后一个时间段功率减前一个时间段功率
            [[4,5],[-1.0,1.0]],[[5,6],[-1.0,1.0]],[[6,7],[-1.0,1.0]],
            [[8,9],[-1.0,1.0]],[[9,10],[-1.0,1.0]],[[10,11],[-1.0,1.0]],
            [[12,13],[-1.0,1.0]],[[13,15],[-1.0,1.0]],[[14,15],[-1.0,1.0]],
            [[16,17],[-1.0,1.0]],[[17,18],[-1.0,1.0]],[[18,19],[-1.0,1.0]]]
    mrhs = np.repeat(PU, 3)
    msense = 'L'*15
    c.linear_constraints.add(lin_expr=cons, senses=msense, rhs=mrhs)
    msense = 'G'*15
    c.linear_constraints.add(lin_expr=cons, senses=msense, rhs=-mrhs)
    # 第一个小时与初始功率的爬坡，下坡限制
    cons = [[[0],[1.0]],[[4],[1.0]],[[8],[1.0]],[[12],[1.0]],[[16],[1.0]]]
    mrhs = PU + Init_power
    msense = 'L'*5
    c.linear_constraints.add(lin_expr=cons, senses=msense, rhs=mrhs)
    mrhs = Init_power - PU
    msense = 'G'*5
    c.linear_constraints.add(lin_expr=cons, senses=msense, rhs=mrhs)
    # 2f,2g
    # GSF[l,m]*(Pgm-Pdm) （<= Fl|>= -Fl) 对于任意时间段
    # GSF[l,m]*Pgm <= GSF[l,m]*Pdm + Fl \ >= GSF[l,m]*Pdm - Fl
    cons = [
        #    [list(range(0,20,4)),[GSF[0,0], GSF[0,0], GSF[0,2], GSF[0,3], GSF[0,4]]], # 因为两台发电机在A，所以GSF[0,0]出现两次，而B处无发电机，就没有GSF[0,1]
        #     [list(range(1,20,4)),[GSF[0,0], GSF[0,0], GSF[0,2], GSF[0,3], GSF[0,4]]],
        #     [list(range(2,20,4)),[GSF[0,0], GSF[0,0], GSF[0,2], GSF[0,3], GSF[0,4]]],
        #     [list(range(3,20,4)),[GSF[0,0], GSF[0,0], GSF[0,2], GSF[0,3], GSF[0,4]]], # 以上是4个时间段A-B线路潮流计算

        #     [list(range(0,20,4)),[GSF[1,0], GSF[1,0], GSF[1,2], GSF[1,3], GSF[1,4]]],
        #     [list(range(1,20,4)),[GSF[1,0], GSF[1,0], GSF[1,2], GSF[1,3], GSF[1,4]]],
        #     [list(range(2,20,4)),[GSF[1,0], GSF[1,0], GSF[1,2], GSF[1,3], GSF[1,4]]],
        #     [list(range(3,20,4)),[GSF[1,0], GSF[1,0], GSF[1,2], GSF[1,3], GSF[1,4]]], # A-D

        #     [list(range(0,20,4)),[GSF[2,0], GSF[2,0], GSF[2,2], GSF[2,3], GSF[2,4]]],
        #     [list(range(1,20,4)),[GSF[2,0], GSF[2,0], GSF[2,2], GSF[2,3], GSF[2,4]]],
        #     [list(range(2,20,4)),[GSF[2,0], GSF[2,0], GSF[2,2], GSF[2,3], GSF[2,4]]],
        #     [list(range(3,20,4)),[GSF[2,0], GSF[2,0], GSF[2,2], GSF[2,3], GSF[2,4]]], # A-E

        #     [list(range(0,20,4)),[GSF[3,0], GSF[3,0], GSF[3,2], GSF[3,3], GSF[3,4]]],
        #     [list(range(1,20,4)),[GSF[3,0], GSF[3,0], GSF[3,2], GSF[3,3], GSF[3,4]]],
        #     [list(range(2,20,4)),[GSF[3,0], GSF[3,0], GSF[3,2], GSF[3,3], GSF[3,4]]],
        #     [list(range(3,20,4)),[GSF[3,0], GSF[3,0], GSF[3,2], GSF[3,3], GSF[3,4]]], # B-C

        #     [list(range(0,20,4)),[GSF[4,0], GSF[4,0], GSF[4,2], GSF[4,3], GSF[4,4]]],
        #     [list(range(1,20,4)),[GSF[4,0], GSF[4,0], GSF[4,2], GSF[4,3], GSF[4,4]]],
        #     [list(range(2,20,4)),[GSF[4,0], GSF[4,0], GSF[4,2], GSF[4,3], GSF[4,4]]],
        #     [list(range(3,20,4)),[GSF[4,0], GSF[4,0], GSF[4,2], GSF[4,3], GSF[4,4]]], # C-D

            [list(range(0,20,4)),[GSF[5,0], GSF[5,0], GSF[5,2], GSF[5,3], GSF[5,4]]],
            [list(range(1,20,4)),[GSF[5,0], GSF[5,0], GSF[5,2], GSF[5,3], GSF[5,4]]],
            [list(range(2,20,4)),[GSF[5,0], GSF[5,0], GSF[5,2], GSF[5,3], GSF[5,4]]],
            [list(range(3,20,4)),[GSF[5,0], GSF[5,0], GSF[5,2], GSF[5,3], GSF[5,4]]], # D-E
            ]
    msense = 'L'*4
    # GSF[l,m]*Pdm计算
    fp = np.array([0,0.3,0.3,0.4,0],dtype=float) # 总负荷分配B:C:D=3:3:4
    tmp = GSF @ fp
    mrhs = np.repeat(tmp, 4) * np.tile(npdm, 6) + np.full([24], Fl, dtype=float)
    c.linear_constraints.add(lin_expr=cons, senses=msense, rhs=mrhs[-4:], names=["eta_blt"]*4)
    msense = 'G'*4
    mrhs = np.repeat(tmp, 4) * np.tile(npdm, 6) - np.full([24], Fl, dtype=float)
    c.linear_constraints.add(lin_expr=cons, senses=msense, rhs=mrhs[-4:], names=["eta_b-lt"]*4)
    # 3a
    cons = [[list(range(20,40,4)),[1.0]*5], # 第一个时间段的功率乘系数1就是直接相加
        [list(range(21,40,4)),[1.0]*5],
        [list(range(22,40,4)),[1.0]*5],
        [list(range(23,40,4)),[1.0]*5]]
    mrhs = np.repeat(D, 4)
    msense = 'E'*4
    c.linear_constraints.add(lin_expr=cons, senses=msense, rhs=mrhs, names=["lambda_rt"]*4)
    # 3b, 3c
    cons = [[[i, i+20],[1.0, 1.0]] for i in range(20)]
    msense = 'L'*20
    mrhs = np.repeat(CU, 4)
    c.linear_constraints.add(lin_expr=cons, senses=msense, rhs=mrhs)
    # 3d, 3e
#     cons = [[list(range(j,40,4)),[GSF[i,0], GSF[i,0], GSF[i,2], GSF[i,3], GSF[i,4]]*2] for i in range(6) for j in range(4)] # 同2f, 2g，但是加入备用项
    cons = [[list(range(i,40,4)),[GSF[5,0], GSF[5,0], GSF[5,2], GSF[5,3], GSF[5,4]]*2] for i in range(4)]
    msense = 'L'*4
    tmp2 = np.repeat(tmp, 4) * np.tile(npdm, 6) + np.repeat(GSF @ np.array([0,0,0,20,0],dtype=float), 4) # GSF[l,m]*Pdm+GSF[l,m]*PRm
    mrhs = tmp2 + np.full([24], Fl, dtype=float)
    c.linear_constraints.add(lin_expr=cons, senses=msense, rhs=mrhs[-4:], names=["eta_rlt"]*4)
    msense = 'G'*4
    mrhs = tmp2 - np.full([24], Fl, dtype=float)
    c.linear_constraints.add(lin_expr=cons, senses=msense, rhs=mrhs[-4:], names=["eta_rlt"]*4)
    # print(tmp)
    c.solve()
    print(f"obj:{c.solution.get_objective_value()}")
    print("时间段： 1   2   3   4")
    print(f"sol:pg1t,pg2t,pg3t,pg4t,pg5t,dpg1t,dpg2t,dpg3t,dpg4t,dpg5t={np.array(c.solution.get_values()).reshape(-1, 4)}")
    # 潮流计算
    weight = [[list(range(j,40,4)),[GSF[i,0], GSF[i,0], GSF[i,2], GSF[i,3], GSF[i,4]]*2] for i in range(6) for j in range(4)]
    x = np.array(c.solution.get_values())
    # GSFm * (Pdm + dPdm)
    I = np.empty(24, dtype=float)
    for ix, cof in enumerate(weight):
        I[ix] = x[cof[0]] @ np.array(cof[1])
    I -= np.array(tmp2)
    print("时间段： 1   2   3   4")
    print(f"A-B:{I[:4]}\n,A-D:{I[4:8]}\n,A-E:{I[8:12]}\n,B-C:{I[12:16]}\n,C-D:{I[16:20]}\n,D-E:{I[20:]}")
    dual_value = np.array(c.solution.get_dual_values())
    lambda_bt = dual_value[:4]
    eta_blt = dual_value[44:48].reshape(-1,4)
    eta_b_lt = dual_value[48:52].reshape(-1,4)
    lambda_rt = dual_value[52:56]
    eta_rlt = dual_value[76:80].reshape(-1,4)
    eta_r_lt = dual_value[80:84].reshape(-1,4)
#     _tmp1 = eta_blt - eta_b_lt
#     _tmp2 = eta_rlt - eta_r_lt
    _tmp1 = np.r_[np.zeros([5, 4], dtype=float), eta_blt - eta_b_lt]
    _tmp2 = np.r_[np.zeros([5, 4], dtype=float), eta_rlt - eta_r_lt]
    LMP = np.repeat(lambda_bt, 5).reshape(4, -1)-(GSF.T @ _tmp1).T - (GSF.T @ _tmp2).T
    RLMP = np.repeat(lambda_rt, 5).reshape(4, -1) - (GSF.T @ _tmp2).T
    print(f"LMP:{LMP}")
    print(f"RLMP:{RLMP}")
    # LMP和RLMP每一行对应一个时间，每列对应一个地点，比如LMP[0,3]表示在第一个时间段在D处的价格
    # print(c.linear_constraints.get_histogram())
