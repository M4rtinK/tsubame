//GlobalOptionsPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : streamSettings
    headerText : qsTr("Global options")
    content : ContentColumn {
        SmartGrid {
            id : smartGrid
            TextButton {
                width : parent.cellWidth
                text: qsTr("<b>Media</b>")
                onClicked : {
                    rWin.pushPageInstance(rWin.loadPage("MediaOptionsPage"))
                }
            }
        }
    }



}



