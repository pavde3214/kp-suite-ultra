from difflib import get_close_matches
DEFAULT_SECTIONS = [
    "Оборудование", "Вентиляция", "Кондиционирование",
    "Электрика", "Сантехника", "Изоляция", "Управление и автоматика"
]
KEYWORDS2SECTION = {
    "вентилятор": "Вентиляция", "канал": "Вентиляция", "решетка": "Вентиляция",
    "lg": "Кондиционирование", "vrf": "Кондиционирование",
    "кабель": "Электрика", "автомат": "Электрика",
    "насос": "Сантехника", "изоляц": "Изоляция",
    "контроллер": "Управление и автоматика", "датчик": "Управление и автоматика",
}
def suggest_sections_from_text(text: str) -> list[str]:
    text_l = text.lower(); found = {sec for k, sec in KEYWORDS2SECTION.items() if k in text_l}
    return list(found) or DEFAULT_SECTIONS[:3]
def fuzzy_category(name: str, catalog: list[str]) -> str | None:
    m = get_close_matches(name, catalog, n=1, cutoff=0.6); return m[0] if m else None
