//MessageBody.qml

import QtQuick 2.0
import UC 1.0
import "../functions.js" as F

Label {
    id: messageText
    property var message
    text : (message != null) ? F.makeUsernamesClickable(message.full_text, false) : ""
    wrapMode : Text.Wrap
    textFormat : Text.StyledText
    onLinkActivated : {
        rWin.log.info('message link clicked: ' + link)
        if (link.substring(0, 1) == "@") {  // username
            var userPage = rWin.loadPage("UserPage")
            userPage.lookupUsername = link.substring(1)
            rWin.pushPageInstance(userPage)

        } else if (link.substring(0, 1) == "#") {  //hashtag
            var hashtagPage = rWin.loadPage("HashtagStreamPage")
            hashtagPage.hashtag = link.substring(1)
            rWin.pushPageInstance(hashtagPage)
        } else {  // URL
            Qt.openUrlExternally(link)
        }
    }
}
