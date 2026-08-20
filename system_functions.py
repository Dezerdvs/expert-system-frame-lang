
from typing import Any, Dict, List, Callable, Optional, Iterable, Set
from frame_lang import Demon
from kb import KnowledgeBase

# === Службові / системні функції ===

# a) Функції управління кадрами
def create_frame(kb: KnowledgeBase, name: str, ftype: str = "Any", parents=None):
    return kb.create_frame(name, ftype, parents)

def destroy_frame(kb: KnowledgeBase, name: str):
    return kb.destroy_frame(name)

def get_frame(kb: KnowledgeBase, name: str):
    return kb.get_frame(name)

def get_frame_type(kb: KnowledgeBase, name: str):
    return kb.get_frame_type(name)

def list_slot_names(kb: KnowledgeBase, name: str):
    return kb.list_slot_names(name)

def inherit_type(kb: KnowledgeBase, name: str):
    return kb.inherit_type(name)

def set_subclass(kb: KnowledgeBase, child: str, parent: str):
    return kb.set_subclass(child, parent)

def define_hierarchy(kb: KnowledgeBase):
    return kb.define_hierarchy()

# b) Функції управління слотами
def create_slot(kb: KnowledgeBase, frame_name: str, slot_name: str, dtype=object, value=None, optional=None, demon: Demon=None):
    return kb.create_slot(frame_name, slot_name, dtype, value, optional, demon)

def destroy_slot(kb: KnowledgeBase, frame_name: str, slot_name: str):
    return kb.destroy_slot(frame_name, slot_name)

def get_slot(kb: KnowledgeBase, frame_name: str, slot_name: str):
    return kb.get_slot(frame_name, slot_name)

def get_value(kb: KnowledgeBase, frame_name: str, slot_name: str):
    return kb.get_slot_value(frame_name, slot_name)

def set_value(kb: KnowledgeBase, frame_name: str, slot_name: str, value):
    return kb.set_slot_value(frame_name, slot_name, value)

def get_opt(kb: KnowledgeBase, frame_name: str, slot_name: str, key: str, default=None):
    return kb.get_slot_optional(frame_name, slot_name, key, default)

def set_opt(kb: KnowledgeBase, frame_name: str, slot_name: str, key: str, value):
    return kb.set_slot_optional(frame_name, slot_name, key, value)

# c) Виклик іншого фрейму (приєднана процедура)
def call_attached(kb: KnowledgeBase, frame_name: str, proc_name: str, **kwargs):
    fr = kb.get_frame(frame_name)
    if not fr:
        raise ValueError(f"No frame '{frame_name}'")
    proc = fr.attached.get(proc_name)
    if not proc:
        raise ValueError(f"No attached procedure '{proc_name}' on frame '{frame_name}'")
    return proc(fr, **kwargs)

# d) Функції перевірки
def is_frame_defined(kb: KnowledgeBase, name: str) -> bool:
    return kb.get_frame(name) is not None

def validate_type(value, expected) -> bool:
    if isinstance(expected, str):
        # очікуємо ім'я типу фрейму — не перевіряємо тут, робить RuleChecker
        return True
    try:
        return isinstance(value, expected)
    except Exception:
        return False

def is_function_registered(kb: KnowledgeBase, frame_name: str, func_name: str) -> bool:
    fr = kb.get_frame(frame_name)
    return bool(fr and func_name in fr.attached)

# e) Інші
def shallow_list(lst: List[Any]) -> List[Any]:
    """Складання списку одиничної глибини (flatten на 1 рівень)."""
    out = []
    for x in lst:
        if isinstance(x, list):
            out.extend(x)
        else:
            out.append(x)
    return out

def write_to_file(path: str, data: str) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)

def list_intersection(a: Iterable[Any], b: Iterable[Any]) -> List[Any]:
    sa: Set[Any] = set(a)
    sb: Set[Any] = set(b)
    return list(sa.intersection(sb))
