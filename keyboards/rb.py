from PIL import Image

board_height = 5
board_width = 10
screen_height = 4
asset_folder = 'rb'
backspace_key = 'backspace'
enter_key = 'enter'
default_layout = 'lower'
preview_keys = {
    'upper': [['0009', '0010'], ['0011', '0012']],
    'lower': [['0041', '0042'], ['0043', '0044']],
    'symbols': [['0081', '0093'], ['0079', '0080']],
    'default': [['0074', '0075']]
}
layouts = {
    'upper': [
        ['0096', '0097', '0098', '0099', '0100', '0101', '0102', '0103', '0104', '0095'],
        ['0009', '0010', '0011', '0012', '0013', '0014', '0015', '0016', '0017', '0018'],
        ['0019', '0020', '0021', '0022', '0023', '0024', '0025', '0026', '0027', '0028'],
        ['0029', '0030', '0031', '0032', '0033', '0034', '0035', '0036', '0037', 'backspace'],
        ['0088', '0094', 'lower', 'symbols', '0000', '0089', '0039', '0040', '0038', 'enter'],
    ],
    'lower': [
        ['0096', '0097', '0098', '0099', '0100', '0101', '0102', '0103', '0104', '0095'],
        ['0041', '0042', '0043', '0044', '0045', '0046', '0047', '0048', '0049', '0050'],
        ['0051', '0052', '0053', '0054', '0055', '0056', '0057', '0058', '0059', '0060'],
        ['0061', '0062', '0063', '0064', '0065', '0066', '0081', '0093', '0073', 'backspace'],
        ['0067', '0090', 'upper', 'symbols', '0000', '0076', '0079', '0080', '0092', 'enter'],
    ],
    'symbols': [
        ['', '0035', '0036', '0068', '0069', '0078', '0077', '0081', '0093', ''],
        ['', '0039', '0040', '0070', '0071', '0072', '0089', '0076', '0073', ''],
        ['', '0037', '0038', '0074', '0075', '0088', '0094', '0079', '0080', ''],
        ['', '0259', '0090', '0091', '0092', '0240', '0258', '0260', '0261', 'backspace'],
        ['', '', 'upper', 'lower', '0000', '0085', '0086', '0087', '', 'enter'],
    ],
}

key_size = 64
top_left = Image.open(f'keyboards/assets/{asset_folder}/0001.png')
top_right = Image.open(f'keyboards/assets/{asset_folder}/0002.png')
bottom_left = Image.open(f'keyboards/assets/{asset_folder}/0003.png')
bottom_right = Image.open(f'keyboards/assets/{asset_folder}/0004.png')
horizontal = Image.open(f'keyboards/assets/{asset_folder}/0005.png')
vertical = Image.open(f'keyboards/assets/{asset_folder}/0006.png')


def postprocess(image: Image.Image) -> Image.Image:
    x, y = 0, 0
    buffer = Image.new(
        mode='RGBA',
        size=(image.width + key_size * 2, image.height + key_size * 2),
        color=(248, 248, 248)
    )
    buffer.alpha_composite(image, (key_size, key_size))
    while y < buffer.height:
        while x < buffer.width:
            if y == 0:
                if x == 0:
                    buffer.paste(top_left, (x, y))
                elif x == buffer.width - key_size:
                    buffer.paste(top_right, (x, y))
                else:
                    buffer.paste(horizontal, (x, y))
            elif y == buffer.height - key_size:
                if x == 0:
                    buffer.paste(bottom_left, (x, y))
                elif x == buffer.width - key_size:
                    buffer.paste(bottom_right, (x, y))
                else:
                    buffer.paste(horizontal, (x, y))
            else:
                if x == 0 or x == buffer.width - key_size:
                    buffer.paste(vertical, (x, y))
            x += key_size
        x = 0
        y += key_size
    return buffer.resize((buffer.width // 8, buffer.height // 8), Image.NEAREST)
