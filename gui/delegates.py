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
        # 全角数字も許可するためValidatorは使わない
        return editor