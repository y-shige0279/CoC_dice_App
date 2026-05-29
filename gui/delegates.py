from PySide6.QtWidgets import (
    QStyledItemDelegate,
    QLineEdit,
)

from PySide6.QtGui import QIntValidator


class IntegerDelegate(QStyledItemDelegate):

    def createEditor(
        self,
        parent,
        option,
        index,
    ):
        editor = QLineEdit(parent)

        editor.setValidator(
            QIntValidator(-999, 9999)
        )

        return editor