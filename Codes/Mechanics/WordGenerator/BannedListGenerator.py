import random
import string

class BannedListGenerator:
    def generate(self, banned_char_num=8):
        # Lấy tất cả ký tự chữ thường a-z
        all_chars = list(string.ascii_lowercase)

        # Đảm bảo không lấy quá số lượng ký tự có thể
        num = min(banned_char_num, len(all_chars))

        # Lấy ngẫu nhiên num ký tự không trùng nhau
        banned_list = random.sample(all_chars, num)

        return banned_list

print(BannedListGenerator().generate())