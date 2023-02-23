import pygame as pg

from FixRawInput.V2.Entry import Entry
from FixRawInput.V2.Handler import Handler

pg.init()

clock = pg.time.Clock()
screen = pg.display.set_mode([1000, 1000])

handler = Handler(screen, ("swe", "spa"))

# abc = "abcdefghijklmnop"
# for x in range(10):
#     Entry(handler.controller,
#           text=str(x),
#           o_text=abc[x],
#           pos=(10, x*50))

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

    handler.compute_frame(events)

    clock.tick(60)
