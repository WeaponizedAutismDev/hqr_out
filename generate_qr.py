import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import GappedSquareModuleDrawer
from qrcode.image.styles.colormasks import HorizontalGradiantColorMask
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode import QRCode
from qrcode.image.svg import SvgPathImage


def gen_png_qr(encoded_data: str):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(encoded_data)
    qr.make(fit=True)
    # img = qr.make_image(fill_color="black", back_color="white")
    img = qr.make_image(back_color="white", fill_color=(255, 32, 78))
    return img


def gen_semi_styled_png_qr(encoded_data: str):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(encoded_data)
    qr.make(fit=True)
    factory = StyledPilImage
    # img = qrcode.make(encoded_data, image_factory=factory)
    # qrcode.image.svg.SvgFillImage
    # qrcode.image.svg.SvgPathFillImage
    # img = qr.make_image(fill_color="black", back_color="white")
    img = qr.make_image(
        image_factory=factory,
        color_mask=SolidFillColorMask(
            front_color=(255, 32, 78), back_color=(255, 255, 255)
        ),
    )
    return img


def gen_styled_png_qr(encoded_data: str, logo_path: str):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=4,
    )
    qr.add_data(encoded_data)
    qr.make(fit=True)
    factory = StyledPilImage
    # img = qr.make_image(image_factory=factory, back_color="white", , embeded_image_path=logo_path, module_drawer=GappedSquareModuleDrawer())
    img = qr.make_image(
        image_factory=factory,
        module_drawer=GappedSquareModuleDrawer(),
        embeded_image_path=logo_path,
        embeded_image_ratio=0.25,
        color_mask=HorizontalGradiantColorMask(
            left_color=(255, 32, 78), right_color=(12, 12, 12), back_color=(255, 255, 255)
        ),
    )

    return img


def qr_to_string(img: QRCode) -> str:
    stringout = img.to_string(encoding="unicode")
    return stringout


encoded_data = "QRC03010003eJwrKnNNzC0vNy/yLogwD041LTUocg13tLW1ijRyK4mK8MpQM1DzDcmu9MlyNfJ3NqkA0rZqFgYGBmpqySWGuSYp5iEVwc5eHkZJHpnhWcFBQK04JVSsjJO8g5IC0gMSU6KcqsxczEuzjfQNA21tAQ4rKR0="
logo_path = "./logo.png"
img1 = gen_png_qr(encoded_data)
img2 = gen_semi_styled_png_qr(encoded_data)
img3 = gen_styled_png_qr(encoded_data, logo_path)

# Save images
img1.save("qr_code_png.png")
img2.save("qr_code_semi_styled.png")
img3.save("qr_code_styled.png")
