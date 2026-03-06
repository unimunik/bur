import random
import re
from typing import Iterable, List

MEME_TEMPLATES = [
    "это звучит как план, который придумали в 3 ночи",
    "брат, ты сейчас сломал логику реальности",
    "чат официально вышел из-под контроля",
    "я записал это в архив кринжа",
    "в параллельной вселенной это уже стало законом",
    "срочно в учебники по абсурдологии",
    "я бы ответил нормально, но мем победил",
    "мы случайно открыли портал в отдел странных идей",
]

PREFIXES = [
    "вердикт:",
    "мнение бота:",
    "бур говорит:",
    "официально:",
    "по данным мем-радаров:",
]

PHILOSOPHY = [
    "если смысл потерян — значит началась магия",
    "иногда хаос — это просто креатив без дедлайна",
    "кринж сегодня, легенда завтра",
    "разум молчит, мемы говорят",
]


class MemeGenerator:
    """Генератор абсурдных и мемных фраз на основе сообщений."""

    def __init__(self) -> None:
        self.word_re = re.compile(r"[\w\-]{3,}", flags=re.UNICODE)

    def _extract_keywords(self, messages: Iterable[str], limit: int = 6) -> List[str]:
        words: List[str] = []
        for text in messages:
            words.extend([w.lower() for w in self.word_re.findall(text)])

        if not words:
            return []

        unique = list(dict.fromkeys(words))
        random.shuffle(unique)
        return unique[:limit]

    def random_phrase(self) -> str:
        choices = MEME_TEMPLATES + PHILOSOPHY
        return random.choice(choices)

    def chaos_distort(self, text: str) -> str:
        """Слегка искажает слово для режима хаоса."""
        if len(text) < 5:
            return text
        idx = random.randint(1, len(text) - 2)
        return text[:idx] + random.choice("ааееииооуу") + text[idx + 1 :]

    def generate_from_messages(self, messages: List[str], chaos_mode: bool = False) -> str:
        if not messages:
            return self.random_phrase()

        keywords = self._extract_keywords(messages)
        prefix = random.choice(PREFIXES)
        meme_tail = random.choice(MEME_TEMPLATES)

        if not keywords:
            base = f"{prefix} {meme_tail}"
        else:
            sampled = random.sample(keywords, k=min(len(keywords), random.randint(2, 4)))
            glue = " • ".join(sampled)
            base = f"{prefix} {glue} — {meme_tail}"

        if chaos_mode and keywords and random.random() < 0.6:
            word = random.choice(keywords)
            base += f". особенно слово «{self.chaos_distort(word)}»"

        if random.random() < 0.35:
            base += f"\n{random.choice(PHILOSOPHY)}"

        return base
