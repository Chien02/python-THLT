import pygame
from tweener import *

class TweenAnimation:
    def pop(self, start, end, duration):
        return Tween(
            begin=start,
            end=end,
            duration=duration,
            easing=Easing.BACK,
            easing_mode=EasingMode.OUT
        )