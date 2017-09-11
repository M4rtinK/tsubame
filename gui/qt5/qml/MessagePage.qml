//MessagePage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : messagePage
    property var message
    headerText : qsTr("Tweet detail")
    headerMenu : TopMenu {
        MenuItem {
            text: qsTr("Open in browser")
            onClicked : {
                rWin.log.info('opening Tweet in browser: ' + message)
                var tweet_url = "https://twitter.com/" + message.user.screen_name + "/status/" + message.id_str
                Qt.openUrlExternally(tweet_url)
            }
        }
    }
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