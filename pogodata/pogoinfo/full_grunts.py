class FullGrunt:
    def __init__(self, data):
        self.active = data.get("active", False)
        self.character = None
        self.team = []
        self.__reward_positions = data.get("lineup", {}).get("rewards", [])

    @property
    def rewards(self):
        rewards = []
        for index in self.__reward_positions:
            rewards += self.team[index]
        return rewards