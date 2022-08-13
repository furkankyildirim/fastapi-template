import os
import uuid
from fastapi import UploadFile
from fastapi.responses import FileResponse

from src.configs import AppConfig
from src.errors import NOT_FOUND_ERROR

from .hash import Hash


class ImageResponse(FileResponse):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ImageUtils: 

    @staticmethod
    def get_image(filename: str, subdir: str) -> ImageResponse:
        """
        Get image:
        - filename: str =  Photo filename.
        - subdir: str =  Photo subdirectory.
        """
        
        directory : str = ImageUtils.__set_image_directory(filename=filename, subdir=subdir)
        if not os.path.exists(directory):
            raise NOT_FOUND_ERROR(message=f"Image with the name {filename} is not available")
        return ImageResponse(directory)


    @staticmethod
    def upload_image(image: UploadFile, subdir: str) -> str:
        """
        Upload image:
        - image: UploadFile = Image.
        """

        ImageUtils.__is_valid_image(image=image)

        image.filename = ImageUtils.__set_image_filename(filename=image.filename)
        directory : str = ImageUtils.__set_image_directory(filename=image.filename, subdir=subdir)

        ImageUtils.__save_image(image=image, directory=directory)
        return image.filename


    @staticmethod
    def delete_image(filename: str, subdir: str) -> None:
        """
        Delete image:
        - filename: str = Image name.
        """

        if filename == AppConfig.NO_PHOTO_FILE:
            return

        directory : str = ImageUtils.__set_image_directory(filename=filename, subdir=subdir)

        if not os.path.exists(directory):
            raise NOT_FOUND_ERROR(message=f"Image with the name {filename} is not available")

        os.remove(directory)


    @staticmethod
    def get_filename_from_url(url: str) -> str:
        """
        Get filename from url:
        - url: str = Image url.
        """
        filename : str = url.split("/")[-1]
        return filename


    @staticmethod
    def get_image_url_from_prefix(prefix: str) -> str:
        """
        Get url from filename:
        - filename: str = Image
        - prefix: str = Image prefix.
        """
        return f"{AppConfig.API_URL}/{prefix}"

    
    @staticmethod
    def get_image_with_prefix(filename: str, prefix: str) -> str:
        """
        Get image with prefix:        
        - filename: str = Image
        - prefix: str = Image prefix.
        """
        return f"{prefix}/{filename}"


    @staticmethod
    def get_default_image() -> str:
        """
        Get default image prefix.
        """
        return f"{AppConfig.NO_PHOTO_FILE}"

        
    @staticmethod
    def __is_valid_image(image: UploadFile) -> None:
        """
        Checks if image is valid:

        - image: UploadFile = Image.

        """
        # if not image.content_type.startswith('image'):
        #    raise BAD_REQUEST_ERROR(message="Image is not valid")


    @staticmethod
    def __set_image_filename(filename: str) -> str:
        """
        Changes filename:

        - image: UploadFile = Image.

        """
        name, ext = filename.split(".")
        filename = str(uuid.uuid4()) + "." + ext
        return filename


    @staticmethod
    def __set_image_directory(filename: str, subdir: str) -> str:
        """
        Changes directory:

        - filename : str = filename.

        """
        directory = f"{AppConfig.MEDIA_FOLDER}/{subdir}/{filename}"
        return directory


    @staticmethod
    def __save_image(image: UploadFile, directory: str) -> None:
        """
        Saves image:

        - image: UploadFile = Image.
        - directory: str = Directory.

        """
        with open(directory, 'wb+') as file:
            file.write(image.file.read())
            file.close()
