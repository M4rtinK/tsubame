//MessageBody.qml

import QtQuick 2.0
import UC 1.0
import "../functions.js" as F

Label {
    id: messageText
    property var message
    width : messageDelegate.width - rWin.c.style.main.spacing * 2
    text : F.makeTextClickable(message.full_text, false)
    wrapMode : Text.Wrap
    textFormat : Text.StyledText
    onLinkActivated : {
        rWin.log.info('message link clicked: ' + link)
        if (link.startsWith("@")) {  // username
            rWin.log.debug("username")
        } else if (link.startsWith("#")) {  //hashtag
            var hashtagPage = rWin.loadPage("HashtagStreamPage")
            rWin.log.debug("CREATE HASHTAG PAGE")
            hashtagPage.hashtag = link.substring(1)
            rWin.log.debug(hashtagPage.hashtag)
            rWin.log.debug(link.substring(1))
            rWin.pushPageInstance(hashtagPage)
        } else {  // URL
            Qt.openUrlExternally(link)
        }
    }
}
