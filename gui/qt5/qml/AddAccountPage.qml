//AddAccountPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"
import "functions.js" as F

BasePage {
    id : addAccountPage

    headerText : qsTr("Add an account")

    content : ContentColumn {
        anchors.left : parent.left
        anchors.right : parent.right
        spacing : rWin.c.style.main.spacing
        SmartGrid {
            Column {
                width : parent.cellWidth
                Label {
                    text : qsTr("Twitter user name")
                }
                TextField {
                    id : accountUsername
                    width : parent.width
                }
            }
            Column {
                width : parent.cellWidth
                Label {
                    text : qsTr("Local name of the account (optional)")
                }
                TextField {
                    id : accountName
                    width : parent.width
                }
            }
        }
        Button {
            text : "Add account"
            anchors.horizontalCenter : parent.horizontalCenter
            onClicked : {
                if (!accountUsername.text) {
                    rWin.notify(qsTr("Account user name not set."))
                }
            }
        }
    }
}
