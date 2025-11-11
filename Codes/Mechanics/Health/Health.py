class HealthSystem:
    def __init__(self, max_health):
        self.max_health = max_health
        self.current_health = max_health

    def take_damage(self, amount):
        self.current_health = max(0, self.current_health - amount)

    def heal(self, amount):
        self.current_health = min(self.max_health, self.current_health + amount)

    def get_current_health(self):
        return self.current_health

    def is_alive(self):
        return self.current_health > 0