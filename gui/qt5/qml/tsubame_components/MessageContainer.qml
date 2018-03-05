//MessageContainer.qml

import QtQuick 2.0
import UC 1.0

Column {
    id : messageContainer
    property var message
    signal userInfoClicked
    signal messageClicked
    // actually more than just the message - basically everything than the header
    property bool messageClickable : true
    property real horizontalMargin : rWin.c.style.main.spacing
    ThemedBackgroundRectangle {
        id : headerTBR
        pressed_override : bodyTBR.pressed || mediaTBR.pressed || originTBR.pressed
        width : messageContainer.width
        height : messageHeader.height + rWin.c.style.main.spacing * 2.0
        UserInfo {
            id : messageHeader
            anchors.top : parent.top
            anchors.topMargin : rWin.c.style.main.spacing
            anchors.left : parent.left
            anchors.leftMargin : horizontalMargin
            width : messageContainer.width - horizontalMargin * 2.0
            user : messageContainer.message.user
        }
        onClicked : {
            messageContainer.userInfoClicked()
        }
    }
    ThemedBackgroundRectangle {
        id : bodyTBR
        pressed_override : mediaTBR.pressed || originTBR.pressed
        enabled : messageClickable
        width : messageContainer.width
        height : messageBody.height + rWin.c.style.main.spacing * 2.0
        MessageBody {
            id : messageBody
            anchors.top : parent.top
            anchors.topMargin : rWin.c.style.main.spacing
            anchors.left : parent.left
            anchors.leftMargin : horizontalMargin
            width : messageContainer.width - horizontalMargin * 2.0
            message : messageContainer.message
        }
        onClicked : {
            messageContainer.messageClicked()
        }
    }
    ThemedBackgroundRectangle {
        id : mediaTBR
        pressed_override : bodyTBR.pressed || mediaTBR.pressed
        enabled : messageClickable
        width : messageContainer.width
        height : mediaGrid.visible ? mediaGrid.height + rWin.c.style.main.spacing * 2.0 : 0
        MediaGrid {
            id : mediaGrid
            anchors.top : parent.top
            anchors.topMargin : rWin.c.style.main.spacing
            anchors.left : parent.left
            anchors.leftMargin : horizontalMargin
            width : messageContainer.width - horizontalMargin * 2.0
            mediaList : messageContainer.message.media
            spacing : rWin.c.style.main.spacing / 2.0
        }
        onClicked : {
            messageContainer.messageClicked()
        }
    }
    ThemedBackgroundRectangle {
        id : originTBR
        pressed_override : bodyTBR.pressed
        enabled : messageClickable
        width : messageContainer.width
        height : messageOrigin.height + rWin.c.style.main.spacing * 2.0
        MessageOrigin {
            id : messageOrigin
            anchors.top : parent.top
            anchors.topMargin : rWin.c.style.main.spacing
            anchors.left : parent.left
            anchors.leftMargin : horizontalMargin
            width : messageContainer.width - horizontalMargin * 2.0
            message : messageContainer.message
        }
        onClicked : {
            messageContainer.messageClicked()
        }
    }
}

