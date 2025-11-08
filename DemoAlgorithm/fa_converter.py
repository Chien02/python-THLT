"""
FA Conversion - Các thuật toán chuyển đổi giữa DFA, NFA, và ε-NFA
"""

from typing import Set, Dict, List, Tuple, FrozenSet
from fa_models import DFA, NFA, EpsilonNFA


class FAConverter:
    """Lớp để chuyển đổi giữa các loại Finite Automata"""
    
    @staticmethod
    def epsilon_nfa_to_nfa(e_nfa: EpsilonNFA) -> NFA:
        """
        Chuyển đổi ε-NFA thành NFA
        
        Phương pháp:
        1. Loại bỏ tất cả các chuyển tiếp epsilon
        2. Mỗi chuyển tiếp trở thành: state -> epsilon_closure(next_states_with_symbol)
        3. Một trạng thái trở thành accept nếu epsilon-closure của nó chứa bất kỳ accept state
        """
        nfa = NFA()
        
        # Thêm tất cả các trạng thái
        for state_name, state in e_nfa.states.items():
            is_accept = state.is_accept
            nfa.add_state(state_name, state.is_start, is_accept)
        
        # Thêm alphabet
        nfa.alphabet = e_nfa.alphabet.copy()
        
        # Thêm các chuyển tiếp mới
        for from_state in e_nfa.states:
            for symbol in e_nfa.alphabet:
                # Lấy tất cả các trạng thái có thể đạt được từ from_state bằng symbol
                direct_nexts = e_nfa.get_transitions(from_state, symbol)
                
                if direct_nexts:
                    # Tính epsilon-closure của các trạng thái tiếp theo
                    closure = e_nfa.epsilon_closure(direct_nexts)
                    for to_state in closure:
                        nfa.add_transition(from_state, symbol, to_state)
        
        # Cập nhật accept states: trạng thái trở thành accept nếu epsilon-closure của nó
        # chứa một accept state hoặc chính nó là accept state
        new_accept_states = set()
        for state_name in nfa.states:
            closure = e_nfa.epsilon_closure({state_name})
            if closure & e_nfa.accept_states:
                new_accept_states.add(state_name)
        
        nfa.accept_states = new_accept_states
        
        return nfa
    
    @staticmethod
    def nfa_to_dfa(nfa: NFA) -> DFA:
        """
        Chuyển đổi NFA thành DFA (Powerset Construction / Subset Construction)
        
        Phương pháp:
        1. Mỗi trạng thái trong DFA là một tập hợp các trạng thái từ NFA
        2. Trạng thái khởi đầu của DFA = {q0 của NFA}
        3. Trạng thái accept của DFA = những tập hợp chứa ít nhất một accept state của NFA
        4. Chuyển tiếp: từ tập {p1, p2, ...} với ký tự a -> {q | q ∈ δ(pi, a), pi ∈ tập hiện tại}
        """
        dfa = DFA()
        
        # Bắt đầu từ tập chứa trạng thái khởi đầu
        start_set = frozenset({nfa.start_state})
        
        # Đặt tên cho các trạng thái của DFA
        state_map = {}  # Từ frozenset sang tên trạng thái
        state_counter = 0
        
        # BFS để tìm tất cả các trạng thái có thể đạt được
        queue = [start_set]
        visited = {start_set}
        
        while queue:
            current_set = queue.pop(0)
            
            # Tạo tên cho trạng thái này
            if current_set not in state_map:
                state_name = f"q{state_counter}"
                state_counter += 1
                state_map[current_set] = state_name
            else:
                state_name = state_map[current_set]
            
            # Kiểm tra xem đây có phải accept state không
            is_accept = bool(current_set & nfa.accept_states)
            is_start = (current_set == start_set)
            
            dfa.add_state(state_name, is_start, is_accept)
            dfa.alphabet = nfa.alphabet.copy()
            
            # Tính chuyển tiếp cho mỗi ký tự
            for symbol in nfa.alphabet:
                next_set = set()
                for state in current_set:
                    next_set.update(nfa.get_transitions(state, symbol))
                
                if next_set:
                    next_set = frozenset(next_set)
                    
                    if next_set not in state_map:
                        state_name_next = f"q{state_counter}"
                        state_counter += 1
                        state_map[next_set] = state_name_next
                    else:
                        state_name_next = state_map[next_set]
                    
                    dfa.add_transition(state_name, symbol, state_name_next)
                    
                    if next_set not in visited:
                        visited.add(next_set)
                        queue.append(next_set)
        
        return dfa
    
    @staticmethod
    def epsilon_nfa_to_dfa(e_nfa: EpsilonNFA) -> DFA:
        """
        Chuyển đổi ε-NFA thành DFA (Direct conversion)
        
        Phương pháp:
        1. Tương tự NFA to DFA nhưng sử dụng epsilon-closure
        2. Trạng thái khởi đầu = epsilon-closure({q0})
        3. Mỗi bước chuyển tiếp bao gồm epsilon-closure của kết quả
        """
        dfa = DFA()
        
        # Bắt đầu từ epsilon-closure của trạng thái khởi đầu
        start_set = frozenset(e_nfa.epsilon_closure({e_nfa.start_state}))
        
        state_map = {}
        state_counter = 0
        
        queue = [start_set]
        visited = {start_set}
        
        while queue:
            current_set = queue.pop(0)
            
            if current_set not in state_map:
                state_name = f"q{state_counter}"
                state_counter += 1
                state_map[current_set] = state_name
            else:
                state_name = state_map[current_set]
            
            is_accept = bool(current_set & e_nfa.accept_states)
            is_start = (current_set == start_set)
            
            dfa.add_state(state_name, is_start, is_accept)
            dfa.alphabet = e_nfa.alphabet.copy()
            
            for symbol in e_nfa.alphabet:
                next_set = set()
                for state in current_set:
                    next_set.update(e_nfa.get_transitions(state, symbol))
                
                if next_set:
                    # Tính epsilon-closure của tập tiếp theo
                    next_set = frozenset(e_nfa.epsilon_closure(next_set))
                    
                    if next_set not in state_map:
                        state_name_next = f"q{state_counter}"
                        state_counter += 1
                        state_map[next_set] = state_name_next
                    else:
                        state_name_next = state_map[next_set]
                    
                    dfa.add_transition(state_name, symbol, state_name_next)
                    
                    if next_set not in visited:
                        visited.add(next_set)
                        queue.append(next_set)
        
        return dfa
    
    @staticmethod
    def dfa_to_nfa(dfa: DFA) -> NFA:
        """
        Chuyển đổi DFA thành NFA (Trivial conversion)
        DFA là một trường hợp đặc biệt của NFA
        """
        nfa = NFA()
        
        # Sao chép tất cả các trạng thái
        for state_name, state in dfa.states.items():
            nfa.add_state(state_name, state.is_start, state.is_accept)
        
        nfa.alphabet = dfa.alphabet.copy()
        nfa.accept_states = dfa.accept_states.copy()
        
        # Sao chép tất cả các chuyển tiếp
        for from_state in dfa.transitions:
            for symbol in dfa.transitions[from_state]:
                to_state = next(iter(dfa.transitions[from_state][symbol]))
                nfa.add_transition(from_state, symbol, to_state)
        
        return nfa
    
    @staticmethod
    def dfa_to_epsilon_nfa(dfa: DFA) -> EpsilonNFA:
        """
        Chuyển đổi DFA thành ε-NFA
        """
        e_nfa = EpsilonNFA()
        
        # Sao chép tất cả các trạng thái
        for state_name, state in dfa.states.items():
            e_nfa.add_state(state_name, state.is_start, state.is_accept)
        
        e_nfa.alphabet = dfa.alphabet.copy()
        e_nfa.accept_states = dfa.accept_states.copy()
        
        # Sao chép tất cả các chuyển tiếp
        for from_state in dfa.transitions:
            for symbol in dfa.transitions[from_state]:
                to_state = next(iter(dfa.transitions[from_state][symbol]))
                e_nfa.add_transition(from_state, symbol, to_state)
        
        return e_nfa
    
    @staticmethod
    def nfa_to_epsilon_nfa(nfa: NFA) -> EpsilonNFA:
        """
        Chuyển đổi NFA thành ε-NFA
        """
        e_nfa = EpsilonNFA()
        
        # Sao chép tất cả các trạng thái
        for state_name, state in nfa.states.items():
            e_nfa.add_state(state_name, state.is_start, state.is_accept)
        
        e_nfa.alphabet = nfa.alphabet.copy()
        e_nfa.accept_states = nfa.accept_states.copy()
        
        # Sao chép tất cả các chuyển tiếp
        for from_state in nfa.transitions:
            for symbol in nfa.transitions[from_state]:
                for to_state in nfa.transitions[from_state][symbol]:
                    e_nfa.add_transition(from_state, symbol, to_state)
        
        return e_nfa
    
    @staticmethod
    def convert(fa, source_type: str, target_type: str):
        """
        Chuyển đổi từ loại automata này sang loại khác
        
        Args:
            fa: Finite Automata cần chuyển đổi
            source_type: Loại nguồn ('DFA', 'NFA', 'EPSILON_NFA')
            target_type: Loại đích ('DFA', 'NFA', 'EPSILON_NFA')
        """
        if source_type == target_type:
            return fa
        
        # Định tuyến chuyển đổi
        conversion_map = {
            ('EPSILON_NFA', 'NFA'): FAConverter.epsilon_nfa_to_nfa,
            ('EPSILON_NFA', 'DFA'): FAConverter.epsilon_nfa_to_dfa,
            ('NFA', 'DFA'): FAConverter.nfa_to_dfa,
            ('NFA', 'EPSILON_NFA'): FAConverter.nfa_to_epsilon_nfa,
            ('DFA', 'NFA'): FAConverter.dfa_to_nfa,
            ('DFA', 'EPSILON_NFA'): FAConverter.dfa_to_epsilon_nfa,
        }
        
        key = (source_type, target_type)
        if key in conversion_map:
            return conversion_map[key](fa)
        else:
            raise ValueError(f"Cannot convert from {source_type} to {target_type}")


