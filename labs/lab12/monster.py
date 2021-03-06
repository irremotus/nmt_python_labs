class Monster:
  def __init__(self, name, health=50, attack=50, defense=50,
    speed=50):
    self.name = name
    self.max_hp = health
    self.current_hp = self.max_hp
    self.attack = attack
    self.defense = defense
    self.speed = speed

  def deal_damage(self, damage):
    damage = damage * (1 - self.defense/100)
    self.current_hp -= damage