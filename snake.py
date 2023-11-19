#snake
import pygame
import sys
import random
import time

pygame.init()
CELL_SIZE = 30
CELL_QUANTITY = 30
screen = pygame.display.set_mode((CELL_SIZE * CELL_QUANTITY, CELL_SIZE * CELL_QUANTITY))
pygame.display.set_caption('Snake')
clock = pygame.time.Clock()

global gameActive, score, winning
score = 0
gameActive = False
winning = False

my_font = pygame.font.SysFont('Comic Sans MS', 30)
score_surf = my_font.render(f'score:{score}', False, (255, 0, 0))
lose_surf = my_font.render(f'You died!', False, (255, 0, 0))
win_surf = my_font.render(f'You won!', False, (255, 0, 0))
bgm = pygame.mixer.Sound('audio/bgm.wav')
bgm.set_volume(0.3)

class Fruit:
    def __init__(self, snake):
        self.x_pos = 5
        self.y_pos = 10
        self.fruit_pos = (self.x_pos, self.y_pos)

    #the fruit is allocated a random x and y coordinate
    def generate_position(self):
        while True:
            self.x_pos = random.randint(0, CELL_QUANTITY-1)
            self.y_pos = random.randint(0, CELL_QUANTITY-1)
            if (self.x_pos,self.y_pos) not in snake.coordList:
                break
        self.rect = pygame.Rect(self.x_pos*CELL_SIZE, self.y_pos*CELL_SIZE, CELL_SIZE, CELL_SIZE)

    def draw_fruit(self):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)   

    #check if the fruit coords equal the snake's head coord
    def update(self):
        self.draw_fruit()


class Snake:
    def __init__(self):
        self.coordList = [(0,int(CELL_QUANTITY/2)),(1,int(CELL_QUANTITY/2)),(2,int(CELL_QUANTITY/2))]
        self.xMovement = 1
        self.yMovement = 0
        self.lastKeyInput = 'right'
        self.eaten = False
        self.dead_sound = pygame.mixer.Sound('audio/dead.wav')
        self.win_sound = pygame.mixer.Sound('audio/win.wav')

    def display_blocks(self):
        #displaying body
        for coords in self.coordList[:-1]:
            x, y = coords[0], coords[1]
            body_rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (0,0,255), body_rect)
        x,y = self.coordList[-1]
        head_rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, (173,216,230), head_rect)
            
    def moving_blocks(self):
        #moves the head according to input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            if self.lastKeyInput != 'left':
                self.xMovement, self.yMovement = 1, 0
                self.lastKeyInput = 'right'
        elif keys[pygame.K_LEFT]:
            if self.lastKeyInput != 'right':
                self.xMovement, self.yMovement = -1, 0
                self.lastKeyInput = 'left'
        elif keys[pygame.K_UP]:
            if self.lastKeyInput != 'down':
                self.xMovement, self.yMovement = 0, -1
                self.lastKeyInput = 'up'
        elif keys[pygame.K_DOWN]:
            if self.lastKeyInput != 'up':
                self.xMovement, self.yMovement = 0, 1
                self.lastKeyInput = 'down'
        headCoord = (self.coordList[-1][0]+self.xMovement, self.coordList[-1][1]+self.yMovement)
        
        #gets rid of last value and appends new head
        if self.eaten == False: self.coordList = self.coordList[1:]
        if self.eaten == True: self.eaten = False
        self.coordList.append(headCoord)                        


    def collisionWBody(self):
        global gameActive, CELL_QUANTITY
        for coord in self.coordList:
            if self.coordList.count(coord) > 1:
                self.dead_sound.play()
                gameActive = False
            x,y = coord
            if (x<0 or x>CELL_QUANTITY) or (y<0 or y>CELL_QUANTITY):
                self.dead_sound.play()
                gameActive = False
        

    def winning(self):
        global winning, gameActive, CELL_QUANTITY
        if len(self.coordList) >= CELL_QUANTITY * CELL_QUANTITY:
            winning = True
            self.win_sound.play()
            gameActive = False
            
    def update(self):
        self.winning()
        self.collisionWBody()
        self.display_blocks()


class Controller:
    def __init__(self, snake, fruit):
        self.eaten = False
        self.apple_sound = pygame.mixer.Sound('audio/apple.wav')
        self.apple_sound.set_volume(3)

    #check if the fruit coords equals to the head coords
    def collision(self):
        global score, score_surf
        if (fruit.x_pos,fruit.y_pos) == snake.coordList[-1]:
            self.apple_sound.play()
            self.eaten = True
            
        if self.eaten == True:
            snake.eaten = True
            score += 1
            #the fruit respawns to a new coord
            fruit.generate_position()
            self.eaten = False
            score_surf = my_font.render(f'score:{score}', False, (255, 0, 0))
        
       
    def update(self):
        self.collision()

        
#custom events
moving_snake_timer = pygame.USEREVENT + 1
pygame.time.set_timer(moving_snake_timer, 100)

snake = Snake()
fruit = Fruit(snake)
controller = Controller(snake, fruit)

scoreList = list()
#if gameActive:
bgm.play(loops=-1)
played = False   
while True:   
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            with open('scores.txt', 'a') as file:
                file.write(f'{str(max(scoreList))} \n')
            pygame.quit()
            sys.exit()
        
        if event.type == moving_snake_timer:
            snake.moving_blocks()
            print(len(snake.coordList))
        if gameActive == False:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    #activate game, place fruit
                    gameActive = True
                    played = True
                    score = 0
                    if winning: winning=False
                    score_surf = my_font.render(f'score:{score}', False, (255, 0, 0))
                    fruit.generate_position()

    if gameActive:
        screen.fill((0,128,0))
        fruit.update()
        snake.update()
        controller.update()

        for i in range(1,30):
            pos = i*30
            pygame.draw.line(screen, (0,0,0), (pos, 0), (pos, CELL_SIZE*CELL_QUANTITY))
            pygame.draw.line(screen, (0,0,0), (0, pos), (CELL_SIZE*CELL_QUANTITY, pos))

        screen.blit(score_surf, (50, 50))
        
    else: 
        screen.fill((0,0,128))
        screen.blit(score_surf, (50, 50))
        
        if winning: screen.blit(win_surf, (400,400))
        elif winning == False and played: screen.blit(lose_surf, (400,400))
        
        snake.coordList = [(0,int(CELL_QUANTITY/2)),(1,int(CELL_QUANTITY/2)),(2,int(CELL_QUANTITY/2))]
        snake.lastKeyInput = 'right'
        snake.xMovement, snake.yMovement = 1,0
        scoreList.append(score)
        
        
        
    pygame.display.update()
    clock.tick(60)
