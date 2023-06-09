"""Converter telegram bot business logic, functions for conversion"""
import os
from PIL import Image
import zipfile
import fitz


supported_pdf_converter_formats = [".png", ".jpeg", ".jpg"]


def convert_images_to_pdf(user_id: str) -> str:
    """Makes pdf from pictures and returns path to generated file

    :param user_id: unique identifier for telegram user
    :type user_id: str
    :rtype: str
    """
    path = f"storage/{user_id}"
    uploaded_files = [f for f in os.listdir(path)
                      if os.path.isfile(os.path.join(path, f))
                      and os.path.splitext(os.path.join(path, f))[1].lower()
                      in supported_pdf_converter_formats]
    if len(uploaded_files) == 0:
        raise ValueError("Oops, looks like no files uploaded or they have wrong format for this operation")
    pdf_path = os.path.join(path, "output.pdf")
    images = [Image.open(os.path.join(path, f)) for f in uploaded_files]
    images[0].save(pdf_path, save_all=True, append_images=images[1:])
    return pdf_path


def convert_pdf_to_images(user_id: str) -> str:
    """Splits pdf into pictures and returns path to the directory with produced pictures

    :param user_id: unique identifier for telegram user
    :type user_id: str
    :rtype: str
    """
    path = f"storage/{user_id}"
    uploaded_files = [f for f in os.listdir(path)
                      if os.path.isfile(os.path.join(path, f))
                      and os.path.splitext(os.path.join(path, f))[1].lower() == ".pdf"]
    if len(uploaded_files) == 0:
        raise ValueError("No files uploaded")
    if len(uploaded_files) > 1:
        raise ValueError("Found too many files, I can only extract images from one pdf file at a time")
    pdf_file = fitz.open(os.path.join(path, uploaded_files[0]))
    os.mkdir(os.path.join(path, "output"))
    files_path = os.path.join(path, "output")
    for page in pdf_file:
        image = page.get_pixmap()
        image.save(os.path.join(files_path, f"{str(page.number)}.png"), output="png")
    return files_path


def convert_files_to_zip(user_id: str) -> str:
    """Archives files and returns path to zip

    :param user_id: unique identifier for telegram user
    :type user_id: str
    :rtype: str
    """
    path = f"storage/{user_id}"
    uploaded_files = [f for f in os.listdir(path)
                      if os.path.isfile(os.path.join(path, f))]
    if len(uploaded_files) == 0:
        raise ValueError("No files uploaded")
    zip_path = os.path.join(path, "output.zip")
    with zipfile.ZipFile(zip_path, "w") as zip:
        for file in uploaded_files:
            fs = file.split("=")
            zip.write(os.path.join(path, file), fs[1] if len(fs) == 2 else file)
    return zip_path


def convert_zip_to_files(user_id: str) -> str:
    """Unzips archive and returns path to the directory with produced pictures

    :param user_id: unique identifier for telegram user
    :type user_id: str
    :rtype: str
    """
    path = f"storage/{user_id}"
    uploaded_files = [f for f in os.listdir(path)
                      if os.path.isfile(os.path.join(path, f))
                      and os.path.splitext(os.path.join(path, f))[1].lower() == ".zip"]
    if len(uploaded_files) == 0:
        raise ValueError("No files uploaded")
    if len(uploaded_files) > 1:
        raise ValueError("Found too many files, I can only unzip one file at a time")
    zip_path = os.path.join(path, uploaded_files[0])
    files_path = os.path.join(path, "output")
    with zipfile.ZipFile(zip_path, "r") as zip:
        zip.extractall(files_path)
    return files_path


def remove_files(user_id: str, only_images=False):
    """Cleans users' directory after conversion

    :param user_id: unique identifier for telegram user
    :type user_id: str
    :param only_images: removes only pictures
    :type only_images: Bool
    :rtype: None
    """
    path = f"storage/{user_id}"
    if only_images:
        uploaded_files = [f for f in os.listdir(path)
                          if os.path.isfile(os.path.join(path, f))
                          and os.path.splitext(os.path.join(path, f))[1].lower() in supported_pdf_converter_formats]
        uploaded_files.append("output.pdf")
    else:
        uploaded_files = [f for f in os.listdir(path)
                          if os.path.isfile(os.path.join(path, f))]
    for f in uploaded_files:
        os.remove(os.path.join(path, f))
