class State:
    def __init__(self, players, mediator):
        self.players = players
        self.mediator = mediator
        print("=========各方自我介绍========")
        self.statement_history = ""
        self.make_statement()
        self.add_statement()
        

    def add_statement(self):
        self.mediator.add_statement_history(self.statement_history)
        for player in self.players:
            player.add_statement_history(self.statement_history)

    def make_statement(self):
        self.mediator.make_statement()
        
        print()
        player_statement = ""
        for player in self.players:
            player.make_statement()
            player_statement += f"""=====
{player.name}:
{player.statement}
"""
            print()
        self.statement_history = f"""【各方自我介绍开始】
=====
{self.mediator.name}: 
{self.mediator.statement}
{player_statement}
【各方自我介绍结束】
"""
