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
    Component.onCompleted : {
        // load the stream list from the Python backend
        rWin.log.info("loading initial message stream list")
        rWin.python.call("tsubame.gui.streams.get_stream_list", [], function(stream_list){
            for (var i=0; i<stream_list.length; i++) {
                var stream = stream_list[i]
                rWin.log.debug("STREAM:")
                rWin.log.debug(stream)
                rWin.log.debug(stream.name)
            }
        })
    }
}