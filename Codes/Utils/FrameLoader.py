import os
import pygame

class FrameLoader:
    def load_frames_from_sheet(sheet_path, frame_width, frame_height, num_frames):
        sheet = pygame.image.load(sheet_path).convert_alpha()
        frames = []
        for i in range(num_frames):
            frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame_surface.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
            frames.append(frame_surface)
        return frames
    # Ví dụ: 4 frame, mỗi frame 64x64 px
    # frames = load_frames_from_sheet("Assets/Images/Characters/Machine/sheet.png", 64, 64, 4)

    def load_frames_from_folder(folder_path):
        frames = []
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith(".png"):
                image = pygame.image.load(os.path.join(folder_path, filename))
                frames.append(image)
        return frames

