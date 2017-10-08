//StreamListPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : streamListPage

    headerText: qsTr("Message streams")
    backButtonVisible : false
    property bool fetchingStreams : false

    content : ContentColumn {
        anchors.leftMargin : rWin.isDesktop ? 0 : rWin.c.style.main.spacing
        anchors.rightMargin : rWin.isDesktop ? 0 : rWin.c.style.main.spacing
        ThemedListView {
            id : streamLW
            anchors.left : parent.left
            anchors.right : parent.right
            height : streamListPage.height - rWin.headerHeight
            model : ListModel {}
            delegate : ThemedBackgroundRectangle {
                id : streamDelegate
                width : streamLW.width
                height : contentC.height + rWin.c.style.listView.itemBorder
                onClicked : {
                    rWin.log.info("stream clicked: " + streamName)
                    var streamPage = rWin.loadPage("NamedStreamPage")
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
        text : qsTr("<h2>No message streams available.</h2>")
        visible : streamLW.model.count == 0 && !streamListPage.fetchingStreams
    }
    BusyIndicator {
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
        visible : streamListPage.fetchingStreams
        running : streamListPage.fetchingStreams
    }
    Component.onCompleted : {
        // get streams from the Python backend
        reload_streams()
    }

    function reload_streams() {
        // reload the stream list from the Python backend
        rWin.log.info("loading message stream list")
        streamListPage.fetchingStreams = true
        rWin.python.call("tsubame.gui.streams.get_stream_list", [], function(stream_list){
            streamLW.model.clear()
            for (var i=0; i<stream_list.length; i++) {
                var stream = stream_list[i]
                streamLW.model.append({"streamName" : stream.name})
            }
            streamListPage.fetchingStreams = false
        })
    }
}