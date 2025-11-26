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
        Tích hợp loop tại mỗi state dựa trên chuỗi đầu vào.
        """
        n = len(input_string)

        # ----------------------------------
        # 1. Tạo main path
        # ----------------------------------
        states : list = [f"q{i}" for i in range(n + 1)]
        start_state = "q0"
        accept_states : list = [f"q{n}"]
        transitions : dict = {s: {} for s in states} # {'q0': {'a': [q0, q1, q3]}}, {'q0': {'b': [q0, q2, q3]}}

        # Main path
        for i, char in enumerate(input_string):
            s = states[i]
            t = states[i + 1]
            transitions[s].setdefault(char, []).append(t)

        alphabet : set = sorted(set(input_string))

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
        # 6. Kiểm tra lại có bất kì state nào không có state khác đi đến thì loại bỏ state đó.
        # Mục đích: loại bỏ sự dư thừa không cần thiết, sự dư thừa này đến từ việc tạo ngẫu nhiên.
        # ----------------------------------
        # Bằng cách kiểm tra trong danh sách các next_state, nếu nó không nằm trong bất kì danh sách nào thì
        # loại bỏ state đó. TRỪ START STATE.
        # Những nơi cần loại bỏ:
        # [all_states, transitions, accept_states(nếu có)]
        # LOOP cho đến khi không còn state nào bị xóa
        while True:
            removed_in_this_iteration = []
            states_to_check = [s for s in all_states if s not in accept_states]
            
            for state in states_to_check:
                # Kiểm tra 1: State không có outgoing transition
                if len(transitions[state]) == 0:
                    self.remove_state_from_transitions(transitions, removed_in_this_iteration, state)
                    print(f"From FAGenerator: Removed {state} 'cause it had no transition")
                
                # Kiểm tra 2: State chỉ có self-loop (đi đến chính nó)
                # Kiểm tra xem tất cả next_states có phải chỉ là chính nó không
                elif self.is_only_self_loop(state, transitions):
                    self.remove_state_from_transitions(transitions, removed_in_this_iteration, state)
                    print(f"From FAGenerator: Removed {state} 'cause it is self-loop only")
                
                # Kiểm tra 3: Không có state nào khác đi đến nó (unreachable)
                elif not self.is_in_next_states(state, transitions) and state != start_state:
                    self.remove_state_from_transitions(transitions, removed_in_this_iteration, state)
                    print(f"From FAGenerator: Removed {state} 'cause no one go to it")
            
            # Nếu không xóa được state nào trong vòng lặp này, thoát
            if len(removed_in_this_iteration) == 0:
                break
            
            # Xóa khỏi all_states
            for state in removed_in_this_iteration:
                if state in all_states:
                    all_states.remove(state)
                if state in accept_states:
                    accept_states.remove(state)
        
        print("FA after removed!")
        print(f"{all_states}")
        print(f"{alphabet}")
        for state in transitions:
            print(f"{state}: {transitions[state].items()}")

        return {
            "states": all_states,
            "alphabet": alphabet,
            "start": start_state,
            "accepts": accept_states,
            "transitions": transitions,
        }

    def is_only_self_loop(self, state, transitions):
        """
        Kiểm tra xem state có chỉ đi đến chính nó không
        (Nghĩa là tất cả next_states đều là chính nó)
        """
        if state not in transitions:
            return False
        
        for char, to_list in transitions[state].items():
            for next_state in to_list:
                if next_state != state:
                    # Có ít nhất một next_state không phải là chính nó
                    return False
        
        # Nếu tất cả next_states đều là chính nó
        return len(transitions[state]) > 0

    def is_in_next_states(self, state, transitions):
        """Kiểm tra xem state có được state nào khác tham chiếu đến không"""
        for _state, edges in transitions.items():
            if _state == state:
                continue
            for char, to_list in edges.items():
                if state in to_list:
                    return True
        return False

    def remove_state_from_transitions(self, transitions, removed_states, state):
        """Xóa state khỏi transitions"""
        removed_states.append(state)
        self.remove_from_to_list(transitions, state)
        if state in transitions:
            transitions.pop(state)

    def remove_from_to_list(self, transitions, state):
        """Xóa state khỏi tất cả danh sách next_states"""
        for _state in list(transitions.keys()):
            for char in list(transitions[_state].keys()):
                if state in transitions[_state][char]:
                    transitions[_state][char].remove(state)
                    