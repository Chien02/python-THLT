from collections import deque, defaultdict

class AutomatonLayoutMixin:

    def _generate_state_positions(self, fa):
        """Tạo layout FA theo dạng layered BFS layout (đẹp, không chồng chéo)."""

        # --- 1. Lấy state bắt đầu ---
        start = fa.start_state
        fa.state_positions = {state: (0, 0) for state in fa.states}

        # --- 2. BFS để phân tầng ---
        layers = defaultdict(list)
        visited = set()
        queue = deque([(start, 0)])
        visited.add(start)

        while queue:
            state, depth = queue.popleft()
            layers[depth].append(state)

            # Duyệt tất cả next_state qua transition
            for (_, next_states) in fa.transitions.get(state, {}).items():
                for next_state in next_states:
                    if next_state not in visited:
                        visited.add(next_state)
                        queue.append((next_state, depth + 1))


        # --- 3. Đặt tọa độ ---
        x_offset = 150              # khoảng cách giữa các layer theo trục X
        y_step = 100                 # khoảng cách dọc giữa các node trong 1 layer
        x_start = 100               # vị trí cố định của state đầu tiên

        for depth, nodes in layers.items():
            x = x_start + depth * x_offset

            # Canh giữa theo màn hình
            total_height = (len(nodes) - 1) * y_step
            y_start = 800 // 2

            for i, state in enumerate(nodes):
                y = y_start + i * y_step
                fa.state_positions[state] = (x, y)
