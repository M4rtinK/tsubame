//globalMenuPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : streamSettings
    headerText : qsTr("Global menu")
    content : ContentColumn {
        SmartGrid {
            id : smartGrid
            TextButton {
                width : parent.cellWidth
                text: qsTr("<b>Main stream list<b/>")
                onClicked : {
                    var streamList = rWin.loadPage("StreamListPage")
                    streamList.backButtonVisible = true
                    rWin.pushPageInstance(streamList)
                }
            }
            TextButton {
                width : parent.cellWidth
                text: qsTr("<b>Accounts<b/>")
                onClicked : {
                    var accountsPage = rWin.loadPage("AccountsPage")
                    rWin.pushPageInstance(accountsPage)
                }
            }
            TextButton {
                width : parent.cellWidth
                text: qsTr("<b>Options</b>")
                onClicked : {
                    rWin.pushPageInstance(rWin.loadPage("GlobalOptionsPage"))
                }
            }
        }
    }
}