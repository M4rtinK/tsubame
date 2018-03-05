//UserPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : userPage

    property var user

    headerText : "@" + user.screen_name

    property real horizontalMargin : rWin.c.style.main.spacing

    content : ContentColumn {
        anchors.left : parent.left
        anchors.right : parent.right

        ThemedBackgroundRectangle {
            id : userTBR
            width : parent.width
            height : userInfo.height + rWin.c.style.main.spacing * 2.0
            UserInfo {
                id : userInfo
                anchors.top : parent.top
                anchors.topMargin : rWin.c.style.main.spacing
                anchors.left : parent.left
                anchors.leftMargin : horizontalMargin
                user : userPage.user
            }
        }
    }
}
