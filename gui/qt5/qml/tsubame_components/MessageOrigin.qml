//MessageOrigin.qml

import QtQuick 2.0
import UC 1.0

Label {
    id : messageSourceInfo
    property var message
    text : message.tsubame_message_source_plaintext + " | " + message.created_at
    wrapMode : Text.Wrap
    textFormat : Text.StyledText
}
