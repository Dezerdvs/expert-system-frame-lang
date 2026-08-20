
from kb import KnowledgeBase
from executor import Executor
from system_functions import define_hierarchy, list_slot_names
from rule_checker import RuleChecker
from domain_text_processing import build_domain
from search_engine import SearchEngine, Query

def ensure_parsed_factory(kb):
    """pre_get: перед читанням 'tokens' знаходимо та викликаємо 'parse'
    у самому фреймі або будь-якому з його предків (успадкування)."""

    def _resolve_attached(frame_name: str, proc: str):
        visited = set()
        def dfs(fname: str):
            if not fname or fname in visited:
                return None
            visited.add(fname)
            fr = kb.get_frame(fname)
            if not fr:
                return None
            if proc in fr.attached:
                return fr.attached[proc]
            for p in fr.parents:
                got = dfs(p)
                if got:
                    return got
            return None
        return dfs(frame_name)

    def ensure_parsed(frame_name, slot_name):
        if slot_name != 'tokens':
            return
        fr = kb.get_frame(frame_name)
        if not fr:
            return
        proc = _resolve_attached(frame_name, 'parse')
        if proc:
            proc(fr)  # викликаємо parse, знайдений у предках
    return ensure_parsed

def pretty_sentence_dump(kb, ex, fname: str):
    print(f"\n=== Фрейм речення: {fname} ===")
    print("Типи (успадкування):", kb.inherit_type(fname))

    # Отримання токенів (спрацює службова процедура pre_get -> parse)
    tokens = ex.get(fname, 'tokens') or []
    print("Tokens:", [kb.get_slot_value(t, 'text') for t in tokens])

    # Демонстрація демонів: lemma.on_get (авто-лематизація)
    lemmas = [ex.get(t, 'lemma') for t in tokens]
    pos = [ex.get(t, 'pos') for t in tokens]
    print("POS:", pos)
    print("Lemma (демон on_get):", lemmas)

    # Демонстрація демона на фразах (phrases.on_get)
    phrases = ex.get(fname, 'phrases') or []
    np_tokens = []
    vp_tokens = []
    for p in phrases:
        ptype = kb.get_frame_type(p)
        toks = [kb.get_slot_value(t, 'text') for t in (kb.get_slot_value(p, 'tokens') or [])]
        if ptype == 'NounPhrase':
            np_tokens = toks
        elif ptype == 'VerbPhrase':
            vp_tokens = toks
    print("Phrases (on_get): NounPhrase ->", np_tokens, "; VerbPhrase ->", vp_tokens)

    # Прапорець наявності дієслова
    print("has_verb:", ex.get(fname, 'has_verb'))

    # Показати доступні слоти (включно з успадкованими)
    print("Слоти (включно з успадкованими):", list_slot_names(kb, fname))

def interactive_demo():
    kb = KnowledgeBase()
    build_domain(kb)
    ex = Executor(kb)

    # Реєструємо службовий hook
    ex.register_pre_get(ensure_parsed_factory(kb))

    # Перевіряємо правила
    ok, errs = RuleChecker(kb).validate()
    print('KB valid:', ok)
    if not ok:
        print('Errors:', errs)

    engine = SearchEngine(kb, ex)
    counter = 1

    print("\n=== Інтерактивний режим ===")
    print("Введи речення українською або англійською. Порожній ввід — вихід.\n")
    while True:
        try:
            text = input("> ").strip()
        except EOFError:
            break
        if not text:
            break

        fname = f"Sentence_{counter}"
        counter += 1

        # створюємо фрейм речення і задаємо слот 'text'
        fr = kb.create_frame(fname, ftype='Sentence', parents=['Sentence'])
        kb.create_slot(fname, 'text', str, value=text)

        # друкуємо розбір і показ механізмів
        pretty_sentence_dump(kb, ex, fname)

        # Пошук усіх речень з дієсловом і токенами
        q = Query(
            frame_type='Sentence',
            has_slots={'has_verb': True, 'tokens': lambda v: isinstance(v, list) and len(v) > 0}
        )
        res = engine.search(q)

        print("\n=== Пошук речень з дієсловом ===")
        if not res:
            print("Знайдено: 0")
        else:
            print(f"Знайдено: {len(res)}")
            for name in res:
                txt = kb.get_slot_value(name, 'text')
                toks = kb.get_slot_value(name, 'tokens') or []
                print(f" • {name}: \"{txt}\"  (tokens={len(toks)})")

        # Показати фрагмент ієрархії (кореневі вузли)
        print("\n=== Ієрархія (фрагмент) ===")
        print(define_hierarchy(kb))

    print("\nГотово. До зустрічі!\n")

if __name__ == '__main__':
    interactive_demo()
