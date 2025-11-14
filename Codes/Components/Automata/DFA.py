class DFA:
    def __init__(self, states: list, characters: list, start_state, end_states: list, transitions: dict = None):
        self.states = states
        self.characters = characters
        self.start_state = start_state
        self.end_states = end_states
        self.transitions = transitions
        self.diagram_string = ''
    
    def init_transitions(self):
        if self.transitions: return

        # Remember that diagram_string is the main thing that would be used
        self.transitions = dict()
        for i in range(0, len(self.characters)):
            self.transitions[(str(i), self.characters[i])] =  str(i+1)
            self.diagram_string += str(i) + self.characters[i]
        self.transitions[(str(i+1), '')] =  ''
        self.diagram_string += str(i+1)
        print("diagram's string: " + self.diagram_string)

    def print_transition(self):
        print(self.transitions)
        


