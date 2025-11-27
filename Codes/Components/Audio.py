import pygame

from Codes.Components.AudioManager import *

class Audio():
    def __init__(self):
        self.audio_manager = AudioManager()
        self.current_music_stream : AudioStreamPlayer = None
        
        # Tạo audio streams
        # region BGM
        self.bgm_menu = self.audio_manager.create_audio_stream(
            "Assets/Audio/BGM/menu.ogg",
            AudioType.MUSIC,
            loop=True
        )

        self.bgm_main_game = self.audio_manager.create_audio_stream(
            "Assets/Audio/BGM/main_game.ogg",
            AudioType.MUSIC,
            loop=True
        )

        self.bgm_highscore = self.audio_manager.create_audio_stream(
            "Assets/Audio/BGM/highscore.ogg",
            AudioType.MUSIC,
            loop=True
        )

        self.bgm_gameover = self.audio_manager.create_audio_stream(
            "Assets/Audio/BGM/game_over.ogg",
            AudioType.MUSIC,
            loop=True
        )
        # endregion
        
        # region SFX
        self.sfx_button_press = self.audio_manager.create_audio_stream(
            "Assets/Audio/SFX/button_press.wav",
            AudioType.SFX
        )

        self.sfx_click = self.audio_manager.create_audio_stream(
            "Assets/Audio/SFX/click.wav",
            AudioType.SFX
        )

        self.sfx_collect = self.audio_manager.create_audio_stream(
            "Assets/Audio/SFX/collect.mp3",
            AudioType.SFX
        )

        self.sfx_click_state = self.audio_manager.create_audio_stream(
            "Assets/Audio/SFX/click_state.mp3",
            AudioType.SFX
        )

        self.sfx_drag = self.audio_manager.create_audio_stream(
            "Assets/Audio/SFX/drag.wav",
            AudioType.SFX
        )

        self.sfx_drop= self.audio_manager.create_audio_stream(
            "Assets/Audio/SFX/drop.wav",
            AudioType.SFX
        )

        self.sfx_gameover = self.audio_manager.create_audio_stream(
            "Assets/Audio/SFX/gameover.wav",
            AudioType.SFX
        )

        self.sfx_highscore = self.audio_manager.create_audio_stream(
            "Assets/Audio/SFX/highscore.mp3",
            AudioType.SFX
        )

        self.sfx_state_wrong = self.audio_manager.create_audio_stream(
            "Assets/Audio/SFX/wrong.wav",
            AudioType.SFX
        )

        self.sfx_hurt = self.audio_manager.create_audio_stream(
            "Assets/Audio/SFX/hurt.wav",
            AudioType.SFX
        )
        # endregion

    def play_bgm(self, music_name):
        match music_name:
            case 'menu': self.play_music(self.bgm_menu)
            case 'main_game': self.play_music(self.bgm_main_game)
            case 'highscore': self.play_music(self.bgm_highscore)
            case 'gameover': self.play_music(self.bgm_gameover)

    def play_sfx(self, sound_name):
        match sound_name:
            case 'click': self.play_sound(self.sfx_click)
            case 'click_state': self.play_sound(self.sfx_click_state)
            case 'wrong_state': self.play_sound(self.sfx_state_wrong)
            case 'highscore': self.play_sound(self.sfx_highscore)
            case 'gameover': self.play_sound(self.sfx_gameover)
            case 'drag': self.play_sound(self.sfx_drag)
            case 'drop': self.play_sound(self.sfx_drop)
            case 'collect': self.play_sound(self.sfx_collect)
            case 'button_press': self.play_sound(self.sfx_button_press)
            case 'hurt': self.play_sound(self.sfx_hurt)

    def stop_music(self, music_name):
        match music_name:
            case 'menu': self.stop(self.bgm_menu)
            case 'main_game': self.stop(self.bgm_main_game)
            case 'highscore': self.stop(self.bgm_highscore)
            case 'gameover': self.stop(self.bgm_gameover)
        
    def play_music(self, audio_stream: AudioStreamPlayer):
        """
        Phát nhạc nền - dừng nhạc cũ trước, rồi phát nhạc mới
        """
        # Nếu là nhạc khác, dừng nhạc cũ
        if self.current_music_stream != audio_stream:
            if self.current_music_stream:
                self.current_music_stream.stop()
            
            # Phát nhạc mới
            self.current_music_stream = audio_stream
            if audio_stream:
                audio_stream.play()

    def play_sound(self, audio_stream: AudioStreamPlayer):
        if audio_stream:
            audio_stream.play()
    
    def stop(self, audio_stream: AudioStreamPlayer):
        if audio_stream:
            audio_stream.stop()
        
