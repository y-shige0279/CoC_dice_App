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
    QApplication,
    QHeaderView,
    QCheckBox,
    QScrollArea,
    QAbstractItemView,
)

from models.config import load_config, Edition
from models.config import BonusType
from models.status import StatusName
from services.generator import generate_character
from utils.input_normalizer import normalize_input
from gui.delegates import IntegerDelegate

from PySide6.QtGui import QFont, QIntValidator
from PySide6.QtCore import Qt

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        
        self.setFont(QFont("Noto Sans CJK JP", 10))

        self.config = load_config()

        self.setWindowTitle("CoC Character Generator")
        self.resize(600, 900)

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        # タイトル
        title_label = QLabel(
            "Call of Cthulhu Character Generator"
        )
        
        self.message_label = QLabel("")# メッセージ表示用ラベル
        self.message_label.setFixedHeight(24)# メッセージ表示用ラベルの高さを固定
        
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
        
        target_layout = QHBoxLayout()

        target_label = QLabel("合計最低値")

        self.target_total_input = QLineEdit()
        self.target_total_input.setPlaceholderText("例: 100")

        target_layout.addWidget(target_label)# 目標合計入力のラベル
        target_layout.addWidget(self.target_total_input)# 目標合計入力欄
        
        self.condition_table = QTableWidget()
        self.condition_table.setColumnCount(3)
        self.condition_table.setHorizontalHeaderLabels([
            "能力値",
            "最低値",
            "最大値",
        ])

        # 行ヘッダーを非表示にする
        self.condition_table.verticalHeader().setVisible(False)
        # 列幅を内容に合わせて自動調整する
        self.condition_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.condition_table.setRowCount(8)# 能力値の数に合わせて行数を設定

        status_names = [
            "STR",
            "CON",
            "POW",
            "DEX",
            "APP",
            "SIZ",
            "INT",
            "EDU",
        ]

        # 条件テーブルに能力値の名前とデフォルトの最低値・最大値を設定
        for row, status_name in enumerate(status_names):
            self.condition_table.setItem(
                row,
                0,
                QTableWidgetItem(status_name)
            )
            
            default_min, default_max = self.config.target_status[
                self.edition_combo.currentData().value
                ][status_name]

            # 条件テーブルにデフォルトの最低値と最大値を設定
            self.condition_table.setItem(
                row,
                1,
                QTableWidgetItem(str(default_min))
            )

            # 条件テーブルにデフォルトの最大値を設定
            self.condition_table.setItem(
                row,
                2,
                QTableWidgetItem(str(default_max))
            )

        # 条件テーブルの高さを固定
        self.condition_table.setFixedHeight(180)
        
        self.condition_table.setItemDelegateForColumn(
            1,
            IntegerDelegate()
        )

        self.condition_table.setItemDelegateForColumn(
            2,
            IntegerDelegate()
        )

        self.generate_button = QPushButton(
            "キャラ生成"
        )
        
        self.save_checkbox = QCheckBox(
            "生成結果を保存する"
        )

        self.save_checkbox.setChecked(False)
        
        # 条件を初期値に戻すボタン
        self.reset_condition_button = QPushButton(
            "条件を初期値に戻す"
        )
        # 条件を初期値に戻すボタンのクリックイベントに条件テーブルを更新する処理を接続
        self.reset_condition_button.clicked.connect(
            self.reset_conditions
        )
        
        self.copy_button = QPushButton(
            "結果をコピー"
        )

        self.copy_button.clicked.connect(
            self.copy_result
        )

        self.result_table = QTableWidget()# 結果表示テーブル
        self.result_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )# 結果表示テーブルを編集不可にする

        self.result_table.setFixedHeight(230)# 結果表示テーブルの高さを固定
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels([
            "能力値",
            "基本値",
            "増加分",
            "一時",
            "最終値",
        ])
        
        self.reroll_label = QLabel(
            "振り直し回数: -"
        )
        
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

        # 補正値入力欄
        self.bonus_value_input = QLineEdit()
        self.bonus_value_input.setPlaceholderText("補正値")

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
        
        self.clear_bonus_button = QPushButton(
            "補正を全削除"
        )

        self.clear_bonus_button.clicked.connect(
            self.clear_bonuses
        )

        bonus_layout.addWidget(self.status_combo) # ステータス選択
        bonus_layout.addWidget(self.bonus_type_combo) # 補正タイプ選択
        bonus_layout.addWidget(self.bonus_value_input) # 補正値入力
        bonus_layout.addWidget(self.bonus_reason_input) # 補正理由入力
        bonus_layout.addWidget(self.add_bonus_button) # 補正追加ボタン

        self.bonus_table = QTableWidget()
        self.bonus_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )# 補正リストを編集不可にする
        self.bonus_table.setFixedHeight(100)

        self.bonus_table.setColumnCount(4)

        self.bonus_table.setHorizontalHeaderLabels([
            "能力値",
            "タイプ",
            "値",
            "理由",
        ])

        # 行ヘッダーを非表示にする
        self.bonus_table.verticalHeader().setVisible(False)

        # 列幅を内容に合わせて自動調整する
        self.bonus_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.bonus_inputs = []

        # キャラ生成ボタンのクリックイベントにキャラクター生成処理を接続
        self.generate_button.clicked.connect(
            self.generate_character
        )
        
        # 目標合計入力欄でEnterキーが押されたときにキャラクター生成処理を接続
        self.target_total_input.returnPressed.connect(
            self.generate_character
        )

        # UI配置
        layout.addWidget(title_label) # タイトル
        layout.addWidget(self.edition_combo)# エディション選択
        
        layout.addLayout(target_layout)# 目標合計入力
        
        layout.addWidget(self.condition_table)# 条件入力テーブル
        layout.addWidget(self.reset_condition_button)# 条件を初期値に戻すボタン

        layout.addLayout(bonus_layout)# 補正入力UI
        layout.addWidget(self.bonus_table)# 補正リスト表示
        
        layout.addWidget(self.current_bonus_label)# 現在の補正表示
        
        layout.addWidget(self.remove_bonus_button)# 補正削除ボタン
        layout.addWidget(self.clear_bonus_button)# 補正全削除ボタン

        layout.addWidget(self.save_checkbox)# 生成結果保存のチェックボックス
        
        layout.addWidget(self.generate_button)# キャラ生成ボタン
        
        layout.addWidget(self.result_table)# 結果表示
        layout.addWidget(self.reroll_label)# 振り直し回数表示
        layout.addWidget(self.copy_button)# 結果コピーボタン
        
        layout.addWidget(self.message_label)# メッセージ表示

        scroll_area.setWidget(content_widget)# スクロールエリアにコンテンツウィジェットをセット
        main_layout.addWidget(scroll_area)# スクロールエリアをメインレイアウトに追加
        
        self.setLayout(main_layout)# UI全体のレイアウトを設定
        self.update_condition_table()# 条件テーブルを初期化

    def generate_character(self):
        
        # キャラクター生成処理
        edition = self.edition_combo.currentData()
        
        # 目標合計や条件を取得
        target_total, target_status = self.get_generation_conditions(
            edition
        )
        
        # 目標合計や条件の取得に失敗した場合は処理を中断
        if target_total is None or target_status is None:
            return

        # 結果表示テーブルを初期化
        self.result_table.clearContents()
        self.result_table.setRowCount(0)
        # キャラクター生成
        character = generate_character(
            edition,
            self.config.status,
            target_total,
            target_status,
            self.bonus_inputs,
        )
        
        self.reroll_label.setText(
            f"振り直し回数: {character.reroll_cnt}"
        )

        self.display_character(character)
        
        # ログを保存
        if self.save_checkbox.isChecked():
            character.logger.save_all(character)
        
            # メッセージ表示
            self.set_message("保存しました", "success")
            
        else:
            self.set_message("保存せずに生成しました")
        
    def get_generation_conditions(self, edition):
        # 目標合計や条件をUIから取得
        target_total = self.config.target_total.copy()

        # 条件の初期値をconfigからコピー
        target_status = {
            edition_key: dict(statuses)
            for edition_key, statuses in self.config.target_status.items()
        }

        # 条件テーブルから最低値と最大値を取得してtarget_statusに反映
        for row in range(self.condition_table.rowCount()):
            status_item = self.condition_table.item(row, 0)
            min_item = self.condition_table.item(row, 1)
            max_item = self.condition_table.item(row, 2)

            if not status_item or not min_item or not max_item:
                continue

            status_name = status_item.text()

            try:
                # 入力値を正規化して整数に変換
                min_value = int(normalize_input(min_item.text()))
                max_value = int(normalize_input(max_item.text()))
            except ValueError:
                self.set_message(
                    f"{status_name} の最低値・最大値は数字で入力してください",
                    "error",
                )
                return None, None

            config_min, config_max = self.config.target_status[
                edition.value
            ][status_name]

            # 入力値の妥当性をチェック
            if min_value < config_min:
                self.set_message(
                    f"{status_name} の最低値は {config_min} 以上にしてください",
                    "error",
                )
                return None, None

            if max_value > config_max:
                self.set_message(
                    f"{status_name} の最大値は {config_max} 以下にしてください",
                    "error",
                )
                return None, None

            if min_value > max_value:
                self.set_message(
                    f"{status_name} の最低値が最大値を超えています",
                    "error",
                )
                return None, None

            # 条件テーブルの値をtarget_statusに反映
            target_status[edition.value][status_name] = (
                min_value,
                max_value,
            )

        # 目標合計を取得してtarget_totalに反映
        target_total_text = self.target_total_input.text().strip()

        # 目標合計の入力がある場合は正規化して整数に変換してtarget_totalに反映
        if target_total_text:
            target_total[edition.value] = int(
                normalize_input(target_total_text)
            )

        return target_total, target_status
        
    def display_character(self, character):
        # キャラクターの能力値を結果表示テーブルに表示
        self.result_table.setRowCount(
            len(character.status) + 1
        )

        row = 0

        # キャラクターの能力値をテーブルに表示
        for status_name, value in character.status.items():
            self.result_table.setItem(row, 0, QTableWidgetItem(status_name.value))
            self.result_table.setItem(row, 1, QTableWidgetItem(str(value.base)))
            self.result_table.setItem(row, 2, QTableWidgetItem(str(value.bonus)))
            self.result_table.setItem(row, 3, QTableWidgetItem(str(value.temp_bonus)))
            self.result_table.setItem(row, 4, QTableWidgetItem(str(value.final_value())))

            row += 1

        total = sum(
            status.final_value()
            for status in character.status.values()
        )

        # 合計をテーブルに表示
        self.result_table.setItem(row, 0, QTableWidgetItem("合計"))
        self.result_table.setItem(row, 4, QTableWidgetItem(str(total)))

        # テーブルの列幅を内容に合わせて自動調整
        self.result_table.resizeColumnsToContents()
        
        # テーブルのスクロールを一番上に移動
        self.result_table.verticalScrollBar().setValue(0)
        self.result_table.scrollToTop()
        self.result_table.clearSelection()
    
    def add_bonus(self):
        # 補正を追加
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
            self.set_message("補正値を入力してください", "error")
            return

        try:
            value = int(normalize_input(value_text))

        except ValueError:
            self.set_message("補正値は数字で入力してください", "error")
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

        summary_text = " / ".join(
            f"{key} {value:+}"
            for key, value in summary.items()
        )

        self.current_bonus_label.setText(
            f"現在補正: {summary_text}"
        )
    
    # 結果をクリップボードにコピー
    def copy_result(self):
        lines = []
    
        for row in range(self.result_table.rowCount()):
            status = self.result_table.item(row, 0)
            base = self.result_table.item(row, 1)
            bonus = self.result_table.item(row, 2)
            temp_bonus = self.result_table.item(row, 3)
            final_value = self.result_table.item(row, 4)
    
            if not status or not final_value:
                continue
            
            if status.text() == "合計":
                lines.append(f"合計: {final_value.text()}")
                continue
            
            lines.append(
                f"{status.text()}: {final_value.text()} "
                f"(基本{base.text()} / 増加{bonus.text()} / 一時{temp_bonus.text()})"
            )
    
        lines.append(self.reroll_label.text())
    
        if self.bonus_inputs:
            lines.append("")
            lines.append("補正:")
    
            for status_name, history_type, value, reason in self.bonus_inputs:
                reason_text = f" : {reason}" if reason else ""
                lines.append(
                    f"{status_name.value} {value:+} ({history_type.value}){reason_text}"
                )
    
        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join(lines))
    
        self.set_message("結果をコピーしました", "success")

        
    def remove_bonus(self):
        selected_row = self.bonus_table.currentRow()

        if selected_row < 0:
            return

        self.bonus_table.removeRow(selected_row)
        self.bonus_inputs.pop(selected_row)

        self.result_table.setRowCount(0)
        self.update_bonus_summary()
        
    def reset_conditions(self):
        self.update_condition_table()
        self.target_total_input.clear()
        self.result_table.setRowCount(0)
        self.set_message("条件を初期値に戻しました", "success")

    def clear_bonuses(self):
        self.bonus_inputs.clear()
        self.bonus_table.setRowCount(0)
        self.result_table.setRowCount(0)

        self.update_bonus_summary()

        self.set_message("補正を全削除しました", "success")

    def on_edition_changed(self):
        self.edition_combo.clearFocus()
        self.result_table.setRowCount(0)
        self.update_condition_table()
        
    def on_status_changed(self):
        self.status_combo.clearFocus()
        self.result_table.setRowCount(0)
        
    def on_bonus_type_changed(self):
        self.bonus_type_combo.clearFocus()
        self.result_table.setRowCount(0)
        
    def update_condition_table(self):
        edition = self.edition_combo.currentData()
        target_status = self.config.target_status[edition.value]

        for row in range(self.condition_table.rowCount()):
            status_item = self.condition_table.item(row, 0)

            if not status_item:
                continue

            status_name = status_item.text()

            min_value, max_value = target_status[status_name]

            self.condition_table.setItem(
                row,
                1,
                QTableWidgetItem(str(min_value))
            )

            self.condition_table.setItem(
                row,
                2,
                QTableWidgetItem(str(max_value))
            )
    
    def set_message(self, text: str, message_type: str = "info"):
        if message_type == "error":
            self.message_label.setStyleSheet("color: red;")
        elif message_type == "success":
            self.message_label.setStyleSheet("color: green;")
        else:
            self.message_label.setStyleSheet("color: black;")

        self.message_label.setText(text)