//StreamPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : streamPage
    property string streamName : ""
    headerText : streamName
    content : ContentColumn {
        ListView {
            id : streamLW
            anchors.left : parent.left
            anchors.right : parent.right
            height : streamPage.height
            spacing : rWin.c.style.listView.spacing
            model : ListModel {}
            clip : true
            VerticalScrollDecorator {}
            delegate : ThemedBackgroundRectangle {
                id : messageDelegate
                width : streamLW.width
                height : contentC.height + rWin.c.style.listView.itemBorder
                onClicked : {
                    rWin.log.info("message clicked: " + messageId)
                }
                Column {
                    id : contentC
                    anchors.left : parent.left
                    anchors.leftMargin : rWin.c.style.main.spacing
                    anchors.verticalCenter : parent.verticalCenter
                    spacing : rWin.c.style.main.spacing
                    Label {
                        text : "<b>" + messageUsername + "</b>"
                    }
                    Label {
                        width : messageDelegate.width - rWin.c.style.main.spacing * 2
                        text : messageText
                        wrapMode : Text.Wrap
                    }
                }
            }
        }
    }
    Label {
        id : noStreamsLabel
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
        text : "<h2>No messages available.</h2>"
        visible : streamLW.model.count == 0
    }

    onStreamNameChanged : {
        get_messages()
    }

    function get_messages() {
        // reload the stream list from the Python backend
        rWin.log.info("loading messages for " + streamName)
        rWin.python.call("tsubame.gui.streams.get_stream_messages", [streamName, true], function(message_list){
            streamLW.model.clear()
            for (var i=0; i<message_list.length; i++) {
                var message = message_list[i]
                streamLW.model.append({"messageUsername" : message.user.screen_name,
                                       "messageText" : message.full_text})
            }
        })
    }
}