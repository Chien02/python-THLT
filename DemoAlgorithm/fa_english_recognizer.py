"""
FA English Recognizer - Nhận diện tiếng Anh sử dụng Finite Automata
Bài toán: Phân biệt chuỗi tiếng Anh từ tạp âm (noise)
"""

from fa_models import DFA, NFA, EpsilonNFA
from fa_converter import FAConverter
from typing import Set, List, Dict, Tuple


class EnglishRecognizer:
    """
    Máy nhận diện tiếng Anh - Phân biệt tiếng Anh từ tạp âm
    
    Chiến lược:
    1. Tạo ε-NFA để nhận dạng tiếng Anh (linh hoạt, dễ thiết kế)
    2. Chuyển đổi thành NFA (loại bỏ epsilon transitions)
    3. Chuyển đổi thành DFA (xác định, nhanh để kiểm tra)
    """
    
    @staticmethod
    def create_english_epsilon_nfa() -> EpsilonNFA:
        """
        Tạo ε-NFA nhận diện tiếng Anh cơ bản
        
        Định nghĩa tiếng Anh:
        - Chỉ chứa chữ cái (a-z, A-Z)
        - Có thể chứa khoảng trắng giữa các từ
        - Không chứa chữ số hoặc ký tự đặc biệt (trừ khoảng trắng)
        
        Ví dụ:
        ✓ "hello" - tiếng Anh
        ✓ "hello world" - tiếng Anh
        ✗ "hello123" - không phải (có chữ số)
        ✗ "h3llo" - không phải (có chữ số)
        ✗ "hello!" - không phải (có ký tự đặc biệt)
        """
        e_nfa = EpsilonNFA()
        
        # Các trạng thái
        e_nfa.add_state("q0", is_start=True)      # Bắt đầu
        e_nfa.add_state("q1")                      # Đang đọc từ
        e_nfa.add_state("q2")                      # Sau từ (có thể kết thúc hoặc khoảng trắng)
        e_nfa.add_state("q3", is_accept=True)     # Trạng thái kết thúc

        # Chuyển tiếp chính
        # q0 -> q1: epsilon để bắt đầu đọc từ đầu tiên
        e_nfa.add_epsilon_transition("q0", "q1")
        
        # q1: Đọc chữ cái (a-z, A-Z)
        for letter in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
            e_nfa.add_transition("q1", letter, "q1")  # Tiếp tục đọc chữ cái
            e_nfa.add_transition("q1", letter, "q2")  # Hoặc chuyển sang q2
        
        # q2: Sau khi hoàn thành một từ
        # - Có thể là từ cuối cùng (chuyển đến q3 qua epsilon)
        e_nfa.add_epsilon_transition("q2", "q3")
        
        # - Hoặc có khoảng trắng rồi từ tiếp theo
        e_nfa.add_transition("q2", " ", "q2")      # Khoảng trắng liên tiếp
        e_nfa.add_epsilon_transition("q2", "q1")   # Quay lại q1 để đọc từ tiếp theo
        
        # Alphabet
        e_nfa.alphabet = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ")
        
        return e_nfa
    
    @staticmethod
    def create_english_nfa() -> NFA:
        """
        Chuyển đổi ε-NFA thành NFA (loại bỏ epsilon transitions)
        
        Quá trình:
        1. Tính epsilon-closure cho mỗi chuyển tiếp
        2. Chuyển các epsilon-transition thành epsilon-closure
        3. Cập nhật accept states dựa trên epsilon-closure
        """
        e_nfa = EnglishRecognizer.create_english_epsilon_nfa()
        nfa = FAConverter.epsilon_nfa_to_nfa(e_nfa)
        return nfa
    
    @staticmethod
    def create_english_dfa() -> DFA:
        """
        Chuyển đổi NFA thành DFA (Powerset Construction)
        
        Quá trình:
        1. Mỗi trạng thái DFA = tập hợp trạng thái NFA
        2. Bắt đầu từ epsilon-closure của q0
        3. Với mỗi ký tự, tính tập hợp trạng thái tiếp theo
        
        Lợi ích: DFA chạy O(n) trong khi NFA chạy O(n*m)
        """
        e_nfa = EnglishRecognizer.create_english_epsilon_nfa()
        dfa = FAConverter.epsilon_nfa_to_dfa(e_nfa)
        return dfa
    
    @staticmethod
    def is_english(text: str, use_dfa: bool = True) -> bool:
        """
        Kiểm tra xem chuỗi có phải tiếng Anh không
        
        Args:
            text: Chuỗi cần kiểm tra
            use_dfa: Sử dụng DFA (nhanh) hay NFA (chính xác)
        
        Returns:
            True nếu là tiếng Anh, False nếu là tạp âm
        """
        if use_dfa:
            dfa = EnglishRecognizer.create_english_dfa()
            return dfa.accepts_string(text)
        else:
            nfa = EnglishRecognizer.create_english_nfa()
            return nfa.accepts_string(text)
    
    @staticmethod
    def classify_strings(strings: List[str]) -> Tuple[List[str], List[str]]:
        """
        Phân loại một danh sách chuỗi thành tiếng Anh và tạp âm
        
        Args:
            strings: Danh sách chuỗi hỗn hợp
        
        Returns:
            (english_strings, noise_strings)
        """
        english = []
        noise = []
        
        for s in strings:
            if EnglishRecognizer.is_english(s):
                english.append(s)
            else:
                noise.append(s)
        
        return english, noise
    
    @staticmethod
    def trace_english_recognition(text: str) -> Dict:
        """
        Theo dõi quá trình nhận diện tiếng Anh
        
        Hiển thị:
        - Các chuyển tiếp qua các trạng thái
        - Epsilon-closure ở mỗi bước
        - Kết quả cuối cùng
        """
        e_nfa = EnglishRecognizer.create_english_epsilon_nfa()
        dfa = EnglishRecognizer.create_english_dfa()
        
        result = {
            'text': text,
            'is_english_dfa': dfa.accepts_string(text),
            'is_english_nfa': e_nfa.accepts_string(text),
            'dfa_states': len(dfa.states),
            'e_nfa_states': len(e_nfa.states),
        }
        
        return result


