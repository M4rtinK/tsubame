//StreamSettingsPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : accountsPage
    headerText : qsTr("Accounts")
    property bool fetchingAccountInfo : false
    headerMenu : TopMenu {
        MenuItem {
            text: qsTr("Add an account")
            onClicked : {
                rWin.pushPageInstance(rWin.loadPage("AddAccountPage"))
            }
        }
    }
    content : ContentColumn {
        id : accounts
        anchors.leftMargin : rWin.isDesktop ? 0 : rWin.c.style.main.spacing
        anchors.rightMargin : rWin.isDesktop ? 0 : rWin.c.style.main.spacing
        ThemedListView {
            id : accountsLW
            anchors.left : parent.left
            anchors.right : parent.right
            height : accountsPage.height - rWin.headerHeight
            model : ListModel {}
            delegate : ThemedBackgroundRectangle {
                id : accountDelegate
                width : accountsLW.width
                height : accountLabel.height + rWin.c.style.listView.itemBorder
                Label {
                    id : accountLabel
                    text : "<b>" + name + "</b><br>@" + username
                    anchors.horizontalCenter : parent.horizontalCenter
                    anchors.verticalCenter : parent.verticalCenter
                    horizontalAlignment : Text.AlignHCenter
                }
                onClicked : {
                    var accountPage = rWin.loadPage("AccountPage")
                    accountPage.lookupUsername = username
                    rWin.pushPageInstance(accountPage)
                }
            }
        }
    }
    Label {
        id : noStreamsLabel
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
        text : qsTr("<h2>No accounts added yet!</h2>")
        visible : accountsLW.model.count == 0 && !accountsPage.fetchingAccountInfo
    }
    BusyIndicator {
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
        visible : accountsPage.fetchingAccountInfo
        running : accountsPage.fetchingAccountInfo
    }
    Component.onCompleted : {
        getAccounts()
    }

    function getAccounts() {
        // get list of Twitter accounts that have been added to Tsubame
        rWin.log.info("fetching account list")
        accountsPage.fetchingAccountInfo = true
        rWin.python.call("tsubame.gui.accounts.get_account_list", [], function(accountList){
            accountsLW.model.clear()
            for (var i=0; i<accountList.length; i++) {
                accountsLW.model.append(accountList[i])
            }
            accountsPage.fetchingAccountInfo = false
        })
    }
}