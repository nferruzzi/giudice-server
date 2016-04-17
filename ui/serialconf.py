# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'serialconf.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DlgSerialConfig(object):
    def setupUi(self, DlgSerialConfig):
        DlgSerialConfig.setObjectName("DlgSerialConfig")
        DlgSerialConfig.resize(280, 208)
        DlgSerialConfig.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(DlgSerialConfig)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(DlgSerialConfig)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.nameBox = QtWidgets.QComboBox(DlgSerialConfig)
        self.nameBox.setObjectName("nameBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.nameBox)
        self.label_2 = QtWidgets.QLabel(DlgSerialConfig)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.speedBox = QtWidgets.QComboBox(DlgSerialConfig)
        self.speedBox.setObjectName("speedBox")
        self.speedBox.addItem("")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.speedBox)
        self.label_3 = QtWidgets.QLabel(DlgSerialConfig)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.bitsBox = QtWidgets.QComboBox(DlgSerialConfig)
        self.bitsBox.setObjectName("bitsBox")
        self.bitsBox.addItem("")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.bitsBox)
        self.label_4 = QtWidgets.QLabel(DlgSerialConfig)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.parityBox = QtWidgets.QComboBox(DlgSerialConfig)
        self.parityBox.setObjectName("parityBox")
        self.parityBox.addItem("")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.parityBox)
        self.stopBox = QtWidgets.QComboBox(DlgSerialConfig)
        self.stopBox.setObjectName("stopBox")
        self.stopBox.addItem("")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.stopBox)
        self.label_5 = QtWidgets.QLabel(DlgSerialConfig)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(DlgSerialConfig)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DlgSerialConfig)
        self.buttonBox.accepted.connect(DlgSerialConfig.accept)
        self.buttonBox.rejected.connect(DlgSerialConfig.reject)
        QtCore.QMetaObject.connectSlotsByName(DlgSerialConfig)

    def retranslateUi(self, DlgSerialConfig):
        _translate = QtCore.QCoreApplication.translate
        DlgSerialConfig.setWindowTitle(_translate("DlgSerialConfig", "Impostazioni collegamento seriale"))
        self.label.setText(_translate("DlgSerialConfig", "Porta seriale"))
        self.label_2.setText(_translate("DlgSerialConfig", "Baud Rate"))
        self.speedBox.setItemText(0, _translate("DlgSerialConfig", "2400"))
        self.label_3.setText(_translate("DlgSerialConfig", "Data Bits"))
        self.bitsBox.setItemText(0, _translate("DlgSerialConfig", "8"))
        self.label_4.setText(_translate("DlgSerialConfig", "Parity"))
        self.parityBox.setItemText(0, _translate("DlgSerialConfig", "None"))
        self.stopBox.setItemText(0, _translate("DlgSerialConfig", "1"))
        self.label_5.setText(_translate("DlgSerialConfig", "Stop Bits"))

