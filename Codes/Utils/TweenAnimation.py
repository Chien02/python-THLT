import pygame
from tweener import *

class TweenAnimation:
    RESET = 1.0
    def pop(self, start, end, duration):
        return Tween(
            begin=start,
            end=end,
            duration=duration,
            easing=Easing.BACK,
            easing_mode=EasingMode.OUT
        )

    def stretch(self, from_value, to_value, duration=250):
        return Tween(
            begin=from_value,
            end=to_value,  # phình ra hơn bình thường
            duration=duration, # milliseconds
            easing=Easing.ELASTIC,
            easing_mode=EasingMode.OUT
        )

    def reset_scale(self, from_value, to_value=RESET, duration=250):
        return Tween(
            begin=self.scale,
            end= to_value,  # trở về kích thước ban đầu
            duration=duration, # milliseconds
            easing=Easing.BACK,
            easing_mode=EasingMode.OUT
        )