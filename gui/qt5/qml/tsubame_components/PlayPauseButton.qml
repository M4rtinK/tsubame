// PlayPauseButton.qml

import QtQuick 2.0
import UC 1.0

ThemedBackgroundRectangle {
    id: playRectangle
    width : 64 * rWin.c.style.m
    height : 64 * rWin.c.style.m
    cornerRadius : width * 0.5 // lets make this into a circle
    borderWidth : 4 * rWin.c.style.m
    property bool play : true
    Label {
        id: playEmoji
        text: play ? "▶️" : "⏸️"
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
    }
}