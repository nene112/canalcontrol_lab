
import os
import json
import math
import numpy as np

import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter, argrelextrema
from findDelaytimeP import *

os.chdir(os.path.dirname(os.path.abspath(__file__)))

import canalcontrol_lab

# step version
solver = canalcontrol_lab.Lab(10)
solver.ClearSolver() 


# 定义网格,  num*step_s=实际的渠道长度
num=1000  # 节点数量
step_s=100 # 节点之间的间距，空间步长, m
solver.autoMesh(num, step_s)
solver.setOutputStep_seconds(3600)

# 定义水源
Gnindex = [0]   # 水源的节点编号
Gflow = [ 10 ]  # 水源的默认流量
solver.createInputGates(Gnindex, Gflow)
# 输出闸门的编号数组，检查闸门位置
a=solver.GetGatesNindex() 
print(a)

# 定义节制闸(check structure)
Gnindex = [ 500,800 ]  # 节点编号，2个闸门
Gflow = [ 8 ,5 ]  # 默认流量
solver.createCheckGates(Gnindex, Gflow)

# 检查闸门编号（位置）
a=solver.GetGatesNindex() 
print(a)
# 检查 时间步长，（根据空间步长自动计算）
step_t=solver.getstep_t()
print("step_t : ", step_t)

# 定义内边界(汇流/分水)
Gnindex = [ 200,600 ] # 定义内边界编号
Gflow = [ 2,-2 ]  # 内边界默认流量,+代表入流，-代表出流
solver.createTurnouts(Gnindex, Gflow)

# 初始化求解器参数
solver.initiateSolver() 

# 开始时间循环
interval=3600
for k in range( int( 24 * 60 * 60 / 4))  :
  solver.stepSolver("Pressure", k)  # 步进求解
  state = solver.GetstepState("wh")   # 获取状态（wh-水位，h-水深，Q-代表流量）
  solver.UpdateResult_pt(k)   # 更新 保存结果的虚拟网格,为了WriteTimeSeries做准备
  if k% (interval/step_t)==0:  # 时间戳输出
    print(k/(interval/step_t))

# 输出结果到文件
solver.WriteTimeSeries("wh","",num)#  状态类型，文件标识，节点数量
solver.WriteTimeSeries("Q","",num)


# 清空内存
solver.ClearSolver()

