//MessagePage.qml

import QtQuick 2.0
import QtWebKit 3.0
import UC 1.0
import "tsubame_components"
import "functions.js" as F

BasePage {
    id : messagePage
    property var message
    headerText : qsTr("Tweet detail")
    property bool furiganaVisible : false
    headerMenu : TopMenu {
        MenuItem {
            text: qsTr("Open in browser")
            onClicked : {
                rWin.log.info('opening Tweet in browser: ' + message)
                var tweet_url = "https://twitter.com/" + message.user.screen_name + "/status/" + message.id_str
                Qt.openUrlExternally(tweet_url)
            }
        }
        MenuItem {
            text : qsTr("Show as text")
            onClicked : {
                rWin.log.info('showing Tweet as text: ' + message)
                var textBoxPage = rWin.loadPage("TextBoxPage", {
                    "headerText" : qsTr("Tweet text"),
                    "text" : message.tsubame_message_full_text_plaintext
                })
                rWin.pushPageInstance(textBoxPage)
            }
        }
    }

    WebView {
            id: webView
            visible : furiganaVisible
            //anchors.fill : parent
            y : messagePage.headerHeight + messageContainer.headerHeight
            width : parent.width
            height : parent.height
            MouseArea {
                anchors.fill : parent
                onClicked : {
                    rWin.log.debug("CLICKED")
                    rWin.log.debug(messageContainer.headerHeight)
                    rWin.log.debug(content.x)
                    messagePage.furiganaVisible = false
                }
            }
    }


    content : ContentColumn {
        anchors.left : parent.left
        anchors.right : parent.right
        MessageContainer {
            id : messageContainer
            message : messagePage.message
            messageClickable : false
            // Explicit width setting is needed due to the MediaGrid
            // for some reason. We should probably fix that.
            width : messagePage.width - rWin.c.style.main.spacing * 2
            onUserInfoClicked : {
                        rWin.log.info("user info clicked")
                        var userPage = rWin.loadPage("UserPage", {"user" : messagePage.message.user, "dataValid" : true})
                        rWin.pushPageInstance(userPage)
            }
        }
        Row {
            visible : !furiganaVisible
            spacing : rWin.c.style.main.spacing
            Label {
                visible : messagePage.message.retweet_count != null
                text: "<b>" +  messagePage.message.retweet_count + "</b> " + qsTr("Retweets")
            }
            Label {
                visible : messagePage.message.favorite_count != null
                text: "<b>" +  messagePage.message.favorite_count + "</b> " + qsTr("Favorites")
            }
        }
        ThemedTextRectangle {
            width : parent.width
            label.horizontalAlignment : Text.AlignHCenter
            property bool messageInJapanese : F.detectJapanese(messagePage.message.full_text)
            property int webViewFontSize: rWin.isDesktop ? 5 : 100
            visible : messageInJapanese && !furiganaVisible
            label.text : qsTr("show furigana")
            onClicked : {

                rWin.python.call("tsubame.gui.japanese.add_furigana_with_html",
                                 [messagePage.message.full_text, webViewFontSize],
                                 function(result){
                                     webView.loadHtml(result, "")
                                     furiganaVisible = true
                                 })
            }
        }
    }
}