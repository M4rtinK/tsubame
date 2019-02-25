//ListsPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : listsPage
    property string username : null
    // does Tsubame have a matching account added
    // - this generally means the list can be fully controlled as they are "ours"
    property bool accountAvailable : false
    // is this a listing of public or private lists ?
    property bool privateLists : false
    property bool isReady: false
    property string privatePublicSymbol: privateLists ? " 🔒 " : " 📢 "
    headerText : username + privatePublicSymbol + qsTr("lists")
    headerMenu : TopMenu {
        MenuItem {
            text: qsTr("Create list")
            visible : accountAvailable
            onClicked : {
                var createListPage = rWin.loadPage("CreateListPage", {
                    "accountUsername" : listsPage.username,
                    "isPrivate" : listsPage.privateLists
                })
                rWin.pushPageInstance(createListPage)
            }
        }
    }
    content : ContentColumn {
        anchors.leftMargin : rWin.isDesktop ? 0 : rWin.c.style.main.spacing
        anchors.rightMargin : rWin.isDesktop ? 0 : rWin.c.style.main.spacing
        ThemedListView {
            id : listsLW
            anchors.left : parent.left
            anchors.right : parent.right
            height : listsPage.height - rWin.headerHeight
            model : ListModel {}
            delegate : ThemedBackgroundRectangle {
                id : listDelegate
                width : listsLW.width
                height : listLabel.height + rWin.c.style.listView.itemBorder
                Label {
                    id : listLabel
                    property string descriptionLine :  description ? "<br>" + description : ""
                    text : "<b>" + name + "</b>" +  descriptionLine
                    anchors.left : parent.left
                    anchors.leftMargin : rWin.c.style.main.spacing
                    anchors.verticalCenter : parent.verticalCenter
                    horizontalAlignment : Text.AlignHCenter
                }
                onClicked : {
                    // If the account is ours, we need to use it to obtain the
                    // corresponding API (or else private lists wll not work).
                    // If it is not ours, we just use one of the available accounts,
                    // which is specified by passing null instead of account username.
                    var accountUsername = null
                    if (listsPage.accountAvailable) {
                        accountUsername = listsPage.username
                    }
                    var listStreamPage = rWin.loadPage("ListStreamPage", {
                        "accountUsername" : accountUsername,
                        "listOwnerUsername" : user.screen_name,
                        "listName" : name,
                        "listSlug" : slug,
                        "isPrivate" : listsPage.privateLists
                    })
                    rWin.pushPageInstance(listStreamPage)
                }
            }
        }
    }
    Label {
        id : noListsLabel
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
        text : qsTr("<h2>no lists available</h2>")
        visible : listsLW.model.count == 0
    }

    Component.onCompleted : {
        rWin.python.setHandler("userListCreated", reloadListListing)
        rWin.python.setHandler("userListDestroyed", reloadListListing)
    }

    function reloadListListing(listUsername) {
        // only process lists owned by our current user
        if (listUsername == listsPage.username) {
            rWin.log.debug("reloading list listing for user " + listUsername)
            rWin.python.call("tsubame.gui.accounts.get_account_user_info", [listUsername], function(result){
                if (result) {
                    var userLists = result[1]
                    if (listsPage.privateLists) {
                        listsPage.setLists(userLists.private_lists)
                    } else {
                        listsPage.setLists(userLists.public_lists)
                    }
                }
            })
        }
    }

    function setLists(lists) {
        // load data about lists into the LW list model
        listsLW.model.clear()
        for (var i=0; i<lists.length; i++) {
            listsLW.model.append(lists[i])
        }
        listsPage.isReady = true
    }
}