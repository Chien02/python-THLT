from collections import deque, defaultdict

class AutomatonLayoutMixin:
    def _generate_state_positions(self, fa):
        """Tạo layout FA theo dạng layered BFS layout"""
        self.screen_size = fa.screen_size
        # --- 1. Lấy state bắt đầu ---
        start = fa.start_state
        fa.state_positions = {state: (0, 0) for state in fa.states} # Khởi tạo dict state_position với tọa độ khởi tạo của các state là (0, 0)

        # --- 2. BFS để phân tầng ---
        layers = defaultdict(list)
        visited = set()
        queue = deque([(start, 0)])
        visited.add(start)

        while queue:
            state, depth = queue.popleft()
            layers[depth].append(state)

            # Duyệt tất cả next_state qua transition
            for next_states in fa.transitions.get(state, {}).values():
                for next_state in next_states:
                    if next_state not in visited:
                        visited.add(next_state)
                        queue.append((next_state, depth + 1))


         # --- 3. Đặt tọa độ ---
        center = (self.screen_size[0] // 2, self.screen_size[1] // 2)
        y_step = 170                   # khoảng cách dọc giữa các node trong 1 layer
        fixed_y_start = center[1] // 3 # vị trí cố định nếu tính toán bị âm

        x_offset = 150                 # khoảng cách giữa các layer theo trục X
        
        # FIX: Tính khoảng cách thực tế từ layer đầu đến layer cuối
        # Nếu có n layers, có (n-1) khoảng cách
        num_layers = len(layers)
        if num_layers == 1:
            total_width = 0
        else:
            total_width = (num_layers - 1) * x_offset
        
        x_start = center[0] - total_width // 2
        print(f"From LayoutMixin: len(layers) = {num_layers} total_width = {total_width} and x_start at: {x_start}")

        for depth, nodes in layers.items():
            x = x_start + depth * x_offset

            # Canh giữa theo màn hình
            total_height = (len(nodes) - 1) * y_step
            y_start = max(center[1] - total_height // 2, fixed_y_start)

            for i, state in enumerate(nodes):
                y = y_start + i * y_step
                fa.state_positions[state] = (x, y)