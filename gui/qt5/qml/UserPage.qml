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
                text : (userPage.user.description  != null) ? F.makeTextClickable(userPage.user.description, true) : ""
                width : parent.width - rWin.c.style.main.spacing * 2
                wrapMode : Text.Wrap
                textFormat : Text.StyledText
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
            property int itemWidth : (width - 2 * spacing) / 3.0
            ThemedTextRectangle {
                width : userItemsRow.itemWidth
                height : userTBR.height
                label.horizontalAlignment : Text.AlignHCenter
                label.text : "<b>" + qsTr("Tweets") + "</b><br>" + userPage.user.statuses_count
            }
            ThemedTextRectangle {
                width : userItemsRow.itemWidth
                height : userTBR.height
                label.horizontalAlignment : Text.AlignHCenter
                label.text : "<b>" + qsTr("Following") + "</b><br>" + userPage.user.friends_count
            }
            ThemedTextRectangle {
                width : userItemsRow.itemWidth
                height : userTBR.height
                label.horizontalAlignment : Text.AlignHCenter
                label.text : "<b>" + qsTr("Followers") + "</b><br>" +  + userPage.user.followers_count
            }
        }
        ThemedTextRectangle {
            width : parent.width
            height : userTBR.height
            label.horizontalAlignment : Text.AlignHCenter
            label.text : "<b>" + qsTr("Favorites") + "</b><br>" + userPage.user.favourites_count
        }
        ThemedTextRectangle {
            width : parent.width
            height : userTBR.height
            visible : userPage.user.url != null
            label.horizontalAlignment : Text.AlignHCenter
            label.text : "<b>URL:</b> " + userPage.user.url
            onClicked : {
                Qt.openUrlExternally(userPage.user.url)
            }
        }
    }
}
