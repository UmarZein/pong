import socket
import pygame
import pygame.draw
import pygame.font
import pygame.time
import pygame.event
import pygame.display
import pygame.transform
import ctypes
import numpy
import numpy.linalg
import sys
from constants import (DISPX, DISPY, BWIDTH, PWIDTH, PHEIGHT, BALL_ACCELERATION, BALL_INIT_VEL, FPS, HEADER, STEP_BACKER)


server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

IP = socket.gethostname()
PORT = int(input('port: '))

server.bind((socket.gethostname(),PORT))

server.listen()

socket_list = [server]

print('ip:port =',socket.gethostbyname(socket.gethostname()) + ':' + str(PORT))

client, client_address = server.accept()

pygame.init()
ctypes.windll.user32.SetProcessDPIAware()

player_2 = client
player_2_client_address = client_address
player_2_y = DISPY // 2
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
pygame.display.set_caption('pong server')

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
    msg = recv_msg(player_2)

    if msg is False:
        pygame.display.quit()

        client, client_address = server.accept()

        player_2: socket.socket = client
        player_2_client_address = client_address
        player_2_y: int = round(DISPY // 2)
        game_running: bool = True
        ball_vel: numpy.ndarray = numpy.array([200., 0.])
        score: list = [0, 0]
        display: pygame.Surface = pygame.Surface((DISPX, DISPY))
        screen: pygame.Surface = pygame.display.set_mode((640, 360), pygame.SCALED + pygame.RESIZABLE)
        ball: pygame.Rect = pygame.Rect(DISPX // 2, (DISPY - BWIDTH) // 2, BWIDTH, BWIDTH)
        pong_1: pygame.Rect = pygame.Rect(20, (DISPY - BWIDTH) // 2, PWIDTH, PHEIGHT)
        pong_2: pygame.Rect = pygame.Rect(DISPX - 20 - PWIDTH, (DISPY - BWIDTH) // 2, PWIDTH, PHEIGHT)
        pygame.display.set_caption('pong server')

        continue

    player_2_y: int = min(max(round(PHEIGHT / 2), round(float(msg['data'].decode('utf-8')))), round(DISPY - PHEIGHT / 2))
    message = '|'.join(list(map(str,(mpos[1], numpy_ball[0], numpy_ball[1], ball_vel[0], ball_vel[1], score[0], score[1]))))
    message = message.encode('utf-8')
    message_header = f'{len(message):<{HEADER}}'.encode('utf-8')
    player_2.send(message_header + message)

    if game_running:
        
        pong_2.centery = player_2_y
        pong_1.centery = min(max(round(PHEIGHT / 2), round(mpos[1])), round(DISPY - PHEIGHT / 2))
        ball_vel = numpy.round(ball_vel)
        numpy_ball += (1 / FPS) * ball_vel 
        ball.center = numpy_ball
        speed: float = numpy.linalg.norm(ball_vel)

        if (ball.colliderect(pong_1)):
            ball_vel = numpy.array(numpy_ball) - numpy.array(pong_1.center) + numpy.array([STEP_BACKER, 1])
            ball_vel = ball_vel / numpy.linalg.norm(ball_vel) * speed * (1 + BALL_ACCELERATION)
            ball.left = pong_1.right
        
        elif (ball.colliderect(pong_2)):
            ball_vel = numpy.array(numpy_ball) - numpy.array(pong_2.center) + numpy.array([-STEP_BACKER, 1])
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
        
        if (ball.top < 0) or (ball.bottom > DISPY):
            if ball.top < 0:
                ball.top = 1
                ball_vel[1] = abs(ball_vel[1])
            else:
                ball.bottom = DISPY - 1
                ball_vel[1] = -abs(ball_vel[1])
            numpy_ball = numpy_ball = numpy.array([ball.centerx, ball.centery]).astype('float64')
    
    score_text = font.render(' : '.join(list(map(str, score))), 1, (255, 255, 255))
    ball.center = numpy_ball

    screen.fill((20, 40, 20))
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
            pygame.quit()
            quit()
            sys.quit()
            raise Exception()
            break
            # "The-Super-Killer-Murderer-inator" ... this should be enough to take it down