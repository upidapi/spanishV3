import pygame as pg

from FixRawInput.V2.Entry import Entry
from FixRawInput.V2.Handler import Handler

pg.init()

clock = pg.time.Clock()
screen = pg.display.set_mode([500, 500])

handler = Handler(screen, ("swe", "spa"))

abc = "abcdefghijklmnop"
for x in range(10):
    Entry(handler.controller,
          text=str(x),
          o_text=abc[x],
          pos=(10, x*50))

running = True
while running:
    events = pg.event.get()

    for event in events:
        if event.type == pg.QUIT:
            running = False

    handler.compute_frame(events)

    clock.tick(60)
