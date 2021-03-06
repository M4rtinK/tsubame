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
                    var streamList = rWin.loadPage("StreamListPage",
                                                   {"backButtonVisible" : rWin.showBackButton})
                    rWin.pushPageInstance(streamList)
                }
            }
            TextButton {
                width : parent.cellWidth
                text: qsTr("<b>Send Tweet<b/>")
                onClicked : {
                    var sendMessagePage = rWin.loadPage("SendMessagePage")
                    rWin.pushPageInstance(sendMessagePage)
                }
            }
            TextButton {
                width : parent.cellWidth
                text: qsTr("<b>Search<b/>")
                onClicked : {
                    var searchPage = rWin.loadPage("SearchPage")
                    rWin.pushPageInstance(searchPage)
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