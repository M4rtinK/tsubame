//AddTwitterAccountStartPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"
import "functions.js" as F

BasePage {
    id : addAccountStartPage

    property bool authorisationRequested : false
    property bool pinValid : false
    property string username : ""
    property string consumerKey
    property string consumerSecret
    property string resourceOwnerKey
    property string resourceOwnerSecret
    property string accessTokenKey
    property string accessTokenSecret

    headerText : qsTr("Add a Twitter account")

    content : ContentColumn {
        anchors.left : parent.left
        anchors.right : parent.right
        spacing : rWin.c.style.main.spacing * 2
        Button {
            text : authorisationRequested ? qsTr("Authorize account again") : qsTr("Authorize account")
            anchors.horizontalCenter : parent.horizontalCenter
            onClicked : {
                rWin.python.call("tsubame.gui.accounts.authorize_twitter_account", [], function(values){
                    consumerKey = values[0]
                    consumerSecret = values[1]
                    resourceOwnerKey = values[2]
                    resourceOwnerSecret = values[3]
                    authorisationRequested = true
                    pinValid = false
                    username = ""
                    customAccountName.text = ""
                    accessTokenKey = null
                    accessTokenSecret = null
                })
            }
        }
        Column {
            anchors.horizontalCenter : parent.horizontalCenter
            visible : authorisationRequested && !pinValid
            Label {
                text : qsTr("Twitter PIN code")
            }
            TextField {
                id : twitterPIN
                width : parent.width
            }
        }
        Button {
            text : "Verify PIN"
            visible : authorisationRequested && twitterPIN.text != "" && !pinValid
            anchors.horizontalCenter : parent.horizontalCenter
            onClicked : {
                 rWin.python.call("tsubame.gui.accounts.verify_twitter_account_pin",
                                  [consumerKey, consumerSecret,
                                   resourceOwnerKey, resourceOwnerSecret,
                                   twitterPIN.text],
                                  function(values){
                    if (values == null) {
                        rWin.notify("Twitter PIN validation failed.")
                        addAccountStartPage.username = ""
                        addAccountStartPage.pinValid = false
                    } else {
                        addAccountStartPage.accessTokenKey = values[0]
                        addAccountStartPage.accessTokenSecret = values[1]
                        addAccountStartPage.username = values[2]
                        customAccountName.text = values[2]
                        addAccountStartPage.pinValid = true
                    }
                 })
            }
        }
        Column {
            anchors.horizontalCenter : parent.horizontalCenter
            visible : pinValid
            Label {
                text : qsTr("Account username")
            }
            Label {
                id : accountUsername
                width : parent.width
                text : addAccountStartPage.username
                font.bold : true
            }
        }
        Column {
            anchors.horizontalCenter : parent.horizontalCenter
            visible : pinValid
            Label {
                text : qsTr("Custom account name")
            }
            TextField {
                id : customAccountName
                width : parent.width
            }
        }
        Button {
            text : "Add account to Tsubame"
            visible : pinValid
            anchors.horizontalCenter : parent.horizontalCenter
            onClicked : {
                rWin.python.call("tsubame.gui.accounts.add_account",
                                  [addAccountStartPage.username,
                                   accessTokenKey, accessTokenSecret,
                                   customAccountName.text], function(values){
                    rWin.log.info("Twitter account " + addAccountStartPage.username +
                                  "(" + customAccountName.text + ") has been added." )
                    rWin.pop()
                })
            }
        }
    }
}
