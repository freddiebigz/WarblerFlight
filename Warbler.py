import pygame
from pygame.locals import *
import cv2
import HandTracking as ht
import random

pygame.init()

CLOCK = pygame.time.Clock()
FPS = 60

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 900

#Game Variables
floor_scroll = 0
scroll_speed = 4
floating = False
game_over = False
wall_space = 200
wall_frequency = 10000
last_wall = pygame.time.get_ticks() - wall_frequency
score = 0
passed_wall = False
font = pygame.font.SysFont('Comic Sans', 60)
score_color = (255, 255, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Warbler Flight')

#Load Images
BACKGROUND = pygame.image.load('img\CaveBackground.png')
FLOOR = pygame.image.load('img\CaveFloor.png')
RESTART = pygame.image.load('img\Button.png')

#Load Sounds
JUMP_SFX = pygame.mixer.Sound('img\jump.wav')

#Draw Score
def draw_score(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

#Reset Game
def reset_game():
    wall_group.empty()
    WARBLER_CHAR.rect.x = 100
    WARBLER_CHAR.rect.y = int(SCREEN_HEIGHT / 2)
    score = 0
    return score

#Warbler Functions
class warbler(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'img\Warbler{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.velocity = 0
        self.jumped = False

    def update(self):
        if floating == True:
            self.velocity += 0.5
            if self.velocity > 8:
                self.velocity = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.velocity)
        if game_over == False:
            #Jump
            if total_fingers == 1 and self.jumped == False:
                JUMP_SFX.play()
                self.velocity = -7
                self.jumped = True
            if total_fingers == 0 and self.jumped == True:
                self.jumped = False


        #Update Animation
        self.counter += 1
        anim_cooldown = 5

        if self.counter > anim_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
        self.image = self.images[self.index]

class wall(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/wall.png')
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(wall_space / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(wall_space / 2)]

    def update(self):
        if game_over == False:
            self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

wall_group = pygame.sprite.Group()
warbler_group = pygame.sprite.Group()
WARBLER_CHAR = warbler(100, int(SCREEN_HEIGHT / 2))

warbler_group.add(WARBLER_CHAR)

button = Button(SCREEN_WIDTH / 2 - 50, SCREEN_HEIGHT / 2 - 100, RESTART)

cap = cv2.VideoCapture(0)
detector = ht.hand_detector(detection_con=0.75)
FINGER_TIPS = [4, 8, 12, 16, 20]
total_fingers = 0

#Update
run = True
while run:

    frame, img = cap.read()
    img = detector.find_hands(img)
    landmark_array = detector.find_pos(img, draw=False)

    CLOCK.tick(FPS)

    #Draw Background
    screen.blit(BACKGROUND, (0,0))
    screen.blit(FLOOR, (floor_scroll, 768))

    wall_group.draw(screen)
    wall_group.update()

    warbler_group.draw(screen)
    warbler_group.update()

    #Score
    if len(wall_group) > 0:
        if warbler_group.sprites()[0].rect.left > wall_group.sprites()[0].rect.left\
            and warbler_group.sprites()[0].rect.right < wall_group.sprites()[0].rect.right and passed_wall == False:
            passed_wall = True
        if passed_wall == True:
            if warbler_group.sprites()[0].rect.left > wall_group.sprites()[0].rect.right:
                score += 1
                passed_wall = False

    draw_score(str(score), font, score_color, int(SCREEN_WIDTH / 2), 20)

    #If Warbler hits a barrier
    if pygame.sprite.groupcollide(warbler_group, wall_group, False, False) or WARBLER_CHAR.rect.top < 0:
        game_over = True

    #Ground Collision
    if WARBLER_CHAR.rect.bottom >= 768:
        game_over = True
        floating = False

    if game_over == False and floating == True:
        #Spawn Walls
        wall_height = random.randint(-100,100)
        current_time = pygame.time.get_ticks()
        if current_time - last_wall > wall_frequency:
            BOTTOM_WALL = wall(SCREEN_WIDTH, int(SCREEN_HEIGHT / 2) + wall_height, -1)
            TOP_WALL = wall(SCREEN_WIDTH, int(SCREEN_HEIGHT / 2) + wall_height, 1)
            wall_group.add(BOTTOM_WALL)
            wall_group.add(TOP_WALL)
            last_wall = current_time

    if game_over == True:
        if button.draw() == True:
            game_over = False
            score = reset_game()

        #Scroll Ground
        floor_scroll -= scroll_speed
        if abs(floor_scroll) > 220:
            floor_scroll = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if len(landmark_array) != 0:
        fingers = []

        #Right Hand Thumb
        if landmark_array[FINGER_TIPS[0]][1] > landmark_array[FINGER_TIPS[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        #4 Fingers
        for id in range(1,5):
            if landmark_array[FINGER_TIPS[id]][2] < landmark_array[FINGER_TIPS[id]-2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        total_fingers = fingers.count(1)

        if total_fingers == 1 and floating == False and game_over == False:
            floating = True

        if game_over == True:
            if total_fingers == 3:
                game_over = False
                score = reset_game()

        print(total_fingers)

    pygame.display.update()
    cv2.waitKey(1)
pygame.quit()