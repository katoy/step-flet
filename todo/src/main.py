import flet as ft
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.assets.translations import translations


class Task(ft.Column):
    def __init__(
        self,
        task_name,
        on_status_changed,
        on_delete_clicked,
        on_edit_clicked,
        on_save_clicked,
    ):
        super().__init__()
        self.completed = False
        self.task_name = task_name
        self.on_status_changed = on_status_changed
        self.on_delete_clicked = on_delete_clicked
        self.on_edit_clicked = on_edit_clicked
        self.on_save_clicked = on_save_clicked

        self.display_task = ft.Checkbox(
            value=False, label=self.task_name, on_change=self.status_changed
        )
        self.edit_name = ft.TextField(expand=1)

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.CREATE_OUTLINED,
                            tooltip="Edit To-Do",
                            on_click=self.edit_clicked,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            tooltip="Delete To-Do",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.Icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.Colors.GREEN,
                    tooltip="Update To-Do",
                    on_click=self.save_clicked,
                ),
            ],
        )

        self.controls = [self.display_view, self.edit_view]

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        if self.on_edit_clicked:
            self.on_edit_clicked()
        self.update()

    def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        if self.on_save_clicked:
            self.on_save_clicked()
        global todo_app
        todo_app.save_tasks()
        self.update()

    def status_changed(self, e):
        self.completed = self.display_task.value
        if self.on_status_changed:
            self.on_status_changed(self)

    def delete_clicked(self, e):
        if self.on_delete_clicked:
            self.on_delete_clicked(self)


class TodoApp(ft.Column):
    def __init__(self, lang="en", json_path="storage/todos.json"):
        """TodoApp の初期化メソッド。

        Args:
            lang (str): アプリの言語設定。デフォルトは "en"。
            json_path (str): タスクを保存する JSON ファイルのパス。デフォルトは "storage/todos.json"。
        """
        super().__init__()
        self.lang = lang
        self.json_path = json_path
        self.translations = translations[self.lang]

        self.new_task = ft.TextField(
            hint_text=self.translations["What needs to be done?"],
            on_submit=self.add_clicked,
            expand=True,
        )
        self.tasks = ft.Column()

        self.items_left = ft.Text("0 items left")

        self.filter = ft.Tabs(
            scrollable=False,
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[
                ft.Tab(text=self.translations["all"]),
                ft.Tab(text=self.translations["active"]),
                ft.Tab(text=self.translations["completed"]),
            ],
        )

        self.items_left = ft.Text("0 items left")
        self.width = 600

        self.controls = [
            ft.Row(
                [
                    ft.Text(
                        value=self.translations["Todos"],
                        theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                controls=[
                    self.new_task,
                    ft.FloatingActionButton(
                        icon=ft.Icons.ADD, on_click=self.add_clicked
                    ),
                ],
            ),
            ft.Column(
                spacing=25,
                controls=[
                    self.filter,
                    self.tasks,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self.items_left,
                            ft.OutlinedButton(
                                text=self.translations["Clear completed"],
                                on_click=self.clear_clicked,
                            ),
                        ],
                    ),
                ],
            ),
        ]

    def add_clicked(self, e):
        if self.new_task.value:
            task = Task(
                task_name=self.new_task.value,
                on_status_changed=self.status_changed,
                on_delete_clicked=self.delete_task,
                on_edit_clicked=self.edit_clicked,
                on_save_clicked=self.save_clicked,
            )
            self.tasks.controls.append(task)
            self.new_task.value = ""
            global todo_app
            todo_app.save_tasks()
            self.update()
            self.new_task.focus()
        else:
            self.update()
        self.update_items_left()  # pragma: no cover

    def status_changed(self, task):
        global todo_app
        todo_app.save_tasks()
        self.update_items_left()

    def delete_task(self, task):
        self.tasks.controls.remove(task)
        global todo_app
        todo_app.save_tasks()
        self.update_items_left()

    def tabs_changed(self, e):
        self.update()
        self.update_task_visibility()
        self.update_items_left()

    def clear_clicked(self, e):
        for task in self.tasks.controls[:]:
            if task.completed:
                self.delete_task(task)

    def update_task_visibility(self):
        for task in self.tasks.controls:
            if self.filter.selected_index == 0:  # "all" tab
                task.visible = True
            elif self.filter.selected_index == 1:  # "active" tab
                task.visible = not task.completed
            elif self.filter.selected_index == 2:  # "completed" tab
                task.visible = task.completed
            task.update()
        if hasattr(self, "translations"):
            self.update_items_left()

    def save_tasks(self):
        task_list = []
        for task in self.tasks.controls:
            task_list.append(
                {"task_name": task.display_task.label, "completed": task.completed}
            )
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(task_list, f, ensure_ascii=False, indent=4)

    def edit_clicked(self):
        self.update()

    def save_clicked(self):
        self.update()

    def load_tasks(self):
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                task_list = json.load(f)
            for task_data in task_list:
                task = Task(
                    task_name=task_data["task_name"],
                    on_status_changed=self.status_changed,
                    on_delete_clicked=self.delete_task,
                    on_edit_clicked=self.edit_clicked,
                    on_save_clicked=self.save_clicked,
                )
                task.completed = task_data["completed"]
                task.display_task.value = task.completed
                self.tasks.controls.append(task)
        except FileNotFoundError:
            print("File not found")
            self.tasks.controls = []
            return
        except json.JSONDecodeError:
            print("Invalid JSON file")
            self.tasks.controls = []
            self.update_items_left()
            return

    def language_changed(self, e):
        if e and hasattr(e, "control") and e.control:
            self.lang = e.control.value
        else:
            self.lang = "ja"
        try:
            self.translations = translations[self.lang]
        except KeyError:
            self.lang = "ja"
            self.translations = translations["ja"]
        self.new_task.hint_text = self.translations["What needs to be done?"]
        self.filter.tabs[0].text = self.translations["all"]
        self.filter.tabs[1].text = self.translations["active"]
        self.filter.tabs[2].text = self.translations["completed"]
        count = 0
        for task in self.tasks.controls:
            if not task.completed:
                count += 1
        self.items_left.value = f"{count} active {self.translations['item(s) left']}"
        self.update()

    def update_items_left(self):
        count = 0
        for task in self.tasks.controls:
            if not task.completed:
                count += 1
        self.items_left.value = f"{count} active {self.translations['item(s) left']}"
        self.update()


todo_app = None


def main(page: ft.Page):
    global todo_app

    page.title = "ToDo App"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE

    # 初回起動
    todo_app = TodoApp(lang="ja")
    todo_app.page = page
    page.add(todo_app)

    language_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option("ja"), ft.dropdown.Option("en")],
        value="ja",
        on_change=todo_app.language_changed,
    )

    page.appbar = ft.AppBar(
        title=ft.Text("ToDo App"),
        actions=[language_dropdown],
    )

    # タスクをロード
    todo_app.load_tasks()
    todo_app.update_items_left()
    page.update()


if __name__ == "__main__":
    ft.app(main)  # pragma: no cover
