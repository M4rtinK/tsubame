// ThemedBackgroundRectangle.qml
// A background rectangle that respects the modRana theme.

import QtQuick 2.0
import UC 1.0

ThemedBackgroundRectangle {
    id : tbr
    property alias label : innerLabel
    signal linkActivated(string link)
    Label {
        id : innerLabel
        anchors.verticalCenter : parent.verticalCenter
        anchors.horizontalCenter : parent.horizontalCenter
        width : parent.width - rWin.c.style.main.spacing * 2
        wrapMode : Text.Wrap
        textFormat : Text.StyledText
        onLinkActivated : {
            tbr.onLinkActivated(link)
        }
    }
}