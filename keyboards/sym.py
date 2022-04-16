board_height = 5
board_width = 13
screen_height = 4
asset_folder = 'letters'
backspace_key = 'backspace'
enter_key = 'enter'
default_layout = 'symbols'
preview_keys = {
    'default': ['46', '44', '33', '63'],
}
layouts = {
    'symbols': [
        ['185', '178', '179', '42', '94', '38', '166', '95', '171', '187', '40', '41', '92'],
        ['188', '189', '190', '58', '59', '35', '182', '167', '39', '34', '91', '93', '124'],
        ['43', '45', '177', '36', '162', '37', '191', '161', '33', '63', '123', '125', '47'],
        ['215', '247', '61', '64', '169', '174', '176', '126', '46', '44', '60', '62', 'backspace'],
        ['', '', '', 'lat_extra', 'en_words', 'lat', '32', 'cyr', 'ru_words', '', '', '', 'enter'],
    ],
}

alt_text = {
    k: [[chr(int(string)) if string.isdigit() else '' for string in row] for row in v] for k, v in layouts.items()
}
