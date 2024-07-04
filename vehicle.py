class Vehicle:
    def __init__(self):
        self.vehicle_type = ""

class Car_4_Seaters(Vehicle):
    def __init__(self):
        super().__init__()
        self.vehicle_type = "car"

    def calculate_fare(self, distance):
        base_fare = 45
        per_km_rate = 15
        return base_fare + (distance / 1000) * per_km_rate

class Car_6_Seaters(Vehicle):
    def __init__(self):
        super().__init__()
        self.vehicle_type = "car"

    def calculate_fare(self, distance):
        base_fare = 50
        per_km_rate = 18
        return base_fare + (distance / 1000) * per_km_rate

class Motorcycle(Vehicle):
    def __init__(self):
        super().__init__()
        self.vehicle_type = "bike"

    def calculate_fare(self, distance):
        base_fare = 40
        per_km_rate = 12
        return base_fare + (distance / 1000) * per_km_rate
