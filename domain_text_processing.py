from typing import List, Dict, Any
from kb import KnowledgeBase
from frame_lang import Demon
import re

def build_domain(kb: KnowledgeBase):
    # Базові типи
    kb.create_frame('Object', ftype='Object')
    kb.create_frame('LinguisticObject', ftype='LinguisticObject', parents=['Object'])
    kb.create_frame('Token', ftype='Token', parents=['LinguisticObject'])
    kb.create_frame('Sentence', ftype='Sentence', parents=['LinguisticObject'])
    kb.create_frame('Phrase', ftype='Phrase', parents=['LinguisticObject'])
    kb.create_frame('NounPhrase', ftype='NounPhrase', parents=['Phrase'])
    kb.create_frame('VerbPhrase', ftype='VerbPhrase', parents=['Phrase'])

    # Загальні слоти на LinguisticObject
    kb.create_slot('LinguisticObject', 'text', str, value=None)
    kb.create_slot('Token', 'pos', str, value=None)   # part-of-speech
    kb.create_slot('Token', 'lemma', str, value=None)

    # Демон для auto-lemma (на get): якщо lemma None — повернути text.lower()
    def auto_lemma_on_get(frame, slot):
        if slot.value:
            return slot.value
        text = frame.slots.get('text').value if 'text' in frame.slots else None
        return text.lower() if text else None

    kb.create_slot('Token', 'lemma', str, value=None, demon=Demon(on_get=auto_lemma_on_get))

    # Sentence має слоти tokens (список Token), phrases (список Phrase), has_verb (bool)
    kb.create_slot('Sentence', 'tokens', list, value=[])
    kb.create_slot('Sentence', 'phrases', list, value=[])
    kb.create_slot('Sentence', 'has_verb', bool, value=False)

    # --- Допоміжне: дуже просте визначення укр. дієслів за закінченнями ---
    UA_VERB_ENDINGS = ("уть","ють","ти","в","ла","ли","ло","є","еш","емо","ете","ють")
    EN_UA_VERB_LEXICON = {
        # англ.
        "is","are","was","were","be","being","been","am",
        "go","goes","went","see","saw","run","runs","ran",
        # укр. (мінімально)
        "буде","є","був","була","були","єсть"
    }
    def is_ua_verb(token: str) -> bool:
        tl = token.lower()
        return any(tl.endswith(suf) for suf in UA_VERB_ENDINGS)

    # Приєднана процедура до Sentence: parse -> токенізація + POS + has_verb
    def sentence_parse(fr, **kwargs):
        txt = fr.slots.get('text').value if 'text' in fr.slots else ''
        # \w+ або один небуквенно-пробільний символ (пунктуація)
        raw = re.findall(r"\w+|[^\w\s]", txt, re.UNICODE)
        tokens = []
        for t in raw:
            tok_name = f"Token:{t}:{id(fr)}:{len(tokens)}"
            kb.create_frame(tok_name, ftype='Token', parents=['Token'])
            kb.create_slot(tok_name, 'text', str, value=t)

            is_punct = bool(re.match(r"\W", t))
            is_verb  = (t.lower() in EN_UA_VERB_LEXICON) or is_ua_verb(t)
            pos = 'VERB' if is_verb else ('PUNCT' if is_punct else 'WORD')
            kb.create_slot(tok_name, 'pos', str, value=pos)

            tokens.append(tok_name)

        kb.set_slot_value(fr.name, 'tokens', tokens)
        kb.set_slot_value(fr.name, 'has_verb',
                          any(kb.get_slot_value(t, 'pos') == 'VERB' for t in tokens))
        return tokens

    sent_proto = kb.get_frame('Sentence')
    sent_proto.attached['parse'] = sentence_parse

    # Демон для побудови фраз NP/VP при першому зверненні
    def phrases_on_get(frame, slot):
        if slot.value:
            return slot.value
        tokens = kb.get_slot_value(frame.name, 'tokens') or []
        noun_phrase, verb_phrase = [], []
        for t in tokens:
            (verb_phrase if kb.get_slot_value(t, 'pos') == 'VERB' else noun_phrase).append(t)

        fr_np = f"NP:{frame.name}"
        if not kb.get_frame(fr_np):
            kb.create_frame(fr_np, ftype='NounPhrase', parents=['NounPhrase'])
            kb.create_slot(fr_np, 'tokens', list, value=noun_phrase)

        fr_vp = f"VP:{frame.name}"
        if not kb.get_frame(fr_vp):
            kb.create_frame(fr_vp, ftype='VerbPhrase', parents=['VerbPhrase'])
            kb.create_slot(fr_vp, 'tokens', list, value=verb_phrase)

        slot.value = [fr_np, fr_vp]
        return slot.value

    from frame_lang import Slot
    sent_proto.define_slot(Slot('phrases', list, value=[], demon=Demon(on_get=phrases_on_get)))

    return kb
