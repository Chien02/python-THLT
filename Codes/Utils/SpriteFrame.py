import pygame

class SpriteFrames:
    def __init__(self):
        self.animations = {}
        self.current_anim = None
        self.current_frame = 0
        self.timer = 0
        self.default_animation = None
        self.loop = True
        self.animation_finished = False

    def set_default_animation(self, name):
        if not self.animations:
            return

        # Auto set 'idle' as default if exists
        if name is None and "idle" in self.animations:
            self.default_animation = "idle"
            return
        if name in self.animations:
            self.default_animation = name
    
    def add_animation(self, name, frames, frame_duration=0.1):
        self.animations[name] = {
            "frames": frames,
            "frame_duration": frame_duration
        }

    def play(self, name, loop=True):
        if name != self.current_anim:
            self.current_anim = name
            self.current_frame = 0
            self.timer = 0
            self.loop = loop
            self.animation_finished = False # Reset flag

    def update(self, delta_time):
        if self.current_anim is None:
            return
        anim = self.animations[self.current_anim]
        self.timer += delta_time
        if self.timer >= anim["frame_duration"]:
            self.timer = 0

            if self.loop:
                # vòng lặp bình thường
                self.current_frame = (self.current_frame + 1) % len(anim["frames"])
            else:
                # animation chỉ chạy 1 lần
                if self.current_frame < len(anim["frames"]) - 1:
                    self.current_frame += 1
                else:
                    # Đã tới frame cuối -> đánh dấu finished
                    self.animation_finished = True
                    # KHÔNG gọi self.play(default) ở đây để tránh reset flag;
                    # Việc chuyển về default nên do caller (ví dụ Machine hoặc Scene) quyết định.


    def get_current_frame(self):
        if self.current_anim is None:
            return None
        return self.animations[self.current_anim]["frames"][self.current_frame]

    def get_current_animation(self):
        return self.current_anim

    def is_finished(self):
        """ Kiểm tra animation đã xong chưa"""
        return self.animation_finished

