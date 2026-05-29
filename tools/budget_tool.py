def calculate_budget(flight_cost, hotel_cost, days):

    food_cost = days * 1000

    transport_cost = days * 500

    total = (
        flight_cost
        + hotel_cost
        + food_cost
        + transport_cost
    )

    return {

        "flight_cost": flight_cost,

        "hotel_cost": hotel_cost,

        "food_cost": food_cost,

        "transport_cost": transport_cost,

        "total": total
    }