class FAMinimizer:
    """Lớp để tối thiểu hóa DFA"""
    
    @staticmethod
    def minimize_dfa(dfa: DFA) -> DFA:
        """
        Tối thiểu hóa DFA bằng thuật toán Hopcroft
        
        Phương pháp:
        1. Phân chia trạng thái thành 2 nhóm: accept và non-accept
        2. Lặp lại: chia nhỏ nhóm nếu các thành viên đi đến các nhóm khác nhau
        3. Tạo DFA mới từ các nhóm
        """
        # Phân chia ban đầu: accept vs non-accept
        accept = dfa.accept_states.copy()
        non_accept = set(dfa.states.keys()) - accept
        
        partition = [accept, non_accept] if non_accept else [accept]
        
        # Lặp lại cho đến khi không còn thay đổi
        changed = True
        while changed:
            changed = False
            new_partition = []
            
            for group in partition:
                sub_groups = {}
                
                for state in group:
                    # Tính "signature" của state: (symbol -> group_id)
                    signature = []
                    for symbol in sorted(dfa.alphabet):
                        next_state = dfa.get_transitions(state, symbol)
                        
                        # Tìm group_id của next_state
                        group_id = -1
                        if next_state:
                            for i, p in enumerate(partition):
                                if next_state in p:
                                    group_id = i
                                    break
                        
                        signature.append((symbol, group_id))
                    
                    signature = tuple(signature)
                    if signature not in sub_groups:
                        sub_groups[signature] = []
                    sub_groups[signature].append(state)
                
                if len(sub_groups) > 1:
                    changed = True
                
                new_partition.extend(sub_groups.values())
            
            partition = new_partition
        
        # Tạo DFA tối thiểu
        minimized = DFA()
        
        # Tạo ánh xạ từ trạng thái cũ sang nhóm mới
        state_to_group = {}
        for i, group in enumerate(partition):
            group_name = f"q{i}"
            for state in group:
                state_to_group[state] = group_name
        
        # Thêm các trạng thái mới
        for i, group in enumerate(partition):
            group_name = f"q{i}"
            representative = next(iter(group))
            
            is_start = dfa.states[representative].is_start
            is_accept = representative in dfa.accept_states
            
            minimized.add_state(group_name, is_start, is_accept)
        
        minimized.alphabet = dfa.alphabet.copy()
        
        # Thêm chuyển tiếp
        added_transitions = set()
        for group in partition:
            representative = next(iter(group))
            for symbol in dfa.alphabet:
                next_state = dfa.get_transitions(representative, symbol)
                if next_state:
                    from_group = state_to_group[representative]
                    to_group = state_to_group[next_state]
                    
                    if (from_group, symbol, to_group) not in added_transitions:
                        minimized.add_transition(from_group, symbol, to_group)
                        added_transitions.add((from_group, symbol, to_group))
        
        return minimized


