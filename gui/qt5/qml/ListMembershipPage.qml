//ListMembershipPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : listMembershipPage
    property string listOwnerUsername : null
    property string membershipUsername : null
    property bool privateLists : false
    property bool isReady: false
    property string privatePublicSymbol: privateLists ? " 🔒 " : " 📢 "
    headerText : listOwnerUsername + privatePublicSymbol + qsTr("lists")
    headerMenu : TopMenu {
        MenuItem {
            text: qsTr("Create list")
            onClicked : {
                var createListPage = rWin.loadPage("CreateListPage", {
                    "accountUsername" : listMembershipPage.listOwnerUsername,
                    "isPrivate" : listMembershipPage.privateLists
                })
                rWin.pushPageInstance(createListPage)
            }
        }
    }
    content : ContentColumn {
        //anchors.leftMargin : rWin.isDesktop ? 0 : rWin.c.style.main.spacing
        anchors.leftMargin : 0
        //anchors.rightMargin : rWin.isDesktop ? 0 : rWin.c.style.main.spacing
        anchors.rightMargin : 0
        ThemedListView {
            id : listsLW
            anchors.left : parent.left
            anchors.right : parent.right
            height : listMembershipPage.height - rWin.headerHeight
            model : ListModel {}
            delegate : ThemedBackgroundRectangle {
                id : listDelegate
                width : listsLW.width
                height : listTextSwitch.height + rWin.c.style.listView.itemBorder
                TextSwitch {
                    id : listTextSwitch
                    anchors.verticalCenter : parent.verticalCenter
                    anchors.left : parent.left
                    anchors.leftMargin : rWin.c.style.main.spacing
                    anchors.right : parent.right
                    anchors.rightMargin : rWin.c.style.main.spacing
                    text : "<b>" + list_info.name + "</b>"
                    checked : is_member
                    property bool initialized: false
                    onCheckedChanged : {
                        // The checked property will trigger a signal
                        // once first set from the list model,
                        // so prevent that from triggering API calls
                        // by ignoring onCheckedChanged until the
                        // component has been completed.
                        if (initialized) {
                            log.debug("list switch toggled")
                            is_member : checked
                            if (checked) {
                                // add to list
                                rWin.python.call("tsubame.gui.lists.add_user_to_list",
                                                 [listOwnerUsername, list_info.slug, membershipUsername])
                            } else {
                                // remove from list
                                rWin.python.call("tsubame.gui.lists.remove_user_from_list",
                                                 [listOwnerUsername, list_info.slug, membershipUsername])
                            }
                            // Save the change also to the list model, so that it will not
                            // revert to original state when the delegate is recreated due to
                            // user having more lists than what fits in the viewport.
                            listsLW.model.setProperty(index, "is_member", checked)
                        }
                    }
                    Component.onCompleted : {
                        listTextSwitch.initialized = true
                    }
                }
                onClicked : {
                    // toggle the switch also when the underlying tbr is clicked
                    listTextSwitch.checked = !listTextSwitch.checked
                }
            }
        }
    }
    BusyIndicator {
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
        visible : !listMembershipPage.isReady
        running : !listMembershipPage.isReady
    }
    Label {
        id : noListsLabel
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
        text : qsTr("<h2>no lists available</h2>")
        visible : listsLW.model.count == 0 && listMembershipPage.isReady
    }

    Component.onCompleted : {
        // fetch data about available lists and eventual existing membership of the user in them
        rWin.python.call("tsubame.gui.accounts.check_account_list_membership",
                         [listOwnerUsername, membershipUsername], setLists)
    }

    function setLists(private_public_lists) {
        // load data about lists into the LW list model

        // check if we should show private or public lists
        var lists = []
        if (privateLists) {
            lists = private_public_lists[0]
        } else {
            lists = private_public_lists[1]
        }
        // load it to the list model
        listsLW.model.clear()
        for (var i=0; i<lists.length; i++) {
            listsLW.model.append(lists[i])
        }
        listMembershipPage.isReady = true
    }
}