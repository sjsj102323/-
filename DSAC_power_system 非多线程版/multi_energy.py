import gym
import numpy as np
import torch
from gym import spaces
import xlrd
import gol
p_coal_max=3000  #p_coal_max/min为火力发电的最大、最小功率
p_coal_min=1000
p_chp_max=1000   #p_chp_max/min为热电联产的最大最小功率
p_chp_min=500
p_eb_max=3000  #p_eb_max/min为电锅炉的最大最小功率
p_eb_min=500
p_hst_max=1000 #p_hst_max/min为储热罐的最大、最小功率
p_hst_min=500
action_num=4
observation_num = 4
Max = 10000
a = 0.7  # 热电联产发电和热的比例
b1 = 1000
b2 = 1000  # b1，b2是对于供电，供热无法满足的惩罚因子
b3=  1000  #b3是动作变化率超限的惩罚因子
action_standard=20#动作变化的最大值统一设为20
data = xlrd.open_workbook("D:\data.xls")
table = data.sheet_by_index(0)

# ele_load和heat_load为24小时的电热负荷
wind_power = table.col_values(1)
light_power = table.col_values(2)
ele_load = table.col_values(3)
heat_load = table.col_values(4)


class multi_energyEnv():
    def __init__(self):  # 该初始化方式待改善
        self.time = 1
        # 存储上一时刻的 风力发电 太阳能发电 电力负荷 热力负荷
        # 6节点电力系统 + 6节点集中供热系统.电力系统包含一个火电机组（节点1）、一个光伏电场(节点2)、一个风电场（节点6）；热力站由一台CHP机组、一台电锅炉和一个储热罐组成；
        # ['gen1','gen_and_heat2','heat1','heat2'] #动作空间 电力系统部分：火电机组出力、CHP机组的出力(电热)，热力系统部分：电锅炉出力、储热罐出力
        self.action_space =np.array([500,500,500,500])
        self.action_space_high=np.array([1000,1000,1000,1000])
        self.action_space_low=np.array([0,0,0,0])
        # 状态空间,包括电力系统负荷、热力负荷、光伏、风电功率。负荷和出力的上下限根据论文算例设置。
        self.observation_space = np.array([wind_power[1], light_power[1],ele_load[1],heat_load[1]])
    def reset(self):
        self.observation_space = np.array([wind_power[1], light_power[1],ele_load[1],heat_load[1]]).reshape(4,1)  # 状态的重置设置，需再考虑重置方法
        self.time=1
        return self.observation_space

    def relu(self, x):  # x负表示发电/热超过负荷，置0不带入下个时刻负荷；x正表示发电小于负荷，将不足的部分带到下个时刻补足
        return max(0, x)
    def punish(self,action_history):
        s=0
        if abs(self.action_space[0]-action_history[0].item(0))>action_standard:
            s=s+abs(self.action_space[0]-action_history.item(0)*b3)
        if abs(self.action_space[1]-action_history.item(1))>action_standard:
            s=s+abs(self.action_space[1]-action_history.item(1))*b3
        if abs(self.action_space[2]-action_history.item(2))>action_standard:
            s=s+abs(self.action_space[2]-action_history.item(2))*b3
        if abs(self.action_space[3]-action_history.item(3))>action_standard:
            s=s+abs(self.action_space[3]-action_history.item(3))*b3
        return s
    def step(self, action):  # self.observation_space表示经过action后的状态，
        # 若电热供给满足需求则为零，否则为未满足需求的量
        # 电力需求➖风力发电➖太阳能发电➖热电联产发的电➖火力发电
        ele_diff = self.observation_space[2] - self.observation_space[0] - self.observation_space[1] - action.item(0) - a * action.item(1)  # 负为超出需求，电量浪费；正为未满足需求
        # 热能需求➖热电联产发的热➖电锅炉发热➖储热罐发热
        heat_diff = self.observation_space[3] - (1 - a) * action.item(1) - action.item(2) - action.item(3)  # 负为超出需求，热能浪费；正为未满足需求
        # 对需求取绝对值，对未满足负荷需求以及超出负荷需求的情况进行惩罚,分别乘以系数b1&b2
        action_history=gol.get_history_action(action)
        print("fuck_env","action",action,"history",action_history)
        reward = -b1 * abs(ele_diff) - b2 * abs(heat_diff)-self.punish(action_history)-1/(np.exp(action-action_history)-0.999)

        # 获得下一时刻的状态
        try:
            self.state_next=np.array([wind_power[self.time],light_power[self.time],ele_load[self.time],heat_load[self.time]])
        except:
            pass
        self.time = self.time + 1
        print("self.time",self.time)
        done = bool(self.time > 95)  # 结束条件 时间为24小时（96个15分钟）


        return self.state_next, reward, done

    def render(self, mode='human'):
        # 用于展示数据
        raise NotImplementedError

    def seed(self, seed=None):
        return
