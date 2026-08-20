
from typing import Dict, List, Set, Tuple
from kb import KnowledgeBase
from frame_lang import Frame, Slot

class RuleChecker:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb

    def _detect_cycles(self) -> List[List[str]]:
        graph = {name: fr.parents for name, fr in self.kb.frames.items()}
        visited: Set[str] = set()
        stack: Set[str] = set()
        cycles: List[List[str]] = []

        def dfs(v: str, path: List[str]):
            visited.add(v)
            stack.add(v)
            path.append(v)
            for u in graph.get(v, []):
                if u not in visited:
                    dfs(u, path)
                elif u in stack:
                    # цикл знайдено
                    i = path.index(u)
                    cycles.append(path[i:] + [u])
            stack.remove(v)
            path.pop()

        for node in graph:
            if node not in visited:
                dfs(node, [])
        return cycles

    def _check_slot_types(self) -> List[str]:
        errors: List[str] = []
        # примітивна перевірка: якщо у нащадка слот з тим же ім'ям і різним dtype
        for name, fr in self.kb.frames.items():
            for p in fr.parents:
                parent = self.kb.get_frame(p)
                if not parent:
                    continue
                for sname, s in fr.slots.items():
                    ps = parent.slots.get(sname)
                    if ps and ps.dtype != s.dtype:
                        errors.append(f"Type conflict for slot '{sname}' in '{name}' vs parent '{p}'")
        return errors

    def validate(self) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        cycles = self._detect_cycles()
        if cycles:
            errors.extend([f"Inheritance cycle: {' -> '.join(c)}" for c in cycles])
        errors.extend(self._check_slot_types())
        return (len(errors) == 0, errors)
