import os

from zipfile import ZipFile
from PIL import Image
from django.conf import settings
from celery import shared_task

@shared_task
def gen_thumbnail(file_path, thumbnails=[]):
    os.chdir(settings.IMAGES_DIR)
    path, file = os.path.split(file_path)
    file_name, file_ext = os.path.splitext(file)

    zipfile_name = file_name + '.zip'
    results = {
        'zip_path' : f"{settings.MEDIA_URL}images/{zipfile_name}",
    }
    try:
        img = Image.open(file_path)
        zipper = ZipFile(zipfile_name, 'w')
        zipper.write(file_path)
        os.remove(file_path)
        for width, height in thumbnails:
            img.thumbnail((width, height), Image.ANTIALIAS)
            thumb_name = f"{file_name}_{width}x{height}.{file_ext}"
            img.save(thumb_name)
            zipper.write(thumb_name)
            os.remove(thumb_name)
        
        zipper.close()
        img.close()
    except IOError as e:
        results['error'] = str(e)

    return results

@shared_task
def add_task(x, y):
    return x + y