//StreamListPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : streamListPage

    headerText: qsTr("Message streams")
    backButtonVisible : false

    content : ContentColumn {
        anchors.leftMargin : rWin.isDesktop ? 0 : rWin.c.style.main.spacing
        anchors.rightMargin : rWin.isDesktop ? 0 : rWin.c.style.main.spacing
        ThemedListView {
            id : streamLW
            anchors.left : parent.left
            anchors.right : parent.right
            height : streamListPage.height
            model : ListModel {}
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