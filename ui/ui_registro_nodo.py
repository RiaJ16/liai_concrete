# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'registro_nodo.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFormLayout, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QTextBrowser, QVBoxLayout, QWidget)

class Ui_registro_nodo(object):
    def setupUi(self, registro_nodo):
        if not registro_nodo.objectName():
            registro_nodo.setObjectName(u"registro_nodo")
        registro_nodo.resize(371, 215)
        registro_nodo.setStyleSheet(u"QWidget#registro_nodo{\n"
"	background-color: #1f1f23;\n"
"}\n"
"\n"
"QWidget{\n"
"	font-family: \"Inter\", \"Verdana\", \"sans-serif\";\n"
"	font-size: 10pt;\n"
"}\n"
"\n"
"QLabel{\n"
"	color: #F0F0F0;\n"
"	font-weight: bold;\n"
"}\n"
"\n"
"QCheckBox{\n"
"	color: #F0F0F0;\n"
"	padding: 2px;\n"
"}\n"
"\n"
"QCheckBox::indicator {\n"
"    width: 18px;\n"
"    height: 18px;\n"
"    border: 1px solid #7a7a7a;\n"
"    background: white;\n"
"}\n"
"\n"
"QCheckBox::indicator:checked {\n"
"    background: #4aa8ff;\n"
"    border: 1px solid #4aa8ff;\n"
"}\n"
"\n"
"QCheckBox::checked{\n"
"	border: 1px solid #4aa8ff;\n"
"}\n"
"\n"
"QTextBrowser{\n"
"	background-color: #1f1f23;\n"
"	color: #f1c40f;\n"
"}\n"
"\n"
"QPushButton{\n"
"	color: black;\n"
"}")
        self.verticalLayout = QVBoxLayout(registro_nodo)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setVerticalSpacing(11)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(14)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.icon_nombre = QLabel(registro_nodo)
        self.icon_nombre.setObjectName(u"icon_nombre")

        self.horizontalLayout_3.addWidget(self.icon_nombre)

        self.lbl_nombre = QLabel(registro_nodo)
        self.lbl_nombre.setObjectName(u"lbl_nombre")

        self.horizontalLayout_3.addWidget(self.lbl_nombre)


        self.formLayout.setLayout(0, QFormLayout.ItemRole.LabelRole, self.horizontalLayout_3)

        self.le_nombre = QLineEdit(registro_nodo)
        self.le_nombre.setObjectName(u"le_nombre")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.le_nombre)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(14)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.icon_id = QLabel(registro_nodo)
        self.icon_id.setObjectName(u"icon_id")

        self.horizontalLayout_4.addWidget(self.icon_id)

        self.lbl_id = QLabel(registro_nodo)
        self.lbl_id.setObjectName(u"lbl_id")

        self.horizontalLayout_4.addWidget(self.lbl_id)


        self.formLayout.setLayout(1, QFormLayout.ItemRole.LabelRole, self.horizontalLayout_4)

        self.le_id = QLineEdit(registro_nodo)
        self.le_id.setObjectName(u"le_id")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.le_id)


        self.verticalLayout.addLayout(self.formLayout)

        self.tb_errores = QTextBrowser(registro_nodo)
        self.tb_errores.setObjectName(u"tb_errores")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tb_errores.sizePolicy().hasHeightForWidth())
        self.tb_errores.setSizePolicy(sizePolicy)
        self.tb_errores.setFrameShape(QFrame.NoFrame)

        self.verticalLayout.addWidget(self.tb_errores)

        self.btn_registrar = QPushButton(registro_nodo)
        self.btn_registrar.setObjectName(u"btn_registrar")

        self.verticalLayout.addWidget(self.btn_registrar)


        self.retranslateUi(registro_nodo)

        QMetaObject.connectSlotsByName(registro_nodo)
    # setupUi

    def retranslateUi(self, registro_nodo):
        registro_nodo.setWindowTitle(QCoreApplication.translate("registro_nodo", u"Registro de dispositivo", None))
        self.icon_nombre.setText("")
        self.lbl_nombre.setText(QCoreApplication.translate("registro_nodo", u"Nombre", None))
        self.icon_id.setText("")
        self.lbl_id.setText(QCoreApplication.translate("registro_nodo", u"ID", None))
        self.tb_errores.setHtml(QCoreApplication.translate("registro_nodo", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Inter','Verdana','sans-serif'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.btn_registrar.setText(QCoreApplication.translate("registro_nodo", u"Registrar", None))
    # retranslateUi

