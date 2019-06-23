//AccountComboBox.qml

import QtQuick 2.0
import UC 1.0

ComboBox {
    property string selectedAccountUsername : ""

    Component.onCompleted : {
        // load account list from the backend
        rWin.log.info("AccountComboBox: fetching account list")
        rWin.python.call("tsubame.gui.accounts.get_account_list", [], function(accountList){
            for (var i=0; i<accountList.length; i++) {
                accountsLM.append({"text" : accountList[i].name, "username" : accountList[i].username})
            }
        rWin.log.info("AccountComboBox: fetched account list")
        })

    }
    //currentIndex: 2
    model: ListModel {
        id: accountsLM
    }
    //width: 200
    onCurrentIndexChanged: {
        selectedAccountUsername = accountsLM.get(currentIndex).username
        rWin.log.debug("account selected: " + accountsLM.get(currentIndex).username)
    }
}
