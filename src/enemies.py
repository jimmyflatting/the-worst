class Enemy:
    def __init__(self, position, health):
        self.position = position
        self.health = health
        self.alive = True

    def update(self):
        if self.health <= 0:
            self.alive = False

    def render(self, renderer):
        if self.alive:
            renderer.draw_enemy(self.position)

    def take_damage(self, amount):
        self.health -= amount
        self.update()