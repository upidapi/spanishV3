import pygame as pg

pg.init()

screen = pg.display.set_mode([500, 500])
cont = Controller(screen)

for x in range(10):
    Entry(cont, str(x), (10, x*50))

clock = pg.time.Clock()

running = True
while running:

    for event in pg.event.get():
        cont.handle_event(event)
        if event.type == pg.QUIT:
            running = False

    screen.fill((255, 255, 255))
    cont.draw()

    pg.display.flip()
    clock.tick(60)

pg.quit()
