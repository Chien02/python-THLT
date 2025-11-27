import pygame
import json
import os
from enum import Enum
from dataclasses import dataclass

class AudioType(Enum):
    MUSIC = 0
    SFX = 1
    MASTER = 2

@dataclass
class AudioStreamPlayer:
    """Tương tự AudioStreamPlayer của Godot"""
    bus: AudioType
    volume: float = 1.0
    pitch: float = 1.0
    is_playing: bool = False
    sound: pygame.mixer.Sound = None
    channel: pygame.mixer.Channel = None
    loop: bool = False
    
    def play(self):
        if self.sound and self.channel:
            self.channel.play(self.sound, loops=-1 if self.loop else 0)
            self.is_playing = True
    
    def stop(self):
        if self.channel:
            self.channel.stop()
            self.is_playing = False
    
    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))
        if self.channel:
            self.channel.set_volume(self.volume)

class AudioBus:
    """Bus âm thanh - quản lý nhóm âm thanh"""
    def __init__(self, name: str, volume: float = 1.0):
        self.name = name
        self.volume = volume
        self.players = []
    
    def set_volume(self, volume: float, master_volume: float = 1.0):
        """
        Đặt âm lượng cho bus
        MỚI: master_volume ảnh hưởng đến âm lượng cuối cùng
        """
        self.volume = max(0.0, min(1.0, volume))
        for player in self.players:
            if player.channel:
                # Âm lượng cuối = volume bus × master volume
                final_volume = player.volume * self.volume * master_volume
                player.channel.set_volume(final_volume)

class AudioManager:
    """Quản lý toàn bộ hệ thống âm thanh"""
    def __init__(self, config_path="settings.json"):
        pygame.mixer.init()
        
        # QUAN TRỌNG: Đặt đủ channels (1 cho BGM + nhiều cho SFX)
        pygame.mixer.set_num_channels(32)
        
        self.config_path = config_path
        self.buses = {
            AudioType.MASTER: AudioBus("Master", 1.0),
            AudioType.MUSIC: AudioBus("Music", 1.0),
            AudioType.SFX: AudioBus("SFX", 1.0),
        }
        
        # MỚI: Channels riêng cho BGM và SFX
        self.music_channel = pygame.mixer.Channel(0)  # Channel 0 dành riêng cho BGM
        self.sfx_channels = [pygame.mixer.Channel(i) for i in range(1, 32)]  # Channel 1-31 cho SFX
        self.current_sfx_channel_index = 0
        
        self.music_player = None
        self.effects = []
        self.load_settings()
    
    def create_audio_stream(self, filepath: str, audio_type: AudioType, 
                          loop: bool = False) -> AudioStreamPlayer:
        """Tạo một audio stream player"""
        try:
            sound = pygame.mixer.Sound(filepath)
            
            # MỚI: Gán channel theo loại âm thanh
            if audio_type == AudioType.MUSIC:
                channel = self.music_channel  # BGM luôn dùng channel 0
            else:
                # SFX dùng các channel khác, xoay vòng
                channel = self.sfx_channels[self.current_sfx_channel_index]
                self.current_sfx_channel_index = (self.current_sfx_channel_index + 1) % len(self.sfx_channels)
            
            player = AudioStreamPlayer(
                bus=audio_type,
                sound=sound,
                channel=channel,
                loop=loop
            )
            self.buses[audio_type].players.append(player)
            return player
        except Exception as e:
            print(f"Lỗi tải audio: {filepath} - {e}")
            return None
    
    def set_bus_volume(self, bus_type: AudioType, volume: float):
        """
        MỚI: Đặt âm lượng cho một bus
        Nếu là MASTER volume, ảnh hưởng đến MUSIC và SFX
        """
        if bus_type not in self.buses:
            return
        
        if bus_type == AudioType.MASTER:
            # Cập nhật master volume
            self.buses[AudioType.MASTER].volume = max(0.0, min(1.0, volume))
            master_vol = self.buses[AudioType.MASTER].volume
            
            # Áp dụng master volume cho MUSIC và SFX
            self.buses[AudioType.MUSIC].set_volume(
                self.buses[AudioType.MUSIC].volume,
                master_vol
            )
            self.buses[AudioType.SFX].set_volume(
                self.buses[AudioType.SFX].volume,
                master_vol
            )
        else:
            # Cập nhật volume của bus khác (MUSIC hoặc SFX)
            master_vol = self.buses[AudioType.MASTER].volume
            self.buses[bus_type].set_volume(volume, master_vol)
    
    def get_bus_volume(self, bus_type: AudioType) -> float:
        """Lấy âm lượng hiện tại của bus"""
        if bus_type in self.buses:
            return self.buses[bus_type].volume
        return 1.0
    
    def stop_all(self):
        """Dừng tất cả âm thanh"""
        pygame.mixer.stop()
        for players in [self.buses[t].players for t in self.buses]:
            for player in players:
                player.is_playing = False
    
    def save_settings(self):
        """Lưu settings vào file JSON"""
        settings = {
            "master_volume": self.buses[AudioType.MASTER].volume,
            "music_volume": self.buses[AudioType.MUSIC].volume,
            "sfx_volume": self.buses[AudioType.SFX].volume,
        }
        try:
            os.makedirs(os.path.dirname(self.config_path) or ".", exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(settings, f, indent=4)
            print(f"Settings đã lưu vào {self.config_path}")
        except Exception as e:
            print(f"Lỗi lưu settings: {e}")
    
    def load_settings(self):
        """Tải settings từ file JSON"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    settings = json.load(f)
                
                self.buses[AudioType.MASTER].volume = settings.get("master_volume", 1.0)
                self.buses[AudioType.MUSIC].volume = settings.get("music_volume", 1.0)
                self.buses[AudioType.SFX].volume = settings.get("sfx_volume", 1.0)
                print(f"Settings đã tải từ {self.config_path}")
            else:
                print(f"File {self.config_path} chưa tồn tại, sử dụng giá trị mặc định")
        except Exception as e:
            print(f"Lỗi tải settings: {e}")