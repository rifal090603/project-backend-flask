import pandas as pd
import numpy as np
from app import db, create_app
from app.models.menu_models import Menu

# Inisialisasi app context
app = create_app()
app.app_context().push()

# Baca CSV
df = pd.read_csv('menu_dataset_kita.csv')

# Ganti NaN dengan None agar kompatibel dengan database
df = df.replace({np.nan: None})

for _, row in df.iterrows():
    try:
        menu_item = Menu(
            nama=row['nama'],
            harga=float(row['harga']) if row['harga'] is not None else 0,
            stock=int(row['stock']) if row['stock'] is not None else 0,
            category=row['category'] or 'Umum',
            image=row.get('image', None),
            deskripsi=row.get('deskripsi', None)
        )
        db.session.add(menu_item)
    except Exception as e:
        print(f"Gagal tambah baris: {row}, error: {e}")

# Commit
try:
    db.session.commit()
    print("✅ Data berhasil diimport.")
except Exception as e:
    print("❌ Gagal commit ke database:", e)
    db.session.rollback()
