# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newgara.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 188)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.description = QtWidgets.QLineEdit(Dialog)
        self.description.setObjectName("description")
        self.horizontalLayout.addWidget(self.description)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.numeroGiudici = QtWidgets.QComboBox(Dialog)
        self.numeroGiudici.setObjectName("numeroGiudici")
        self.numeroGiudici.addItem("")
        self.numeroGiudici.addItem("")
        self.numeroGiudici.addItem("")
        self.numeroGiudici.addItem("")
        self.numeroGiudici.addItem("")
        self.horizontalLayout_2.addWidget(self.numeroGiudici)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Nuova gara"))
        self.label.setText(_translate("Dialog", "Descrizione"))
        self.label_2.setText(_translate("Dialog", "Numero giudici"))
        self.numeroGiudici.setItemText(0, _translate("Dialog", "1"))
        self.numeroGiudici.setItemText(1, _translate("Dialog", "2"))
        self.numeroGiudici.setItemText(2, _translate("Dialog", "3"))
        self.numeroGiudici.setItemText(3, _translate("Dialog", "4"))
        self.numeroGiudici.setItemText(4, _translate("Dialog", "5"))

