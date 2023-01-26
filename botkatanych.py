import vk_api
import requests
import pathlib
import random

from base64 import b64decode
from data import *
from translatepy import Translator




class BotKatanych():
    """Класс бота VK под названием Katanych"""
    
    def __init__(self, login, password, token, owner_id):
        """Свойства класса BotKatanych с авторизацией

        Принимаемые параметры функции:
        - login: информация для авторизации;
        - password: информация для авторизации;
        - token: уникальный код группы ВКонтакте для взаимодействия с ней;
        - owned_id: уникальный идентификатор созданного приложения во ВКонтакте;

        """

        self.login = login
        self.password = password
        self.token = token
        self.owner_id = owner_id
        
        self.vk_session = vk_api.VkApi(self.login, self.password)
        try:
            self.vk_session.auth(token_only=True)
            print('Готов к работе!')
        except vk_api.AuthError as error_msg:
            return error_msg
    
    def img_to_album(self, group_id, album_id, paths):
        """Метод добавления изображения в альбом группы

        - group_id: уникальный идентификатор группы;
        - album_id: уникальный идентификатор альбома;
        - paths: список путей расположения изображений.

        Метод возвращает список путей загруженных в группу изображений.

        """

        photos = []

        upload = vk_api.VkUpload(self.vk_session)
        for path in paths:
            print(path.__str__())
            photo = upload.photo(  # Подставьте свои данные
                path.__str__(),
                album_id=album_id,
                group_id=group_id
            )
            vk_photo_url = 'https://vk.com/photo{}_{}'.format(
                photo[0]['owner_id'], photo[0]['id']
            )
            photos.append(vk_photo_url.__str__().split('/')[-1])

        return photos

    def img_download(self, uri, path, file_name):
        """Метод скачивания изображения по URI
        
        Метод принимает на вход параметры:
        - uri: ссылка на изображение в формате uri;
        - path: путь для сохранения изображения с желаемым именем.

        """

        path_file = pathlib.Path(path) / (str(file_name) + '.png')
        with open(path_file, 'wb') as fh:
            fh.write(b64decode(uri))
        return path_file

    def generate_imgs(self, text):
        """Метод генерации изображений
        
        Входные данные:
        - text: текстовый запрос к генерации.
        Возвращает список URI до изображения.

        """

        response = requests.post(
            url='https://backend.craiyon.com/generate', 
            json={'prompt': text}
            )
        return response.json()['images']

    def getting_imgs(self, path, text):
        """Метод генерации и получения снимков
        
        Входные данные: 
        - path: директория для сохранения снимков;
        - text: текстовый запрос к генерации изображений.

        Возвращает список путей до изображений.

        """

        imgs = self.generate_imgs(text)
        return [self.img_download(img, path, number) for number, img in enumerate(imgs)]

    def create_post(self, photos, text, publish_date, version=VERSION):
        """Метод создания поста

        Входные данные:
        - photos: URL ссылки на изображения в альбоме группы;
        - text: текстовая подпись к посту;
        - version: версия VK API

        """
        
        data={
            'access_token': self.token,
            'owner_id': -self.owner_id,
            'from_group': 1,
            'message': text,
            'attachments': f"{photos[0]},{photos[1]},{photos[2]},{photos[3]},{photos[4]},{photos[5]},{photos[6]},{photos[7]},{photos[8]}",
            'signed': 0,
            'publish_date': publish_date,
            'v':version
        }
        
        response = requests.post('https://api.vk.com/method/wall.post', params=data).json()
        print(response)


if __name__ == '__main__':
    bot = BotKatanych(LOGIN, PASSWORD, TOKEN, OWNER_ID)
    translator = Translator()

    for i in range(len(ANIMALS)):
        animal = random.choice(ANIMALS)
        request_message = f'{animal} with katana'
        paths_imgs = bot.getting_imgs(DIR_IMGS, request_message)
        imgs = bot.img_to_album(GROUP_ID, ALBUM_ID, paths_imgs)
        bot.create_post(imgs, f'{str(translator.translate(animal, "Russian")).lower()} с катаной', 1674721628+i*3600)
    