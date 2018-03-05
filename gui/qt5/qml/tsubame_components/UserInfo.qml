//MessageHeader.qml

import QtQuick 2.0
import UC 1.0

Row {
    property var user : null
    spacing : rWin.c.style.main.spacing * 1.5
    Image {
        id : userAvatar
        source : user.profile_image_url
        width : 48 * rWin.c.style.m
        height : 48 * rWin.c.style.m
        smooth : true
        asynchronous : true
    }
    Column {
        anchors.verticalCenter : userAvatar.verticalCenter
        id : namesColumn
        spacing : rWin.c.style.main.spacing / 2.0
        Label {
            id : nameLabel
            text : "<b>" + user.name + "</b>"
        }
        Label {
            id : usernameLabel
            text : "@" + user.screen_name
        }
    }
}

