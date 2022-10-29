from __future__ import print_function
import torch
import numpy as np
import torch.multiprocessing as mp
from torch.multiprocessing import Process, Queue
import time
from Model import QNet, PolicyNet
import gym
from utils import *


class Actor():
    def __init__(self, args, shared_queue, shared_value,share_net, lock, i):
        super(Actor, self).__init__()
        self.shared_queue=shared_queue
        self.agent_id = i

        seed = args.seed + np.int64(self.agent_id)
        np.random.seed(seed)
        torch.manual_seed(seed)

        self.counter = shared_value[0]
        self.stop_sign = shared_value[1]
        self.stop_sign=0  #修改处
        self.lock = lock
        self.env =args.env
        self.args = args
        self.experience_in_queue = []
        for i in range(args.num_buffers):
            self.experience_in_queue.append(shared_queue[0][i])

        self.device = torch.device("cpu")
        self.actor = PolicyNet(args).to(self.device)
        self.Q_net1 = QNet(args).to(self.device)


        self.Q_net1_share = share_net[0]
        self.actor_share = share_net[4]


    def put_data(self):
        if not self.stop_sign:
            index = self.agent_id
            if self.experience_in_queue[index].full():
                print("agent", self.agent_id, "is full")
                self.stop_sign=1
            else:
                self.experience_in_queue[index].put((self.state, self.u, \
                   [self.reward*self.args.reward_scale], self.state_next, [self.done], self.TD.detach().cpu().numpy().squeeze()))
                print("agent", self.agent_id, "is putting data")

        else:
            pass
    def get_experience_in_queue(self):
        return self.experience_in_queue

    def run(self):
            time_init = time.time()
            step = 0
            while not self.stop_sign:
                self.state = self.env.reset()
                self.episode_step = 0
                for i in range(self.args.max_step-1):
                    #state_tensor = torch.FloatTensor(self.state.copy()).to(self.device)
                    if self.args.NN_type == "CNN":
                        state_tensor = state_tensor.permute(2, 0, 1)
                    self.u, _, _ = self.actor.get_action(torch.from_numpy(np.float32(self.state)), False)
                    self.state_next, self.reward, self.done= self.env.step(self.u)
                    self.TD = torch.zeros(1)
                    #print("fuck","state",self.state,"state_next",self.state_next,"action",self.u,"time",self.env.time,"i_num",i,"done",self.done)
                    self.put_data()
                    self.state = self.state_next

                    with self.lock:
                        self.counter.value += 1

                    if step%self.args.load_param_period == 0:
                        #self.Q_net1.load_state_dict(self.Q_net1_share.state_dict())
                        self.actor.load_state_dict(self.actor_share.state_dict())
                    step += 1
                    self.episode_step += 1
                    if self.done == True:
                        break



def test():
    def xxxx():
        time.sleep(1)
        print("!!!!!!")
        xxxx()
    xxxx()


if __name__ == "__main__":
    test()