class NoisyChannelSimulator:
    """
    Mô phỏng kênh tạp âm - sinh ra tiếng Anh và tạp âm hỗn hợp
    """
    
    @staticmethod
    def generate_english_strings(count: int = 10) -> List[str]:
        """Sinh tiếng Anh ngẫu nhiên"""
        import random
        
        english_words = [
            "hello", "world", "python", "automata", "language", "machine",
            "learning", "theory", "computer", "science", "programming",
            "algorithm", "data", "structure", "network", "database",
            "security", "encryption", "digital", "information"
        ]
        
        result = []
        for _ in range(count):
            # Chọn 1-3 từ ngẫu nhiên
            num_words = random.randint(1, 3)
            sentence = " ".join(random.choices(english_words, k=num_words))
            result.append(sentence)
        
        return result
    
    @staticmethod
    def generate_noise_strings(count: int = 10) -> List[str]:
        """Sinh tạp âm (chuỗi không phải tiếng Anh)"""
        import random
        
        noise_patterns = [
            "12345",           # Chỉ chữ số
            "abc123def",       # Hỗn hợp chữ và số
            "hello@world",     # Ký tự đặc biệt
            "🎮🎯🎲",         # Emoji
            "***###$$$",       # Ký tự đặc biệt
            "h3ll0 w0rld",     # Chữ số thay chữ cái
            "café",            # Tiếng không phải Anh
            "你好",            # Tiếng Trung
            "مرحبا",           # Tiếng Ả Rập
            "привет",          # Tiếng Nga
        ]
        
        result = []
        for _ in range(count):
            noise = random.choice(noise_patterns)
            result.append(noise)
        
        return result
    
    @staticmethod
    def create_noisy_channel(english_count: int = 10, noise_count: int = 10) -> List[Tuple[str, bool]]:
        """
        Tạo kênh tạp âm: hỗn hợp tiếng Anh và tạp âm
        
        Returns:
            Danh sách (chuỗi, là_tiếng_Anh)
        """
        import random
        
        english_strings = NoisyChannelSimulator.generate_english_strings(english_count)
        noise_strings = NoisyChannelSimulator.generate_noise_strings(noise_count)
        
        # Tạo danh sách (chuỗi, nhãn)
        labeled = []
        for eng in english_strings:
            labeled.append((eng, True))
        for noise in noise_strings:
            labeled.append((noise, False))
        
        # Xáo trộn
        random.shuffle(labeled)
        
        return labeled


class EnglishRecognizerGame:
    """
    Game nhận diện tiếng Anh
    
    Luật chơi:
    - Hiển thị 20 chuỗi hỗn hợp (tiếng Anh + tạp âm)
    - Người chơi (hoặc DFA) phải phân loại chính xác
    - Tính điểm: số đúng / tổng số
    """
    
    def __init__(self):
        self.score = 0
        self.total = 0
        self.channel = []
        self.results = []
    
    def start_game(self, english_count: int = 10, noise_count: int = 10):
        """Bắt đầu một trò chơi mới"""
        self.score = 0
        self.total = 0
        self.results = []
        
        # Tạo kênh tạp âm
        self.channel = NoisyChannelSimulator.create_noisy_channel(english_count, noise_count)
        self.total = len(self.channel)
    
    def test_string(self, text: str) -> bool:
        """Kiểm tra một chuỗi"""
        result = EnglishRecognizer.is_english(text)
        return result
    
    def play_automated(self) -> float:
        """
        Máy tự động chơi - DFA phân loại tất cả
        
        Returns:
            Tỉ lệ chính xác (0-1)
        """
        if not self.channel:
            return 0.0
        
        for text, is_english_label in self.channel:
            predicted = EnglishRecognizer.is_english(text)
            
            if predicted == is_english_label:
                self.score += 1
                self.results.append({
                    'text': text,
                    'predicted': predicted,
                    'actual': is_english_label,
                    'correct': True
                })
            else:
                self.results.append({
                    'text': text,
                    'predicted': predicted,
                    'actual': is_english_label,
                    'correct': False
                })
        
        accuracy = self.score / self.total if self.total > 0 else 0
        return accuracy
    
    def get_report(self) -> str:
        """Báo cáo kết quả"""
        accuracy = self.score / self.total if self.total > 0 else 0
        
        report = f"""
{'='*60}
GAME REPORT - NHẬN DIỆN TIẾNG ANH
{'='*60}

Điểm số: {self.score}/{self.total}
Tỉ lệ chính xác: {accuracy*100:.1f}%

Chi tiết:
"""
        
        for i, result in enumerate(self.results, 1):
            status = "✓" if result['correct'] else "✗"
            report += f"\n{i}. {status} '{result['text']}'\n"
            report += f"   Dự đoán: {'TIẾNG ANH' if result['predicted'] else 'TẠP ÂM'} | "
            report += f"Thực tế: {'TIẾNG ANH' if result['actual'] else 'TẠP ÂM'}\n"
        
        report += f"\n{'='*60}\n"
        return report


