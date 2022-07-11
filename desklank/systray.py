from pystray import Icon as Base, Menu, MenuItem
from PIL import Image, ImageDraw


class Icon(Base):
    def __init__(self, app):
        self.app = app
        icon_image = self.create_image(64, 64, 'green', 'white')

        super().__init__(
            'desklank',
            icon=icon_image,
            menu=Menu(
                #MenuItem(
                #    'With submenu',
                #    Menu(
                #        MenuItem(
                #            'Submenu item 1',
                #            lambda icon, item: 1
                #        ),
                #        MenuItem(
                #            'Submenu item 2',
                #            lambda icon, item: 2
                #        )
                #    )
                #),
                #MenuItem('Show / Hide', self.app.show_hide, default=True),
                MenuItem('Quit', self.app.quit)
            )
        )

    @staticmethod
    def create_image(width, height, color1, color2):
        image = Image.new('RGBA', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle(
            (width // 2, 0, width, height // 2),
            fill=color2)
        dc.rectangle(
            (0, height // 2, width // 2, height),
            fill=color2)

        return image

