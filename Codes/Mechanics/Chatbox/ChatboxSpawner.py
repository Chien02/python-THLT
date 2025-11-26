import pygame
import random
import string
from Codes.Mechanics.Chatbox.Chatbox import Chatbox
from Codes.Utils.FrameLoader import FrameLoader

class ChatboxSpawner:

    CHATBOX_STATE = ('idle', 'picked')
    def __init__(self, spawn_interval=4.0, chatbox_lifetime=5.0, machine_pos=None):
        """
        base_sprites: danh sách các sprite (ít nhất 3 loại)
        spawn_interval: thời gian giữa các lượt spawn
        chatbox_lifetime: thời gian tồn tại của mỗi chatbox
        """
        chatbox_size = (216, 216)
        self.base_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Elements/Chatbox/chatbox.png", chatbox_size[0], chatbox_size[1], 6)
        self.picked_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Elements/Chatbox/chatbox_picked.png", chatbox_size[0], chatbox_size[1], 6)
        self.holding_sprites = FrameLoader.load_frames_from_sheet("Assets/Images/Elements/Chatbox/chatbox_holding.png", chatbox_size[0], chatbox_size[1], 6)

        self.spawn_interval = spawn_interval
        self.chatbox_lifetime = chatbox_lifetime

        self.chatboxes: list[Chatbox] = []
        self.fixed_chatboxes = {} # {0: chatboxes[0], 1: chatboxes[1], ...}
        self.time_since_last_spawn = 0.0
        self.spawnable = True

        # Định nghĩa các tập ký tự
        self.letters = string.ascii_lowercase  # a-z
        self.digits = string.digits  # 0-9
        self.special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?/"
        
        # Tỉ lệ xuất hiện
        self.SPECIAL_CHAR_RATE = 0.05  # 5% có ký tự đặc biệt
        self.NUMBER_RATE = 0.10  # 10% có số
        self.LETTER_ONLY_RATE = 0.85  # 85% chỉ chữ cái

        # Kiểm tra input để điều khiển chatbox
        self.user_input = []
        self.machine_pos = machine_pos
        self.order_nums = {} # {'current_state': idle or picked or holding}

        # Nếu có chatbox đang di chuyển thì dừng đếm ngược của spawner
        # Tuy nhiên, khi mới bắt đầu thì entry timer sẽ được bật lên, trong thời gian này
        # spanwer phải dừng spawn
        self.sending_chatbox = False
        self.entry_time = self.spawn_interval
        self.entry_flag = True

    def _generate_random_text(self, min_length=3, max_length=5):
        """
        Generate random text theo tỉ lệ:
        - 5%: Text có ký tự đặc biệt
        - 10%: Text có số
        - 85%: Text chỉ có chữ cái
        
        Args:
            min_length: Độ dài tối thiểu
            max_length: Độ dài tối đa
            
        Returns:
            str: Text đã generate
        """
        # Quyết định loại text dựa trên xác suất
        rand = random.random()
        
        if rand < self.SPECIAL_CHAR_RATE:
            # 5%: Text có ký tự đặc biệt
            return self._generate_with_special_chars(min_length, max_length)
        elif rand < self.SPECIAL_CHAR_RATE + self.NUMBER_RATE:
            # 10%: Text có số
            return self._generate_with_numbers(min_length, max_length)
        else:
            # 85%: Text chỉ có chữ cái
            return self._generate_letters_only(min_length, max_length)
    
    def _generate_letters_only(self, min_length, max_length):
        """Generate text chỉ có chữ cái (a-z)"""
        length = random.randint(min_length, max_length)
        return ''.join(random.choice(self.letters) for _ in range(length))
    
    def _generate_with_numbers(self, min_length, max_length):
        """
        Generate text có chứa số
        Ví dụ: "abc123", "hello42", "test1"
        """
        length = random.randint(min_length, max_length)
        
        # Quyết định số lượng chữ số (1-3 số)
        num_digits = random.randint(1, min(3, length))
        num_letters = length - num_digits
        
        # Tạo các ký tự
        letters_part = [random.choice(self.letters) for _ in range(num_letters)]
        digits_part = [random.choice(self.digits) for _ in range(num_digits)]
        
        # Quyết định vị trí của số
        position = random.choice(['end', 'start', 'middle', 'mixed'])
        
        if position == 'end':
            # Số ở cuối: "hello123"
            result = letters_part + digits_part
        elif position == 'start':
            # Số ở đầu: "123hello"
            result = digits_part + letters_part
        elif position == 'middle':
            # Số ở giữa: "he123llo"
            mid = len(letters_part) // 2
            result = letters_part[:mid] + digits_part + letters_part[mid:]
        else:
            # Trộn ngẫu nhiên
            result = letters_part + digits_part
            random.shuffle(result)
        
        return ''.join(result)
    
    def _generate_with_special_chars(self, min_length, max_length):
        """
        Generate text có chứa ký tự đặc biệt
        Ví dụ: "hello!", "test@123", "#hello"
        """
        length = random.randint(min_length, max_length)
        
        # Quyết định số lượng ký tự đặc biệt (1-2 ký tự)
        num_special = random.randint(1, min(2, length))
        remaining = length - num_special
        
        # 30% có cả số
        has_numbers = random.random() < 0.3
        
        if has_numbers and remaining >= 2:
            num_digits = random.randint(1, min(2, remaining))
            num_letters = remaining - num_digits
            
            letters_part = [random.choice(self.letters) for _ in range(num_letters)]
            digits_part = [random.choice(self.digits) for _ in range(num_digits)]
            normal_chars = letters_part + digits_part
        else:
            normal_chars = [random.choice(self.letters) for _ in range(remaining)]
        
        special_part = [random.choice(self.special_chars) for _ in range(num_special)]
        
        # Quyết định vị trí ký tự đặc biệt
        position = random.choice(['start', 'end', 'mixed'])
        
        if position == 'start':
            # Ký tự đặc biệt ở đầu: "!hello", "@test"
            result = special_part + normal_chars
        elif position == 'end':
            # Ký tự đặc biệt ở cuối: "hello!", "test@"
            result = normal_chars + special_part
        else:
            # Trộn ngẫu nhiên
            result = normal_chars + special_part
            random.shuffle(result)
        
        return ''.join(result)
    
    def _spawn_chatboxes(self):
        """Tạo ra 3 chatbox mỗi lượt."""
        self.chatboxes.clear()  # xóa hết chatbox cũ
        self.fixed_chatboxes.clear()
        self.user_input.clear() # Xóa input cũ
        self.order_nums.clear()

        for i in range(3):
            sprite = self.base_sprites[i % len(self.base_sprites)]
            text = self._generate_random_text()
            pos = pygame.Vector2(80 + i * 195, 550)  # for position testing
            chatbox = Chatbox(self, base_sprite=sprite, text=text, pos=pos, lifetime=self.chatbox_lifetime)
            chatbox._on_chatbox_die = self._on_chatbox_die
            self.chatboxes.append(chatbox)

            # Thêm trạng thái cho các chatbox
            self.order_nums[str(i+1)] = {'current_state': self.CHATBOX_STATE[0]} # idle

            # Đánh dấu input cho các chatbox
            self.fixed_chatboxes[str(i+1)] = chatbox
    
    def _on_chatbox_die(self):
        self.sending_chatbox = False

    def update(self, dt):
        # Sinh chatbox lần đầu nếu chưa có
        if self.spawnable:
            self.spawnable = False
            self._spawn_chatboxes()
            return
        
        # Cập nhật từng chatbox
        for chatbox in self.chatboxes[:]:
            chatbox.update(dt)
            if chatbox.is_dead():
                self.chatboxes.remove(chatbox)
        
        self.time_since_last_spawn += dt

        # Nếu hết entry time thì tắt cờ để spawn chatbox
        if self.entry_flag and self.time_since_last_spawn >= self.entry_time:
            self.entry_flag = False

        # Sinh chatbox mới sau mỗi chu kỳ
        if self.time_since_last_spawn >= (self.spawn_interval + self.chatbox_lifetime):
            self.time_since_last_spawn = 0.0
            self.spawnable
        
        self.spawnable = not self.sending_chatbox and not self.entry_flag and not self.chatboxes

    def handle_events(self, events):
        if not self.chatboxes: return False
        if self.sending_chatbox: return False # Đang gửi thì không nhận input
        
        for event in events:
            for chatbox in self.chatboxes:
                chatbox.handle_events([event])
            
            if event.type == pygame.KEYDOWN:
                 #  Nhận input 1, 2, 3
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    chatbox_index = max(0, int(event.unicode) - 1)
                    # Nếu chưa có trong hàng đợi thì thêm vào, ngược lại thì bỏ ra
                    if event.unicode in self.user_input:
                        self.user_input.remove(event.unicode)
                        # Đổi trạng thái trở về bình thường
                        self.order_nums[event.unicode] = {'current_state': self.CHATBOX_STATE[0]} # 0 - 1: picked
                        chatbox : Chatbox = self.fixed_chatboxes[event.unicode]
                        if not chatbox:
                            return
                        chatbox.current_sprite = self.base_sprites[chatbox_index]
                    else:
                        self.user_input.append(event.unicode)

                        # Đổi trạng thái của chatbox được chọn
                        self.order_nums[event.unicode] = {'current_state': self.CHATBOX_STATE[1]} # 0 - 1: picked
                        chatbox : Chatbox = self.fixed_chatboxes[event.unicode]
                        if not chatbox:
                            self.user_input.remove(event.unicode)
                            return
                        chatbox.current_sprite = self.picked_sprites[chatbox_index]

                        print(f"From ChatboxSpawner: Added chatbox {event.unicode} to queue")
                    return True
                
                #  Enter để gửi
                elif event.key == pygame.K_RETURN:
                    if not self.user_input:
                        return False
                    
                    print(f"Sending chatboxes: {self.user_input}")
                    self.sending_chatbox = True
                    
                    for input_char in self.user_input:
                        chatbox_index = int(input_char)  # '1' → index 0
                            
                        chatbox : Chatbox = self.fixed_chatboxes[str(chatbox_index)]
                        chatbox.current_sprite = self.holding_sprites[chatbox_index]
                        if not chatbox: return False
                        chatbox.move_to(self.machine_pos)

                    self.user_input.clear()
                    return True
        return False

    def draw(self, screen):
        if not self.chatboxes:
            return
        for chatbox in self.chatboxes:
            chatbox.draw(screen)
        
        self._draw_chatbox_order(screen)
        self._draw_input_queue(screen)
    
    def _draw_chatbox_order(self, screen):
        BLACK = (0, 0, 0)
        
        font = pygame.font.Font(None, 24)

        # Nếu current_state là idle thì màu trắng, nếu được chọn thì màu xanh nhạt
        for i in range(len(self.chatboxes)):
            chatbox_num = [key for key, value in self.fixed_chatboxes.items() if value == self.chatboxes[i]]
            chatbox_pos = self.chatboxes[i].current_pos
            chatbox_alpha = self.chatboxes[i].alpha

            WHITE = (255, 255, 255, chatbox_alpha)
            BLUE = (143, 211, 255, chatbox_alpha)

            order_surf = font.render(chatbox_num[0], True, BLACK) # 1 - 2 - 3
            order_surf.set_alpha(chatbox_alpha)

            order_bg_color = WHITE if self.order_nums[chatbox_num[0]]['current_state'] == self.CHATBOX_STATE[0] else BLUE
            order_rect = order_surf.get_rect(center = (chatbox_pos[0], chatbox_pos[1] + 45))
            bg_rect = order_rect.inflate(20, 10)

            pygame.draw.rect(screen, order_bg_color, bg_rect, border_radius=5)  # background for the text
            screen.blit(order_surf, order_rect)

    def _draw_input_queue(self, screen):
        '''Hiển thị các chatbox đã chọn'''
        if not self.user_input:
            return
        
        font = pygame.font.Font(None, 32)
        queue_text = f"Selected: {', '.join(self.user_input)}"
        text_surf = font.render(queue_text, True, (255, 255, 255))
        
        # Background
        bg_rect = text_surf.get_rect(center=(400, 50))
        bg_rect.inflate_ip(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(screen, (255, 255, 0), bg_rect, 2)
        
        # Text
        screen.blit(text_surf, text_surf.get_rect(center=(400, 50)))
