import os, json

CHANNELS_DATA_DIR = 'channels_data'
channel_name = 'Cosasqpensar'
nombre_base = ''.join(c for c in channel_name if c.isalnum() or c in (' ', '_', '-')).strip()
nombre_base = nombre_base.replace(' ', '_').lower()
print(f'nombre_base: {nombre_base}')

for f in os.listdir(CHANNELS_DATA_DIR):
    match = f.lower() == (nombre_base + '.json')
    print(f'Archivo: {f}, Match: {match}')

# Ahora probar la función completa
from app.services.channel_service import _find_channel_file_by_name, _load_channel_data_from_file
json_path, jpg_path = _find_channel_file_by_name('Cosasqpensar')
print(f'json_path: {json_path}')
print(f'jpg_path: {jpg_path}')

if json_path:
    data = _load_channel_data_from_file(json_path)
    print(f'data: {json.dumps(data, indent=2, ensure_ascii=False)}')