class FAEquivalenceChecker:
    """Lớp để kiểm tra tương đương giữa các automata"""
    
    @staticmethod
    def are_dfa_equivalent(dfa1: DFA, dfa2: DFA) -> bool:
        """
        Kiểm tra xem hai DFA có tương đương không
        Hai DFA tương đương nếu chúng chấp nhận cùng một ngôn ngữ
        """
        # Tối thiểu hóa cả hai
        min1 = FAMinimizer.minimize_dfa(dfa1)
        min2 = FAMinimizer.minimize_dfa(dfa2)
        
        # So sánh cấu trúc
        # Kiểm tra bằng cách kiểm tra xem chúng chấp nhận các chuỗi giống nhau
        # (Đây là phương pháp đơn giản, trong thực tế có thể dùng phương pháp phức tạp hơn)
        
        # Sinh các chuỗi test từ alphabet
        test_strings = FAEquivalenceChecker._generate_test_strings(
            min1.alphabet | min2.alphabet, max_length=5
        )
        
        for string in test_strings:
            if min1.accepts_string(string) != min2.accepts_string(string):
                return False
        
        return True
    
    @staticmethod
    def _generate_test_strings(alphabet: Set[str], max_length: int = 3) -> List[str]:
        """Sinh các chuỗi test"""
        strings = ['']  # Chuỗi rỗng
        
        for length in range(1, max_length + 1):
            def generate(current, depth):
                if depth == 0:
                    strings.append(current)
                    return
                for symbol in alphabet:
                    generate(current + symbol, depth - 1)
            
            generate('', length)
        
        return strings
