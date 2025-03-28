board_height = 6
board_width = 13
screen_height = 3
asset_folder = 'letters'
backspace_key = 'backspace'
enter_key = 'enter'
default_layout = 'accents'
preview_keys = {
    'default': ['198', '199', '207', '209']
}
layouts = {
    'accents': [
        ['192', '193', '194', '195', '196', '197', '198', '199', '200', '201', '202', '203', '204'],
        ['205', '206', '207', '208', '209', '210', '211', '212', '213', '214', '216', '217', '218'],
        ['219', '220', '221', '222', '223', '224', '225', '226', '227', '228', '229', '230', '231'],
        ['232', '233', '234', '235', '236', '237', '238', '239', '240', '241', '242', '243', '244'],
        ['', '245', '246', '248', '249', '250', '/sym', '251', '252', '253', '254', '255', 'backspace'],
        ['', '', '', '', '/en_words', '/lat', '32', '/cyr', '/ru_words', '', '', '', 'enter'],
    ],
}

alt_text = {
    k: [[chr(int(string)) if string.isdigit() else '' for string in row] for row in v] for k, v in layouts.items()
}
