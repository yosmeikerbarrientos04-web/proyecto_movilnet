from django.db import connection

cursor = connection.cursor()
cursor.execute("SET mi_app.confirmar_borrado = 'SI'")

cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'etiquetas'")
cols = [r[0] for r in cursor.fetchall()]
print('Existing columns:', cols)

if 'porcentaje' not in cols:
    print('Adding porcentaje column...')
    cursor.execute("ALTER TABLE etiquetas ADD COLUMN porcentaje integer NOT NULL DEFAULT 0")
    print('Done.')
else:
    print('porcentaje already exists.')

if 'es_fase' not in cols:
    print('Adding es_fase column...')
    cursor.execute("ALTER TABLE etiquetas ADD COLUMN es_fase boolean NOT NULL DEFAULT false")
    print('Done.')
else:
    print('es_fase already exists.')

if 'orden' not in cols:
    print('Adding orden column...')
    cursor.execute("ALTER TABLE etiquetas ADD COLUMN orden integer NOT NULL DEFAULT 0")
    print('Done.')
else:
    print('orden already exists.')

cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'etiquetas'")
cols2 = [r[0] for r in cursor.fetchall()]
print('Final columns:', cols2)
