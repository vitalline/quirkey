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
        ['tile_corner', 'tile_line', 'rotate_cw', 'dir_u', 'rotate_cc'],
        ['tile_corners', 'tile_t', 'dir_l', 'clear', 'dir_r'],
        ['tile_bridge', 'tile_cross', 'tile_empty', 'dir_d', 'rotate_flip'],
    ],
}
