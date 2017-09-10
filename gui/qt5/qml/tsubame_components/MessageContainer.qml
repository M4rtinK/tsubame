//MessageContainer.qml

import QtQuick 2.0
import UC 1.0

Column {
        id : messageContainer
        property var message
        spacing : rWin.c.style.main.spacing * 2.0
        MessageHeader {
            message : messageContainer.message
        }
        MessageBody {
            message : messageContainer.message
        }
        MessageOrigin {
            message : messageContainer.message
        }
        MediaGrid {
            width : messageContainer.width
            //width : 300
//            anchors.left : parent.left
//            anchors.leftMargin : rWin.c.style.main.spacing
//            anchors.right : parent.left
//            anchors.rightMargin : rWin.c.style.main.spacing
            mediaList : messageContainer.message.media
            spacing : rWin.c.style.main.spacing / 2.0
        }
}

