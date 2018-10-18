//AccountListCategories.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : alcPage
    headerText : qsTr("Add/remove user from lists")
    property bool fetchingAccountInfo : false
    property string membershipUsername : ""
    content : ContentColumn {
        id : accounts
        anchors.leftMargin : rWin.isDesktop ? 0 : rWin.c.style.main.spacing
        anchors.rightMargin : rWin.isDesktop ? 0 : rWin.c.style.main.spacing
        ThemedListView {
            id : accountsLW
            anchors.left : parent.left
            anchors.right : parent.right
            height : alcPage.height - rWin.headerHeight
            model : ListModel {}
            delegate : Item {
                id : accountDelegate
                width : accountsLW.width
                height : accountLabel.height + listCategoryRow.height + rWin.c.style.main.spacing*4
                Label {
                    id : accountLabel
                    text : "<b>" + name + "</b><br>@" + username
                    anchors.top : parent.top
                    anchors.topMargin : rWin.c.style.main.spacing * 2
                    anchors.horizontalCenter : parent.horizontalCenter
                    horizontalAlignment : Text.AlignHCenter
                }
                Row {
                    id : listCategoryRow
                    anchors.top : accountLabel.bottom
                    anchors.topMargin : rWin.c.style.main.spacing * 2
                    spacing : rWin.c.style.main.spacing
                    ThemedBackgroundRectangle {
                        id: privateTBR
                        width : accountsLW.width / 2 + rWin.c.style.main.spacing / 2
                        Label {
                            id : privateLabel
                            text : "<b>" + qsTr("private lists") + "</b>"
                            anchors.horizontalCenter : parent.horizontalCenter
                            anchors.verticalCenter : parent.verticalCenter
                            horizontalAlignment : Text.AlignHCenter
                        }
                        onClicked : {
                            var listMembershipPage = rWin.loadPage("ListMembershipPage")
                            listMembershipPage.listOwnerUsername = username
                            listMembershipPage.membershipUsername = membershipUsername
                            listMembershipPage.privateLists = true
                            rWin.pushPageInstance(listMembershipPage)
                        }
                    }
                    ThemedBackgroundRectangle {
                        id : publicTBR
                        width : accountsLW.width / 2 + rWin.c.style.main.spacing / 2
                        Label {
                            id : publicLabel
                            text : "<b>" + qsTr("public lists") + "</b>"
                            anchors.horizontalCenter : parent.horizontalCenter
                            anchors.verticalCenter : parent.verticalCenter
                            horizontalAlignment : Text.AlignHCenter
                        }
                        onClicked : {
                            var listMembershipPage = rWin.loadPage("ListMembershipPage")
                            listMembershipPage.listOwnerUsername = username
                            listMembershipPage.membershipUsername = membershipUsername
                            listMembershipPage.privateLists = true
                            rWin.pushPageInstance(listMembershipPage)
                        }
                    }
                }
            }
        }
    }
    Label {
        id : noStreamsLabel
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
        text : qsTr("<h2>No accounts added yet!</h2>")
        visible : accountsLW.model.count == 0 && !alcPage.fetchingAccountInfo
    }
    BusyIndicator {
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
        visible : alcPage.fetchingAccountInfo
        running : alcPage.fetchingAccountInfo
    }
    Component.onCompleted : {
        getAccounts()
    }

    function getAccounts() {
        // get list of Twitter accounts that have been added to Tsubame
        rWin.log.info("fetching account list")
        alcPage.fetchingAccountInfo = true
        rWin.python.call("tsubame.gui.accounts.get_account_list", [], function(accountList){
            accountsLW.model.clear()
            for (var i=0; i<accountList.length; i++) {
                var item = accountList[i]
                accountsLW.model.append(item)
            }
            alcPage.fetchingAccountInfo = false
        })
    }
}