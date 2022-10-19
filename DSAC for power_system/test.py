from get import muti_power_env
import gol

obj=muti_power_env()
gol._init()
for i in range(24):
    obj.forward()
    print(obj.action_space)