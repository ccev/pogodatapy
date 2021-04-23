from enum import Enum

from .misc import httpget, INFO_URL, match_enum


class QuestType(Enum):
    UNSET = 0
    REGULAR = 1
    EVENT = 2
    SPONSORED = 3
    AR = 4


TYPE_CONVERSION = {
    "quests": QuestType.REGULAR,
    "event": QuestType.EVENT,
    "sponsored": QuestType.SPONSORED,
    "ar": QuestType.AR
}


REWARD_TYPE_CONVERSION = {
    "pokemon": "pokemon_encounter",
    "energy": "mega_resource"
}


class GenericReward:
    def __str__(self):
        return "GenericReward"

    def __bool__(self):
        return True


class Quest:
    def __init__(self, task="", quest_type=QuestType.UNSET):
        self.task = task
        self.type = quest_type

        self.rewards = []

    def __str__(self):
        return self.task

    def __bool__(self):
        return bool(self.type.value)


def _make_quest_list(pogodata):
    info_quests = httpget(INFO_URL + "active/quests.json").json()
    reward_types = pogodata.get_enum("Type", message="QuestRewardProto", as_enum=True)
    pogodata.quests = []

    for quest_type, quests in info_quests.items():
        quest_type = TYPE_CONVERSION.get(quest_type, QuestType(0))
        for raw_quest in quests:
            task = raw_quest["task"]
            quest = Quest(task, quest_type)

            for raw_reward in raw_quest["rewards"]:
                raw_type = raw_reward["type"]
                raw_type = REWARD_TYPE_CONVERSION.get(raw_type, raw_type)
                reward_type = match_enum(reward_types, raw_type)

                if reward_type in (reward_types.POKEMON_ENCOUNTER, reward_types.MEGA_RESOURCE):
                    reward_args = raw_reward["reward"]
                    reward = pogodata.get_mon(**reward_args).copy()
                elif reward_type == reward_types.ITEM:
                    reward = pogodata.get_item(id=raw_reward["id"]).copy()
                else:
                    reward = GenericReward()

                if reward_type in (reward_types.STARDUST, reward_types.ITEM):
                    reward.amount = raw_reward.get("amount", 0)

                reward.reward_type = reward_type

                quest.rewards.append(reward)

            pogodata.quests.append(quest)
