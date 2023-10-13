import gurobipy as gp
from gurobipy import Model, quicksum, GRB
import matplotlib.pyplot as plt;

chips = [
    'Plain',
    'Cream',
    'Mexican',
    'Bugles',
];

stages = [
    'Slicing',
    'Frying',
    'Packing',
];

capacity = {
    'Slicing': 345,
    'Frying': 480,
    'Packing': 330,
};

requirements = {
    ('Plain', 'Slicing'): 2,
    ('Cream', 'Slicing'): 2.5,
    ('Mexican', 'Slicing'): 4,
    ('Bugles', 'Slicing'): 5,
    ('Plain', 'Frying'): 4,
    ('Cream', 'Frying'): 4,
    ('Mexican', 'Frying'): 5,
    ('Bugles', 'Frying'): 4,
    ('Plain', 'Packing'): 4,
    ('Cream', 'Packing'): 3,
    ('Mexican', 'Packing'): 2,
    ('Bugles', 'Packing'): 3,
};

profits = {
    'Plain': 2,
    'Cream': 1.9,
    'Mexican': 1.5,
    'Bugles': 1.8
};

try:
    model = Model('Chip production');

    production = model.addVars(chips, name='production', lb=0, ub=GRB.INFINITY);
    model.setObjective(
        quicksum(profits[c] * production[c] for c in chips), 
        sense=GRB.MAXIMIZE);
    
    model.addConstrs(
        (quicksum(requirements[c, s] * production[c] for c in chips) <= capacity[s] 
                for s in stages),
            name = 'Satisfy capacity'
    );

    model.optimize();
    if model.status != GRB.OPTIMAL:
        raise Exception(f'Optimizer exited with status {model.status}.');

    print(f'Optimal objective value: {model.objVal}\n');
    for t in production.values():
        print(f'{t.varName} = {t.x}');

    shadow_price = model.getAttr(GRB.Attr.Pi);
    print(f'Shadow prices: {shadow_price}');

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))

except AttributeError:
    print('Encountered an attribute error')

### DUAL ###
try:
    model = Model('Chip production dual');

    production_dual = model.addVars(stages, name='production_dual', lb=0, ub=GRB.INFINITY);
    model.setObjective(
        quicksum(capacity[s] * production_dual[s] for s in stages), 
        sense=GRB.MINIMIZE);
    
    model.addConstrs(
        (quicksum(requirements[c, s] * production_dual[s] for s in stages) >= profits[c] 
                for c in chips),
            name = 'Satisfy capacity dual'
    );

    model.optimize();
    if model.status != GRB.OPTIMAL:
        raise Exception(f'Optimizer exited with status {model.status}.');

    print(f'Optimal objective value: {model.objVal}\n');
    for t in production_dual.values():
        print(f'{t.varName} = {t.x}');

    shadow_price = model.getAttr(GRB.Attr.Pi);
    print(f'Shadow prices: {shadow_price}');

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))

except AttributeError as e:
    print(f'Encountered an attribute error: {e}')


### SENSITIVITY Slicing ###

results = [];
for i in range(35, 1400):
    capacity['Slicing'] = i;
    try:
        model = Model('Chip production');

        production = model.addVars(chips, name='production', lb=0, ub=GRB.INFINITY);
        model.setObjective(
            quicksum(profits[c] * production[c] for c in chips), 
            sense=GRB.MAXIMIZE);
        
        model.addConstrs(
            (quicksum(requirements[c, s] * production[c] for c in chips) <= capacity[s] 
                    for s in stages),
                name = 'Satisfy capacity'
        );

        model.optimize();
        if model.status != GRB.OPTIMAL:
            raise Exception(f'Optimizer exited with status {model.status}.');

        results.insert(i, model.objVal);
    except gp.GurobiError as e:
        print('Error code ' + str(e.errno) + ': ' + str(e))

    except AttributeError:
        print('Encountered an attribute error')

plt.plot(results);
plt.show();
capacity['Slicing'] = 345;

### SENSITIVITY PLAIN ###

results = [];
for i in range(20, 800):
    profits['Plain'] = i / 100;
    try:
        model = Model('Chip production');

        production = model.addVars(chips, name='production', lb=0, ub=GRB.INFINITY);
        model.setObjective(
            quicksum(profits[c] * production[c] for c in chips), 
            sense=GRB.MAXIMIZE);
        
        model.addConstrs(
            (quicksum(requirements[c, s] * production[c] for c in chips) <= capacity[s] 
                    for s in stages),
                name = 'Satisfy capacity'
        );

        model.optimize();
        if model.status != GRB.OPTIMAL:
            raise Exception(f'Optimizer exited with status {model.status}.');

        results.insert(i, model.objVal);
    except gp.GurobiError as e:
        print('Error code ' + str(e.errno) + ': ' + str(e))

    except AttributeError:
        print('Encountered an attribute error')

plt.plot(results);
plt.show();