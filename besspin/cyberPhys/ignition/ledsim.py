import pygame
import numpy as np
import cyberphyslib.demonstrator.leds as cled
import typing as typ


hack_names = ["nominal pattern",
              "ssith pattern",
              "steering hack pattern",
              "transmission hack pattern",
              "throttle hack pattern",
              "brake hack pattern",
              "all off",
              "all on"]
hack_default = hack_names[0]


class LedGame:
    BLACK = (0, 0, 0)
    MARGIN = 2
    HMARGIN = 30
    TMARGIN = 170
    WIDTH = 12
    HEIGHT = 12

    def __init__(self, lstrings: typ.Sequence[cled.LedString]):
        self._lstrings = lstrings
        self.nrows = len(self._lstrings)
        self.ncols = max([l.length for l in self._lstrings])
        self.hack_idx = 0

    def mainloop(self):
        # Initialize pygame
        pygame.init()

        self.font = pygame.font.Font(pygame.font.get_default_font(), 10)
        self.title_font = pygame.font.Font(pygame.font.get_default_font(), 24)
        WINDOW_SIZE = [(self.WIDTH + self.MARGIN) * self.ncols + self.TMARGIN + 5, max((self.HEIGHT + self.MARGIN) * self.nrows, 255) + self.HMARGIN + 5]
        screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("LedManagementSim")

        # Loop until the user clicks the close button.
        done = False

        # Used to manage how fast the screen updates
        clock = pygame.time.Clock()

        # -------- Main Program Loop -----------
        while not done:
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    done = True  # Flag that we are done so we exit this loop
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.hack_idx += 1
                        self.hack_idx %= len(hack_names)
                        for l in self._lstrings:
                            l.update_pattern(hack_names[self.hack_idx])
                    elif event.key == pygame.K_LEFT:
                        self.hack_idx -= 1
                        self.hack_idx %= len(hack_names)
                        for l in self._lstrings:
                            l.update_pattern(hack_names[self.hack_idx])

            screen.fill(self.BLACK)

            for row in range(self.nrows):
                for column in range(self.ncols):
                    color = tuple(self._lstrings[row].pixel_array[column])
                    pygame.draw.rect(screen,
                                     color,
                                     [(self.MARGIN + self.WIDTH) * column + self.MARGIN + self.TMARGIN,
                                      (self.MARGIN + self.HEIGHT) * row + self.MARGIN + self.HMARGIN,
                                      self.WIDTH,
                                      self.HEIGHT])
                text_surface = self.font.render(self._lstrings[row].name, True, (255, 255, 255))
                screen.blit(text_surface, dest=(0, (self.MARGIN + self.HEIGHT) * row + self.MARGIN + self.HMARGIN))
                title_text_surface = self.title_font.render(f"Mode: {hack_names[self.hack_idx]}", True, (255, 255, 255))
                screen.blit(title_text_surface, dest=(0, 0))

            clock.tick(30)

            for lstring in self._lstrings:
                lstring.update()

            pygame.display.flip()

        pygame.quit()


import pandas as pd
ledf = pd.read_csv("../cyberphyslib/cyberphyslib/demonstrator/utils/led_strings_comprehensive_tuple_colors.csv")
lstrings = []
for idx, row in ledf.iterrows():
    hd = {}
    for hack_name in hack_names:
        pat,  color = row[hack_name], eval(row[hack_name + " color"])
        assert len(color) == 3
        if pat == "off":
            pattern = cled.ConstantPattern((0, 0, 0))
        elif pat == "on":
            pattern = cled.ConstantPattern(color)
        elif pat == "ants":
            pattern = cled.AntsPattern(color, 4, False)
        elif pat == "ants_reverse":
            pattern = cled.AntsPattern(color, 4, True)
        elif pat == "pulse":
            pattern = cled.PulsePattern(color, 1.0, 10, 10)
        else:
            raise ValueError(f"invalid pattern {pat}")
        hd[hack_name] = pattern
    lstrings += [cled.LedString(row["name"], hd, hack_default, row["length"])]

game = LedGame(lstrings)
game.mainloop()

