def sanitize_supply_cost(a, cost, name):
    if cost is None:
        cost = a.default_cost
        if len(a.cost_names) > 1:
            a.log.info(f"Using default cost, {cost}, for {name}.")

    if cost not in a.cost_names:
        raise ValueError(f"{cost} not an available cost.")

    return cost


def sanitize_demand_cost(a, cost, name):
    if cost is None:
        cost = a.neighbor_default_cost
        if len(a.cost_names) > 1:
            a.log.info(f"Using default neighbor cost, {cost}, for {name}.")

    if cost not in a.neighbor_cost_names:
        raise ValueError(f"{cost} not an available neighbor cost.")

    return cost


def sanitize_supplies(a, supply_values):
    if type(supply_values) is str:
        supply_values = [supply_values]
    elif supply_values is None:
        supply_values = a.supply_types
    elif type(supply_values) is not list:
        raise ValueError(
            "supply_values should be a list or string (or -- default -- None)"
        )

    return supply_values


def normalized_access(a, columns):
    mean_access_values = (
        a.access_df[columns].multiply(a.access_df[a.demand_value], axis=0).sum()
        / a.access_df[a.demand_value].sum()
    )

    return a.access_df[columns].divide(mean_access_values)
