# -*- coding: utf-8 -*-
from app.db import SessionLocal
from app.models import Material

items = [
    # Электрика
    {"name":"Кабель ВВГнг-LS 3x2.5", "model":"Электрика", "unit":"м", "price_material":120, "price_labor":45},
    {"name":"Автоматический выключатель 16А", "model":"Электрика", "unit":"шт", "price_material":260, "price_labor":120},
    {"name":"Щиток распределительный 12 модулей", "model":"Электрика", "unit":"шт", "price_material":1800, "price_labor":900},
    # Сантехника
    {"name":"Труба PPR Ø25", "model":"Сантехника", "unit":"м", "price_material":95, "price_labor":60},
    {"name":"Фитинги PPR (угол/тройник)", "model":"Сантехника", "unit":"шт", "price_material":70, "price_labor":50},
    {"name":"Смеситель умывальника", "model":"Сантехника", "unit":"шт", "price_material":3200, "price_labor":900},
    # Оборудование (HVAC)
    {"name":"Вентилятор канальный Ø200", "model":"Оборудование", "unit":"шт", "price_material":7800, "price_labor":1800},
    {"name":"Канальный кондиционер 7 кВт", "model":"Оборудование", "unit":"шт", "price_material":145000, "price_labor":24000},
    {"name":"Воздуховод оцинкованный 315х200", "model":"Оборудование", "unit":"м", "price_material":950, "price_labor":300},
    # Изоляция
    {"name":"Теплоизоляция каучук 13 мм", "model":"Изоляция", "unit":"м", "price_material":170, "price_labor":80},
    {"name":"Шумоглушащая вставка", "model":"Изоляция", "unit":"шт", "price_material":1200, "price_labor":400},
    # Работы
    {"name":"Демонтаж старого кондиционера", "model":"Работы", "unit":"шт", "price_material":0, "price_labor":2500},
    {"name":"Разгрузочные работы (бригада)", "model":"Работы", "unit":"час", "price_material":0, "price_labor":1200},
    {"name":"Уборочные работы по окончании", "model":"Работы", "unit":"час", "price_material":0, "price_labor":800},
]

db = SessionLocal()
for it in items:
    row = db.query(Material).filter(Material.name==it["name"], Material.model==it["model"]).first()
    if row:
        row.unit = it["unit"]; row.price_material = it["price_material"]; row.price_labor = it["price_labor"]
    else:
        db.add(Material(**it))
db.commit(); db.close()
print("Каталог готов.")
