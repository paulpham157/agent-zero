from helpers.extension import Extension
from helpers import skills
from tools.skills_tool import DATA_NAME_LOADED_SKILLS
from agent import LoopData


class IncludeLoadedSkills(Extension):
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        if not self.agent:
            return

        loop_data.extras_persistent.pop("loaded_skills", None)
        skill_names = self.agent.data.get(DATA_NAME_LOADED_SKILLS)
        if not skill_names:
            return

        # `skills_tool load` now appends full skill instructions as a normal
        # tool-result history message. Keep this legacy ledger pruned, but do
        # not reinject loaded skills through prompt extras every turn.
        visible_skill_names = []
        for skill_name in skill_names:
            if not skills.find_skill(skill_name, agent=self.agent):
                continue
            visible_skill_names.append(skill_name)
        self.agent.data[DATA_NAME_LOADED_SKILLS] = visible_skill_names
