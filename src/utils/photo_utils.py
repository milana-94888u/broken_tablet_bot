from pathlib import Path

from PIL import Image, ImageFilter


def create_blurred_image(image_path: str) -> str:
    original_image = Image.open(image_path)
    gauss_image = original_image.filter(ImageFilter.GaussianBlur(100))
    initial_path = Path(image_path)
    save_path = initial_path.parent.joinpath(
        f"{initial_path.stem}_blurred{initial_path.suffix}"
    )
    gauss_image.save(save_path)
    return str(save_path)
