import gurobipy as gp
from gurobipy import Model, quicksum, GRB
import pandas as pd

data = pd.read_excel('data_mp_assignment_2wo20.ods');
df = pd.DataFrame(data);
numRows = 10;
numCols = 10;
fine = {
    50: 250,
    90: 200,
    110: 150,
    130: 100
};
EXCEED = 30;
DISTANCE = 100;
def speedlimith(i, j): 
    return df.iat[10-i, j+1];
def speedlimitv(i, j):
    return df.iat[25-i, j+1];

def optimise(budget: int, relax: bool = False):
    model = Model('Road network');
    model.setParam('LogToConsole', 0);
    x = {}; y = {}; u={}; v={}; b = {}; c = {};

    for i in range(numRows):
        for j in range(numCols):
            if j != numCols-1:
                x[i,j] = model.addVar(name=f'horr({i},{j})', lb=0, ub=1, vtype=GRB.CONTINUOUS);
                y[i,j] = model.addVar(name=f'horl({i},{j})', lb=0, ub=1, vtype=GRB.CONTINUOUS);
                b[i,j] = model.addVar(name=f'breakh({i},{j})', lb=0, ub=1, vtype=GRB.CONTINUOUS if relax else GRB.INTEGER);
                model.addConstr(x[i,j]+y[i,j] >= b[i,j]);
            if i != numRows-1:
                u[i,j] = model.addVar(name=f'veru({i},{j})', lb=0, ub=1, vtype=GRB.CONTINUOUS);
                v[i,j] = model.addVar(name=f'verd({i},{j})', lb=0, ub=1, vtype=GRB.CONTINUOUS);
                c[i,j] = model.addVar(name=f'breakv({i},{j})', lb=0, ub=1, vtype=GRB.CONTINUOUS if relax else GRB.INTEGER);
                model.addConstr(u[i,j]+v[i,j] >= c[i,j]);
            if i==0 and j==0:
                model.addConstr(x[0,0]-y[0,0] + u[0,0]-v[0,0] == 1);
            elif i==numRows-1 and j==numCols-1:
                model.addConstr(-x[numRows-1,numCols-2]+y[numRows-1,numCols-2] + -u[numRows-2,numCols-1]+v[numRows-2,numCols-1] == -1);
            elif i==0 and j==numCols-1:
                model.addConstr(u[i,j]-v[i,j] - x[i,j-1]+y[i,j-1] == 0);
            elif i==numRows-1 and j==0:
                model.addConstr(x[i,j]-y[i,j] - u[i-1,j]+v[i-1,j] == 0);
            elif i==0:
                model.addConstr(x[i,j]-y[i,j] + u[i,j]-v[i,j] - x[i,j-1]+y[i,j-1] == 0);
            elif j==0:
                model.addConstr(x[i,j]-y[i,j] + u[i,j]-v[i,j] - u[i-1,j]+v[i-1,j] == 0);
            elif i == numRows-1:
                model.addConstr(x[i,j]-y[i,j] - u[i-1,j]+v[i-1,j] - x[i,j-1]+y[i,j-1] == 0);
            elif j == numCols-1:
                model.addConstr(u[i,j]-v[i,j] - u[i-1,j]+v[i-1,j] - x[i,j-1]+y[i,j-1] == 0);
            else:
                model.addConstr(x[i,j]-y[i,j] + u[i,j]-v[i,j] - u[i-1,j]+v[i-1,j] - x[i,j-1]+y[i,j-1] == 0);
    model.addConstr(
        quicksum(b[i,j]*fine[speedlimith(i,j)] for j in range(numCols - 1) for i in range(numRows)) + 
        quicksum(c[i,j]*fine[speedlimitv(i,j)] for i in range(numRows - 1) for j in range(numCols)) <= budget
    );

    model.setObjective(
        quicksum(DISTANCE/speedlimith(i,j) * (x[i,j]+y[i,j]) - DISTANCE*EXCEED/(speedlimith(i,j)*(speedlimith(i,j)+EXCEED)) * b[i,j] for j in range(numCols - 1) for i in range(numRows)) +
        quicksum(DISTANCE/speedlimitv(i,j) * (u[i,j]+v[i,j]) - DISTANCE*EXCEED/(speedlimitv(i,j)*(speedlimitv(i,j)+EXCEED)) * c[i,j] for i in range(numRows - 1) for j in range(numCols)), sense=GRB.MINIMIZE);

    model.optimize();
    print(f'Optimal objective value: {model.objVal}\n');
    
    #printPath(x, y, u, v, b, c);
    path = [];
    i=0; j=0;
    while(i!=9 or j!=9):
        brk = '';
        if(j < 9 and b[i,j].x > 0):
            brk += f'B{b[i,j].x}';
        elif(i < 9 and c[i,j].x > 0):
            brk = f'B{c[i,j].x}';
        path.append([i,j,brk]);

        if j < 9 and x[i,j].x == 1:
            j+=1;
        elif i < 9 and u[i,j].x == 1:
            i+=1;
        elif j > 0 and y[i,j-1].x == 1:
            j-=1;
        elif i > 0 and v[i-1,j].x == 1:
            i-=1;
    return [path, model.objVal, model.Runtime];

def printPath(x, y, u, v, b, c):
    for t in x.values():
        if t.x != 0: print(f'{t.varName} = {t.x}');
    for t in y.values():
        if t.x != 0: print(f'{t.varName} = {t.x}');
    for t in u.values():
        if t.x != 0: print(f'{t.varName} = {t.x}');
    for t in v.values():
        if t.x != 0: print(f'{t.varName} = {t.x}');
    for t in b.values():
        if t.x != 0: print(f'{t.varName} = {t.x}');
    for t in c.values():
        if t.x != 0: print(f'{t.varName} = {t.x}');

    i=0; j=0;
    while(i!=9 or j!=9):
        if j < 9 and x[i,j].x == 1:
            j+=1;
            print('+x');
        elif i < 9 and u[i,j].x == 1:
            i+=1;
            print('+y');
        elif j > 0 and y[i,j-1].x == 1:
            j-=1;
            print('-x');
        elif i > 0 and v[i-1,j].x == 1:
            i-=1;
            print('-y');
        #print(f'({i},{j})');

### Q1 ###
result = optimise(0, False);
print(result);

### Q3 ###
xaxis = range(0, 2850, 50);
costs = [];
times = [];
for budget in xaxis:
    result = optimise(budget);
    #print(budget, result);
    costs.append(result[1]);
    times.append(result[2]);
print(costs);

import matplotlib.pyplot as plt

#plt.plot(xaxis, costs);
plt.plot(xaxis, times);
plt.title('title name')
plt.xlabel('budget')
plt.ylabel('running time')
plt.ylim(bottom=0);
plt.xlim(left=0);
plt.show();

### Q4 ###
result = optimise(500, False);
print(result);
