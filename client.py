import sys
import socket
import pygame
import pygame.draw
import pygame.time
import pygame.font
import pygame.event
import pygame.display
import pygame.transform
import ctypes
import numpy
import numpy.linalg
import sys
from constants import (DISPX, DISPY, BWIDTH, PWIDTH, PHEIGHT, BALL_ACCELERATION, BALL_INIT_VEL, FPS, HEADER, STEP_BACKER)

IPPORT = input('ip:port = ').split(':')
IP = IPPORT[0]
PORT = int(IPPORT[1])

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((IP,PORT))

pygame.init()
ctypes.windll.user32.SetProcessDPIAware()

game_running = True
ball_vel = numpy.array([BALL_INIT_VEL, 0])
score = [0, 0]

display: pygame.Surface = pygame.Surface((DISPX, DISPY))
screen: pygame.Surface = pygame.display.set_mode((640, 360), pygame.SCALED + pygame.RESIZABLE)
ball: pygame.Rect = pygame.Rect(DISPX // 2, (DISPY - BWIDTH) // 2, BWIDTH, BWIDTH)
numpy_ball = numpy.array([ball.centerx, ball.centery]).astype('float64')
pong_1: pygame.Rect = pygame.Rect(20, (DISPY - BWIDTH) // 2, PWIDTH, PHEIGHT)
pong_2: pygame.Rect = pygame.Rect(DISPX - 20 - PWIDTH, (DISPY - BWIDTH) // 2, PWIDTH, PHEIGHT)
font: pygame.font.Font = pygame.font.SysFont('consolas',40)
pygame.display.set_caption('pong client')

def send_message(message: str) -> None:
    message = message
    message = message.encode('utf-8')
    message_header = f"{len(message):<{HEADER}}".encode('utf-8')
    client.send(message_header+message)

def recv_msg(client: socket.socket):
    try:
        msg_header = client.recv(HEADER)
        if not len(msg_header):
            return False
        msg_len = int(msg_header.decode('utf-8').strip())
        return {'header':msg_header,
                'data':client.recv(msg_len)}
    except:
        return False


clock = pygame.time.Clock()

while True:
    clock.tick(FPS)

    mpos = list(pygame.mouse.get_pos())
    mpos[0] /= screen.get_size()[0] / display.get_size()[0]
    mpos[1] /= screen.get_size()[1] / display.get_size()[1]
    
    send_message(str(mpos[1]))
    
    msg = recv_msg(client)

    if not msg:
        print('lost connection to host')
        pygame.display.quit()
        pygame.quit()
        quit()
    
    message = msg['data'].decode('utf-8')
    message = message.split('|')

    pong_1.centery = min(max(round(PHEIGHT / 2), round(float(message[0]))), round(DISPY - PHEIGHT / 2))
    pong_2.centery = min(max(round(PHEIGHT / 2), round(mpos[1])), round(DISPY - PHEIGHT / 2))
    ball.centerx = float(message[1])
    ball.centery = float(message[2])
    ball_vel[0] = round(float(message[3]))
    ball_vel[1] = round(float(message[4]))
    score[0] = round(float(message[5]))
    score[1] = round(float(message[6]))
    
    numpy_ball += (1 / FPS) * ball_vel
    speed: float = numpy.linalg.norm(ball_vel)

    if (ball.colliderect(pong_1)):
        ball_vel = numpy.array(numpy_ball)-numpy.array(pong_1.center) + numpy.array([STEP_BACKER, 1])
        ball_vel = ball_vel / numpy.linalg.norm(ball_vel) * speed * (1 + BALL_ACCELERATION)
        ball.left = pong_1.right
    
    elif (ball.colliderect(pong_2)):
        ball_vel = numpy.array(numpy_ball)-numpy.array(pong_2.center) + numpy.array([-STEP_BACKER, 1])
        ball_vel = ball_vel / numpy.linalg.norm(ball_vel) * speed * (1 + BALL_ACCELERATION)
        ball.right = pong_2.left
    
    if numpy_ball[0] < 0:
        numpy_ball = numpy.array([DISPX / 2, DISPY / 2]).astype('float64')
        ball_vel = numpy.array([200, 0])
        score[1] += 1

    elif numpy_ball[0] > DISPX:
        numpy_ball = numpy.array([DISPX / 2, DISPY / 2]).astype('float64')
        ball_vel = numpy.array([-200, 0])
        score[0] += 1
    
    ball.center = numpy_ball

    if (ball.top < 0) or (ball.bottom > DISPY):
        if ball.top < 0:
            ball.top = 0
        else:
            ball.bottom = DISPY
        numpy_ball = numpy_ball = numpy.array([ball.centerx, ball.centery]).astype('float64')
        ball_vel[1] *= -1
    
    score_text = font.render(' : '.join(list(map(str, score))), 1, (255, 255, 255))
    
    display.fill((0, 0, 0))
    pygame.draw.rect(display, (255, 255 ,255), pong_1)
    pygame.draw.rect(display, (255, 255 ,255), pong_2)
    pygame.draw.rect(display, (255, 255 ,255), ball)
    display.blit(score_text, ((DISPX - score_text.get_width()) // 2, 10))
    screen.blit(pygame.transform.scale(display, screen.get_size()), (0, 0))
    pygame.display.update()
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.display.quit()
            quit()
            sys.quit()
            raise Exception()
            break