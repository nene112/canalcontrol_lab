
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

# 创建 Lab 实例，并调用 add 函数,输入的参数是定义的求解器序号
obj = canalcontrol_lab.Lab(0)


# auto batch versino
ras= obj.ReadAndSolve(".", "vwn","sh-RMGateSchedule.txt.json","Roe")


# batch versino
solver_batch = canalcontrol_lab.Lab(10)
solver_batch.setEpisodeDuration_minites(3 * 24 * 60) 
solver_batch.setOutputStep_seconds(60 * 60) 
solver_batch.ClearSolver()
solver_batch.ReadMesh(".", "vwn") 
# //修改参数,先获取当前离散点数量num
num = solver_batch.GetPointsNum() 
# 给定每个离散点的参数
width = np.full(num, fill_value=100)
# 设置参数
solver_batch.setWidth(width) 
solver_batch.setBC("sh-RMGateSchedule.txt.json") 
solver_batch.Solver("Roe") 
solver_batch.WriteTimeSeries("wh","",595)
solver_batch.ClearSolver() 

# step version
solver = canalcontrol_lab.Lab(10)
solver.setEpisodeDuration_minites(3 * 24 * 60) 
solver.setOutputStep_seconds(60 * 60) 
solver.ClearSolver() 
solver.ReadMesh(".", "vwn") 
solver.setBC("sh-RMGateSchedule.txt.json") 
solver.initiateSolver() 
for k in range( int(3 * 24 * 60 * 60 / 4))  :
  solver.updateBC(k) 
  solver.stepSolver("Roe", k) 
  state = solver.GetstepState("wh") 
  solver.UpdateResult_pt(k) 

solver.WriteTimeSeries("wh","",595)
solver.ClearSolver()

