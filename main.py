# main.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QLineEdit, QSpinBox, QLabel, QHBoxLayout, QDateTimeEdit
from PyQt5.QtCore import QDateTime
from db import init_db, add_task, get_all_tasks,add_new_columns,get_active_tasks, get_completed_tasks


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
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.complete_btn)
        layout.addLayout(btn_layout)

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


if __name__ == "__main__":
    init_db()
    add_new_columns()
    app = QApplication(sys.argv)
    window = TodoApp()
    window.show()
    sys.exit(app.exec_())
