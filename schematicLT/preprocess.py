from PIL import Image


def contrast(img_path: str, threshold: int=170, save_path: None=None) -> Image.Image:
    """
    Convert an image to grayscale and boost its contrast to
    black and white.

    PARAMETERS
    ----------
    `img_path`: `str`, `path`-like object
        Path to image.
    `threshold`: `int`
        Contrast threshold relative to `uint8_t` scaling. Default is `170`.
    `save_path`: `str`, `path`-like object
        Optional parameter for saving the image. Default is `None`, image
        will not be saved.
    """
    img = Image.open(img_path)
    fn = lambda x : 255 if x > threshold else 0
    r = img.convert('L').point(fn, mode='1')
    if save_path != None:
        r.save(save_path)

    return r
