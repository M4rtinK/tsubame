//StreamListPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

Page {
    id : streamListPage
    ContentColumn {
        ListView {
            id : streamLW
            anchors.left : parent.left
            anchors.right : parent.right
            height : streamListPage.height
            spacing : rWin.c.style.listView.spacing
            model : ListModel {}
            clip : true
            VerticalScrollDecorator {}
            delegate : ThemedBackgroundRectangle {
                id : streamDelegate
                width : streamLW.width
                height : contentC.height + rWin.c.style.listView.itemBorder
                onClicked : {
                    rWin.log.info("stream clicked: " + streamName)
                    var streamPage = rWin.loadPage("StreamPage")
                    streamPage.streamName = streamName
                    rWin.pushPageInstance(streamPage)
                }
                Column {
                    id : contentC
                    anchors.left : parent.left
                    anchors.leftMargin : rWin.c.style.main.spacing
                    anchors.verticalCenter : parent.verticalCenter
                    spacing : rWin.c.style.main.spacing
                    Label {
                        text : "<b>" + streamName + "</b>"
                    }
                }
            }
        }
    }
    Label {
        id : noStreamsLabel
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
        text : "<h2>No message streams available.</h2>"
        visible : streamLW.model.count == 0
    }
    Component.onCompleted : {
        // get streams from the Python backend
        reload_streams()
    }

    function reload_streams() {
        // reload the stream list from the Python backend
        rWin.log.info("loading initial message stream list")
        rWin.python.call("tsubame.gui.streams.get_stream_list", [], function(stream_list){
            streamLW.model.clear()
            for (var i=0; i<stream_list.length; i++) {
                var stream = stream_list[i]
                streamLW.model.append({"streamName" : stream.name})
            }
        })
    }
}