import numpy as np

ACTIONS = [0, 1, 2]
ACTION_NAMES = {0: "HOLD", 1: "BUY", 2: "SELL"}


class QLearningAgent:
    def __init__(
        self,
        n_actions=3,
        alpha=0.1,
        gamma=0.95,
        epsilon_start=1.0,
        epsilon_end=0.05,
        epsilon_decay=0.97,
        seed=42,
    ):
        self.n_actions = n_actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.rng = np.random.default_rng(seed)
        self.q_table = {}

    def get_q_values(self, state):
        key = tuple(state)
        if key not in self.q_table:
            self.q_table[key] = np.zeros(self.n_actions, dtype=float)
        return self.q_table[key]

    def select_action(self, state, training=True):
        q_values = self.get_q_values(state)
        if training and self.rng.random() < self.epsilon:
            return int(self.rng.integers(self.n_actions))
        if not training:
            return int(np.argmax(q_values))

        best_actions = np.flatnonzero(q_values == q_values.max())
        return int(self.rng.choice(best_actions))

    def update(self, state, action, reward, next_state):
        q_values = self.get_q_values(state)
        next_q_values = self.get_q_values(next_state)
        td_target = reward + self.gamma * float(next_q_values.max())
        q_values[action] += self.alpha * (td_target - q_values[action])

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)

    def learned_states(self):
        return len(self.q_table)

    def export_q_table(self, top_n=200):
        ranked_items = sorted(
            self.q_table.items(),
            key=lambda item: float(np.max(np.abs(item[1]))),
            reverse=True,
        )

        exported = []
        for state, q_values in ranked_items[:top_n]:
            exported.append(
                {
                    "state": list(state),
                    "q_values": [float(value) for value in q_values],
                    "best_action": ACTION_NAMES[int(np.argmax(q_values))],
                }
            )
        return exported
