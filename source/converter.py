import os
import signal
from aiogram import Bot, types
from PIL import Image
import zipfile


def convert_images_to_pdf(user_id: str) -> str:
    path = f"storage/{user_id}"
    uploaded_files = [f for f in os.listdir(path)
                     if os.path.isfile(os.path.join(path, f))]
    if len(uploaded_files) == 0:
        raise Exception("No files uploaded")
    pdf_path = os.path.join(path, "output.pdf")
    images = [Image.open(os.path.join(path, f)) for f in uploaded_files]
    images[0].save(pdf_path, save_all=True, append_images=images[1:])
    return pdf_path

def convert_images_to_zip(user_id: str) -> str:
    path = f"storage/{user_id}"
    uploaded_files = [f for f in os.listdir(path)
                     if os.path.isfile(os.path.join(path, f))]
    if len(uploaded_files) == 0:
        raise Exception("No files uploaded")
    zip_path = os.path.join(path, "output.zip")
    with zipfile.ZipFile(zip_path, "w") as zip:
        for file in uploaded_files:
            zip.write(os.path.join(path, file), file)
    return zip_path


def remove_files(user_id: str):
    path = f"storage/{user_id}"
    uploaded_files = [f for f in os.listdir(path)
                     if os.path.isfile(os.path.join(path, f))]
    for f in uploaded_files:
        os.remove(os.path.join(path, f))

