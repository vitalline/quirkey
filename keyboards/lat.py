board_height = 5
board_width = 13
screen_height = 4
asset_folder = 'letters'
backspace_key = 'backspace'
enter_key = 'enter'
default_layout = 'lower'
preview_keys = {
    'upper': ['65', '66', '67', '68'],
    'lower': ['97', '98', '99', '100'],
    'upper:lang': 'lat',
    'lower:lang': 'lat',
    'default': 'lat'
}
layouts = {
    'upper': [
        ['49', '50', '51', '52', '53', '54', '55', '56', '57', '48', '91', '93', '124'],
        ['65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '123', '125', '166'],
        ['75', '76', '77', '78', '79', '80', '81', '82', '83', '84', '95', '43', '92'],
        ['85', '86', '87', '88', '89', '90', '38', '64', '35', '42', '94', '37', 'backspace'],
        ['', '', '', 'lat_extra', 'lower', 'sym', '32', 'en_words', 'cyr/upper:lang', '', '', '', 'enter'],
    ],
    'lower': [
        ['49', '50', '51', '52', '53', '54', '55', '56', '57', '48', '40', '41', '58'],
        ['97', '98', '99', '100', '101', '102', '103', '104', '105', '106', '60', '62', '59'],
        ['107', '108', '109', '110', '111', '112', '113', '114', '115', '116', '45', '61', '47'],
        ['117', '118', '119', '120', '121', '122', '46', '44', '33', '63', '39', '34', 'backspace'],
        ['', '', '', 'lat_extra', 'upper', 'sym', '32', 'en_words', 'cyr/lower:lang', '', '', '', 'enter'],
    ],
}
