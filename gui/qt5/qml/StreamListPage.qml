//StreamPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : bitcoinPage
    headerText: "Tsubame"
    property string url : ""
    backButtonWidth : 0
    content : ContentColumn {
        id: dialogContent
        Text {
            anchors.horizontalCenter : parent.horizontalCenter
            text: "Such Twitter client!"
        }
        Button {
            anchors.horizontalCenter : parent.horizontalCenter
            text: qsTr("Wow!")
            onClicked : {
                rWin.notify("So very wow!", 2000)
            }
        }
    }
}