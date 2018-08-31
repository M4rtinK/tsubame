//StreamSettingsPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : streamSettings
    headerText : qsTr("Global menu")
    content : ContentColumn {
        anchors.left : parent.left
        anchors.right : parent.right
    }
}