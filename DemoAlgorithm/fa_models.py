"""
FA Models - Định nghĩa các lớp đại diện cho DFA, NFA, ε-NFA
"""

from typing import Set, Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class State:
    """Đại diện cho một trạng thái trong automata"""
    name: str
    is_start: bool = False
    is_accept: bool = False
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if isinstance(other, State):
            return self.name == other.name
        return False
    
    def __repr__(self):
        markers = []
        if self.is_start:
            markers.append("START")
        if self.is_accept:
            markers.append("ACCEPT")
        markers_str = f" [{','.join(markers)}]" if markers else ""
        return f"State({self.name}{markers_str})"


@dataclass
class Transition:
    """Đại diện cho một chuyển tiếp"""
    from_state: str
    symbol: str
    to_states: Set[str]  # Có thể có nhiều trạng thái (cho NFA)
    
    def __repr__(self):
        to_str = ','.join(sorted(self.to_states))
        return f"{self.from_state} --{self.symbol}--> {{{to_str}}}"


class FiniteAutomata(ABC):
    """Lớp cơ sở cho tất cả các loại automata"""
    
    def __init__(self):
        self.states: Dict[str, State] = {}
        self.alphabet: Set[str] = set()
        self.transitions: Dict[str, Dict[str, Set[str]]] = {}
        self.start_state: Optional[str] = None
        self.accept_states: Set[str] = set()
    
    def add_state(self, name: str, is_start: bool = False, is_accept: bool = False):
        """Thêm một trạng thái"""
        if name not in self.states:
            self.states[name] = State(name, is_start, is_accept)
            if is_start:
                self.start_state = name
            if is_accept:
                self.accept_states.add(name)
    
    def add_transition(self, from_state: str, symbol: str, to_state: str):
        """Thêm một chuyển tiếp"""
        if from_state not in self.transitions:
            self.transitions[from_state] = {}
        if symbol not in self.transitions[from_state]:
            self.transitions[from_state][symbol] = set()
        
        self.transitions[from_state][symbol].add(to_state)
        self.alphabet.add(symbol)
    
    def get_transitions(self, state: str, symbol: str) -> Set[str]:
        """Lấy tập hợp trạng thái tiếp theo từ một trạng thái với một ký tự"""
        if state not in self.transitions:
            return set()
        if symbol not in self.transitions[state]:
            return set()
        return self.transitions[state][symbol].copy()
    
    def accepts_string(self, string: str) -> bool:
        """Kiểm tra xem automata có chấp nhận chuỗi không"""
        raise NotImplementedError("Subclass must implement this method")
    
    def to_dict(self) -> dict:
        """Chuyển đổi automata thành dictionary"""
        transitions_list = []
        for from_state in self.transitions:
            for symbol in self.transitions[from_state]:
                for to_state in self.transitions[from_state][symbol]:
                    transitions_list.append({
                        'from': from_state,
                        'symbol': symbol,
                        'to': to_state
                    })
        
        return {
            'states': [{'name': s.name, 'start': s.is_start, 'accept': s.is_accept} 
                      for s in self.states.values()],
            'alphabet': sorted(list(self.alphabet)),
            'transitions': transitions_list,
            'start_state': self.start_state,
            'accept_states': sorted(list(self.accept_states)),
            'type': self.__class__.__name__
        }
    
    def __repr__(self):
        return f"{self.__class__.__name__}(states={len(self.states)}, transitions={sum(len(v) for v in self.transitions.values())})"


class DFA(FiniteAutomata):
    """
    Deterministic Finite Automata (Automata Hữu hạn Xác định)
    - Từ mỗi trạng thái, với mỗi ký tự có đúng 1 chuyển tiếp
    """
    
    def get_transitions(self, state: str, symbol: str) -> str:
        """Trong DFA, trả về đúng 1 trạng thái (hoặc None)"""
        if state not in self.transitions:
            return None
        if symbol not in self.transitions[state]:
            return None
        return next(iter(self.transitions[state][symbol]))
    
    def accepts_string(self, string: str) -> bool:
        """Kiểm tra xem DFA chấp nhận chuỗi"""
        current_state = self.start_state
        
        for symbol in string:
            if symbol not in self.alphabet:
                return False
            next_state = self.get_transitions(current_state, symbol)
            if next_state is None:
                return False
            current_state = next_state
        
        return current_state in self.accept_states
    
    def trace_string(self, string: str) -> List[Tuple[str, str, str]]:
        """Theo dõi đường đi của chuỗi qua DFA - trả về danh sách (state, symbol, next_state)"""
        trace = []
        current_state = self.start_state
        
        for symbol in string:
            if symbol not in self.alphabet:
                break
            next_state = self.get_transitions(current_state, symbol)
            if next_state is None:
                break
            trace.append((current_state, symbol, next_state))
            current_state = next_state
        
        return trace


