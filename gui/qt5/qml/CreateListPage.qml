//CreateListPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : createListPage
    property string accountUsername : ""
    property bool isPrivate: false
    headerText: isPrivate ? qsTr("new private list") : qsTr("new public list")
    content : ContentColumn {
        Label {
            text : qsTr("Name")
            width : parent.width
            wrapMode : Text.WordWrap
        }
        TextField {
            id : nameTextField
            width : parent.width
        }
        Label {
            text : qsTr("Description")
            width : parent.width
            wrapMode : Text.WordWrap
        }
        TextArea {
            id : descriptionTextField
            width : parent.width
            wrapMode : TextInput.WordWrap
        }
        Button {
            anchors.horizontalCenter : parent.horizontalCenter
            text : qsTr("Create list")
            onClicked : {
                // do some validation
                // TODO: do this interactively
                var listName = nameTextField.text
                var listDescription = descriptionTextField.text
                if (listName.length == 0) {
                    rWin.notify("list name not set")
                } else if (listName.length > 25) {
                    rWin.notify("list name needs to be shorter than 25 characters")
                } else {
                    rWin.python.call("tsubame.gui.lists.create_new_list",
                    [accountUsername, listName, listDescription, isPrivate], function(){})
                    // and we are done, return to the previous page
                    rWin.pop()
                }
            }
        }
    }
}



