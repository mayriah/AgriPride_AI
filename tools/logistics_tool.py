def plan_route(location, quantity):
    return {
        "origin": location,
        "quantity_kg": quantity,
        "distance_km": 120,
        "transport_cost_ratio": 0.25,
        "risk": "moderate",
        "road_condition": "fair",
        "estimated_cost": 210000,
    }
