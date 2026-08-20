
from typing import List, Dict, Any, Callable, Optional
from kb import KnowledgeBase
from executor import Executor

class Query:
    def __init__(self,
                 frame_type: Optional[str] = None,
                 has_slots: Optional[Dict[str, Any]] = None):
        self.frame_type = frame_type
        self.has_slots = has_slots or {}

class SearchEngine:
    def __init__(self, kb: KnowledgeBase, ex: Executor):
        self.kb = kb
        self.ex = ex

    def _is_instance_of(self, frame_name: str, ftype: str) -> bool:
        # Перевірка за шляхом успадкування
        types = set(self.kb.inherit_type(frame_name))
        types.add(self.kb.get_frame_type(frame_name) or '')
        return ftype in types

    def search(self, query: Query) -> List[str]:
        results: List[str] = []
        for name, fr in self.kb.frames.items():
            if query.frame_type and not self._is_instance_of(name, query.frame_type):
                continue
            ok = True
            for sname, expected in query.has_slots.items():
                val = self.ex.get(name, sname)
                if callable(expected):
                    if not expected(val):
                        ok = False
                        break
                else:
                    if val != expected:
                        ok = False
                        break
            if ok:
                results.append(name)
        return results
