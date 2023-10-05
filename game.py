import pygame
import os
import random


class DinoGame:
    pygame.init()

    SCREEN_HEIGHT = 600
    SCREEN_WIDTH = 1100
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
            pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]
    JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))
    DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
            pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png"))]

    SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                    pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                    pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
    LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                    pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                    pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

    BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
            pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]

    CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))

    BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

    class Dinosaur:
        X_POS = 80
        Y_POS = 310
        Y_POS_DUCK = 340
        JUMP_VEL = 8.5

        def __init__(self, game):
            self.duck_img = game.DUCKING
            self.run_img = game.RUNNING
            self.jump_img = game.JUMPING

            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False
            
            self.step_index = 0
            self.jump_vel=self.JUMP_VEL
            self.image = self.run_img[0]
            self.dino_rect = self.image.get_rect()
            self.dino_rect.x = self.X_POS
            self.dino_rect.y = self.Y_POS

        def update(self, action):
            if self.dino_duck:
                self.duck()
            if self.dino_run:
                self.run()
            if self.dino_jump:
                self.jump()

            if self.step_index >= 10:
                self.step_index = 0

            if bool(action[2]) and not self.dino_jump:
                self.dino_jump=True
                self.dino_duck=False
                self.dino_run=False
            elif bool(action[1]) and not self.dino_jump:
                self.dino_jump=False
                self.dino_duck=True
                self.dino_run=False
            elif not (self.dino_jump or bool(action[1])):
                self.dino_jump=False
                self.dino_duck=False
                self.dino_run=True

        def duck(self):
            self.image = self.duck_img[self.step_index // 5]
            self.dino_rect = self.image.get_rect()
            self.dino_rect.x = self.X_POS
            self.dino_rect.y = self.Y_POS_DUCK
            self.step_index += 1

        def jump(self):
            self.image = self.jump_img
            if self.dino_jump:
                self.dino_rect.y -= self.jump_vel * 4
                self.jump_vel -= 0.8
            if self.jump_vel < - self.JUMP_VEL:
                self.dino_jump = False
                self.jump_vel = self.JUMP_VEL

        def run(self):
            self.image = self.run_img[self.step_index // 5]
            self.dino_rect = self.image.get_rect()
            self.dino_rect.x = self.X_POS
            self.dino_rect.y = self.Y_POS
            self.step_index += 1

        def draw(self, SCREEN):
            SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))
            

    class Cloud:
        def __init__(self, game):
            self.x = game.SCREEN_WIDTH + random.randint(800, 1000)
            self.y = random.randint(50, 100)
            self.image = game.CLOUD
            self.width = self.image.get_width()

        def update(self, game):
            self.x -= game.game_speed
            if self.x < -self.width:
                self.x = game.SCREEN_WIDTH + random.randint(2500, 3000)
                self.y = random.randint(50, 100)

        def draw(self, SCREEN):
            SCREEN.blit(self.image, (self.x, self.y))


    class Obstacle:
        def __init__(self, image, type, game):
            self.image = image
            self.type = type
            self.id = game.obstacle_id
            self.rect = self.image[self.type].get_rect()
            self.rect.x = game.SCREEN_WIDTH

        def update(self, game):
            self.rect.x -= game.game_speed
            if self.rect.x < -self.rect.width:
                game.obstacles.pop()

        def draw(self, SCREEN):
            SCREEN.blit(self.image[self.type], self.rect)

    class SmallCactus(Obstacle):
        def __init__(self, image, game):
            self.type = random.randint(0, 2)
            super().__init__(image, self.type, game)
            self.rect.y = 325
            self.family = 0


    class LargeCactus(Obstacle):
        def __init__(self, image, game):
            self.type = random.randint(0, 2)
            super().__init__(image, self.type, game)
            self.rect.y = 300
            self.family = 1


    class Bird(Obstacle):
        def __init__(self, image, game):
            self.type = 0
            super().__init__(image, self.type, game)
            self.rect.y = 250
            self.index = 0
            self.family = 2

        def draw(self, SCREEN):
            if self.index >= 9:
                self.index = 0
            SCREEN.blit(self.image[self.index//5], self.rect)
            self.index += 1


    def __init__(self):
        self.reset()

    def reset(self):
        self.game_speed = 20
        self.obstacle_id = 0
        self.x_pos_bg = 0
        self.reward = 0
        self.y_pos_bg = 380
        self.points=0
        self.obstacles = []
        self.run = True
        self.clock = pygame.time.Clock()
        self.player = self.Dinosaur(self)
        self.cloud = self.Cloud(self)  
        self.font = pygame.font.Font('freesansbold.ttf', 20)

    def score(self):
        self.points += 1
        if self.points % 100 == 0:
            self.game_speed += 1

        text = self.font.render("Points: " + str(self.points), True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (1000, 40)
        self.SCREEN.blit(text, textRect)


    def background(self):
        image_width = self.BG.get_width()
        self.SCREEN.blit(self.BG, (self.x_pos_bg, self.y_pos_bg))
        self.SCREEN.blit(self.BG, (image_width + self.x_pos_bg, self.y_pos_bg))
        if self.x_pos_bg <= -image_width:
            self.SCREEN.blit(self.BG, (image_width + self.x_pos_bg, self.y_pos_bg))
            self.x_pos_bg = 0
        self.x_pos_bg -= self.game_speed
    
    def stop_check(self):
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                    return True
        return False

    def check_collisions(self):
        for obstacle in self.obstacles:
                obstacle.draw(self.SCREEN)
                obstacle.update(self)
                if self.player.dino_rect.colliderect(obstacle.rect):
                    pygame.draw.rect(self.SCREEN, (255,0,0), self.player.dino_rect,2)
                    self.reward -= 10
                    return True
        return False
    
    def check_reward(self, collision):
        for obstacle in self.obstacles:
            if obstacle.rect.x < 80 and not collision and obstacle.rect.x > 50:
                print("U rewardo")
                return 10
                self.reward = self.reward + 10
        return 0

    def play_step(self, action):
        self.stop_check()
        self.SCREEN.fill((255,255,255))

        self.player.draw(self.SCREEN)
        self.player.update(action)

        if len(self.obstacles) == 0:
            if random.randint(0, 2) == 0:
                self.obstacles.append(self.SmallCactus(self.SMALL_CACTUS, self))
            elif random.randint(0, 2) == 1:
                self.obstacles.append(self.LargeCactus(self.LARGE_CACTUS, self))
            elif random.randint(0, 2) == 2:
                self.obstacles.append(self.Bird(self.BIRD, self))
            self.obstacle_id += 1

        collision = self.check_collisions()
        #self.check_reward(collision)
        self.background()

        self.cloud.draw(self.SCREEN)
        self.cloud.update(self)

        self.score()
        
        self.clock.tick(30)
        pygame.display.update()

        return collision, self.points, self.reward
        

                   
        