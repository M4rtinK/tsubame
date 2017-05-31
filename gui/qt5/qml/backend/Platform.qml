import QtQuick 2.0

Item {
    property bool valid : false
    property string tsubameVersion : "unknown"
    property bool showQuitButton : true
    property bool fullscreen_only : false
    property bool should_start_in_fullscreen : false
    property bool needs_back_button : true
    property bool needs_page_background : false
    property bool sailfish : false

    function setValuesFromPython(values) {
        tsubameVersion = values.tsubame_version
        showQuitButton = values.show_quit_button
        fullscreen_only = values.fullscreen_only
        should_start_in_fullscreen = values.should_start_in_fullscreen
        needs_back_button = values.needs_back_button
        needs_page_background = values.needs_page_background
        sailfish = values.sailfish
        // done, we now have the values from Python we needed
        valid = true
    }
}