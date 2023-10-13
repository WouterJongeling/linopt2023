import gurobipy as gp
from gurobipy import Model, quicksum, GRB
import pandas as pd
    
try:
    df = pd.read_excel('data_mp_assignment_2wo20.ods');
    print(df);
    numRows = 10;
    numCols = 10;

    model = Model('Road network');

    lengths = [];
    d = {};

    for i in range(numRows):
        for j in range(numCols):
            d[i,j] = model.addVar(name=f'distance({i},{j})',
                                       lb=0, ub=GRB.INFINITY);
    
    for x in range(numCols):
        for y in range(numRows):
            if x != 0:
                model.addConstr(d[x,y] - d[x-1,y] <= lengths[x-1,y]);
                model.addConstr(d[x-1,y] - d[x,y] <= lengths[x-1,y]);
            if x != numCols - 1:
                model.addConstr(d[x,y] - d[x+1,y] <= lengths[x,y]);
                model.addConstr(d[x+1,y] - d[x,y] <= lengths[x,y]);
            if y != 0:
                model.addConstr(d[x,y] - d[x,y-1] <= lengths[x,y-1]);
                model.addConstr(d[x,y-1] - d[x,y] <= lengths[x,y-1]);
            if y != numRows - 1:
                model.addConstr(d[x,y] - d[x,y+1] <= lengths[x,y+1]);
                model.addConstr(d[x,y+1] - d[x,y] <= lengths[x,y+1]);

    model.optimize();
    if model.status != GRB.OPTIMAL:
        raise Exception(f'Optimizer exited with status {model.status}.');

    print(f'Optimal objective value: {model.objVal}\n');
    for t in d.values():
        print(f'{t.varName} = {t.x}');

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))

except AttributeError:
    print('Encountered an attribute error')