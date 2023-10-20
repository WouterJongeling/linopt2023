import gurobipy as gp
from gurobipy import Model, quicksum, GRB
import pandas as pd
import numpy as np
import sys;
import matplotlib.pyplot as plt;

data = pd.read_excel(sys.argv[1] if len(sys.argv) > 1 else 'data_mp_assignment_2wo20.ods');
df = pd.DataFrame(data);
numRows = 10;
numCols = 10;
fines = {
    50: 250,
    90: 200,
    110: 150,
    130: 100
};
EXCEED = 30;
DISTANCE = 100;
def speedlimith(i, j, alwaysBreak = False): 
    return df.iat[10-i, j+1] + (EXCEED if alwaysBreak else 0);
def speedlimitv(i, j, alwaysBreak = False):
    return df.iat[25-i, j+1] + (EXCEED if alwaysBreak else 0);
def fine(speedlimit):
    if(speedlimit in fines):
        return fines[speedlimit];
    return 0;

def optimise(budget: int, relax: bool = False):
    alwaysBreak = False;
    if budget < 0:
        alwaysBreak = True;
        budget = 0;
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
                model.addConstr(x[0,0]-y[0,0] + u[0,0]-v[0,0] == 1); #Vertex (0,0) (bottom left)
            elif i==numRows-1 and j==numCols-1:
                model.addConstr(-x[numRows-1,numCols-2]+y[numRows-1,numCols-2] + -u[numRows-2,numCols-1]+v[numRows-2,numCols-1] == -1); #Vertex (9,9) (top right)
            elif i==0 and j==numCols-1:
                model.addConstr(u[i,j]-v[i,j] - x[i,j-1]+y[i,j-1] == 0); #Vertex (0,9) (bottom right)
            elif i==numRows-1 and j==0:
                model.addConstr(x[i,j]-y[i,j] - u[i-1,j]+v[i-1,j] == 0); #Vertex (9,0) (top left)
            elif i==0:
                model.addConstr(x[i,j]-y[i,j] + u[i,j]-v[i,j] - x[i,j-1]+y[i,j-1] == 0); #(bottom row)
            elif j==0:
                model.addConstr(x[i,j]-y[i,j] + u[i,j]-v[i,j] - u[i-1,j]+v[i-1,j] == 0); #(left column)
            elif i == numRows-1:
                model.addConstr(x[i,j]-y[i,j] - u[i-1,j]+v[i-1,j] - x[i,j-1]+y[i,j-1] == 0); #(top row)
            elif j == numCols-1:
                model.addConstr(u[i,j]-v[i,j] - u[i-1,j]+v[i-1,j] - x[i,j-1]+y[i,j-1] == 0); #(right column)
            else:
                model.addConstr(x[i,j]-y[i,j] + u[i,j]-v[i,j] - u[i-1,j]+v[i-1,j] - x[i,j-1]+y[i,j-1] == 0); #(interior)
    model.addConstr(
        quicksum(b[i,j]*fine(speedlimith(i,j)) for j in range(numCols - 1) for i in range(numRows)) + 
        quicksum(c[i,j]*fine(speedlimitv(i,j)) for i in range(numRows - 1) for j in range(numCols)) <= budget
    );
    model.setObjective(
        quicksum(DISTANCE/speedlimith(i,j, alwaysBreak) * (x[i,j]+y[i,j]) - DISTANCE*EXCEED/(speedlimith(i,j)*(speedlimith(i,j)+EXCEED)) * b[i,j] for j in range(numCols - 1) for i in range(numRows)) +
        quicksum(DISTANCE/speedlimitv(i,j, alwaysBreak) * (u[i,j]+v[i,j]) - DISTANCE*EXCEED/(speedlimitv(i,j)*(speedlimitv(i,j)+EXCEED)) * c[i,j] for i in range(numRows - 1) for j in range(numCols)), sense=GRB.MINIMIZE);

    model.optimize();
    #print(f'Optimal objective value: {model.objVal}\n');
    
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
        else:
            path = [];
            break;
    if len(path) > 0:
        path.append([9,9,'']);
    return [path, model.objVal, model.Runtime, model.NodeCount];

def plotPath(path, savePath = None):
    plt.clf();
    data = np.asarray([[j,i] for [i,j,b] in path]);
    plt.xlim(0,9);
    plt.ylim(0,9);
    plt.plot(*data.transpose(), linewidth='4');
    if savePath is not None:
        plt.savefig(savePath);
    else:
        plt.show();

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

    # i=0; j=0;
    # while(i!=9 or j!=9):
    #     if j < 9 and x[i,j].x == 1:
    #         j+=1;
    #         print('+x');
    #     elif i < 9 and u[i,j].x == 1:
    #         i+=1;
    #         print('+y');
    #     elif j > 0 and y[i,j-1].x == 1:
    #         j-=1;
    #         print('-x');
    #     elif i > 0 and v[i-1,j].x == 1:
    #         i-=1;
    #         print('-y');
    #     #print(f'({i},{j})');

### Q1 ###
result = optimise(0, relax=False);
resultB = optimise(-1, relax=False);
print("Q1", result);
print("Q1", resultB);
plotPath(result[0], 'img/path_q1.png');
plotPath(resultB[0], 'img/path_q1b.png');

### Q2 ###
budgets = range(0, 2450, 50);
NUMRUNS = 1;
costs = [];
times = [];
nodes = [];
for budget in budgets:
    result = optimise(budget, relax=False);
    costs.append(result[1]);
    nodes.append(result[3]);
    sumTimes = result[2];
    for run in range(0, NUMRUNS - 1):
        result = optimise(budget, relax=False);
        sumTimes += result[2];
    times.append(sumTimes / NUMRUNS * 1000);

### Q3 ###
fig, axs = plt.subplots(3);

axs[0].plot(budgets, costs);
axs[0].set(xlabel='budget', ylabel='travel time (h)');
axs[0].set_ylim(bottom=0);
axs[0].set_xlim(left=0);

axs[1].scatter(budgets, times);
axs[1].set(xlabel='budget', ylabel='running time (ms)');
axs[1].set_ylim(bottom=0);
axs[1].set_xlim(left=0);

axs[2].plot(budgets, nodes);
axs[2].set(xlabel='budget', ylabel='nodes');
axs[2].set_ylim(bottom=0);
axs[2].set_xlim(left=0);

plt.savefig('img/stats.png')
sys.exit(0);

### Q4 ###
result = optimise(500, relax=False);
print("Q4", result);
