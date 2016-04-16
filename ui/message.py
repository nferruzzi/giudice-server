# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'message.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DlgMessage(object):
    def setupUi(self, DlgMessage):
        DlgMessage.setObjectName("DlgMessage")
        DlgMessage.resize(400, 103)
        DlgMessage.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(DlgMessage)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(DlgMessage)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(DlgMessage)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.buttonBox = QtWidgets.QDialogButtonBox(DlgMessage)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DlgMessage)
        self.buttonBox.accepted.connect(DlgMessage.accept)
        self.buttonBox.rejected.connect(DlgMessage.reject)
        QtCore.QMetaObject.connectSlotsByName(DlgMessage)

    def retranslateUi(self, DlgMessage):
        _translate = QtCore.QCoreApplication.translate
        DlgMessage.setWindowTitle(_translate("DlgMessage", "Manda messaggio"))
        self.label.setText(_translate("DlgMessage", "Testo da trasmettere:"))

