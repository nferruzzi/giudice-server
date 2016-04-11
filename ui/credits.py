# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'credits.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogCredits(object):
    def setupUi(self, DialogCredits):
        DialogCredits.setObjectName("DialogCredits")
        DialogCredits.resize(400, 300)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(DialogCredits)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(DialogCredits)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableView = QtWidgets.QTableView(self.groupBox)
        self.tableView.setObjectName("tableView")
        self.verticalLayout.addWidget(self.tableView)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.message = QtWidgets.QLabel(DialogCredits)
        self.message.setText("")
        self.message.setObjectName("message")
        self.verticalLayout_2.addWidget(self.message)
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogCredits)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.SaveAll)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(DialogCredits)
        self.buttonBox.accepted.connect(DialogCredits.accept)
        self.buttonBox.rejected.connect(DialogCredits.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogCredits)

    def retranslateUi(self, DialogCredits):
        _translate = QtCore.QCoreApplication.translate
        DialogCredits.setWindowTitle(_translate("DialogCredits", "Dialog"))
        self.groupBox.setTitle(_translate("DialogCredits", "Configurazione crediti e pettorine"))

