//UserPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"
import "functions.js" as F

BasePage {
    id : userPage
    property bool dataValid : false
    property bool listDataValid : false
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
        "public_lists" : null,
        "public_list_count" : 0
    }

    headerText : userPage.dataValid ? "@" + user.screen_name : qsTr("fetching user info")
    headerMenu : TopMenu {
        MenuItem {
            text: qsTr("Open profile in browser")
            onClicked : {
                rWin.log.info('opening user profile in browser: ' + user.screen_name)
                var profile_url = "https://twitter.com/" + user.screen_name
                Qt.openUrlExternally(profile_url)
            }
        }
        MenuItem {
            text: qsTr("Add to/remove from lists")
            onClicked : {
               var alcPage = rWin.loadPage("AccountListCategoriesPage",
                                           {"membershipUsername" : user.screen_name})
               rWin.pushPageInstance(alcPage)
            }
        }

    }

    property real horizontalMargin : rWin.c.style.main.spacing

    onLookupUsernameChanged : {
        getUserInfo()
    }

    function getListInfo(listSearchUsername) {
        if (listSearchUsername) {
            rWin.python.call("tsubame.gui.users.get_user_lists", [listSearchUsername], function(listInfo){
                if (listInfo) {
                    rWin.log.debug("got information about public lists owned user @" + listSearchUsername)
                    userPage.lists = listInfo
                } else {
                    rWin.log.debug("got no information about public lists owned by user @" + listSearchUsername)
                }
                // no data found for username is also valid data
                userPage.listDataValid = true
            })
        }
    }

    function getUserInfo() {
        rWin.python.call("tsubame.gui.users.get_user_info", [lookupUsername], function(userInfo){
            if (userInfo) {
                rWin.log.debug("got information about user @" + lookupUsername)
                userPage.user = userInfo
                // also set public list info which should also be included
                // in the result
                userPage.lists = userInfo.public_list_info
            } else {
                rWin.log.debug("got no information about user @" + lookupUsername)
            }
            // no data found for username is also valid data
            userPage.dataValid = true
            userPage.listDataValid = true
        })
    }

    content : ContentColumn {
        anchors.left : parent.left
        anchors.right : parent.right
        spacing : rWin.c.style.main.spacing

        ThemedBackgroundRectangle {
            id : userTBR
            visible : userPage.dataValid
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
        }
        Row {
            id : userItemsRow
            visible : userPage.dataValid
            width : parent.width
            spacing : rWin.c.style.main.spacing
            property int itemWidth : (width - 2 * spacing) / 3.0
            ThemedTextRectangle {
                width : userItemsRow.itemWidth
                height : userTBR.height
                label.horizontalAlignment : Text.AlignHCenter
                label.text : "<b>" + qsTr("Tweets") + "</b><br>" + userPage.user.statuses_count
                onClicked : {
                    var userTweetsPage = rWin.loadPage("UserTweetsStreamPage")
                    userTweetsPage.username = userPage.user.screen_name
                    rWin.pushPageInstance(userTweetsPage)
                }
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
            visible : userPage.dataValid
            label.horizontalAlignment : Text.AlignHCenter
            label.text : "<b>" + qsTr("Favorites") + "</b><br>" + userPage.user.favourites_count
            onClicked : {
                var userFavoritesPage = rWin.loadPage("UserFavoritesStreamPage")
                userFavoritesPage.username = userPage.user.screen_name
                rWin.pushPageInstance(userFavoritesPage)
            }
        }
        ThemedBackgroundRectangle {
            id : interactionTR
            width : parent.width
            height : interactLabel.height + activeItem.height + rWin.c.style.main.spacing * 3
            visible : userPage.dataValid
            property bool followStateKnown : false
            property bool accountFollowsUser : false
            property bool operationInProgress : false
            property string accountUsername : ""
            onAccountUsernameChanged : {
                if (accountUsername) {
                    interactionTR.followStateKnown = false
                    rWin.python.call("tsubame.gui.users.check_account_follows_user",
                        [accountUsername, user.screen_name],
                        function(result) {
                            interactionTR.followStateKnown = true
                            interactionTR.accountFollowsUser = result
                    })
                }
            }
            Label {
                id : interactLabel
                anchors.top : interactionTR.top
                anchors.topMargin : rWin.c.style.main.spacing
                anchors.horizontalCenter : parent.horizontalCenter
                text : "<b>" + qsTr("Interact") + "</b>"
            }
            Item {
                id : activeItem
                anchors.top : interactLabel.bottom
                height : accountCB.height
                width : parent.width
                AccountComboBox {
                    id : accountCB
                    label : qsTr("Account")
                    anchors.top : parent.top
                    anchors.topMargin : rWin.c.style.main.spacing
                    anchors.left : parent.left
                    anchors.leftMargin : rWin.c.style.main.spacing
                    width : parent.width / 2.0
                    onSelectedAccountUsernameChanged : {
                        interactionTR.accountUsername = selectedAccountUsername
                    }
                }
                Button {
                    id : followButton
                    visible : interactionTR.accountUsername && interactionTR.followStateKnown
                    text : interactionTR.accountFollowsUser ? qsTr("Unfollow") : qsTr("Follow")
                    width : parent.width / 3.0
                    anchors.top : parent.top
                    anchors.topMargin : rWin.c.style.main.spacing * 2
                    anchors.right : parent.right
                    anchors.rightMargin : rWin.c.style.main.spacing
                    onClicked : {
                        if (!interactionTR.operationInProgress) {
                            interactionTR.operationInProgress = true
                            if (interactionTR.accountFollowsUser) {
                                rWin.python.call("tsubame.gui.users.unfollow_user",
                                                 [interactionTR.accountUsername, user.screen_name],
                                                 function(result){
                                    interactionTR.operationInProgress = false
                                    if (result[0]) {
                                        interactionTR.accountFollowsUser = false
                                    } else if (result[1]) {
                                        var message = qsTr("Can't unfollow") + ": " + result[1]
                                        rWin.notify(message)
                                    }
                                })
                            } else {
                                rWin.python.call("tsubame.gui.users.follow_user",
                                                 [interactionTR.accountUsername, user.screen_name],
                                                 function(result){
                                    interactionTR.operationInProgress = false
                                    if (result[0]) {
                                        interactionTR.accountFollowsUser = true
                                    } else if (result[1]) {
                                        var message = qsTr("Can't follow") + ": " + result[1]
                                        rWin.notify(message)
                                    }
                                })
                            }
                        }
                    }
                }
            }
        }
        ThemedTextRectangle {
            width : parent.width
            height : userTBR.height
            visible : userPage.dataValid
            label.horizontalAlignment : Text.AlignHCenter
            label.text : "<b>" + qsTr("Lists") + "</b>"
        }
        ThemedTextRectangle {
            width : parent.width
            height : userTBR.height
            visible : userPage.user.url != null
            label.horizontalAlignment : Text.AlignHCenter
            label.text : "<b>" + qsTr("URL") + ":</b> " + userPage.user.url
            onClicked : {
                Qt.openUrlExternally(userPage.user.url)
            }
        }
        ThemedTextRectangle {
            width : parent.width
            height : userTBR.height
            visible : userPage.user.location != null
            label.horizontalAlignment : Text.AlignHCenter
            label.text : "<b>" + qsTr("location") +":</b> " + userPage.user.location
        }
        ThemedTextRectangle {
            width : parent.width
            height : userTBR.height
            visible : userPage.user.time_zone != null
            label.horizontalAlignment : Text.AlignHCenter
            label.text : "<b>" + qsTr("timezone") + ":</b> " + userPage.user.time_zone
        }
    }
    BusyIndicator {
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
        visible : !userPage.dataValid
        running : !userPage.dataValid
    }
}
