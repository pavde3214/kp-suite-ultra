import csv, io
from app.models import Material

def import_materials_csv(db, content: bytes):
    # Try utf-8 then cp1251
    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        text = content.decode('cp1251', errors='ignore')
    reader = csv.DictReader(io.StringIO(text))
    created = 0
    for row in reader:
        name = (row.get('name') or row.get('Наименование') or '').strip()
        if not name: continue
        m = Material(
            name=name,
            model=(row.get('model') or row.get('Модель') or '').strip() or None,
            unit=(row.get('unit') or row.get('Ед') or 'шт').strip() or 'шт',
            price_material=float((row.get('price_material') or row.get('ЦенаМат') or 0) or 0),
            price_labor=float((row.get('price_labor') or row.get('ЦенаМонтаж') or 0) or 0),
        )
        db.add(m); created += 1
    db.commit()
    return {"created": created}
