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

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

IP = socket.gethostname()
PORT = int(input('port:'))

server.bind((socket.gethostname(),PORT))

server.listen()

socket_list = [server]

input('Server initiated ... Press enter to reveal local ip address and port')

print(socket.gethostbyname(socket.gethostname()) + ':' + str(PORT))

print('Waiting for player 2 ...')

client, client_address = server.accept()

print('Player 2 has joined')

pygame.init()
ctypes.windll.user32.SetProcessDPIAware()

dispx, dispy = 640, 360
bwidth = dispy // 15
pwidth = bwidth // 4
pheight = dispy // 4
player_2 = client
player_2_client_address = client_address
player_2_y = dispy // 2
game_running = True
ball_vel = numpy.array([200, 0])
ball_acceleration = 0.05
score = [0, 0]

display = pygame.Surface((dispx, dispy))
screen = pygame.display.set_mode((640, 360), pygame.SCALED + pygame.RESIZABLE)
ball = pygame.Rect(dispx // 2, (dispy - bwidth) // 2, bwidth, bwidth)
pong_1 = pygame.Rect(20, (dispy - bwidth) // 2, pwidth, pheight)
pong_2 = pygame.Rect(dispx - 20 - pwidth, (dispy - bwidth) // 2, pwidth, pheight)
font = pygame.font.SysFont('consolas',40)
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

delta = 1 / 60
last_delta_time = time.perf_counter()

while 1:
    delta = time.perf_counter() - last_delta_time
    last_delta_time = time.perf_counter()
    mpos = list(pygame.mouse.get_pos())
    mpos[0] /= screen.get_size()[0] / display.get_size()[0]
    mpos[1] /= screen.get_size()[1] / display.get_size()[1]
    msg = recv_msg(player_2)

    if msg is False:
        pygame.display.quit()

        print('Player 2 has left\nwaiting for connections ...')

        client, client_address = server.accept()

        print('Player 2 has joined')

        player_2 = client
        player_2_client_address = client_address
        player_2_y = round(dispy // 2)
        game_running = True
        ball_vel = numpy.array([200, 0])
        ball_acceleration = 0.05
        score = [0, 0]
        display = pygame.Surface((dispx, dispy))
        screen = pygame.display.set_mode((640, 360), pygame.SCALED + pygame.RESIZABLE)
        ball = pygame.Rect(dispx // 2, (dispy - bwidth) // 2, bwidth, bwidth)
        pong_1 = pygame.Rect(20, (dispy - bwidth) // 2, pwidth, pheight)
        pong_2 = pygame.Rect(dispx - 20 - pwidth, (dispy - bwidth) // 2, pwidth, pheight)
        pygame.display.set_caption('pong server')

        continue

    player_2_y = min(max(0, round(float(msg['data'].decode('utf-8')))), dispy)
    message = '|'.join(list(map(str,(mpos[1],ball.centerx,ball.centery,ball_vel[0],ball_vel[1],score[0],score[1]))))
    message = message.encode('utf-8')
    message_header = f'{len(message):<{HEADER}}'.encode('utf-8')
    player_2.send(message_header + message)

    if game_running:
        pong_2.centery = player_2_y
        pong_1.centery = mpos[1]
        ball_vel = numpy.round(ball_vel)
        ball.center += delta * ball_vel
        speed: float = numpy.linalg.norm(ball_vel)

        if (ball.colliderect(pong_1)):
            ball_vel = numpy.array(ball.center) - numpy.array(pong_1.center) + numpy.array([60,1])
            ball_vel = ball_vel / numpy.linalg.norm(ball_vel) * (speed + ball_acceleration)
            ball.left = pong_1.right
        
        elif (ball.colliderect(pong_2)):
            ball_vel = numpy.array(ball.center) - numpy.array(pong_2.center)+numpy.array([-60,1])
            ball_vel = ball_vel / numpy.linalg.norm(ball_vel) * (speed + ball_acceleration)
            ball.right = pong_2.left
        
        if ball.centerx < 0:
            ball.center = (dispx / 2, dispy / 2)
            ball_vel = numpy.array([200, 0])
            score[1] += 1

        elif ball.centerx > dispx:
            ball.center = (dispx / 2, dispy / 2)
            ball_vel = numpy.array([-200, 0])
            score[0] += 1
        
        if (ball.top < 0) or (ball.bottom > dispy):
            if ball.top < 0:
                ball.top = 0
            else:
                ball.bottom = dispy
            ball_vel *= numpy.array([1, -1])
    
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
            print('exitting ...')
            run = False
            pygame.display.quit()
            quit()
            import sys
            sys.quit()
            raise Exception()
            break