//MessageHeader.qml

import QtQuick 2.0
import UC 1.0

Row {
    property alias avatarUrl : userAvatar.source
    property alias name : nameLabel.text
    property alias username : usernameLabel.text
    spacing : rWin.c.style.main.spacing * 1.5

    Image {
        id : userAvatar
        width : 48 * rWin.c.style.m
        height : 48 * rWin.c.style.m
        smooth : true
    }
    Column {
        anchors.verticalCenter : userAvatar.verticalCenter
        id : namesColumn
        spacing : rWin.c.style.main.spacing / 2.0
        Label {
            id : nameLabel
        }
        Label {
            id : usernameLabel
        }

    }
}
