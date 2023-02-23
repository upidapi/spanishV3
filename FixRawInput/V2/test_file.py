import pygame as pg

from FixRawInput.V2.Entry import Entry
from FixRawInput.V2.Handler import Handler

pg.init()

clock = pg.time.Clock()
screen = pg.display.set_mode([500, 500])

handler = Handler(screen, ("swe", "spa"))

for x in range(10):
    Entry(handler.controller, text=str(x), pos=(10, x*50))

while True:
    handler.next_frame()

    clock.tick(60)
