//MessageContainer.qml

import QtQuick 2.0
import UC 1.0

Column {
    id : messageContainer
    property var message
    signal messageHeaderClicked
    signal messageClicked
    property real horizontalMargin : rWin.c.style.main.spacing
    ThemedBackgroundRectangle {
        width : messageContainer.width
        height : messageHeader.height + rWin.c.style.main.spacing * 2.0
        MessageHeader {
            id : messageHeader
            anchors.top : parent.top
            anchors.topMargin : rWin.c.style.main.spacing
            anchors.left : parent.left
            anchors.leftMargin : horizontalMargin
            width : messageContainer.width - horizontalMargin * 2.0
            message : messageContainer.message
        }
        onClicked : {
            messageContainer.messageHeaderClicked()
        }
    }
    ThemedBackgroundRectangle {
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
    }
    ThemedBackgroundRectangle {
        width : messageContainer.width
        height : mediaGrid.height + rWin.c.style.main.spacing * 2.0
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
    }
}

