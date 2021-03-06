from filelock import FileLock
from random import randint
from collections import *
import eztext
import pygame
import time
import sys
import os

position = 512,50
os.environ['SDL_VIDEO_WINDOW_POS'] = str(position[0]) + "," + str(position[1])
pygame.init()

screen = pygame.display.set_mode((900, 900))
clock = pygame.time.Clock()
font = pygame.font.SysFont("impact",50)
font2 = pygame.font.SysFont("impact", 30)
x = 500
y = 876
squares = []
user = ''
score = 0
multiplier = 1
multi_count = 0
line_count = 0
shield = False
drop_speed = 5
drop_bool = False
lines_up = False


def highscores():
    global screen, font2, score, user

    screen.fill((0,0,0))
    
    with FileLock('//tester-hist-203/TD/_Associates/Alex/Dodge/highscores.txt'):
        with open('//tester-hist-203/TD/_Associates/Alex/Dodge/highscores.txt', 'r+') as f:
            
            d = defaultdict(list)
            scores = []
            if os.stat('//tester-hist-203/TD/_Associates/Alex/Dodge/highscores.txt').st_size != 0:   
                scores, d = get_scores(f,d, scores)
                
            if len(scores) == 0 or score > scores[-1]:
                txt = 'New High Score! ' + str(score)
                print(txt)
                txt = font2.render(txt, True, (255,255,255))
                screen.blit(txt,(450 - txt.get_width()//2, 256))
            else:
                txt = 'Score: ' + str(score)
                print(txt)
                txt = font2.render(txt, True, (255,255,255))
                screen.blit(txt,(450 - txt.get_width()//2, 256))
            scores.append(score)
            d[score].append(user)    
            scores.sort()        

            if len(scores) > 10:
                del d[scores[0]]
                del scores[0]
            
            f.seek(0)
            f.truncate()
            count = 0
            d = OrderedDict(sorted(d.items(), reverse = True))
            for k,v in d.items():
                for i in v:
                    count += 30
                    s = i + ' ' + str(k)
                    txt = "{:10}{:6}".format(i, k)
                    txt = font2.render(txt, True, (255,255,255))
                    screen.blit(txt,(390, 384+count))
                    f.write(s + '\n')
            pygame.display.flip()
    while 1:
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_RETURN] or pressed[pygame.K_ESCAPE] or pressed[pygame.K_SPACE]:
            return
        pygame.event.pump()

def get_scores(f,d,scores):
    for i in f:
        fuser, fscore = i.replace('\n','').split()
        fscore = int(fscore)
        d[fscore].append(fuser)
        scores.append(fscore)
    scores.sort()
    return scores, d

def move_right(pressed):
    global x
    if pressed[pygame.K_LEFT] and x-3 > -3: x -= 3

def move_left(pressed):
    global x
    if pressed[pygame.K_RIGHT] and x+3 < 879: x += 3

def intersect(fsquare):
    global x, y, drop_bool, drop_speed, multi_count, multiplier, line_count, lines_up, shield
    cx = x+12
    cy = y+12
    
    if abs(fsquare[0]+6-cx) < 18 and abs(fsquare[1]+6-cy) < 18:
        if fsquare[2] == 1:
            drop_bool = True
            drop_speed = 7
            return 1
        elif fsquare[2] == 2:
            multi_count += 500
            if multiplier == 1:
                multiplier += 1    
            else:
                multiplier += 2
            return 1
        elif fsquare[2] == 3:        
            line_count = 0
            lines_up = True
            return 1
        elif fsquare[2] == 4:
            shield = True
            return 1
        else:
            if shield:
                shield = False
                return 1
            else:
                return 2
    return 0 
        
def drop():
    global screen, lines_up, squares
    colors = [(255,255,102),(255,204,102),(255,153,0)]
    c = randint(0,900)
    fill = 1    #1 is hollow -1 is filled

    #Determines type of block to fall
    if c%75 == 0:
        typ = 4
        color = (255,255,0)
        fill = 0
        
    elif c%50 == 0:   #Speed up
        typ = 1
        color = (255,0,0)
        fill = 0
        
    elif c%30 == 0: #2x Points
        typ = 2
        color = (255,255,255)
        
    elif c%20 == 0: #Lines
        typ = 3
        color = (61,236,232)
        
    else: #Normal
        typ = 0
        color = (255,0,255)
        
    pygame.draw.rect(screen,color,pygame.Rect(c-6,0,12,12),fill)
    if lines_up == True:
        pygame.draw.aaline(screen,color,(x+12,y+12),(c+6,6))    
    squares.append([c-6,0,typ,color,fill])

def fall():
    global screen, x,y, squares, lines_up, score, multiplier, drop_speed
    color = (255,0,255)
    count = 0
    for i in xrange(len(squares)):
        i = i-count
        r = intersect(squares[i])

        if r == 2:  #intersected and died
            squares = []
            highscores()
            return True
            
        elif r == 1 or squares[i][1] >= 900:    #intersected a bonus/ purple block went off screen/ purple block intersected with shield
            count += 1
            score += (1*multiplier)
            del squares[i]
            
        else:
            squares[i][1] += drop_speed + int(score/200)
            color = squares[i][3]
            fill = squares[i][4]
            pygame.draw.rect(screen,color,pygame.Rect(squares[i][0],squares[i][1],12,12),fill)
            if lines_up:
                pygame.draw.aaline(screen,color,(x+12,y+12),(squares[i][0]+6,squares[i][1]+6))

    return False

def bonus():
    global screen, multiplier, multi_count, line_count, lines_up, drop_count, drop_speed, score, drop_bool, shield

    if multiplier != 1:
        pygame.draw.rect(screen,(255,255,255),pygame.Rect(0,30,40,10))
        multi_count -= 1
        if multi_count%500 == 0:
            multiplier -= 2
            multi_count = 0
            
        if multiplier < 1:
            multiplier = 1
    if lines_up:
        pygame.draw.rect(screen,(61,236,232),pygame.Rect(50,30,40,10))
        line_count += 1
        if line_count >= 750:
            lines_up = False

    if drop_bool:
        drop_speed = 7
        pygame.draw.rect(screen,(255,0,0),pygame.Rect(100,30,40,10))
        drop_count += 1
        if drop_count >= 500:
            drop_bool = False
            drop_count = 0
            drop_speed = 5
            
    if shield:
        pygame.draw.rect(screen,(255,255,0),pygame.Rect(150,30,40,10))

def get_user():
    global user
    screen.fill((0,0,0))
    entry = False
    txtbx = eztext.Input(x=350, y=450, font=font, maxlength=45, color=(255,255,255), prompt='User: ')
    while 1:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.display.quit()
                sys.exit(1)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
               return True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return False
            
        screen.fill((0,0,0))
        if entry:
            user = txtbx.update(events)
        entry = True
        txtbx.draw(screen)
        pygame.display.flip()
        
    return False
def start():
    global screen, font2, x, y, squares, score, multiplier, multi_count, line_count, lines_up, drop_speed, drop_count, user, drop_bool, shield

    squares = []
    x = 500
    y = 876 
    score = 0
    multiplier = 1
    multi_count = 0
    line_count = 0
    lines_up = False
    drop_speed = 5
    drop_count = 0
    drop_bool = False
    frequency = 0
    if user == '':
        if get_user():
            main()

    while 1:
        screen.fill((0,0,0))            
        pressed = pygame.key.get_pressed()

        move_right(pressed)
        move_left(pressed)
        if pressed[pygame.K_ESCAPE]:
            screen.fill((0,0,0))
            break
        pygame.event.pump()
        text = font2.render("Score: " + str(score), True, (255,255,255))
        screen.blit(text,(0,-5))
        bonus()
        if fall():
            screen.fill((0,0,0))
            break
        
        if not frequency:
            drop()
        elif frequency >= (5-int(score/500)):
            frequency = -1
        frequency += 1

        if shield:
            pygame.draw.rect(screen, (255,255,0), pygame.Rect(x,y,24,24))
        else:
            pygame.draw.rect(screen, (0,255,0), pygame.Rect(x,y,24,24))
        pygame.display.flip()
        clock.tick(60)
    return        
        
def main():
    global x, y, screen, clock, font
    
    while 1:
        screen.fill((0,0,0))
        text = font.render("Start(y/n)", True, (255,255,255))
        screen.blit(text, (450 - text.get_width() // 2, 450 - text.get_height() // 2))
        pygame.display.flip()
        
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_y]:
            start()
        elif pressed[pygame.K_n]:
            pygame.display.quit()
            sys.exit(1)
        pygame.event.pump()

if __name__ == "__main__":
    main()
