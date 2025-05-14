class SimpleDebateEnv:
    def __init__(self, players, mediator, num_turns=3):
        self.player_names = []
        for player in players:
            self.player_names.append(player.name)
        self.player_names.append(mediator.name)
        self.current_turn = 0
        self.max_turns = num_turns
        self.history = []  # 存储所有对话记录
        self.next_player_index = 0

    def get_next_player(self):
        return self.player_names[self.next_player_index]

    def get_observation(self, player_name):
        return {
            "history": self.history,
        }

    def check_action(self, action, player_name):
        return isinstance(action, str) and len(action.strip()) > 0

    def step(self, player_name, action):
        self.history.append({"agent_name": player_name, "content": action})
        self.current_turn += 1
        self.next_player_index = (self.next_player_index + 1) % len(self.player_names)
            
        return {
            "observation": self.history,
            "terminal": self.current_turn >= self.max_turns * len(self.player_names),
        }
