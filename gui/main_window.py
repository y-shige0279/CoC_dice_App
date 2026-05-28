from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QHBoxLayout,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QApplication,
    QHeaderView,
)

from models.config import load_config, Edition
from models.config import BonusType
from models.status import StatusName
from models.character import Character
from services.generator import generate_character
from utils.input_normalizer import normalize_input

from PySide6.QtGui import QFont, QIntValidator
from PySide6.QtCore import Qt, QTimer

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        
        self.setFont(QFont("Noto Sans CJK JP", 10))

        self.config = load_config()

        self.setWindowTitle("CoC Character Generator")
        self.resize(600, 500)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # タイトル
        title_label = QLabel(
            "Call of Cthulhu Character Generator"
        )
        
        # タイトルを中央揃えにする
        self.current_bonus_label = QLabel()
        self.current_bonus_label.setText(
            "現在補正: なし"
        )
        
        self.edition_combo = QComboBox()
        self.edition_combo.addItem("6版", Edition.COC6)
        self.edition_combo.addItem("7版", Edition.COC7)
        
        self.edition_combo.currentIndexChanged.connect(
            self.on_edition_changed
        )

        self.generate_button = QPushButton(
            "キャラ生成"
        )
        
        self.copy_button = QPushButton(
            "結果をコピー"
        )

        self.copy_button.clicked.connect(
            self.copy_result
        )

        self.result_table = QTableWidget()
        self.result_table.setFixedHeight(260)# 結果表示テーブルの高さを固定
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels([
            "能力値",
            "基本値",
            "増加分",
            "一時",
            "最終値",
        ])
        
        # 行ヘッダーを非表示にする
        self.result_table.verticalHeader().setVisible(False)
        
        # 列幅を内容に合わせて自動調整する
        self.result_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        
        # 補正入力UI
        bonus_layout = QHBoxLayout()

        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "STR",
            "CON",
            "POW",
            "DEX",
            "APP",
            "SIZ",
            "INT",
            "EDU",
        ])
        
        self.status_combo.currentIndexChanged.connect(
            self.on_status_changed
        )

        self.bonus_type_combo = QComboBox()
        self.bonus_type_combo.addItems([
            "増加分",
            "一時",
        ])
        
        self.bonus_type_combo.currentIndexChanged.connect(
            self.on_bonus_type_changed
        )

        self.bonus_value_input = QLineEdit()
        self.bonus_value_input.setPlaceholderText("補正値")
        self.bonus_value_input.setValidator(
            QIntValidator(-999, 999)
        )

        self.bonus_reason_input = QLineEdit()
        self.bonus_reason_input.setPlaceholderText("理由")
        self.bonus_reason_input.setInputMethodHints(Qt.ImhNone)

        self.add_bonus_button = QPushButton(
            "補正追加"
        )

        self.add_bonus_button.clicked.connect(
            self.add_bonus
        )
        
        self.bonus_value_input.returnPressed.connect(
            self.add_bonus
        )

        self.bonus_reason_input.returnPressed.connect(
            self.add_bonus
        )
        
        self.remove_bonus_button = QPushButton(
            "選択した補正を削除"
        )

        self.remove_bonus_button.clicked.connect(
            self.remove_bonus
        )

        bonus_layout.addWidget(self.status_combo) # ステータス選択
        bonus_layout.addWidget(self.bonus_type_combo) # 補正タイプ選択
        bonus_layout.addWidget(self.bonus_value_input) # 補正値入力
        bonus_layout.addWidget(self.bonus_reason_input) # 補正理由入力
        bonus_layout.addWidget(self.add_bonus_button) # 補正追加ボタン

        self.bonus_table = QTableWidget()

        self.bonus_table.setColumnCount(4)

        self.bonus_table.setHorizontalHeaderLabels([
            "能力値",
            "タイプ",
            "値",
            "理由",
        ])

        self.bonus_table.verticalHeader().setVisible(False)

        self.bonus_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.bonus_inputs = []

        self.generate_button.clicked.connect(
            self.generate_character
        )

        # UI配置
        layout.addWidget(title_label) # タイトル
        layout.addWidget(self.edition_combo)# エディション選択

        layout.addLayout(bonus_layout)# 補正入力UI
        layout.addWidget(self.bonus_table)# 補正リスト表示
        
        layout.addWidget(self.current_bonus_label)# 現在の補正表示
        
        layout.addWidget(self.remove_bonus_button)# 補正削除ボタン

        layout.addWidget(self.generate_button)# キャラ生成ボタン
        
        layout.addWidget(self.result_table)# 結果表示
        layout.addWidget(self.copy_button)# 結果コピーボタン

        
        
        self.setLayout(layout)

    def generate_character(self):
        # キャラクター生成処理
        edition = self.edition_combo.currentData()
        # 結果表示テーブルを初期化
        self.result_table.clearContents()
        self.result_table.setRowCount(0)
        # キャラクター生成
        character = generate_character(
            edition,
            self.config.status,
            self.config.target_total,
            self.config.target_status,
            self.bonus_inputs,
        )

        self.result_table.setRowCount(
            len(character.status) + 1
        )

        row = 0

        for status_name, value in character.status.items():
            self.result_table.setItem(
                row,
                0,
                QTableWidgetItem(status_name.value)
            )
            self.result_table.setItem(
                row,
                1,
                QTableWidgetItem(str(value.base))
            )
            self.result_table.setItem(
                row,
                2,
                QTableWidgetItem(str(value.bonus))
            )
            self.result_table.setItem(
                row,
                3,
                QTableWidgetItem(str(value.temp_bonus))
            )
            self.result_table.setItem(
                row,
                4,
                QTableWidgetItem(str(value.final_value()))
            )

            row += 1

        total = sum(
            status.final_value()
            for status in character.status.values()
        )

        self.result_table.setItem(
            row,
            0,
            QTableWidgetItem("合計")
        )
        self.result_table.setItem(
            row,
            4,
            QTableWidgetItem(str(total))
        )

        # 列幅を内容に合わせて自動調整する
        self.result_table.resizeColumnsToContents()
        
        character.logger.save_all(character)

        QMessageBox.information(
            self,
            "保存完了",
            "キャラクター結果を保存しました。",
        )
        # 結果表示テーブルのスクロールをリセット
        self.result_table.verticalScrollBar().setValue(0)
        self.result_table.scrollToTop()
        self.result_table.clearSelection()
        
    def add_bonus(self):
        status_name = StatusName[
            self.status_combo.currentText()
        ]

        bonus_type_text = self.bonus_type_combo.currentText()

        history_type = (
            BonusType.PERMANENT
            if bonus_type_text == "増加分"
            else BonusType.TEMPORARY
        )

        value_text = self.bonus_value_input.text()

        if not value_text:
            QMessageBox.warning(
                self,
                "入力エラー",
                "補正値を入力してください。",
            )
            return

        try:
            value = int(normalize_input(value_text))

        except ValueError:
            QMessageBox.warning(
                self,
                "入力エラー",
                "補正値は数字で入力してください。",
            )
            return

        reason = self.bonus_reason_input.text().strip()

        self.bonus_inputs.append(
            (
                status_name,
                history_type,
                value,
                reason
            )
        )

        # 補正リストに追加
        row = self.bonus_table.rowCount()

        self.bonus_table.setRowCount(row + 1)
        
        self.bonus_table.setItem(
            row,
            0,
            QTableWidgetItem(status_name.value)
        )
        
        self.bonus_table.setItem(
            row,
            1,
            QTableWidgetItem(bonus_type_text)
        )
        
        self.bonus_table.setItem(
            row,
            2,
            QTableWidgetItem(f"{value:+}")
        )
        
        self.bonus_table.setItem(
            row,
            3,
            QTableWidgetItem(reason)
        )

        # 入力欄をクリア
        self.bonus_value_input.clear()
        self.bonus_reason_input.clear()
        
        # 補正追加後、値入力欄にフォーカスして全選択状態にする
        self.bonus_value_input.setFocus()
        self.bonus_value_input.selectAll()
        # 補正サマリーを更新
        self.update_bonus_summary()
        
    def update_bonus_summary(self):
        summary = {}

        for (
            status_name,
            history_type,
            value,
            reason,
        ) in self.bonus_inputs:

            key = status_name.value

            if key not in summary:
                summary[key] = 0

            summary[key] += value

        if not summary:
            self.current_bonus_label.setText(
                "現在補正: なし"
            )
            return

        lines = ["現在補正:"]

        for key, value in summary.items():
            lines.append(
                f"{key} {value:+}"
            )

        self.current_bonus_label.setText(
            "\n".join(lines)
        )
    
    # 結果をクリップボードにコピー
    def copy_result(self):
        lines = []

        for row in range(
            self.result_table.rowCount()
        ):
            status = self.result_table.item(row, 0)
            final_value = self.result_table.item(row, 4)

            if status and final_value:
                lines.append(
                    f"{status.text()}: "
                    f"{final_value.text()}"
                )

        text = "\n".join(lines)

        clipboard = QApplication.clipboard()
        clipboard.setText(text)

        QMessageBox.information(
            self,
            "コピー完了",
            "結果をコピーしました。",
        )

        
    def remove_bonus(self):
        selected_row = self.bonus_table.currentRow()

        if selected_row < 0:
            return

        self.bonus_table.removeRow(selected_row)
        self.bonus_inputs.pop(selected_row)

        self.result_table.setRowCount(0)
        self.update_bonus_summary()

    def on_edition_changed(self):
        self.edition_combo.clearFocus()
        self.result_table.setRowCount(0)
        
    def on_status_changed(self):
        self.status_combo.clearFocus()
        self.result_table.setRowCount(0)
        
    def on_bonus_type_changed(self):
        self.bonus_type_combo.clearFocus()
        self.result_table.setRowCount(0)
        
    