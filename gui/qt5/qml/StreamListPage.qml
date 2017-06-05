//StreamPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

Page {
    id : streamListPage
    property var streams : []
    ContentColumn {
    }
    Label {
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
        text : "<h2>No message streams available.</h2>"
        visible: streamListPage.streams.length == 0
    }
}