class NFA(FiniteAutomata):
    """
    Non-deterministic Finite Automata (Automata Hữu hạn Không xác định)
    - Từ mỗi trạng thái, với mỗi ký tự có thể có 0, 1 hoặc nhiều chuyển tiếp
    """
    
    def get_transitions(self, state: str, symbol: str) -> Set[str]:
        """Trong NFA, trả về tập hợp các trạng thái"""
        if state not in self.transitions:
            return set()
        if symbol not in self.transitions[state]:
            return set()
        return self.transitions[state][symbol].copy()
    
    def accepts_string(self, string: str) -> bool:
        """Kiểm tra xem NFA chấp nhận chuỗi (sử dụng BFS/DFS)"""
        current_states = {self.start_state}
        
        for symbol in string:
            if symbol not in self.alphabet:
                return False
            
            next_states = set()
            for state in current_states:
                next_states.update(self.get_transitions(state, symbol))
            
            if not next_states:
                return False
            current_states = next_states
        
        # Kiểm tra xem có bất kỳ trạng thái kết thúc nào trong current_states
        return bool(current_states & self.accept_states)
    
    def trace_string(self, string: str) -> Dict[str, List[Tuple[str, str, str]]]:
        """Theo dõi tất cả các đường đi của chuỗi qua NFA"""
        all_traces = {self.start_state: []}
        
        for symbol in string:
            if symbol not in self.alphabet:
                break
            
            next_traces = {}
            for from_state, trace in all_traces.items():
                for to_state in self.get_transitions(from_state, symbol):
                    new_trace = trace + [(from_state, symbol, to_state)]
                    if to_state not in next_traces:
                        next_traces[to_state] = new_trace
                    else:
                        next_traces[to_state] = new_trace
            
            all_traces = next_traces
        
        return all_traces


class EpsilonNFA(FiniteAutomata):
    """
    Epsilon-NFA (Automata Hữu hạn Không xác định với chuyển tiếp ε)
    - Tương tự NFA nhưng cho phép chuyển tiếp với ký tự rỗng (epsilon)
    """
    
    def __init__(self):
        super().__init__()
        self.epsilon_transitions: Dict[str, Set[str]] = {}
    
    def add_epsilon_transition(self, from_state: str, to_state: str):
        """Thêm một chuyển tiếp epsilon"""
        if from_state not in self.epsilon_transitions:
            self.epsilon_transitions[from_state] = set()
        self.epsilon_transitions[from_state].add(to_state)
    
    def epsilon_closure(self, states: Set[str]) -> Set[str]:
        """Tính epsilon-closure (bao đóng epsilon) của một tập hợp trạng thái"""
        closure = set(states)
        stack = list(states)
        
        while stack:
            state = stack.pop()
            if state in self.epsilon_transitions:
                for next_state in self.epsilon_transitions[state]:
                    if next_state not in closure:
                        closure.add(next_state)
                        stack.append(next_state)
        
        return closure
    
    def get_transitions(self, state: str, symbol: str) -> Set[str]:
        """Lấy tất cả các trạng thái có thể đạt được với ký tự (tính epsilon-closure)"""
        if state not in self.transitions:
            direct_transitions = set()
        else:
            if symbol not in self.transitions[state]:
                direct_transitions = set()
            else:
                direct_transitions = self.transitions[state][symbol].copy()
        
        return direct_transitions
    
    def accepts_string(self, string: str) -> bool:
        """Kiểm tra xem ε-NFA chấp nhận chuỗi"""
        # Bắt đầu từ epsilon-closure của trạng thái khởi đầu
        current_states = self.epsilon_closure({self.start_state})
        
        for symbol in string:
            if symbol not in self.alphabet:
                return False
            
            next_states = set()
            for state in current_states:
                next_states.update(self.get_transitions(state, symbol))
            
            if not next_states:
                return False
            
            # Tính epsilon-closure của các trạng thái tiếp theo
            current_states = self.epsilon_closure(next_states)
        
        # Kiểm tra xem có bất kỳ trạng thái kết thúc nào trong current_states
        return bool(current_states & self.accept_states)
    
    def to_dict(self) -> dict:
        """Chuyển đổi ε-NFA thành dictionary"""
        result = super().to_dict()
        epsilon_trans = []
        for from_state in self.epsilon_transitions:
            for to_state in self.epsilon_transitions[from_state]:
                epsilon_trans.append({
                    'from': from_state,
                    'to': to_state
                })
        result['epsilon_transitions'] = epsilon_trans
        return result
