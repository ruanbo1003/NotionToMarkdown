import os
import requests
import shutil
from urllib.parse import urlparse


class FileUtil(object):
    @staticmethod
    def get_image_format(url):
        # output: .png, .jpeg
        parsed_url = urlparse(url)
        return os.path.splitext(parsed_url.path)[1]

    @staticmethod
    def create_dir(path):
        if os.path.exists(path):
            return
        os.mkdir(path)

    @staticmethod
    def delete_dir(path):
        shutil.rmtree(path, ignore_errors=True)
