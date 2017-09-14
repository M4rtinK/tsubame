//MessageOrigin.qml

import QtQuick 2.0
import UC 1.0
import "../moment.js" as M

Label {
    id : messageSourceInfo
    property var message
    text : message.tsubame_message_source_plaintext + " | "
           + M.moment(message.created_at, 'dd MMM DD HH:mm:ss ZZ YYYY', 'en').fromNow()
    wrapMode : Text.Wrap
    textFormat : Text.StyledText
}
