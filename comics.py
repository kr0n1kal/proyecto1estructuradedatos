import sys
import hashlib
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QTextBrowser, QDialog
import requests

class MarvelComicViewer(QMainWindow):
    def __init__(self, api_key, private_key, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.private_key = private_key
        self.current_page = 1
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Marvel Comic Viewer')
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.info_label = QLabel(self)
        self.layout.addWidget(self.info_label)

        self.comics_text_browser = QTextBrowser(self)
        self.layout.addWidget(self.comics_text_browser)

        self.character_button = QPushButton('Ver Personajes', self)
        self.character_button.clicked.connect(self.show_character_dialog)
        self.layout.addWidget(self.character_button)

        self.prev_button = QPushButton('Anterior', self)
        self.prev_button.clicked.connect(self.load_prev_page)
        self.layout.addWidget(self.prev_button)

        self.next_button = QPushButton('Siguiente', self)
        self.next_button.clicked.connect(self.load_next_page)
        self.layout.addWidget(self.next_button)

        self.load_comics()

    def generate_hash(self):
        ts = str(int(time.time()))
        hash_input = ts + self.private_key + self.api_key
        return ts, hashlib.md5(hash_input.encode('utf-8')).hexdigest()

    def load_comics(self):
        self.comics_text_browser.clear()
        comics_url = 'https://gateway.marvel.com/v1/public/comics'
        ts, hash_value = self.generate_hash()

        params = {
            'apikey': self.api_key,
            'ts': ts,
            'hash': hash_value,
            'limit': 5,
            'offset': (self.current_page - 1) * 5
        }

        try:
            response = requests.get(comics_url, params=params)
            data = response.json()

            if data['code'] == 200:
                for comic in data['data']['results']:
                    title = comic['title']
                    isbn = comic['isbn'] if 'isbn' in comic else 'No disponible'
                    description = comic['description'] if comic['description'] else 'Sin descripción disponible.'

                    self.comics_text_browser.append(
                        f'\nCómic: {title}\n'
                        f'ISBN: {isbn}\n'
                        f'Descripción: {description}\n'
                        f'{"-" * 50}\n'
                    )

                self.info_label.setText(f'Página {self.current_page}')
            else:
                self.info_label.setText(f'Error al cargar cómics. Código de error: {data["code"]}')
        except requests.exceptions.RequestException as e:
            self.info_label.setText(f'Error de conexión: {str(e)}')

    def load_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_comics()

    def load_next_page(self):
        self.current_page += 1
        self.load_comics()

    def show_character_dialog(self):
        dialog = CharacterDialog(self.api_key, self.private_key)
        dialog.exec()

class CharacterDialog(QDialog):
    def __init__(self, api_key, private_key, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.private_key = private_key
        self.setWindowTitle('Marvel Characters')
        self.setLayout(QVBoxLayout())

        self.character_text_browser = QTextBrowser()
        self.layout().addWidget(self.character_text_browser)

        self.load_characters()

    def generate_hash(self):
        ts = str(int(time.time()))
        hash_input = ts + self.private_key + self.api_key
        return ts, hashlib.md5(hash_input.encode('utf-8')).hexdigest()

    def load_characters(self):
        self.character_text_browser.clear()
        characters_url = 'https://gateway.marvel.com/v1/public/characters'
        ts, hash_value = self.generate_hash()

        params = {
            'apikey': self.api_key,
            'ts': ts,
            'hash': hash_value,
            'limit': 5
        }

        try:
            response = requests.get(characters_url, params=params)
            data = response.json()

            if data['code'] == 200:
                for character in data['data']['results']:
                    name = character['name']
                    description = character['description'] if character['description'] else 'Sin descripción disponible.'

                    comics = ', '.join([comic['name'] for comic in character['comics']['items']])
                    if not comics:
                        comics = 'Ninguno'

                    events = ', '.join([event['name'] for event in character['events']['items']])
                    if not events:
                        events = 'Ninguno'

                    creators = ', '.join([creator['name'] for creator in character.get('creators', {}).get('items', [])])
                    if not creators:
                        creators = 'Ninguno'

                    self.character_text_browser.append(
                        f'\nNombre: {name}\n'
                        f'Descripción: {description}\n'
                        f'Creadores: {creators}\n'
                        f'Comics: {comics}\n'
                        f'Eventos: {events}\n'
                        f'{"-" * 50}\n'
                    )
        except requests.exceptions.RequestException as e:
            print(f'Error de conexión: {str(e)}')

if __name__ == '__main__':
    api_key = '83e2fb96ed102b9ce7ac383761eea7cb'
    private_key = '870e8cf06c7afbe315adf5eefa237554299944c1'
    app = QApplication(sys.argv)
    viewer = MarvelComicViewer(api_key, private_key)
    viewer.show()
    sys.exit(app.exec())
