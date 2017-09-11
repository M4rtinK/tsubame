//MessageBody.qml

import QtQuick 2.0
import UC 1.0


Label {
    id: messageText
    property var message
    width : messageDelegate.width - rWin.c.style.main.spacing * 2
    text : message.full_text
    wrapMode : Text.Wrap
    textFormat : Text.StyledText
    onLinkActivated : {
        rWin.log.info('message link clicked: ' + link)
        Qt.openUrlExternally(link)
    }
}
