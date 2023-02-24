import pygame as pg

from FixRawInput.Controller import Controller

pg.init()

clock = pg.time.Clock()
screen = pg.display.set_mode([1000, 1000])

controller = Controller(screen, ("swe", "spa"))

running = True
while running:
    events = pg.event.get()

    for event in events:
        if event.type == pg.QUIT:
            running = False

    # import cProfile
    # import pstats
    #
    # with cProfile.Profile() as pr:
    #     handler.compute_frame(events)
    #
    # stats = pstats.Stats(pr)
    # stats.sort_stats(pstats.SortKey.TIME)
    # stats.print_stats()

    controller.compute_frame(events)

    clock.tick(60)
