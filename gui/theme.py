# Default theme.
THEME_DEFAULT = {
    "id" : "default",
    "color" : {
        "main_fill" : ("white"),
        "main_outline" : ("#3c60fa"),
        "main_text" : ("#00004d"),
        "main_highlight_fill" : ("#f5f5f5"),
        "main_highlight_outline " : ( "#3352d5"),
        "special_button_fill" : ("#ffec8b"),
        "special_button_outline" : ("#8b814c"),
        "widget_background" : ("#0000ff"),
        "widget_text" : ("#ffffff"),
        "icon_grid_toggled" : ("#c6d1f3"),
        "icon_button_normal" : ("#f5f5f5"),
        "icon_button_toggled" : ("#d2d2d2"),
        "icon_button_text" : ("black"),
        "page_header_text" : ("black"),
        "page_background" : ("black"),
        "list_view_background" : ("#d2d2d2")
    }
}
# Theme for use with the Universal Components Controls backend.
# At the moment the Controls theme is the same as the default theme.
THEME_CONTROLS = THEME_DEFAULT.copy()
THEME_CONTROLS["id"] = "controls"

# Theme for use with the Universal Components Silica backend.
THEME_SILICA = {
    "id" : "silica",
    "color": {
        "main_fill" :  ("transparent"),
        "main_outline" :  ("red"),
        "main_text" :  ("red"),
        "main_highlight_fill" : ("#1a1a1ade"),
        "widget_background" :  ("black"),
        "widget_text" :  ("white"),
        "icon_grid_toggled" :  ("#1a1a1aaf"),
        "icon_button_normal" :  ("#525252"),
        "icon_button_toggled" :  ("#1a1a1ade"),
        "icon_button_text" :  ("white"),
        "page_header_text" :  ("white"),
        "list_view_background" : ("transparent")
    }
}

THEMES = {
    "controls" : THEME_CONTROLS,
    "silica" : THEME_SILICA
}