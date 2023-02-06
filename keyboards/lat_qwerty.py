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
        ['81', '87', '69', '82', '84', '89', '85', '73', '79', '80', '123', '125', '166'],
        ['65', '83', '68', '70', '71', '72', '74', '75', '76', '42', '95', '43', '92'],
        ['90', '88', '67', '86', '66', '78', '77', '64', '35', '38', '94', '37', 'backspace'],
        ['', '', '/color_picker', '/lat_extra', '~/lower', '/sym', '32', '/en_words', '/cyr/upper:lang', '', '', '', 'enter'],
    ],
    'lower': [
        ['49', '50', '51', '52', '53', '54', '55', '56', '57', '48', '40', '41', '58'],
        ['113', '119', '101', '114', '116', '121', '117', '105', '111', '112', '60', '62', '59'],
        ['97', '115', '100', '102', '103', '104', '106', '107', '108', '39', '45', '61', '47'],
        ['122', '120', '99', '118', '98', '110', '109', '46', '44', '33', '63', '34', 'backspace'],
        ['', '', '/color_picker', '/lat_extra', '~/upper', '/sym', '32', '/en_words', '/cyr/lower:lang', '', '', '', 'enter'],
    ],
}
keymap = {
    'upper': [
        ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'bracketleft', 'bracketright', 'bar,shift+backslash'],
        ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'braceleft,shift+bracketleft', 'braceright,shift+bracketright', 'ctrl+backslash'],
        ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'asterisk,shift+8', 'underscore,shift+minus', 'plus,shift+equals', 'backslash'],
        ['z', 'x', 'c', 'v', 'b', 'n', 'm', 'at,shift+2', 'hash,shift+3', 'ampersand,shift+7', 'asciicircum,shift+6', 'percent,shift+5', 'backspace'],
        ['', '', '', '', 'capslock', '', 'space', '', '', '', '', '', 'enter'],
    ],
    'lower': [
        ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'parenleft,shift+9', 'parenright,shift+0', 'colon,shift+semicolon'],
        ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'less,shift+comma', 'greater,shift+period', 'semicolon'],
        ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'apostrophe', 'minus', 'equal', 'slash'],
        ['z', 'x', 'c', 'v', 'b', 'n', 'm', 'period', 'comma', 'exclamation,shift+1', 'question,shift+slash', 'doublequote,shift+apostrophe', 'backspace'],
        ['', '', '', '', 'capslock', '', 'space', '', '', '', '', '', 'enter'],
    ],
}

alt_text = {
    k: [[chr(int(string)) if string.isdigit() else '' for string in row] for row in v] for k, v in layouts.items()
}
