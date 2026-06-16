from helpers.extension import Extension
from helpers import skills, tokens
from tools.skills_tool import DATA_NAME_LOADED_SKILLS
from agent import LoopData


SKILL_REATTACHMENT_TOKEN_BUDGET = 12_000
SKILL_REATTACHMENT_HEADER = (
    "Reattached loaded skill instructions after history compaction."
)


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
        loaded_skills = []
        for skill_name in skill_names:
            skill = skills.find_skill(skill_name, agent=self.agent)
            if not skill:
                continue
            visible_skill_names.append(skill.name)
            loaded_skills.append(skill)
        self.agent.data[DATA_NAME_LOADED_SKILLS] = visible_skill_names

        self._reattach_missing_skill_bodies(loop_data, loaded_skills)

    def _reattach_missing_skill_bodies(self, loop_data: LoopData, loaded_skills):
        if not self.agent or not loaded_skills:
            return

        visible_revisions = _visible_skill_revisions(loop_data.history_output)
        selected = []
        used_tokens = 0

        for skill in reversed(loaded_skills):
            skill_data = skills.load_skill_for_agent(
                skill_name=skill.name,
                agent=self.agent,
            )
            revision = skills.skill_revision(skill_data)
            if (skill.name, revision) in visible_revisions:
                continue

            message = f"{SKILL_REATTACHMENT_HEADER}\n\n{skill_data}"
            message_tokens = tokens.approximate_tokens(message)
            if used_tokens + message_tokens > SKILL_REATTACHMENT_TOKEN_BUDGET:
                continue

            selected.append((skill, revision, message))
            used_tokens += message_tokens

        for skill, revision, message in reversed(selected):
            history_message = self.agent.hist_add_tool_result(
                "skills_tool",
                message,
                skill_instructions={
                    "name": skill.name,
                    "path": str(skill.path),
                    "revision": revision,
                    "source": "skills_tool:reattach",
                    "content_included": True,
                },
            )
            loop_data.history_output.extend(history_message.output())


def _visible_skill_revisions(history_output) -> set[tuple[str, str]]:
    visible = set()
    for message in history_output or []:
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if not isinstance(content, dict):
            continue
        meta = content.get("skill_instructions")
        if not isinstance(meta, dict):
            continue
        if not meta.get("content_included"):
            continue
        name = str(meta.get("name") or "").strip()
        revision = str(meta.get("revision") or "").strip()
        if name and revision:
            visible.add((name, revision))
    return visible
