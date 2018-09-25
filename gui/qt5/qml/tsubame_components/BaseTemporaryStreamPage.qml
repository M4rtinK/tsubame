//BaseTemporaryStreamPage.qml
//
// This is basically the BaseStreamPage + top menu suitable
// for temporary pages.
// This is done so that apparently at least with Silica
// if two header menus are defined, both are shown, intead
// of the first one replacing the other.
// So we need to make sure only one top menu is instantiated
// per page via all inheritance.

import QtQuick 2.0
import UC 1.0

BaseStreamPage {
    headerMenu : TopMenu {
        MenuItem {
            text: qsTr("Global menu")
            onClicked : {
                var globalMenuPage = rWin.loadPage("GlobalMenuPage")
                rWin.pushPageInstance(globalMenuPage)
            }
        }
        MenuItem {
            text : qsTr("Refresh")
            onClicked : {
                refreshStream(streamName)
            }
        }
    }

}
