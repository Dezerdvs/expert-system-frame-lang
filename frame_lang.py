
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Типи даних для слотів
DataType = Union[type, str]  # str для доменних "типів" (наприклад 'Token', 'Sentence')

class Demon:
    """Демон (attached procedure): може спрацьовувати на get/set або окремий call."""
    def __init__(self,
                 on_get: Optional[Callable[['Frame','Slot'], Any]] = None,
                 on_set: Optional[Callable[['Frame','Slot', Any], Any]] = None,
                 on_call: Optional[Callable[['Frame', str, dict], Any]] = None):
        self.on_get = on_get
        self.on_set = on_set
        self.on_call = on_call

class Slot:
    def __init__(self,
                 name: str,
                 dtype: DataType = object,
                 value: Any = None,
                 optional: Optional[Dict[str, Any]] = None,
                 demon: Optional[Demon] = None):
        self.name = name
        self.dtype = dtype
        self.value = value
        self.optional = optional or {}
        self.demon = demon

class Frame:
    """Фрейм з підтримкою успадкування і приєднаних процедур (демонів)."""
    def __init__(self,
                 name: str,
                 ftype: str = "Any",            # ім'я типу фрейму
                 parents: Optional[List[str]] = None,  # імена батьків
                 attached: Optional[Dict[str, Callable]] = None):  # приєднані процедури
        self.name = name
        self.ftype = ftype
        self.parents = parents or []
        self.slots: Dict[str, Slot] = {}
        self.attached = attached or {}

    # --- робота зі слотами ---
    def define_slot(self, slot: Slot):
        self.slots[slot.name] = slot

    def has_slot_local(self, slot_name: str) -> bool:
        return slot_name in self.slots

    def get_slot_local(self, slot_name: str) -> Optional[Slot]:
        return self.slots.get(slot_name)

    # --- успадкування обробляється на рівні KB (де відомі батьки) ---
