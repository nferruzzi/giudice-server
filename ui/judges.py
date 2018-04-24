# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'judges.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DlgPickJudges(object):
    def setupUi(self, DlgPickJudges):
        DlgPickJudges.setObjectName("DlgPickJudges")
        DlgPickJudges.resize(233, 216)
        DlgPickJudges.setModal(True)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(DlgPickJudges)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(DlgPickJudges)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.checkBox_1 = QtWidgets.QCheckBox(DlgPickJudges)
        self.checkBox_1.setObjectName("checkBox_1")
        self.verticalLayout.addWidget(self.checkBox_1)
        self.checkBox_2 = QtWidgets.QCheckBox(DlgPickJudges)
        self.checkBox_2.setObjectName("checkBox_2")
        self.verticalLayout.addWidget(self.checkBox_2)
        self.checkBox_3 = QtWidgets.QCheckBox(DlgPickJudges)
        self.checkBox_3.setObjectName("checkBox_3")
        self.verticalLayout.addWidget(self.checkBox_3)
        self.checkBox_4 = QtWidgets.QCheckBox(DlgPickJudges)
        self.checkBox_4.setObjectName("checkBox_4")
        self.verticalLayout.addWidget(self.checkBox_4)
        self.checkBox_5 = QtWidgets.QCheckBox(DlgPickJudges)
        self.checkBox_5.setObjectName("checkBox_5")
        self.verticalLayout.addWidget(self.checkBox_5)
        self.checkBox_6 = QtWidgets.QCheckBox(DlgPickJudges)
        self.checkBox_6.setObjectName("checkBox_6")
        self.verticalLayout.addWidget(self.checkBox_6)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(DlgPickJudges)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(DlgPickJudges)
        self.buttonBox.accepted.connect(DlgPickJudges.accept)
        self.buttonBox.rejected.connect(DlgPickJudges.reject)
        QtCore.QMetaObject.connectSlotsByName(DlgPickJudges)

    def retranslateUi(self, DlgPickJudges):
        _translate = QtCore.QCoreApplication.translate
        DlgPickJudges.setWindowTitle(_translate("DlgPickJudges", "Dialog"))
        self.label.setText(_translate("DlgPickJudges", "Scegliere i voti da rimuovere"))
        self.checkBox_1.setText(_translate("DlgPickJudges", "Giudice 1"))
        self.checkBox_2.setText(_translate("DlgPickJudges", "Giudice 2"))
        self.checkBox_3.setText(_translate("DlgPickJudges", "Giudice 3"))
        self.checkBox_4.setText(_translate("DlgPickJudges", "Giudice 4"))
        self.checkBox_5.setText(_translate("DlgPickJudges", "Giudice 5"))
        self.checkBox_6.setText(_translate("DlgPickJudges", "Giudice 6"))

