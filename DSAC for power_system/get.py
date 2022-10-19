import gym
import numpy as np
from gym import spaces
import gol
class muti_power_env():
    def __init__(self):  # 该初始化方式待改善
        self.time = 1
        self.state = np.array([1, 1, 1, 1])  # 存储上一时刻的 风力发电 太阳能发电 电力负荷 热力负荷
        # 6节点电力系统 + 6节点集中供热系统.电力系统包含一个火电机组（节点1）、一个光伏电场(节点2)、一个风电场（节点6）；热力站由一台CHP机组、一台电锅炉和一个储热罐组成；
        # ['gen1','gen_and_heat2','heat1','heat2'] #动作空间 电力系统部分：火电机组出力、CHP机组的出力(电热)，热力系统部分：电锅炉出力、储热罐出力
        # 状态空间,包括电力系统负荷、热力负荷、光伏、风电功率。负荷和出力的上下限根据论文算例设置。


        self.action_space=np.array([1,1,1])# 火力发电出力 燃气发热出力 热电联产出力
        # self.observation_space=np.array([1,1]) # 电力负荷 热力负荷

    def forward(self):
        self.action_space=np.array([self.time*4,1,1])
        self.action_space[0]=gol.get_fire_action(self)
        self.time=self.time+1
