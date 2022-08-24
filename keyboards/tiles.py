board_height = 3
board_width = 5
screen_height = 5
asset_folder = 'tiles'
default_layout = 'basic'
preview_keys = {
    'default': 'tile_cross'
}
fixed_layout = True
layouts = {
    'basic': [
        ['tile_corner', 'tile_line', '_rotate_cc', '_dir_u', '_rotate_cw'],
        ['tile_corners', 'tile_t', '_dir_l', '_clear', '_dir_r'],
        ['tile_bridge', 'tile_cross', '_flip_x', '_dir_d', '_flip_y'],
    ],
}
