
import os
import json
import math
import numpy as np

import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter, argrelextrema

os.chdir(os.path.dirname(os.path.abspath(__file__)))

import canalcontrol_lab

# step version
solver = canalcontrol_lab.Lab(0)
sim_time=10*60# min
solver.setEpisodeDuration_minites(sim_time) 
solver.setOutputStep_seconds(60 * 60) 
solver.ClearSolver() 
solver.ReadMesh(".", "vwn") 
# solver.setBC("sh-RMGateSchedule.txt.json") 


solver.initiateSolver() 
for k in range( int(sim_time * 60 / 4))  :
  # solver.updateBC(k,[]) 
  id1 = 0
  flow1 = 10
  id2 = 100
  flow2 = 2
  solver.executeControl(id1, flow1)
  solver.executeControl(id2, flow2)
  solver.stepSolver("Roe", k) 
  state = solver.GetstepState("wh") 
  solver.UpdateResult_pt(k) 
  if k% 900==0:
    print(k/900)

solver.WriteTimeSeries("wh","",200)
solver.WriteTimeSeries("Q","",200)
solver.ClearSolver()

