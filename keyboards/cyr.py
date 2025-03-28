board_height = 5
board_width = 13
screen_height = 4
asset_folder = 'letters'
backspace_key = 'backspace'
enter_key = 'enter'
default_layout = 'lower'
preview_keys = {
    'upper': ['1040', '1041', '1042', '1043'],
    'lower': ['1072', '1073', '1074', '1075'],
    'upper:lang': 'cyr',
    'lower:lang': 'cyr',
    'default': 'cyr'
}
layouts = {
    'upper': [
        ['49', '50', '51', '52', '53', '54', '55', '56', '57', '48', '1025', '1168', '1028'],
        ['1040', '1041', '1042', '1043', '1044', '1045', '1046', '1047', '1048', '1049', '1050', '1030', '1031'],
        ['1051', '1052', '1053', '1054', '1055', '1056', '1057', '1058', '1059', '1060', '1061', '43', '42'],
        ['1062', '1063', '1064', '1065', '1066', '1067', '1068', '1069', '1070', '1071', '58', '59', 'backspace'],
        ['64', '35', '37', '38', '~/lower', '/sym', '32', '/ru_words', '/lat/upper:lang', '95', '60', '62', 'enter'],
    ],
    'lower': [
        ['49', '50', '51', '52', '53', '54', '55', '56', '57', '48', '1105', '1169', '1108'],
        ['1072', '1073', '1074', '1075', '1076', '1077', '1078', '1079', '1080', '1081', '1082', '1110', '1111'],
        ['1083', '1084', '1085', '1086', '1087', '1088', '1089', '1090', '1091', '1092', '1093', '39', '34'],
        ['1094', '1095', '1096', '1097', '1098', '1099', '1100', '1101', '1102', '1103', '33', '63', 'backspace'],
        ['40', '41', '47', '61', '~/upper', '/sym', '32', '/ru_words', '/lat/lower:lang', '45', '46', '44', 'enter'],
    ],
}
keymap = {
    'upper': [
        ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'grave', 'shift+grave', 'shift+apostrophe'],
        ['f', 'comma', 'd', 'u', 'l', 't', 'semicolon', 'p', 'b', 'q', 'r', 'shift+s', 'shift+bracketright'],
        ['k', 'v', 'y', 'j', 'g', 'h', 'c', 'n', 'e', 'a', 'bracketleft', 'shift+equal', 'shift+8'],
        ['w', 'x', 'i', 'o', 'bracketright', 's', 'm', 'apostrophe', 'period', 'z', 'shift+6,ctrl+shift+semicolon', 'shift+4,ctrl+semicolon', 'backspace'],
        ['shift+2', 'shift+3', 'shift+5', 'shift+7,ctrl+7', 'capslock', '', 'space', '', '', 'shift+minus', 'shift+comma', 'shift+period', 'enter'],
    ],
    'lower': [
        ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'grave', 'shift+grave', 'shift+apostrophe'],
        ['f', 'comma', 'd', 'u', 'l', 't', 'semicolon', 'p', 'b', 'q', 'r', 'shift+s', 'shift+bracketright'],
        ['k', 'v', 'y', 'j', 'g', 'h', 'c', 'n', 'e', 'a', 'bracketleft', 'ctrl+apostrophe,ctrl+2', 'shift+2'],
        ['w', 'x', 'i', 'o', 'bracketright', 's', 'm', 'apostrophe', 'period', 'z', 'shift+1', 'shift+7', 'backspace'],
        ['shift+9', 'shift+0', 'shift+backslash', 'equal', 'capslock', '', 'space', '', '', 'minus', 'slash', 'shift+slash', 'enter'],
    ],
}

alt_text = {
    k: [[chr(int(string)) if string.isdigit() else '' for string in row] for row in v] for k, v in layouts.items()
}
