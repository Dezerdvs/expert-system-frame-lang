
from typing import Any, Dict, List, Optional
from frame_lang import Frame, Slot, Demon

class KnowledgeBase:
    def __init__(self):
        self.frames: Dict[str, Frame] = {}

    # === Функції управління кадрами (створення, знищення, отримання, тип, слоти, успадкування) ===
    def create_frame(self, name: str, ftype: str = "Any", parents: Optional[List[str]] = None) -> Frame:
        if name in self.frames:
            raise ValueError(f"Frame '{name}' already exists")
        fr = Frame(name=name, ftype=ftype, parents=parents or [])
        self.frames[name] = fr
        return fr

    def destroy_frame(self, name: str) -> None:
        self.frames.pop(name, None)

    def get_frame(self, name: str) -> Optional[Frame]:
        return self.frames.get(name)

    def get_frame_type(self, name: str) -> Optional[str]:
        fr = self.get_frame(name)
        return fr.ftype if fr else None

    def list_slot_names(self, name: str) -> List[str]:
        fr = self.get_frame(name)
        if not fr:
            return []
        # включає успадковані слоти
        names = set(fr.slots.keys())
        for p in fr.parents:
            names.update(self.list_slot_names(p))
        return sorted(names)

    def inherit_type(self, name: str) -> List[str]:
        fr = self.get_frame(name)
        if not fr:
            return []
        path = [fr.ftype]
        for p in fr.parents:
            path.extend(self.inherit_type(p))
        return path

    def set_subclass(self, child: str, parent: str) -> None:
        fr = self.get_frame(child)
        if not fr:
            raise ValueError(f"No frame '{child}'")
        if parent not in fr.parents:
            fr.parents.append(parent)

    def define_hierarchy(self) -> Dict[str, List[str]]:
        tree: Dict[str, List[str]] = {}
        for name, fr in self.frames.items():
            for p in fr.parents:
                tree.setdefault(p, []).append(name)
            tree.setdefault(name, [])
        return tree

    # === Функції управління слотами ===
    def create_slot(self, frame_name: str, slot_name: str, dtype=object, value=None, optional=None, demon: Demon=None):
        fr = self.get_frame(frame_name)
        if not fr:
            raise ValueError(f"No frame '{frame_name}'")
        fr.define_slot(Slot(slot_name, dtype, value, optional, demon))

    def destroy_slot(self, frame_name: str, slot_name: str):
        fr = self.get_frame(frame_name)
        if fr and slot_name in fr.slots:
            del fr.slots[slot_name]

    def _resolve_slot(self, frame_name: str, slot_name: str) -> Optional[Slot]:
        fr = self.get_frame(frame_name)
        if not fr:
            return None
        if slot_name in fr.slots:
            return fr.slots[slot_name]
        # пошук у батьках (успадкування)
        for p in fr.parents:
            s = self._resolve_slot(p, slot_name)
            if s:
                return s
        return None

    def get_slot(self, frame_name: str, slot_name: str):
        s = self._resolve_slot(frame_name, slot_name)
        return s

    def get_slot_value(self, frame_name: str, slot_name: str):
        s = self._resolve_slot(frame_name, slot_name)
        if not s:
            return None
        # демон on_get
        fr = self.get_frame(frame_name)
        if s.demon and s.demon.on_get:
            return s.demon.on_get(fr, s)
        return s.value

    def set_slot_value(self, frame_name: str, slot_name: str, value):
        s = self._resolve_slot(frame_name, slot_name)
        if not s:
            raise ValueError(f"No slot '{slot_name}' on frame '{frame_name}'")
        fr = self.get_frame(frame_name)
        if s.demon and s.demon.on_set:
            s.demon.on_set(fr, s, value)
        else:
            s.value = value

    def set_slot_optional(self, frame_name: str, slot_name: str, key: str, value):
        s = self._resolve_slot(frame_name, slot_name)
        if not s:
            raise ValueError(f"No slot '{slot_name}' on frame '{frame_name}'")
        s.optional[key] = value

    def get_slot_optional(self, frame_name: str, slot_name: str, key: str, default=None):
        s = self._resolve_slot(frame_name, slot_name)
        if not s:
            return default
        return s.optional.get(key, default)
