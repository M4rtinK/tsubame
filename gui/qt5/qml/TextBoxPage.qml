//TextBoxPage.qml
//
// A page that displays a piece of text in a textboax
// with a header. This way the user can copy paste
// pieces of the text (generally a Twitter message, user
// profile text, etc.) or even first edit and then copy paste
// the result.

import QtQuick 2.0
import UC 1.0
import "tsubame_components"
import "functions.js" as F

BasePage {
    id : textBoxPage

    headerText : ""
    property string text : ""
    content : ContentColumn {
        ThemedTextRectangle {
            width : textBoxPage.width - rWin.c.style.main.spacing * 2
            height : textArea.height
            TextArea {
                id : textArea
                width : parent.width
                text : textBoxPage.text
                readOnly : false
                wrapMode : TextEdit.WordWrap
                // only enable select by mouse on desktop
                selectByMouse : rWin.isDesktop
            }
        }
    }
}

