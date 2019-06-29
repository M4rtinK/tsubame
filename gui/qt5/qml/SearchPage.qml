//StreamSettingsPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : streamSettings
    headerText : qsTr("Search")
    content : ContentColumn {
        SearchField {
            id : searchInput
            anchors.left : parent.left
            anchors.leftMargin : rWin.c.style.main.spacingBig
            anchors.right : parent.right
            anchors.rightMargin : rWin.c.style.main.spacingBig
            //anchors.top : parent.top
            //anchors.topMargin : rWin.c.style.main.spacing
            //height : rWin.headerHeight - rWin.c.style.main.spacing*2
            placeholderText: qsTr("enter your search query")
            Component.onCompleted : {
                selectAll()
            }
            Keys.onPressed : {
                if (event.key == Qt.Key_Return || event.key == Qt.Key_Enter){
                    // turn off the virtual keyboard (if any) if there is some text in the search field
                    if (text !== "") {
                        focus = false
                    }
                    rWin.log.info("Twitter search for: " + text)
                    /*
                    if (searchPage.lastSearchKey != "") {
                        rWin.log.info("search: saving " + text)
                        rWin.set(searchPage.lastSearchKey, text)
                    }*/
                    var searchStreamPage = rWin.loadPage("SearchStreamPage", {"searchTerm" : text})
                    rWin.pushPageInstance(searchStreamPage)
                }
            }
            text : ""
        }
    }
}