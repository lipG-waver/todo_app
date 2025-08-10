# main.py
import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QLineEdit, QSpinBox, QLabel, QHBoxLayout, QDateTimeEdit, QFileDialog, QMessageBox
from PyQt5.QtCore import QDateTime, Qt
from db import init_db, add_task, get_all_tasks,add_new_columns,get_active_tasks, get_completed_tasks, update_task_priority, batch_add_tasks


class TodoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do List")
        self.setGeometry(200, 200, 500, 400)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 输入区域
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("任务标题")
        self.priority_input = QSpinBox()
        self.priority_input.setRange(0, 10)
        self.soft_deadline_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.hard_deadline_input = QDateTimeEdit(QDateTime.currentDateTime())

        input_layout.addWidget(self.task_input)
        input_layout.addWidget(QLabel("优先级"))
        input_layout.addWidget(self.priority_input)
        input_layout.addWidget(QLabel("软截止"))
        input_layout.addWidget(self.soft_deadline_input)
        input_layout.addWidget(QLabel("硬截止"))
        input_layout.addWidget(self.hard_deadline_input)

        layout.addLayout(input_layout)

        # 添加/删除按钮
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("添加任务")
        self.add_btn.clicked.connect(self.add_task)
        self.delete_btn = QPushButton("删除选中任务")
        self.delete_btn.clicked.connect(self.delete_selected_task)
        self.complete_btn = QPushButton("完成选中任务")
        self.complete_btn.clicked.connect(self.complete_selected_task)
        self.increase_priority_btn = QPushButton("+ 增加优先级")
        self.increase_priority_btn.clicked.connect(lambda: self.adjust_priority(1))
        self.decrease_priority_btn = QPushButton("- 降低优先级")
        self.decrease_priority_btn.clicked.connect(lambda: self.adjust_priority(-1))
        self.import_btn = QPushButton("批量导入任务")
        self.import_btn.clicked.connect(self.import_tasks)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.complete_btn)
        btn_layout.addWidget(self.increase_priority_btn)
        btn_layout.addWidget(self.decrease_priority_btn)
        btn_layout.addWidget(self.import_btn)
        layout.addLayout(btn_layout)

        # 添加批量导入说明
        self.import_label = QLabel("批量导入格式: JSON文件，包含title, priority(0-10), soft_deadline, hard_deadline字段")
        layout.addWidget(self.import_label)

        # 任务列表
        self.task_list = QListWidget()
        layout.addWidget(QLabel("📌 当前任务"))
        layout.addWidget(self.task_list)
        # 历史记录
        self.completed_list = QListWidget()
        self.completed_list.setSelectionMode(QListWidget.SingleSelection)
        self.completed_list.setFixedHeight(150)
        layout.addWidget(QLabel("📖 历史记录"))
        layout.addWidget(self.completed_list)

        # 删除历史任务按钮
        self.delete_history_btn = QPushButton("删除选中历史任务")
        self.delete_history_btn.clicked.connect(self.delete_selected_completed_task)
        layout.addWidget(self.delete_history_btn)

        self.setLayout(layout)
        self.load_tasks()

    def load_tasks(self):
        self.task_list.clear()
        self.completed_list.clear()
        self.active_tasks = get_active_tasks()
        self.completed_tasks = get_completed_tasks()

        for task in self.active_tasks:
            self.task_list.addItem(f"[优先级 {task[2]}] {task[1]} 软:{task[3]} 硬:{task[4]}")

        for task in self.completed_tasks:
            completion_time = task[6] if len(task) > 6 else "2025-07-27 00:00"
            self.completed_list.addItem(f"[✓] {task[1]} 截止时间：{task[4]}，完成于:{completion_time}")

    def add_task(self):
        title = self.task_input.text()
        priority = self.priority_input.value()
        soft = self.soft_deadline_input.dateTime().toString("yyyy-MM-dd HH:mm")
        hard = self.hard_deadline_input.dateTime().toString("yyyy-MM-dd HH:mm")
        if title:
            add_task(title, priority, soft, hard)
            self.task_input.clear()
            self.load_tasks()


    def delete_selected_task(self):
        selected_items = self.task_list.selectedIndexes()
        if selected_items:
            index = selected_items[0].row()
            task_id = self.active_tasks[index][0]
            from db import delete_task
            delete_task(task_id)
            self.load_tasks()

    def complete_selected_task(self):
        selected_items = self.task_list.selectedIndexes()
        if selected_items:
            index = selected_items[0].row()
            task_id = self.active_tasks[index][0]
            from db import mark_task_completed
            mark_task_completed(task_id)
            self.load_tasks()

    def delete_selected_completed_task(self):
        selected_items = self.completed_list.selectedIndexes()
        if selected_items:
            index = selected_items[0].row()
            task_id = self.completed_tasks[index][0]
            from db import delete_task
            delete_task(task_id)
            self.load_tasks()

    def keyPressEvent(self, event):
        # 处理优先级调整
        if event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal and event.modifiers() == Qt.ShiftModifier:
            self.adjust_priority(1)
        elif event.key() == Qt.Key_Minus:
            self.adjust_priority(-1)
        super().keyPressEvent(event)

    def adjust_priority(self, change):
        selected_items = self.task_list.selectedIndexes()
        if selected_items:
            index = selected_items[0].row()
            task_id = self.active_tasks[index][0]
            current_priority = self.active_tasks[index][2]
            new_priority = max(0, min(10, current_priority + change))
            if new_priority != current_priority:
                update_task_priority(task_id, new_priority)
                self.load_tasks()
                # 重新选中更新后的任务
                self.task_list.setCurrentRow(index)

    def import_tasks(self):
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择JSON文件", "", "JSON Files (*.json)"
        )
        if not file_path:
            return

        try:
            # 读取JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)

            # 验证数据格式
            if not isinstance(tasks_data, list):
                raise ValueError("JSON文件必须包含一个任务列表")

            valid_tasks = []
            for task in tasks_data:
                if not all(key in task for key in ['title', 'priority', 'soft_deadline', 'hard_deadline']):
                    raise ValueError(f"任务缺少必要字段: {task}")
                if not (0 <= task['priority'] <= 10):
                    raise ValueError(f"优先级必须在0-10之间: {task['priority']}")
                valid_tasks.append(task)

            # 批量添加任务
            success, message = batch_add_tasks(valid_tasks)

            # 显示结果
            if success:
                QMessageBox.information(self, "成功", message)
                self.load_tasks()
            else:
                QMessageBox.critical(self, "失败", message)

        except json.JSONDecodeError:
            QMessageBox.critical(self, "错误", "JSON文件格式无效")
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))


if __name__ == "__main__":
    init_db()
    add_new_columns()
    app = QApplication(sys.argv)
    window = TodoApp()
    window.show()
    sys.exit(app.exec_())
