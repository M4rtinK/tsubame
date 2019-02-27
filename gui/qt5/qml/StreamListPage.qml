//StreamListPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : streamListPage

    headerText: qsTr("Message streams")
    headerMenu : TopMenu {
        MenuItem {
            text: qsTr("Global menu")
            onClicked : {
                var globalMenuPage = rWin.loadPage("GlobalMenuPage")
                rWin.pushPageInstance(globalMenuPage)
            }
        }
    }

    property bool noStreamsAvailable : streamLW.model.count == 0 && !streamListPage.fetchingStreams

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
        visible : noStreamsAvailable && rWin.accountsAvailableAtStartup
    }
    Column {
        id : noAccountsNotice
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
        visible : noStreamsAvailable && !rWin.accountsAvailableAtStartup
        Label {
            text : qsTr("<h2>No accounts have been added.</h2>")
            anchors.horizontalCenter : parent.horizontalCenter
        }
        Button {
            text : qsTr("Add an account")
            anchors.horizontalCenter : parent.horizontalCenter
            onClicked : {
                rWin.pushPageInstance(rWin.loadPage("AddTwitterAccountStartPage"))
            }
        }
    }
    BusyIndicator {
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
        visible : streamListPage.fetchingStreams
        running : streamListPage.fetchingStreams
    }
    Component.onCompleted : {
        // reload streams when account list changes
        rWin.python.setHandler("streamListChanged", function(){
            reload_streams()
        })
        // get streams from the Python backend
        reload_streams()
    }

    function reload_streams() {
        // reload the stream list from the Python backend
        rWin.log.info("loading message stream list")
        streamListPage.fetchingStreams = true
        rWin.python.call("tsubame.gui.streams.get_named_stream_list", [], function(stream_list){
            streamLW.model.clear()
            for (var i=0; i<stream_list.length; i++) {
                var stream = stream_list[i]
                streamLW.model.append({"streamName" : stream.name})
            }
            streamListPage.fetchingStreams = false
        })
    }
}