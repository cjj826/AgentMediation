import logging
import time
from src.chat import *

class SimpleArena:
    def __init__(self, players, mediator, stage, environment, adaptive):
        self.players = players
        self.environment = environment
        self.stage = stage
        self.name_to_player = {p.name: p for p in self.players}
        self.name_to_player[mediator.name] = mediator
        self.invalid_actions_retry = 3
        self.adaptive = adaptive


    def step(self):
        player_name = self.environment.get_next_player()
        player = self.name_to_player[player_name]
        observation = self.environment.get_observation(player_name)
        for attempt in range(self.invalid_actions_retry):
            try:
                action = player(observation, self.stage)
            except Exception as e:
                logging.warning(f"Error during player {player_name} generation: {e}")
                continue

            if self.environment.check_action(action, player_name):
                timestep = self.environment.step(player_name, action)
                return timestep
            else:
                logging.warning(f"Invalid action from {player_name}: {action}")

        raise RuntimeError(f"Player {player_name} failed to generate valid action after {self.invalid_actions_retry} tries")

    def launch_cli(self, interactive=False, show_all=False):
        if self.stage == 3:
            print("=====情感宣泄阶段=====")
        elif self.stage == 5:
            print("=====理性协商阶段=====")
        round_counter = 1
        while True:
            timestep = self.step()
            messages = timestep.get("observation", [])

            print(f"\n🌀 Round {(round_counter - 1) // (len(self.players) + 1)}\n")

            display_msgs = messages if show_all else messages[-1:]

            for msg in display_msgs:
                name = msg["agent_name"]
                content = msg["content"].strip()
                print(f"{name}: {content}")

            if interactive:
                input("⏎ 按 Enter 键继续下一轮...")
            else:
                time.sleep(0.5) 
            
            if round_counter % (len(self.players) + 1) == 0:
                if self.adaptive:
                    for p in self.players:
                        p.update_state(messages)
                        print(f"{p.name}: {p.state}")

            if timestep.get("terminal", False):
                history = ""
                for msg in messages:
                    name = msg["agent_name"]
                    content = msg["content"].strip()
                    history += f"{name}: {content}\n"
                return history, messages
            round_counter += 1