import pygame 
import random
from math import sqrt
import colorsys

WIDTH = 1280
HEIGHT = 800
BG_COLOR = (10,50,40)
BALL_RADIUS = 7
TOTAL_BALLS = 2000
GRAVITY = 0.0
REPULSION_RADIUS = BALL_RADIUS * 2.75
ATTRACTION_RADIUS = BALL_RADIUS * 7.5
REPULSION_STRENGTH = 200
ATTRACTION_STRENGTH = 15
STARTING_VELOCITY = 50
DAMPING = 0.97
PHYSICS_STEPS = 2

GRID_SIZE = ATTRACTION_RADIUS
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()

running = True

class Ball:
    def __init__(self, x,y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-STARTING_VELOCITY, STARTING_VELOCITY)
        self.vy = random.uniform(-STARTING_VELOCITY, STARTING_VELOCITY)
        self.ax = 0
        self.ay = 0
        self.radius = BALL_RADIUS
        
        
        self.color = color
        
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
        
def compute_force(dist):
    if dist < REPULSION_RADIUS:
        # Linearly goes from max repulsion at dist=0, to 0 at repulsion_radius
        return -REPULSION_STRENGTH * (1 - dist / REPULSION_RADIUS)
    elif dist < ATTRACTION_RADIUS:
        # Linearly goes from 0 at repulsion_radius, peaks, fades back to 0
        return ATTRACTION_STRENGTH * (1 - dist / ATTRACTION_RADIUS)
    else:
        return 0

def createGrid():
    grid = {}
    for i, ball in enumerate(balls):
        cell = (int(ball.x // GRID_SIZE), int(ball.y // GRID_SIZE))
        grid.setdefault(cell, []).append((i, ball))
        
    return grid
def applyForces(grid):
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
                    if j <= i: # avoid double counting
                        continue
                    delta_x = other.x - ball.x
                    delta_y = other.y - ball.y
                    dist = sqrt(delta_x**2 + delta_y**2)
                    
                    if dist == 0:
                        continue
                        
                    
                    # --- Force magnitude (scalar) ---
                    force = compute_force(dist)
                    
                    # --- Direction (unit vector toward `other`) ---
                    nx = delta_x / dist
                    ny = delta_y / dist
                    
                    # --- Apply equal and opposite (Newton's 3rd law) ---
                    ball.ax  += force * nx    # positive force = pulled toward other
                    ball.ay  += force * ny
                    other.ax -= force * nx    # other gets pushed opposite direction
                    other.ay -= force * ny
                    


    
balls = []
for i in range(TOTAL_BALLS):
        hue = (i/TOTAL_BALLS) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
        color = (int(r*255), int(g*255), int(b*255))
        balls.append(Ball(random.randint(0,WIDTH),random.randint(0,HEIGHT), color))

while running:
    frame_dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    screen.fill(BG_COLOR)
    
    sub_dt = frame_dt / PHYSICS_STEPS
    for _ in range(PHYSICS_STEPS):
        grid = createGrid()
        applyForces(grid)
        
        for ball in balls:
            ball.update(sub_dt)
        

                
    for ball in balls:
        ball.draw(screen)
        
        
    pygame.display.set_caption(f"FPS: {clock.get_fps():.0f}")
    
    pygame.display.flip()
    
    
pygame.quit()
