class MarvelComicViewer(QMainWindow):
    def __init__(self, api_key, private_key, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.private_key = private_key
        self.current_page = 1
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Mundo Comic - Comics')
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
            'limit': 10,
            'offset': (self.current_page - 1) * 10
        }

        try:
            response = requests.get(comics_url, params=params)
            data = response.json()

            if data['code'] == 200:
                self.info_label.setText(f'Página {self.current_page}')
                comics = data['data']['results']
                for comic in comics:
                    title = comic['title']
                    isbn = comic.get('isbn', 'N/A')
                    description = comic.get('description', 'N/A')

                    characters = 'N/A'
                    if 'characters' in comic:
                        characters_data = comic['characters']['items']
                        if characters_data:
                            characters = ', '.join(char['name'] for char in characters_data)

                    creators = 'N/A'
                    if 'creators' in comic:
                        creators_data = comic['creators']['items']
                        if creators_data:
                            creators = ', '.join(creator['name'] for creator in creators_data)

                    self.comics_text_browser.append(
                        f'\nTítulo: {title}\n'
                        f'ISBN: {isbn}\n'
                        f'Descripción: {description}\n'
                        f'Personajes: {characters}\n'
                        f'Creadores: {creators}\n'
                        f'{"-" * 50}\n'
                    )
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
        self.setWindowTitle('Mundo Comic - Personajes')
        self.setLayout(QVBoxLayout())

        self.character_image_label = QLabel(self)
        self.layout().addWidget(self.character_image_label)
        self.character_image_label.mousePressEvent = self.show_character_info

        self.current_page = 1

        self.prev_button = QPushButton('Anterior', self)
        self.prev_button.clicked.connect(self.load_prev_page)
        self.layout().addWidget(self.prev_button)

        self.next_button = QPushButton('Siguiente', self)
        self.next_button.clicked.connect(self.load_next_page)
        self.layout().addWidget(self.next_button)

        self.load_characters()

    def show_character_info(self, event):
        character_info = self.get_character_info()
        if character_info:
            QMessageBox.information(self, 'Información del Personaje', character_info)

    def generate_hash(self):
        ts = str(int(time.time()))
        hash_input = ts + self.private_key + self.api_key
        return ts, hashlib.md5(hash_input.encode('utf-8')).hexdigest()

    def get_character_info(self):
        characters_url = 'https://gateway.marvel.com/v1/public/characters'
        ts, hash_value = self.generate_hash()

        params = {
            'apikey': self.api_key,
            'ts': ts,
            'hash': hash_value,
            'limit': 1,
            'offset': (self.current_page - 1)
        }

        try:
            response = requests.get(characters_url, params=params)
            data = response.json()

            if data['code'] == 200:
                characters = data['data']['results']
                if characters:
                    first_character = characters[0]
                    name = first_character['name']
                    description = first_character['description'] or 'Sin descripción disponible.'
                    creators = ', '.join([creator['name'] for creator in first_character.get('creators', {}).get('items', [])]) or 'Ninguno'
                    comics = ', '.join([comic['name'] for comic in first_character.get('comics', {}).get('items', [])]) or 'Ninguno'
                    return f'Nombre: {name}\nDescripción: {description}\nCreadores: {creators}\nComics: {comics}'
        except requests.exceptions.RequestException as e:
            print(f'Error de conexión: {str(e)}')

    def load_characters(self):
        characters_url = 'https://gateway.marvel.com/v1/public/characters'
        ts, hash_value = self.generate_hash()

        params = {
            'apikey': self.api_key,
            'ts': ts,
            'hash': hash_value,
            'limit': 1,
            'offset': (self.current_page - 1)
        }

        try:
            response = requests.get(characters_url, params=params)
            data = response.json()

            if data['code'] == 200:
                characters = data['data']['results']
                if characters:
                    first_character = characters[0]
                    if 'thumbnail' in first_character:
                        character_image_url = f"{first_character['thumbnail']['path']}/portrait_incredible.{first_character['thumbnail']['extension']}"
                        pixmap = QPixmap()
                        pixmap.loadFromData(requests.get(character_image_url).content)
                        self.character_image_label.setPixmap(pixmap)
                        self.character_image_label.setScaledContents(True)
                    else:
                        self.character_image_label.clear()
        except requests.exceptions.RequestException as e:
            print(f'Error de conexión: {str(e)}')

    def load_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_characters()

    def load_next_page(self):
        self.current_page += 1
        self.load_characters()


if __name__ == '__main__':
    api_key = '83e2fb96ed102b9ce7ac383761eea7cb'
    private_key = '870e8cf06c7afbe315adf5eefa237554299944c1'
    app = QApplication(sys.argv)
    viewer = MarvelComicViewer(api_key, private_key)
    viewer.show()
    sys.exit(app.exec())
