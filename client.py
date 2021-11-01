import sys
import socket
import pygame
import pygame.draw
import pygame.font
import pygame.event
import pygame.display
import pygame.transform
import ctypes
import numpy
import numpy.linalg
import time

HEADER = 10
IPPORT = input('ip:port = ').split(':')
IP = IPPORT[0]
PORT = int(IPPORT[1])

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print(IP, PORT)
client.connect((IP,PORT))
#client.setblocking(False)#the recieve functionality wont be bolcking

pygame.init()
ctypes.windll.user32.SetProcessDPIAware()

dispx, dispy = 640, 360
bwidth = dispy // 15
pwidth = bwidth // 4
pheight = dispy // 4
game_running = True
ball_vel = numpy.array([200, 0])
ball_acceleration = 0.05
score = [0, 0]

display: pygame.Surface = pygame.Surface((dispx, dispy))
screen: pygame.display = pygame.display.set_mode((640, 360), pygame.SCALED + pygame.RESIZABLE)
ball: pygame.Rect = pygame.Rect(dispx // 2, (dispy - bwidth) // 2, bwidth, bwidth)
pong_1: pygame.Rect = pygame.Rect(20, (dispy - bwidth) // 2, pwidth, pheight)
pong_2: pygame.Rect = pygame.Rect(dispx - 20 - pwidth, (dispy - bwidth) // 2, pwidth, pheight)
font: pygame.font.Font  = pygame.font.SysFont('consolas',40)
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


delta = 1 / 60
last_delta_time = time.perf_counter()

while 1:
    
    delta = time.perf_counter() - last_delta_time
    last_delta_time = time.perf_counter()

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
    # expecting: ball pos + vel + pong1 pos
    message = msg['data'].decode('utf-8')
    message = message.split('|')#[mpos[1], ball x, ball y, ball vel x, ball vel y]
    pong_1.centery = round(float(message[0]))
    pong_2.centery = round(mpos[1])
    ball.centerx = round(float(message[1]))
    ball.centery = round(float(message[2]))
    ball_vel[0] = round(float(message[3]))
    ball_vel[1] = round(float(message[4]))
    score[0] = round(float(message[5]))
    score[1] = round(float(message[6]))
    
    ball.center += delta * ball_vel
    speed: float = numpy.linalg.norm(ball_vel)

    if (ball.colliderect(pong_1)):
        ball_vel = numpy.array(ball.center)-numpy.array(pong_1.center) + numpy.array([60, 1])
        ball_vel = ball_vel / numpy.linalg.norm(ball_vel) * (speed + ball_acceleration)
        ball.left = pong_1.right
    
    elif (ball.colliderect(pong_2)):
        ball_vel = numpy.array(ball.center)-numpy.array(pong_2.center) + numpy.array([-60, 1])
        ball_vel = ball_vel / numpy.linalg.norm(ball_vel) * (speed + ball_acceleration)
        ball.right = pong_2.left
    
    if ball.centerx < 0:
        ball.center = (dispx / 2, dispy / 2)
        ball_vel = numpy.array([200, 0])
        print('Player 2 scored !')
        score[1] += 1

    elif ball.centerx > dispx:
        ball.center = (dispx / 2, dispy / 2)
        ball_vel = numpy.array([-200, 0])
        print('Player 1 scored !')
        score[0] += 1
    
    if (ball.top < 0) or (ball.bottom > dispy):
        if ball.top < 0:
            ball.top = 0
        else:
            ball.bottom = dispy
        ball_vel *= numpy.array([1,-1])
    
    score_text = font.render(' : '.join(list(map(str, score))), 1, (255, 255, 255))
    
    display.fill((0, 0, 0))
    pygame.draw.rect(display, (255, 255 ,255), pong_1)
    pygame.draw.rect(display, (255, 255 ,255), pong_2)
    pygame.draw.rect(display, (255, 255 ,255), ball)
    display.blit(score_text, ((dispx - score_text.get_width()) // 2, 10))
    screen.blit(pygame.transform.scale(display, screen.get_size()), (0, 0))
    pygame.display.update()
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.display.quit()
            quit()
            import sys
            sys.quit()
            raise Exception()
            break