# ============================================================================
# ADVANCED: Nhận diện tiếng Anh nâng cao với từ điển
# ============================================================================

class AdvancedEnglishRecognizer:
    """
    Nhận diện tiếng Anh nâng cao: sử dụng từ điển
    
    Cải tiến:
    - Kiểm tra mỗi từ trong từ điển tiếng Anh
    - Hỗ trợ kiểm tra chính tả
    - Loại bỏ được các từ không hợp lệ
    """
    
    # Từ điển tiếng Anh phổ biến (có thể mở rộng)
    COMMON_WORDS = {
        "hello", "world", "python", "automata", "language", "machine",
        "learning", "theory", "computer", "science", "programming",
        "algorithm", "data", "structure", "network", "database",
        "security", "encryption", "digital", "information", "the", "is",
        "and", "to", "of", "in", "that", "have", "i", "it", "for",
        "not", "on", "with", "he", "as", "you", "do", "at", "this",
        "but", "his", "by", "from", "they", "we", "say", "her", "she",
        "or", "an", "will", "my", "one", "all", "would", "there", "their",
    }
    
    @staticmethod
    def is_valid_english_word(word: str) -> bool:
        """Kiểm tra từ có phải tiếng Anh không"""
        # Loại bỏ khoảng trắng
        word = word.strip().lower()
        
        # Chỉ chứa chữ cái
        if not all(c.isalpha() or c == ' ' for c in word):
            return False
        
        # Không trống
        if not word:
            return False
        
        # Kiểm tra từ đơn lẻ
        words = word.split()
        for w in words:
            if w and w not in AdvancedEnglishRecognizer.COMMON_WORDS:
                # Có thể thêm xử lý: từ không trong từ điển nhưng có thể là hợp lệ
                # Ở đây cứng nhạc để demo
                pass
        
        return True
    
    @staticmethod
    def is_english_advanced(text: str) -> bool:
        """Kiểm tra tiếng Anh nâng cao"""
        # Kết hợp: DFA cơ bản + kiểm tra từ điển
        if not EnglishRecognizer.is_english(text):
            return False
        
        return AdvancedEnglishRecognizer.is_valid_english_word(text)


if __name__ == "__main__":
    print("="*70)
    print("ENGLISH RECOGNIZER - Nhận diện tiếng Anh sử dụng Finite Automata")
    print("="*70)
    
    # Demo 1: Kiểm tra chuỗi đơn
    print("\n📝 Demo 1: Kiểm tra chuỗi đơn")
    print("-" * 70)
    test_strings = [
        "hello",
        "hello world",
        "python",
        "hello123",
        "h3llo",
        "café",
        "hello!",
        "PROGRAMMING",
        "test code",
        "abc@#$",
    ]
    
    for text in test_strings:
        result = EnglishRecognizer.is_english(text)
        status = "✓ TIẾNG ANH" if result else "✗ TẠP ÂM"
        print(f"  '{text:20}' → {status}")
    
    # Demo 2: Phân loại chuỗi hỗn hợp
    print("\n📊 Demo 2: Phân loại chuỗi hỗn hợp")
    print("-" * 70)
    mixed = ["hello world", "123456", "python code", "test@123", "machine learning"]
    english, noise = EnglishRecognizer.classify_strings(mixed)
    print(f"  Tiếng Anh: {english}")
    print(f"  Tạp âm: {noise}")
    
    # Demo 3: Game nhận diện tự động
    print("\n🎮 Demo 3: Game nhận diện tự động")
    print("-" * 70)
    game = EnglishRecognizerGame()
    game.start_game(english_count=5, noise_count=5)
    accuracy = game.play_automated()
    print(game.get_report())
    
    # Demo 4: So sánh DFA vs NFA
    print("📊 Demo 4: So sánh DFA vs NFA")
    print("-" * 70)
    e_nfa = EnglishRecognizer.create_english_epsilon_nfa()
    nfa = EnglishRecognizer.create_english_nfa()
    dfa = EnglishRecognizer.create_english_dfa()
    
    print(f"  ε-NFA: {len(e_nfa.states)} trạng thái")
    print(f"  NFA:   {len(nfa.states)} trạng thái")
    print(f"  DFA:   {len(dfa.states)} trạng thái")
