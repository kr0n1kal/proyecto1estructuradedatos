import tkinter as tk
import requests
import hashlib
import time

def generate_hash(ts, private_key, public_key):
    hash_input = f'{ts}{private_key}{public_key}'
    hashed = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
    return hashed

def make_request(endpoint, params={}):
    ts = str(int(time.time()))
    hash_value = generate_hash(ts, private_key, public_key)

    params['ts'] = ts
    params['apikey'] = public_key
    params['hash'] = hash_value

    response = requests.get(base_url + endpoint, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error {response.status_code}: {response.text}')
        return None

def get_character_info():
    character_name = entry.get()
    if not character_name:
        result_label.config(text="Por favor, ingresa un nombre de personaje.")
        return

    params = {'name': character_name}
    response = make_request('characters', params)

    if response:
        results = response.get('data', {}).get('results', [])
        if results:
            character_data = results[0]
            result_label.config(text=f"Nombre: {character_data['name']}\nDescripción: {character_data['description']}")
        else:
            result_label.config(text=f"No se encontró información para {character_name}")

# Configuración de la API de Marvel
public_key = 'llave_publica'
private_key = 'llave_privada'
base_url = 'https://gateway.marvel.com/v1/public/'

# Crear la ventana principal
root = tk.Tk()
root.title("Marvel API Search")

# Crear y añadir widgets
label = tk.Label(root, text="Ingresa el nombre de un personaje de Marvel:")
label.pack(pady=10)

entry = tk.Entry(root)
entry.pack(pady=10)

search_button = tk.Button(root, text="Buscar", command=get_character_info)
search_button.pack(pady=10)

result_label = tk.Label(root, text="")
result_label.pack(pady=10)

# Ejecutar el bucle principal
root.mainloop()
