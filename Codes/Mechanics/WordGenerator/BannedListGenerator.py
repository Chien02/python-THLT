import random
import string

class BannedListGenerator:
    def __init__(self):
        self.current_banned_list = []

    def generate(self, banned_char_num=8):
        # reset list cũ
        self.current_banned_list.clear()

        # Lấy tất cả ký tự chữ thường a-z
        all_chars = list(string.ascii_lowercase)

        # Đảm bảo không lấy quá số lượng ký tự có thể
        num = min(banned_char_num, len(all_chars))

        # Lấy ngẫu nhiên num ký tự không trùng nhau
        banned_list = random.sample(all_chars, num)
        self.current_banned_list = banned_list
        
        # Debug
        print("This is banned list: ")
        print(banned_list)
        return banned_list

    def is_in_banned_list(self, text):
        if len(self.current_banned_list) == 0:
            return

        for char in text:
            if char in self.current_banned_list:
                return True
        return False