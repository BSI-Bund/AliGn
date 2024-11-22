# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DialogOpenNpyJpaPfs.ui'
##
## Created by: Qt User Interface Compiler version 6.5.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class Ui_OpenNpyDialogFrame(object):
    def setupUi(self, OpenNpyDialogFrame):
        if not OpenNpyDialogFrame.objectName():
            OpenNpyDialogFrame.setObjectName("OpenNpyDialogFrame")
        OpenNpyDialogFrame.resize(731, 354)
        self.gridLayout = QGridLayout(OpenNpyDialogFrame)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout_2.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.frame = QFrame(OpenNpyDialogFrame)
        self.frame.setObjectName("frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.gridLayout_4 = QGridLayout(self.frame)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_em = QLabel(self.frame)
        self.label_em.setObjectName("label_em")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_em.sizePolicy().hasHeightForWidth())
        self.label_em.setSizePolicy(sizePolicy)
        self.label_em.setMinimumSize(QSize(40, 0))
        self.label_em.setLayoutDirection(Qt.LeftToRight)
        self.label_em.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.label_em)

        self.lineEdit = QLineEdit(self.frame)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy1)
        self.lineEdit.setMinimumSize(QSize(0, 0))
        self.lineEdit.setLayoutDirection(Qt.LeftToRight)

        self.horizontalLayout_5.addWidget(self.lineEdit)

        self.bt_select_em_2 = QPushButton(self.frame)
        self.bt_select_em_2.setObjectName("bt_select_em_2")
        self.bt_select_em_2.setMinimumSize(QSize(0, 0))

        self.horizontalLayout_5.addWidget(self.bt_select_em_2)

        self.verticalLayout_3.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_power = QLabel(self.frame)
        self.label_power.setObjectName("label_power")
        sizePolicy.setHeightForWidth(self.label_power.sizePolicy().hasHeightForWidth())
        self.label_power.setSizePolicy(sizePolicy)
        self.label_power.setMinimumSize(QSize(40, 0))
        self.label_power.setAlignment(
            Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter
        )

        self.horizontalLayout_4.addWidget(self.label_power)

        self.lineEdit_4 = QLineEdit(self.frame)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.lineEdit_4.setMinimumSize(QSize(0, 0))

        self.horizontalLayout_4.addWidget(self.lineEdit_4)

        self.bt_select_power_2 = QPushButton(self.frame)
        self.bt_select_power_2.setObjectName("bt_select_power_2")

        self.horizontalLayout_4.addWidget(self.bt_select_power_2)

        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_plain = QLabel(self.frame)
        self.label_plain.setObjectName("label_plain")
        sizePolicy.setHeightForWidth(self.label_plain.sizePolicy().hasHeightForWidth())
        self.label_plain.setSizePolicy(sizePolicy)
        self.label_plain.setMinimumSize(QSize(40, 0))
        self.label_plain.setAlignment(
            Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter
        )

        self.horizontalLayout_3.addWidget(self.label_plain)

        self.lineEdit_3 = QLineEdit(self.frame)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.lineEdit_3.setMinimumSize(QSize(0, 0))

        self.horizontalLayout_3.addWidget(self.lineEdit_3)

        self.bt_select_plain = QPushButton(self.frame)
        self.bt_select_plain.setObjectName("bt_select_plain")

        self.horizontalLayout_3.addWidget(self.bt_select_plain)

        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_cipher = QLabel(self.frame)
        self.label_cipher.setObjectName("label_cipher")
        sizePolicy.setHeightForWidth(self.label_cipher.sizePolicy().hasHeightForWidth())
        self.label_cipher.setSizePolicy(sizePolicy)
        self.label_cipher.setMinimumSize(QSize(40, 0))
        self.label_cipher.setAlignment(
            Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter
        )

        self.horizontalLayout_2.addWidget(self.label_cipher)

        self.lineEdit_6 = QLineEdit(self.frame)
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.lineEdit_6.setMinimumSize(QSize(0, 0))

        self.horizontalLayout_2.addWidget(self.lineEdit_6)

        self.bt_select_cipher = QPushButton(self.frame)
        self.bt_select_cipher.setObjectName("bt_select_cipher")

        self.horizontalLayout_2.addWidget(self.bt_select_cipher)

        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_aux = QLabel(self.frame)
        self.label_aux.setObjectName("label_aux")
        sizePolicy.setHeightForWidth(self.label_aux.sizePolicy().hasHeightForWidth())
        self.label_aux.setSizePolicy(sizePolicy)
        self.label_aux.setMinimumSize(QSize(40, 0))
        self.label_aux.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.horizontalLayout.addWidget(self.label_aux)

        self.lineEdit_8 = QLineEdit(self.frame)
        self.lineEdit_8.setObjectName("lineEdit_8")
        sizePolicy1.setHeightForWidth(self.lineEdit_8.sizePolicy().hasHeightForWidth())
        self.lineEdit_8.setSizePolicy(sizePolicy1)
        self.lineEdit_8.setMinimumSize(QSize(0, 0))

        self.horizontalLayout.addWidget(self.lineEdit_8)

        self.bt_select_aux = QPushButton(self.frame)
        self.bt_select_aux.setObjectName("bt_select_aux")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.bt_select_aux.sizePolicy().hasHeightForWidth()
        )
        self.bt_select_aux.setSizePolicy(sizePolicy2)
        self.bt_select_aux.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout.addWidget(self.bt_select_aux)

        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.gridLayout_4.addLayout(self.verticalLayout_3, 0, 0, 1, 1)

        self.gridLayout_2.addWidget(self.frame, 1, 0, 1, 1)

        self.frame_2 = QFrame(OpenNpyDialogFrame)
        self.frame_2.setObjectName("frame_2")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy3)
        self.frame_2.setMinimumSize(QSize(0, 100))
        self.frame_2.setMaximumSize(QSize(16777215, 100))
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.gridLayout_3 = QGridLayout(self.frame_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_6 = QLabel(self.frame_2)
        self.label_6.setObjectName("label_6")
        font = QFont()
        font.setFamilies(["MS Shell Dlg 2"])
        font.setPointSize(10)
        font.setBold(True)
        font.setUnderline(False)
        font.setKerning(True)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_2.addWidget(self.label_6)

        self.textBrowser = QTextBrowser(self.frame_2)
        self.textBrowser.setObjectName("textBrowser")

        self.verticalLayout_2.addWidget(self.textBrowser)

        self.gridLayout_3.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.gridLayout_2.addWidget(self.frame_2, 0, 0, 1, 1)

        self.frame_3 = QFrame(OpenNpyDialogFrame)
        self.frame_3.setObjectName("frame_3")
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.gridLayout_7 = QGridLayout(self.frame_3)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.btn_cancel = QPushButton(self.frame_3)
        self.btn_cancel.setObjectName("btn_cancel")
        sizePolicy4 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.btn_cancel.sizePolicy().hasHeightForWidth())
        self.btn_cancel.setSizePolicy(sizePolicy4)

        self.horizontalLayout_6.addWidget(self.btn_cancel)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_6.addItem(self.horizontalSpacer)

        self.btn_load_files = QPushButton(self.frame_3)
        self.btn_load_files.setObjectName("btn_load_files")
        sizePolicy4.setHeightForWidth(
            self.btn_load_files.sizePolicy().hasHeightForWidth()
        )
        self.btn_load_files.setSizePolicy(sizePolicy4)

        self.horizontalLayout_6.addWidget(self.btn_load_files)

        self.gridLayout_7.addLayout(self.horizontalLayout_6, 0, 0, 1, 1)

        self.gridLayout_2.addWidget(self.frame_3, 2, 0, 1, 1)

        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        self.retranslateUi(OpenNpyDialogFrame)

        QMetaObject.connectSlotsByName(OpenNpyDialogFrame)

    # setupUi

    def retranslateUi(self, OpenNpyDialogFrame):
        OpenNpyDialogFrame.setWindowTitle(
            QCoreApplication.translate("OpenNpyDialogFrame", "Frame", None)
        )
        self.label_em.setText(
            QCoreApplication.translate("OpenNpyDialogFrame", "EM", None)
        )
        self.bt_select_em_2.setText(
            QCoreApplication.translate("OpenNpyDialogFrame", "Select file", None)
        )
        self.label_power.setText(
            QCoreApplication.translate("OpenNpyDialogFrame", "Power", None)
        )
        self.bt_select_power_2.setText(
            QCoreApplication.translate("OpenNpyDialogFrame", "Select file", None)
        )
        self.label_plain.setText(
            QCoreApplication.translate("OpenNpyDialogFrame", "Plain", None)
        )
        self.bt_select_plain.setText(
            QCoreApplication.translate("OpenNpyDialogFrame", "Select file", None)
        )
        self.label_cipher.setText(
            QCoreApplication.translate("OpenNpyDialogFrame", "Cipher", None)
        )
        self.bt_select_cipher.setText(
            QCoreApplication.translate("OpenNpyDialogFrame", "Select file", None)
        )
        self.label_aux.setText(
            QCoreApplication.translate("OpenNpyDialogFrame", "Aux", None)
        )
        self.bt_select_aux.setText(
            QCoreApplication.translate("OpenNpyDialogFrame", "Select file", None)
        )
        self.label_6.setText(
            QCoreApplication.translate(
                "OpenNpyDialogFrame", "Select npy data files", None
            )
        )
        self.textBrowser.setHtml(
            QCoreApplication.translate(
                "OpenNpyDialogFrame",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><meta charset="utf-8" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "hr { height: 1px; border-width: 0; }\n"
                'li.unchecked::marker { content: "\\2610"; }\n'
                'li.checked::marker { content: "\\2612"; }\n'
                "</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;">Select files that contains the given data</span></p></body></html>',
                None,
            )
        )
        self.btn_cancel.setText(
            QCoreApplication.translate("OpenNpyDialogFrame", "Cancel", None)
        )
        self.btn_load_files.setText(
            QCoreApplication.translate("OpenNpyDialogFrame", "Load files", None)
        )

    # retranslateUi
