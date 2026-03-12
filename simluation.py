import pygame 
import random
from math import sqrt

WIDTH = 1280
HEIGHT = 800
TEAL = (20,150,140)
BALL_RADIUS = 5
GRID_SIZE = BALL_RADIUS * 2 + 1
GRAVITY = 0.0
REPULSION_RADIUS = BALL_RADIUS * 2
ATTRACTION_RADIUS = BALL_RADIUS * 4
REPULSION_STRENGTH = 0.5
ATTRACTION_STRENGTH = 0.1
DAMPING = 0.99
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()

running = True

class Ball:
    def __init__(self, x,y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-250,250)
        self.vy = random.uniform(-250,250)
        self.ax = 0
        self.ay = 0
        self.radius = BALL_RADIUS
        self.color = (0,0,255)
        
    def update(self, dt):
        self.vy += GRAVITY  * dt# gravity
        
        self.x += self.vx * dt + 0.5 * self.ax * dt**2 # change position due to velocity
        self.y += self.vy * dt + 0.5 * self.ay * dt**2
        
        self.vx += self.ax * dt # change velocity due to acceleration
        self.vy += self.ay * dt
        
        self.vx *= DAMPING
        self.vy *= DAMPING # damping to slow down over time
        
        self.ax = 0
        self.ay = 0 # reset acceleration for next frame

        if self.x - self.radius < 0:
            self.vx *= -0.9
            self.x = self.radius
        if self.x + self.radius > WIDTH:
            self.vx *= -0.9
            self.x = WIDTH - self.radius
    
        if self.y - self.radius < 0:
            self.vy *= -0.9
            self.y = self.radius
        if self.y + self.radius > HEIGHT:
            self.vy *= -0.9
            self.y = HEIGHT - self.radius
        
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        


        
def checkCollision(ball1,ball2):
    distance_x = ball1.x - ball2.x
    distance_y = ball1.y - ball2.y
    return distance_x**2 + distance_y**2 < (ball1.radius + ball2.radius)**2

def resolveOverlap(ball1, ball2):
    distance_x = ball2.x - ball1.x
    distance_y = ball2.y - ball1.y
    
    dist_sq = distance_x*distance_x + distance_y*distance_y
    radius_sum = ball1.radius + ball2.radius

    if dist_sq >= radius_sum*radius_sum:
        return
    
    distance = sqrt(dist_sq)
    
    if distance == 0:
        return
    
    overlap = ball1.radius + ball2.radius - distance
    if overlap > 0:
        normal_x = distance_x/distance
        normal_y = distance_y/distance
        
        ball1.x -= normal_x * overlap/2
        ball1.y -= normal_y * overlap/2

        ball2.x += normal_x * overlap/2
        ball2.y += normal_y * overlap/2
     
def resolveCollision(ball1, ball2):
    distance_x = ball2.x - ball1.x
    distance_y = ball2.y - ball1.y
    distance = sqrt(distance_x*distance_x + distance_y*distance_y)
    if distance == 0:
        return  
    normal_x = distance_x / distance
    normal_y = distance_y / distance
    
    relative_vx = ball2.vx - ball1.vx
    relative_vy = ball2.vy - ball1.vy
    
    velocity_along_normal = relative_vx * normal_x + relative_vy * normal_y
    if velocity_along_normal > 0:
        return

    restitution = 0.9
    impulse = -(1 + restitution) * velocity_along_normal / 2
    
    ball1.vx -= impulse * normal_x
    ball1.vy -= impulse * normal_y

    ball2.vx += impulse * normal_x
    ball2.vy += impulse * normal_y
        
def createGrid():
    grid = {}
    for i, ball in enumerate(balls):
        cell = (int(ball.x // GRID_SIZE), int(ball.y // GRID_SIZE))
        grid.setdefault(cell, []).append((i, ball))
        
    return grid
def collisionPass(grid):
    for i, ball in enumerate(balls):
        cell_x = int(ball.x // GRID_SIZE)
        cell_y = int(ball.y // GRID_SIZE)
        NEIGHBOR_OFFSETS = [
            (-1,-1),(-1,0),(-1,1),
            (0,-1),(0,0),(0,1),
            (1,-1),(1,0),(1,1)
            ]
        for dx, dy in NEIGHBOR_OFFSETS:
                neighbor_cell = (cell_x + dx, cell_y + dy)
                
                for j, other in grid.get(neighbor_cell, []):
                    if j <= i:
                        continue

                    if checkCollision(ball, other):
                        resolveOverlap(ball, other)
                        resolveCollision(ball, other)
                    


    
balls = []
for _ in range(5000):
        balls.append(Ball(random.randint(0,WIDTH),random.randint(0,HEIGHT)))   

while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    screen.fill(TEAL)
    
    
    for ball in balls:
        ball.update(dt)
        
    grid = createGrid()
    for _ in range(5):
        collisionPass(grid)
                
    for ball in balls:
        ball.draw(screen)
        
    pygame.display.set_caption(f"FPS: {clock.get_fps():.0f}")
    
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()