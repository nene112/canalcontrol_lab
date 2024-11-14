# canalcontrol_lab
软件包说明
# 环境要求
windows+python3.9


调用时候请参考给出的调用例子，调用api的前后顺序有要求。

# 读取文件并直接求解

该方式无法提前设置参数，相关参数全部定义在输入文件中

相关结果会直接输出在根目录

```python
obj = canalcontrol_lab.Lab(10)
# auto batch versino
ras= obj.ReadAndSolve(".", "vwn","sh-RMGateSchedule.txt.json","Roe")
```



# 读取文件、设置参数、求解

该方法能够将模型拆分为四个步骤，

1. 读取文件
2. 设置参数
3. 求解
4. 输出结果

## 批处理调用方法与函数、参数解释

```python
# batch version
solver_batch = canalcontrol_lab.Lab(10)  #初始化求解器
solver_batch.setEpisodeDuration_minites(3 * 24 * 60) #设置仿真时间（单位：min）
solver_batch.setOutputStep_seconds(60 * 60) #设置输出结果的时间间隔（单位：seconds）
solver_batch.ClearSolver() # 清空内存，保证求解器从空数据开始
solver_batch.ReadMesh(".", "vwn") # 读取输入文件，指定边界条件处理方法，PSH灌区全部采用“vwn”，其他灌区无限制，但该参数必须填写（"vwn"或任意字符串）
# //修改参数,先获取当前离散点数量num
num = solver_batch.GetPointsNum() # 获取求解器中的离散点数量
# 给定每个离散点的参数
width = np.full(num, fill_value=100) # 根据离散点数量，定义每个点的参数
# 设置参数
solver_batch.setWidth(width) # 根据离散点数量，设置每个点的参数

solver_batch.setBC("sh-RMGateSchedule.txt.json") # 读取调度方案文件（每个闸门的过流量时间序列）
solver_batch.Solver("Roe") # 求解，可指定不同求解器，目前参数选项包括：Roe，Pressure
solver_batch.WriteTimeSeries("wh") # 输出仿真结果到文件
solver_batch.ClearSolver() # 清空内存，防止内存泄漏
```

## 参数设置接口

相关参数设置接口与上面给出的`solver_batch.setWidth(width)`使用方法一样。

```c++
    .def("setWidth", &Lab::setWidth)
    .def("setElevation", &Lab::setElevation)
    .def("setWaterDepth", &Lab::setWaterDepth)
    .def("setwWaterLevel", &Lab::setwWaterLevel)
    .def("settanb", &Lab::settanb)
    .def("setmanning", &Lab::setmanning)
```



# 读取文件、设置参数、逐时间步求解、获取结果、输出结果

该方法将求解器拆解为时间步级别，提供更高的自由度：

1. 读取文件
2. 设置边界
3. 设置参数
4. 指定时间循环
5. 更新边界条件
6. 求解当前时间步的方程组
7. 获取当前时间步的计算结果
8. 保存当前时间步的计算结果

## 调用方法与函数、参数解释

```python
# step version
solver = canalcontrol_lab.Lab(10)
solver.setEpisodeDuration_minites(3 * 24 * 60) 
solver.setOutputStep_seconds(60 * 60) 
solver.ClearSolver() 
solver.ReadMesh(".", "vwn") 
solver.setBC("sh-RMGateSchedule.txt.json") 
solver.initiateSolver() # 初始化计算参数
for k in range( int(3 * 24 * 60 * 60 / 4))  : # 时间步循环（ 仿真时间/计算时间步，计算时间步=4 ）
  solver.updateBC(k) # 更新边界条件，在此之前必须ReadMesh，setBC
  solver.stepSolver("Roe", k) # 逐时间步求解控制方程
  state = solver.GetstepState("wh") # 获取当前时间步的水位（wh）数据
  solver.UpdateResult_pt(k) # 将当前时间步的结果保存到 专用于输出结果的 虚拟离散点中

solver.WriteTimeSeries("wh") # 将水位（wh）数据输出到文件“wh.csv”
solver.ClearSolver()
```



## GetstepState(string str)函数的其他选项

该函数的C实现如下，

```c++
std::vector<double> UpwindSVE::GetstepState(string stateType) {
  std::vector<double> state; state.resize(num);
  if (stateType == "h") {                                       //水深
    for (int i = 0; i < num; i++) {
      state[i] = param.wNode[i].h;
    }
  }
  else if (stateType == "wh")                                   //水位
  {
    for (int i = 0; i < num; i++) {
      state[i] = param.wNode[i].wh;
    }
  }
  else if (stateType == "ux")                                   //流速
  {
    for (int i = 0; i < num; i++) {
      state[i] = param.wNode[i].ux;
    }
  }
  else if (stateType == "Q")                                    //流量
  {
    for (int i = 0; i < num; i++) {
      state[i] = param.wNode[i].Q;
    }
  }
  else if (stateType == "As")                                    //过流面积
  {
    for (int i = 0; i < num; i++) {
      state[i] = param.wNode[i].Q;
    }
  }
  else if (stateType == "Bs")                                    //水面宽度
  {
    for (int i = 0; i < num; i++) {
      state[i] = param.wNode[i].B;
    }
  }
  return state;
}
```

## WriteTimeSeries()函数的要求与其他选项

要使用`WriteTimeSeries`必须逐时间步保存计算结果，即调用`solver.UpdateResult_pt(k)`

该函数的C实现如下，通过该实现可知其他的参数选项，

```python
void UpwindSVE::WriteTimeSeries(string stateType) {

  if (stateType == "wh") {
    h_csv_double wl = GetPointsWaterLevel();
    write_h_csv_double("wh.csv", wl, ',');
  }
  else if (stateType == "h")
  {
    h_csv_double wh = GetPointsWaterDepth();
    write_h_csv_double("h.csv", wh, ',');
  }
  else if (stateType == "ux")
  {
    h_csv_double wh = GetPointsUx();
    write_h_csv_double("ux.csv", wh, ',');
  }
  else if (stateType == "Q")
  {
    h_csv_double wh = GetPointsFlowQ();
    write_h_csv_double("Q.csv", wh, ',');
  }

  else if (stateType == "As")
  {
    h_csv_double wh = GetPointsAs();
    write_h_csv_double("As.csv", wh, ',');
  }
  else if (stateType == "Bs")
  {
    h_csv_double wh = GetPointsBs();
    write_h_csv_double("Bs.csv", wh, ',');
  }
}
```



