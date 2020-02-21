import pygame
pygame.init()
from pybfcontrol import bf_button, bf_panel
screen = pygame.display.set_mode((320, 420))

def do_click1(btn):
    from main import run
    run(1)

def do_click2(btn):
    from main import run
    run(2)

def do_click3(btn):
    from main import run
    run(3)

panel = bf_panel.BFPanel()
btn1 = bf_button.BFButton(screen, (60, 60, 200, 40), text=u'诗句填空', click=do_click1)
btn2 = bf_button.BFButton(screen, (60, 140, 200, 40), text=u'成语填空', click=do_click2)
btn3 = bf_button.BFButton(screen, (60, 220, 200, 40), text=u'英语单词填空', click=do_click3)
panel.add_control(btn1)
panel.add_control(btn2)
panel.add_control(btn3)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        panel.update(event)

    screen.fill((255, 255, 255))
    panel.draw()

    pygame.display.update() 