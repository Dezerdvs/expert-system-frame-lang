
from typing import Any, Callable, Dict, List, Optional
from kb import KnowledgeBase
from frame_lang import Demon, Slot

class Executor:
    """Виконуючий механізм/керування виводом.
    1) Приєднані процедури (демони) — на get/set/explicit call.
    2) Службові процедури — глобальні трансформації до/після доступу.
    3) Механізм успадкування — резолюція слотів через предків.
    """
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.pre_get_hooks: List[Callable[[str, str], None]] = []
        self.post_get_hooks: List[Callable[[str, str, Any], None]] = []

    # --- керування службовими процедурами ---
    def register_pre_get(self, fn: Callable[[str, str], None]):
        self.pre_get_hooks.append(fn)

    def register_post_get(self, fn: Callable[[str, str, Any], None]):
        self.post_get_hooks.append(fn)

    # --- доступ до слотів ---
    def get(self, frame_name: str, slot_name: str):
        for hook in self.pre_get_hooks:
            hook(frame_name, slot_name)
        val = self.kb.get_slot_value(frame_name, slot_name)  # тут спрацює demon.on_get або успадкування
        for hook in self.post_get_hooks:
            hook(frame_name, slot_name, val)
        return val

    def set(self, frame_name: str, slot_name: str, value: Any):
        # set може активувати demon.on_set або просто встановити значення
        return self.kb.set_slot_value(frame_name, slot_name, value)

    def call(self, frame_name: str, proc_name: str, **kwargs):
        fr = self.kb.get_frame(frame_name)
        if not fr:
            raise ValueError(f"No frame '{frame_name}'")
        proc = fr.attached.get(proc_name)
        if not proc:
            raise ValueError(f"No attached procedure '{proc_name}' on frame '{frame_name}'")
        return proc(fr, **kwargs)
