//MessagePage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : messagePage
    // TODO: use something more useful in the header ?
    headerText : qsTr("Tweet detail")
    property var message

    content : ContentColumn {
        anchors.left : parent.left
        anchors.right : parent.right
        MessageContainer {
            id : messageContainer
            message : messagePage.message
            // Explicit width setting is needed due to the MediaGrid
            // for some reason. We should probably fix that.
            width : messagePage.width - rWin.c.style.main.spacing * 2
        }
    }
}