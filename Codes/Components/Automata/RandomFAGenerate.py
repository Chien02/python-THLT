import random

# Ví dụ về FA sau khi được tạo bởi RandomAutomatonGenerator
# {
#  'states': ['q0','q1','q2','q3','q4','q_extra_0','q_extra_1'],
#  'alphabet': ['a','m'],
#  'start': 'q0',
#  'accept': ['q4'],
#  'transitions': {
#     'q0': {'m': ['q1', 'q_extra_1']},
#     'q1': {'a': ['q2'], 'm': ['q_extra_0']},
#     'q2': {'a': ['q3'], 'm': ['q2']},
#     'q3': {'m': ['q4'], 'a': ['q3']},
#     'q4': {'a': ['q4']},
#     'q_extra_0': {'a': ['q3'], 'm': ['q_extra_0']},
#     'q_extra_1': {'m': ['q1']}
#  }
# }

class RandomAutomatonGenerator:
    def __init__(self, extra_branch_prob=0.3, max_extra_states=3, loop_prob=0.3):
        """
        extra_branch_prob: xác suất thêm nhánh phụ
        max_extra_states: số state phụ tối đa
        loop_prob: xác suất tạo loop ngẫu nhiên cho mỗi ký tự
        """
        self.extra_branch_prob = extra_branch_prob
        self.max_extra_states = max_extra_states
        self.loop_prob = loop_prob

    def generate(self, input_string):
        """
        Sinh NFA ngẫu nhiên nhưng luôn chấp nhận chuỗi.
        Tích hợp loop thông minh dựa trên chuỗi đầu vào.
        """
        n = len(input_string)

        # ----------------------------------
        # 1. Tạo main path
        # ----------------------------------
        states = [f"q{i}" for i in range(n + 1)]
        start_state = "q0"
        accept_state = f"q{n}"

        transitions = {s: {} for s in states}

        # Main path
        for i, char in enumerate(input_string):
            s = states[i]
            t = states[i + 1]
            transitions[s].setdefault(char, []).append(t)

        alphabet = sorted(set(input_string))

        # ----------------------------------
        # 2. Thêm extra states
        # ----------------------------------
        extra_states = []
        for i in range(self.max_extra_states):
            s = f"q_extra_{i}"
            extra_states.append(s)
            transitions[s] = {}

        all_states = states + extra_states

        # ----------------------------------
        # 3. Loop (dựa vào ký tự liên tiếp)
        # ----------------------------------
        for i in range(1, n):
            prev_char = input_string[i - 1]
            current_char = input_string[i]

            if prev_char == current_char:
                loop_state = states[i]  # q1, q2, q3...

                # Tạo loop: qi -(char)-> qi
                transitions[loop_state].setdefault(current_char, [])
                if loop_state not in transitions[loop_state][current_char]:
                    transitions[loop_state][current_char].append(loop_state)

        # ----------------------------------
        # 4. Thêm các nhánh phụ ngẫu nhiên
        # ----------------------------------
        for s in all_states:
            for c in alphabet:
                if random.random() < self.extra_branch_prob:
                    to_state = random.choice(all_states)
                    transitions[s].setdefault(c, [])
                    if to_state not in transitions[s][c]:
                        transitions[s][c].append(to_state)

        # ----------------------------------
        # 5. Thêm loop ngẫu nhiên (loop_prob = 0.3)
        # ----------------------------------
        for s in all_states:
            for c in alphabet:
                if random.random() < self.loop_prob:
                    transitions[s].setdefault(c, [])
                    if s not in transitions[s][c]:
                        transitions[s][c].append(s)

        # ----------------------------------
        # 6. Đảm bảo mỗi state có ít nhất 1 transition cho mỗi ký tự (tùy chọn)
        #    Nhưng để game khó, ta để 70% rơi vào dead-end tự nhiên.
        # ----------------------------------

        return {
            "states": all_states,
            "alphabet": alphabet,
            "start": start_state,
            "accepts": [accept_state],
            "transitions": transitions,
        }
