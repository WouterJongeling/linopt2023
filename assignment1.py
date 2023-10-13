import gurobipy as gp
from gurobipy import Model, quicksum, GRB

try:

    plants = [
        'Haarlem',
        'Eindhoven'
    ];

    customers = [
        'Amsterdam',
        'Breda',
        'Gouda',
        'Amersfoort',
        'Den Bosch'
    ];

    supply = {
        'Haarlem': 47,
        'Eindhoven': 63
    };

    demand = {
        'Amsterdam': 28,
        'Breda': 16,
        'Gouda': 22,
        'Amersfoort': 31,
        'Den Bosch': 12
    };

    unit_transport_cost = {
        ('Haarlem', 'Amsterdam'): 131,
        ('Haarlem', 'Breda'): 405,
        ('Haarlem', 'Gouda'): 188,
        ('Haarlem', 'Amersfoort'): 396,
        ('Haarlem', 'Den Bosch'): 485,
        ('Eindhoven', 'Amsterdam'): 554,
        ('Eindhoven', 'Breda'): 351,
        ('Eindhoven', 'Gouda'): 479,
        ('Eindhoven', 'Amersfoort'): 366,
        ('Eindhoven', 'Den Bosch'): 155
    };

    model = Model('Beer transport');

    transport = model.addVars(plants, customers, name='transport', lb=0, ub=GRB.INFINITY);
    model.setObjective(
        quicksum(unit_transport_cost[p,c] * transport[p, c] 
                 for c in customers for p in plants), 
        sense=GRB.MINIMIZE);
    
    model.addConstrs(
        (quicksum(transport[p, c] for c in customers) <= supply[p] 
                for p in plants),
            name = 'Satisfy supply'
    );
    model.addConstrs(
        (quicksum(transport[p, c] for p in plants) >= demand[c] 
                for c in customers),
            name = 'Satisfy demand'
    );

    model.optimize();
    if model.status != GRB.OPTIMAL:
        raise Exception(f'Optimizer exited with status {model.status}.');

    print(f'Optimal objective value: {model.objVal}\n');
    for t in transport.values():
        print(f'{t.varName} = {t.x}');

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))

except AttributeError:
    print('Encountered an attribute error')