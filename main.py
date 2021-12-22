import datetime
import os
import instaloader
from instaloader import Profile
import config
import requests
import shutil
from tqdm import tqdm as loading_bar
from PIL import Image
import fnmatch


L = instaloader.Instaloader()


def connect(inst_user, inst_password):
    """
    Опционально можно выбрать:
    * Через Логин и Пароль
    * Через Логин + пароль в терминале
    * Через Сессию
    """
    try:
        L.login(inst_user, inst_password)
    except Exception as exx:
        print(str(exx))
    else:
        print('Подключился к аккаунту!')


class User(object):
    def __init__(self, target_name):
        self.target_name = target_name
        self.photo_path = os.path.join('photos', target_name)
        self.video_path = os.path.join('videos', target_name)

    def download_all_posts(self):
        profile = Profile.from_username(L.context, self.target_name)
        for post in profile.get_posts():
            L.download_post(post, target=profile.username)
        self._scatter_files()
        self.paste_watermarks_to_images()

    def download_photos(self):
        profile = Profile.from_username(L.context, self.target_name)
        os.mkdir(self.photo_path)
        for num, post in enumerate(profile.get_posts()):
            if not post.is_video:
                image_name = os.path.join(self.photo_path, str(num))
                L.download_pic(filename=image_name, url=post.url, mtime=datetime.datetime.now())
        self.paste_watermarks_to_images()

    def download_videos(self):
        profile = Profile.from_username(L.context, self.target_name)
        os.mkdir(self.video_path)
        for num, post in enumerate(profile.get_posts()):
            if post.is_video:
                video_name = os.path.join(self.video_path, f'{num}.mp4')
                self._download_file(post.video_url, video_name)

    def _scatter_files(self):
        os.mkdir(self.photo_path)
        os.mkdir(self.video_path)
        all_files_names = os.listdir(self.target_name)
        photos_names = [file for file in all_files_names if fnmatch.fnmatch(file, "*.jpg")]
        videos_names = [file for file in all_files_names if fnmatch.fnmatch(file, "*.mp4")]
        for file_name in photos_names:
            dir1 = os.path.join(self.target_name, file_name)
            dir2 = os.path.join(self.photo_path, file_name)
            shutil.move(dir1, dir2)
        for file_name in videos_names:
            dir1 = os.path.join(self.target_name, file_name)
            dir2 = os.path.join(self.video_path, file_name)
            shutil.move(dir1, dir2)
        shutil.rmtree(self.target_name, ignore_errors=True)

    @staticmethod
    def _download_file(file_url, file_name):
        file_data = requests.get(file_url).content
        with open(file_name, 'wb') as handler:
            handler.write(file_data)

    def delete_files(self, photo: bool = False, video: bool = False):
        try:
            if photo:
                shutil.rmtree(self.photo_path)
            if video:
                shutil.rmtree(self.video_path)
        except FileNotFoundError as err:
            print(str(err))

    def paste_watermarks_to_images(self):
        files = os.listdir(self.photo_path)
        pattern = "*.jpg"
        photos = [file for file in files if fnmatch.fnmatch(file, pattern)]
        for photo in loading_bar(photos, desc='Установка водяных знаков на фото'):
            self._paste_watermark(photo)

    def _paste_watermark(self, image_name):
        directory = os.path.join(self.photo_path, image_name)

        image = Image.open(directory)

        watermark = Image.open('static/watermark.png')
        watermark_size_x = int(image.size[0] / 3)
        watermark_size_y = int(watermark_size_x / 4.46)
        new_watermark = watermark.resize((watermark_size_x, watermark_size_y), Image.ANTIALIAS)

        image.paste(new_watermark, (image.size[0] - watermark_size_x - 30, image.size[1] - watermark_size_y - 30),
                    new_watermark)
        image.save(directory, "JPEG", optimize=True)


if __name__ == '__main__':
    connect(config.INST_USERNAME, config.INST_PASSWORD)
    user = User('aru_symbat')
    user.download_photos()
