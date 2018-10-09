//AccountPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"
import "functions.js" as F

BasePage {
    id : accountPage
    property bool dataValid : false
    // If the lookupUsername property is set
    // it means we need to lookup information
    // about the user as it will not be provided
    // at page creation time.
    property string lookupUsername : ""
    property var user : {
        "screen_name" : null,
        "description" : null,
        "statuses_count" : null,
        "friends_count" : null,
        "followers_count" : null,
        "favourites_count" : null,
        "url" : null,
        "location" : null,
        "time_zone" : null
    }
    property var lists : {
        "private_lists" : null,
        "private_list_count" : 0,
        "public_lists" : null,
        "public_list_count" : 0
    }

    headerText : accountPage.dataValid ? "@" + user.screen_name : qsTr("fetching user info")
    headerMenu : TopMenu {
        MenuItem {
            text: qsTr("Open profile in browser")
            onClicked : {
                rWin.log.info('opening user profile in browser: ' + user.screen_name)
                var profile_url = "https://twitter.com/" + user.screen_name
                Qt.openUrlExternally(profile_url)
            }
        }
    }

    property real horizontalMargin : rWin.c.style.main.spacing

    onLookupUsernameChanged : {
        rWin.python.call("tsubame.gui.accounts.get_account_user_info", [lookupUsername], function(userInfo){
            if (userInfo) {
                rWin.log.debug("got information about user @" + lookupUsername)
                accountPage.user = userInfo
                accountPage.lists = userInfo.list_info
            } else {
                rWin.log.debug("got no information about user @" + lookupUsername)
            }
            // no data found for username is also valid data
            accountPage.dataValid = true
        })
    }

    content : ContentColumn {
        anchors.left : parent.left
        anchors.right : parent.right
        spacing : rWin.c.style.main.spacing

        ThemedBackgroundRectangle {
            id : userTBR
            visible : accountPage.dataValid
            width : parent.width
            height : userInfo.height + rWin.c.style.main.spacing * 2.0
            UserInfo {
                id : userInfo
                anchors.top : parent.top
                anchors.topMargin : rWin.c.style.main.spacing
                anchors.left : parent.left
                anchors.leftMargin : horizontalMargin
                user : accountPage.user
            }
        }

        ThemedBackgroundRectangle {
            width : parent.width
            visible : accountPage.user.description != null
            height : descriptionLabel.height + rWin.c.style.main.spacing * 2
            onClicked : {
                rWin.log.debug(descriptionLabel.text)
            }
            Label {
                id : descriptionLabel
                anchors.verticalCenter : parent.verticalCenter
                anchors.horizontalCenter : parent.horizontalCenter
                text : (accountPage.user.description  != null) ? F.makeTextClickable(accountPage.user.description, true) : ""
                width : parent.width - rWin.c.style.main.spacing * 2
                wrapMode : Text.Wrap
                textFormat : Text.StyledText
                onLinkActivated : {
                    rWin.log.info('user description link clicked: ' + link)
                    if (link.substring(0, 1) == "@") {  // username
                        var accountPage = rWin.loadPage("UserPage")
                        accountPage.lookupUsername = link.substring(1)
                        rWin.pushPageInstance(accountPage)
                    } else if (link.substring(0, 1) == "#") {  //hashtag
                        var hashtagPage = rWin.loadPage("HashtagStreamPage")
                        hashtagPage.hashtag = link.substring(1)
                        rWin.pushPageInstance(hashtagPage)
                    } else {  // URL
                        Qt.openUrlExternally(link)
                    }
                }
            }
        }
        Row {
            id : userItemsRow
            visible : accountPage.dataValid
            width : parent.width
            spacing : rWin.c.style.main.spacing
            property int itemWidth : (width - 2 * spacing) / 3.0
            ThemedTextRectangle {
                width : userItemsRow.itemWidth
                height : userTBR.height
                label.horizontalAlignment : Text.AlignHCenter
                label.text : "<b>" + qsTr("Tweets") + "</b><br>" + accountPage.user.statuses_count
                onClicked : {
                    var userTweetsPage = rWin.loadPage("UserTweetsStreamPage")
                    userTweetsPage.username = accountPage.user.screen_name
                    rWin.pushPageInstance(userTweetsPage)
                }
            }
            ThemedTextRectangle {
                width : userItemsRow.itemWidth
                height : userTBR.height
                label.horizontalAlignment : Text.AlignHCenter
                label.text : "<b>" + qsTr("Following") + "</b><br>" + accountPage.user.friends_count
            }
            ThemedTextRectangle {
                width : userItemsRow.itemWidth
                height : userTBR.height
                label.horizontalAlignment : Text.AlignHCenter
                label.text : "<b>" + qsTr("Followers") + "</b><br>" +  + accountPage.user.followers_count
            }
        }
        ThemedTextRectangle {
            width : parent.width
            height : userTBR.height
            visible : accountPage.dataValid
            label.horizontalAlignment : Text.AlignHCenter
            label.text : "<b>" + qsTr("Favorites") + "</b><br>" + accountPage.user.favourites_count
            onClicked : {
                var userFavoritesPage = rWin.loadPage("UserFavoritesStreamPage")
                userFavoritesPage.username = accountPage.user.screen_name
                rWin.pushPageInstance(userFavoritesPage)
            }
        }

        Row {
            id : listsRow
            visible : accountPage.dataValid
            width : parent.width
            spacing : rWin.c.style.main.spacing
            property int itemWidth : (width - spacing) / 2.0

            ThemedTextRectangle {
                width : listsRow.itemWidth
                height : userTBR.height
                visible : accountPage.dataValid
                label.horizontalAlignment : Text.AlignHCenter
                label.text : "<b>" + qsTr("Private Lists") + "</b><br>" + accountPage.lists.private_list_count
            }
            ThemedTextRectangle {
                width : listsRow.itemWidth
                height : userTBR.height
                visible : accountPage.dataValid
                label.horizontalAlignment : Text.AlignHCenter
                label.text : "<b>" + qsTr("Public Lists") + "</b><br>" + accountPage.lists.public_list_count
            }
        }
        ThemedTextRectangle {
            width : parent.width
            height : userTBR.height
            visible : accountPage.user.url != null
            label.horizontalAlignment : Text.AlignHCenter
            label.text : "<b>" + qsTr("URL") + ":</b> " + accountPage.user.url
            onClicked : {
                Qt.openUrlExternally(accountPage.user.url)
            }
        }
        ThemedTextRectangle {
            width : parent.width
            height : userTBR.height
            visible : accountPage.user.location != null
            label.horizontalAlignment : Text.AlignHCenter
            label.text : "<b>" + qsTr("location") +":</b> " + accountPage.user.location
        }
        ThemedTextRectangle {
            width : parent.width
            height : userTBR.height
            visible : accountPage.user.time_zone != null
            label.horizontalAlignment : Text.AlignHCenter
            label.text : "<b>" + qsTr("timezone") + ":</b> " + accountPage.user.time_zone
        }
    }
    BusyIndicator {
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
        visible : !accountPage.dataValid
        running : !accountPage.dataValid
    }
}
