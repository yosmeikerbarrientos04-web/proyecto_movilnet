from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;")
rows = cursor.fetchall()
print('Tablas actuales en gestion_de_seguimiento:')
for r in rows:
    print(' -', r[0])
print('Total tablas:', len(rows))
