import time
import pygame, random

class Circle:
    def __init__(self, x, y, weight):
        self.x = x
        self.y = y
        self.weight = weight
        self.color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        self.get_radius_by_weight()
    
    def get_radius_by_weight(self):
        self.radius = self.weight ** 0.5

    def draw(self, screen):
        self.get_radius_by_weight()
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
    
    def check_takeover(self, other):
        return abs(self.x - other.x) < self.radius + other.radius and abs(self.y - other.y) < self.radius + other.radius


class Enemy(Circle):
    def __init__(self, x, y, weight):
        super().__init__(x, y, weight)
        self.life = True

    def move(self, dx, dy):
        self.x = max(min(dx + self.x, 800 - self.radius), self.radius)
        self.y = max(min(dy + self.y, 600 - self.radius), self.radius)

    def takeover(self, other):
        self.weight += other.weight * 0.8
    
    def find_nearest_meal(self, circles):
        nearest_circle = None
        nearest_distance = None
        for circle in circles:
            distance = (self.x - circle.x) ** 2 + (self.y - circle.y) ** 2
            if (nearest_distance is None or distance < nearest_distance) and circle.radius * 1.2 < self.radius:
                nearest_circle = circle
                nearest_distance = distance
        if nearest_circle is None:
            return None
        self.go_target(nearest_circle.x, nearest_circle.y)

    def go_target(self, x, y):
        step = 2
        if x > self.x:
            self.move(step, 0)
        elif x < self.x:
            self.move(-step, 0)
        if y > self.y:
            self.move(0, step)
        elif y < self.y:
            self.move(0, -step)
    
    def draw(self, screen):
        self.get_radius_by_weight()
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius, 1)

class Player(Enemy):
    def __init__(self, x, y, weight):
        super().__init__(x, y, weight)
        self.dx = 0
        self.dy = 0
        self.stage = 0
    
    def control(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.dx = -2
                elif event.key == pygame.K_RIGHT:
                    self.dx = 2
                elif event.key == pygame.K_UP:
                    self.dy = -2
                elif event.key == pygame.K_DOWN:
                    self.dy = 2
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    self.dx = 0
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    self.dy = 0
        self.go_target(self.x + self.dx, self.y + self.dy)



class Meal(Circle):
    def __init__(self, weight, x = None, y = None):
        if x is None:
            x = random.randint(0, 800)
            y = random.randint(0, 600)
        super().__init__(x, y, weight)

    def set_empty_coordinates(self, enimies):
        while self.check_takeover_enimies(enimies):
            self.x = random.randint(0, 800)
            self.y = random.randint(0, 600)

    def check_takeover_enimies(self, enimies):
        for enemy in enimies:
            if self.check_takeover(enemy):
                return True
        return False

class Bomb(Meal):
    def __init__(self):
        super().__init__(70)
        self.life = True
        self.color = (255, 255, 255)

class Background():
    def set_black_screen():
        """ Set black screen """
        screen = pygame.display.set_mode((800, 600))
        screen.fill((0, 0, 0))

    def draw_text(text):
        screen = pygame.display.set_mode((800, 600))
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont('Arial', 50)
        text = font.render(f'You {text}!', True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (400, 300)
        screen.blit(text, text_rect)
        pygame.display.flip()

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('Circles')
        self.clock = pygame.time.Clock()
        self.running = True
        self.max_players = 10
        self.player = Player(400, 300, 20)
        self.enemies  = [Enemy(random.randint(0, 800), random.randint(0, 600), random.randint(10, 30)) for _ in range(self.max_players - 1)] + [self.player]
        self.meals = []
        self.bombes = []

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.player.control(pygame.event.get())
            self.add_things()
            self.update()
            self.draw()
        time.sleep(2)
    
    def add_things(self):
        meal = Meal(random.randint(1, 2))
        meal.set_empty_coordinates(self.enemies)
        self.meals.append(meal)
        if random.random() < 0.01 and len(self.bombes) < 5:
            self.bombes.append(Bomb())
    
    def update(self):
        for enemy in self.enemies:
            for other in self.enemies:
                if enemy == other or enemy.life is False or other.life is False:
                    continue
                if enemy.check_takeover(other) and max(enemy.radius, other.radius) > min(enemy.radius, other.radius) * 1.2:
                    if enemy.radius > other.radius:
                        enemy.takeover(other)
                        other.life = False
                    else:
                        other.takeover(enemy)
                        enemy.life = False

            for meal in self.meals:
                if enemy.check_takeover(meal):
                    enemy.takeover(meal)
                    self.meals.remove(meal)

            for bomb in self.bombes:
                if enemy.check_takeover(bomb) and enemy.weight > bomb.weight:
                    enemy.weight /= 2
                    self.meals.append(Meal(enemy.weight))
                    self.bombes.remove(bomb)

        for enemy in self.enemies[:-1]:
            if enemy.life is False:
                self.enemies.remove(enemy)
            else:
                enemy.find_nearest_meal(self.meals + self.enemies)
        
        if self.player.life is False:
            self.player.stage = -1
            self.running = False
        elif len(self.enemies) == 1:
            self.player.stage = 1
            self.running = False

        if len(self.enemies) != self.max_players:
            self.enemies.insert(1, Enemy(random.randint(0, 800), random.randint(0, 600), random.randint(10, 30)))
    
    def draw(self):
        if self.player.stage == 0:
            self.screen.fill((0, 0, 0))
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for meal in self.meals:
                meal.draw(self.screen)
            for bomb in self.bombes:
                bomb.draw(self.screen)
        elif self.player.stage == 1:
            Background.draw_text('win')
        elif self.player.stage == -1:
            Background.draw_text('lose')
        pygame.display.flip()
    
game = Game()
game.run()