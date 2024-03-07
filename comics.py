import sys
import hashlib
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QTextBrowser
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
                    
                    characters = [character['name'] for character in comic['characters']['items']]
                    characters_str = ', '.join(characters) if characters else 'Ninguno'

                    creators = [creator['name'] for creator in comic['creators']['items']]
                    creators_str = ', '.join(creators) if creators else 'Ninguno'

                    self.comics_text_browser.append(
                        f'\nCómic: {title}\n'
                        f'ISBN: {isbn}\n'
                        f'Descripción: {description}\n'
                        f'Personajes: {characters_str}\n'
                        f'Creadores: {creators_str}\n'
                        f'{"-" * 50}\n'
                    )

                self.info_label.setText(f'Página {self.current_page}')
            else:
                self.info_label.setText(f'Error al cargar cómics. Código de error: {data["code"]}')
        except Exception as e:
            self.info_label.setText(f'Error de conexión: {str(e)}')

    def load_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_comics()

    def load_next_page(self):
        self.current_page += 1
        self.load_comics()

if __name__ == '__main__':
    api_key = 'clavepublica'  
    private_key = 'claveprivada'  
    app = QApplication(sys.argv)
    viewer = MarvelComicViewer(api_key, private_key)
    viewer.show()
    sys.exit(app.exec())
