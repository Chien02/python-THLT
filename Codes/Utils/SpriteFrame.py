import pygame

class SpriteFrames:
    def __init__(self):
        self.animations = {}
        self.current_anim = None
        self.current_frame = 0
        self.timer = 0

    def add_animation(self, name, frames, frame_duration=0.1):
        self.animations[name] = {
            "frames": frames,
            "frame_duration": frame_duration
        }

    def play(self, name):
        if name != self.current_anim:
            self.current_anim = name
            self.current_frame = 0
            self.timer = 0

    def update(self, delta_time):
        if self.current_anim is None:
            return
        anim = self.animations[self.current_anim]
        self.timer += delta_time
        if self.timer >= anim["frame_duration"]:
            self.timer = 0
            self.current_frame = (self.current_frame + 1) % len(anim["frames"])

    def get_current_frame(self):
        if self.current_anim is None:
            return None
        return self.animations[self.current_anim]["frames"][self.current_frame]

# frames_idle = load_frames_from_folder("Assets/Images/Characters/Machine/Idle")
# frames_run = load_frames_from_folder("Assets/Images/Characters/Machine/Run")

# sprite = SpriteFrames()
# sprite.add_animation("idle", frames_idle, 0.2)
# sprite.add_animation("run", frames_run, 0.1)

# sprite.play("idle")

# # Trong game loop:
# sprite.update(delta_time)
# screen.blit(sprite.get_current_frame(), (x, y))

