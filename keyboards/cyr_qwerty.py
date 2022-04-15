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
        ['49', '50', '51', '52', '53', '54', '55', '56', '57', '48', '1025', '1168', '1030'],
        ['1049', '1062', '1059', '1050', '1045', '1053', '1043', '1064', '1065', '1047', '1061', '1066', '1031'],
        ['1060', '1067', '1042', '1040', '1055', '1056', '1054', '1051', '1044', '1046', '1069', '1028', '42'],
        ['1071', '1063', '1057', '1052', '1048', '1058', '1068', '1041', '1070', '43', '58', '59', 'backspace'],
        ['64', '35', '37', '38', 'lower', 'sym', '32', 'ru_words', 'lat/upper:lang', '95', '60', '62', 'enter'],
    ],
    'lower': [
        ['49', '50', '51', '52', '53', '54', '55', '56', '57', '48', '1105', '1169', '1110'],
        ['1081', '1094', '1091', '1082', '1077', '1085', '1075', '1096', '1097', '1079', '1093', '1098', '1111'],
        ['1092', '1099', '1074', '1072', '1087', '1088', '1086', '1083', '1076', '1078', '1101', '1108', '39'],
        ['1103', '1095', '1089', '1084', '1080', '1090', '1100', '1073', '1102', '34', '33', '63', 'backspace'],
        ['40', '41', '47', '61', 'upper', 'sym', '32', 'ru_words', 'lat/lower:lang', '45', '46', '44', 'enter'],
    ],
}
keymap = {
    'upper': [
        ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'grave', 'shift+grave', 'shift+s'],
        ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'bracketleft', 'bracketright', 'shift+bracketright'],
        ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'semicolon', 'apostrophe', 'shift+apostrophe', 'shift+8'],
        ['z', 'x', 'c', 'v', 'b', 'n', 'm', 'comma', 'period', 'shift+equal', 'shift+6,ctrl+shift+semicolon', 'shift+4,ctrl+semicolon', 'backspace'],
        ['shift+2', 'shift+3', 'shift+5', 'shift+7,ctrl+7', 'capslock', '', 'space', '', '', 'shift+minus', 'shift+comma', 'shift+period', 'enter'],
    ],
    'lower': [
        ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'grave', 'shift+grave', 'shift+s'],
        ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'bracketleft', 'bracketright', 'shift+bracketright'],
        ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'semicolon', 'apostrophe', 'shift+apostrophe', 'ctrl+apostrophe,ctrl+2'],
        ['z', 'x', 'c', 'v', 'b', 'n', 'm', 'comma', 'period', 'shift+2', 'shift+1', 'shift+7', 'backspace'],
        ['shift+9', 'shift+0', 'shift+backslash', 'equal', 'capslock', '', 'space', '', '', 'minus', 'slash', 'shift+slash', 'enter'],
    ],
}
