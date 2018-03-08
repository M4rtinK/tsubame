//UserPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"
import "functions.js" as F

BasePage {
    id : userPage

    property var user

    headerText : "@" + user.screen_name

    property real horizontalMargin : rWin.c.style.main.spacing

    content : ContentColumn {
        anchors.left : parent.left
        anchors.right : parent.right
        spacing : rWin.c.style.main.spacing

        ThemedBackgroundRectangle {
            id : userTBR
            width : parent.width
            height : userInfo.height + rWin.c.style.main.spacing * 2.0
            UserInfo {
                id : userInfo
                anchors.top : parent.top
                anchors.topMargin : rWin.c.style.main.spacing
                anchors.left : parent.left
                anchors.leftMargin : horizontalMargin
                user : userPage.user
            }
        }

        ThemedBackgroundRectangle {
            width : parent.width
            visible : userPage.user.description != null
            height : descriptionLabel.height + rWin.c.style.main.spacing * 2
            onClicked : {
                rWin.log.debug(descriptionLabel.text)
            }
            Label {
                id : descriptionLabel
                anchors.verticalCenter : parent.verticalCenter
                anchors.horizontalCenter : parent.horizontalCenter
                text : (userPage.user.description  != null) ? F.makeTextClickable(userPage.user.description) : ""
                width : parent.width - rWin.c.style.main.spacing * 2
                wrapMode : Text.Wrap
                textFormat : Text.StyledText
                /*
                function makeTextClickable(inputString) {
                    // make Twitter related things & URLs clickable in a piece of text
                    return inputString.replace(/(@\w+)|(#\w+)|(http\S+)/g,'<a href="$&">$&</a>')
                }*/
                onLinkActivated : {
                    rWin.log.info('user description link clicked: ' + link)
                    if (link.startsWith("@")) {  // username
                        rWin.log.debug("username")
                    } else if (link.startsWith("#")) {  //hashtag
                        rWin.log.debug("hashtag")
                    } else {  // URL
                        Qt.openUrlExternally(link)
                    }
                }
            }
        }

        Row {
            id : userItemsRow
            width : parent.width
            spacing : rWin.c.style.main.spacing
            property int itemWidth : (width - 3 * spacing) / 4.0
            ThemedBackgroundRectangle {
                width : userItemsRow.itemWidth
                height : userTBR.height
                Label {
                    anchors.verticalCenter : parent.verticalCenter
                    anchors.horizontalCenter : parent.horizontalCenter
                    text : qsTr("Tweets")
                    font.bold : true
                }
            }
            ThemedBackgroundRectangle {
                width : userItemsRow.itemWidth
                height : userTBR.height
                Label {
                    anchors.verticalCenter : parent.verticalCenter
                    anchors.horizontalCenter : parent.horizontalCenter
                    text : qsTr("Followers")
                    font.bold : true
                }
            }
            ThemedBackgroundRectangle {
                width : userItemsRow.itemWidth
                height : userTBR.height
                Label {
                    anchors.verticalCenter : parent.verticalCenter
                    anchors.horizontalCenter : parent.horizontalCenter
                    text : qsTr("Following")
                    font.bold : true
                }
            }
            ThemedBackgroundRectangle {
                width : userItemsRow.itemWidth
                height : userTBR.height
                Label {
                    anchors.verticalCenter : parent.verticalCenter
                    anchors.horizontalCenter : parent.horizontalCenter
                    text : qsTr("Lists")
                    font.bold : true
                }
            }
        }
    }
}
