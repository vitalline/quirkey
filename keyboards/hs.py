board_height = 5
board_width = 10
screen_height = 4
resample = 0
asset_folder = 'hs'
backspace_key = 'backspace'
enter_key = 'enter'
default_layout = 'lower'
preview_keys = {
    'upper': [['upper_a', 'upper_b'], ['upper_c', 'upper_d']],
    'lower': [['lower_a', 'lower_b'], ['lower_c', 'lower_d']],
    'symbols': [['symbol_01', 'symbol_02'], ['symbol_03', 'symbol_04']],
    'default': [['upper_h', 'upper_s']]
}
layouts = {
    'upper': [
        ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
        ['upper_a', 'upper_b', 'upper_c', 'upper_d', 'upper_e',
         'upper_f', 'upper_g', 'upper_h', 'upper_i', 'upper_j'],
        ['upper_k', 'upper_l', 'upper_m', 'upper_n', 'upper_o',
         'upper_p', 'upper_q', 'upper_r', 'upper_s', 'upper_t'],
        ['upper_u', 'upper_v', 'upper_w', 'upper_x', 'upper_y',
         'upper_z', 'symbol_30', 'symbol_32', 'symbol_05', 'backspace'],
        ['', '', 'lower', 'symbols', 'space',
         'symbol_22', 'symbol_07', 'symbol_08', 'symbol_06', 'enter'],
    ],
    'lower': [
        ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
        ['lower_a', 'lower_b', 'lower_c', 'lower_d', 'lower_e',
         'lower_f', 'lower_g', 'lower_h', 'lower_i', 'lower_j'],
        ['lower_k', 'lower_l', 'lower_m', 'lower_n', 'lower_o',
         'lower_p', 'lower_q', 'lower_r', 'lower_s', 'lower_t'],
        ['lower_u', 'lower_v', 'lower_w', 'lower_x', 'lower_y',
         'lower_z', 'symbol_01', 'symbol_02', 'symbol_13', 'backspace'],
        ['', '', 'upper', 'symbols', 'space',
         'symbol_11', 'symbol_04', 'symbol_03', 'symbol_12', 'enter'],
    ],
    'symbols': [
        ['', 'symbol_07', 'symbol_08', 'symbol_33', 'symbol_34',
         'symbol_17', 'symbol_18', 'symbol_11', 'symbol_31', ''],
        ['', 'symbol_24', 'symbol_26', 'symbol_35', 'symbol_36',
         'symbol_19', 'symbol_20', 'symbol_22', 'symbol_23', ''],
        ['', 'symbol_27', 'symbol_29', 'symbol_12', 'symbol_13',
         'symbol_21', 'symbol_10', 'symbol_05', 'symbol_06', ''],
        ['symbol_15', 'symbol_30', 'symbol_32', 'symbol_16', 'symbol_37',
         'symbol_14', 'symbol_28', 'symbol_01', 'symbol_02', 'backspace'],
        ['', '', 'upper', 'lower', 'space',
         'symbol_09', 'symbol_25', 'symbol_04', 'symbol_03', 'enter'],
    ]
}
