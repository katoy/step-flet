import flet as ft
from assets.translations import translations


class Task(ft.Column):
    def __init__(self, task_name, on_status_changed, on_delete_clicked, on_edit_clicked, on_save_clicked):
        super().__init__()
        self.completed = False
        self.task_name = task_name
        self.on_status_changed = on_status_changed
        self.on_delete_clicked = on_delete_clicked
        self.on_edit_clicked = on_edit_clicked
        self.on_save_clicked = on_save_clicked

        self.display_task = ft.Checkbox(
            value=False,
            label=self.task_name,
            on_change=self.status_changed
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
        self.update()

    def status_changed(self, e):
        self.completed = self.display_task.value
        if self.on_status_changed:
            self.on_status_changed(self)

    def delete_clicked(self, e):
        if self.on_delete_clicked:
            self.on_delete_clicked(self)


class TodoApp(ft.Column):
    def __init__(self, lang="en"):
        super().__init__()
        self.lang = lang
        self.translations = translations[self.lang]

        self.new_task = ft.TextField(
            hint_text=self.translations["What needs to be done?"],
            on_submit=self.add_clicked,
            expand=True
        )
        self.tasks = ft.Column()

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
                [ft.Text(value=self.translations["Todos"],
                         theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                controls=[
                    self.new_task,
                    ft.FloatingActionButton(
                        icon=ft.Icons.ADD,
                        on_click=self.add_clicked
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
                                on_click=self.clear_clicked
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
                on_save_clicked=self.save_clicked
            )
            self.tasks.controls.append(task)
            self.new_task.value = ""
            self.new_task.focus()
            self.update()

    def status_changed(self, task):
        self.update()

    def delete_task(self, task):
        self.tasks.controls.remove(task)
        self.update()

    def tabs_changed(self, e):
        self.update()

    def clear_clicked(self, e):
        for task in self.tasks.controls[:]:
            if task.completed:
                self.delete_task(task)

    def before_update(self):
        # タブの選択インデックスで表示を制御
        idx = self.filter.selected_index  # 0=all, 1=active, 2=completed
        count = 0
        for task in self.tasks.controls:
            if idx == 0:
                task.visible = True
            elif idx == 1:
                task.visible = not task.completed
            else:
                task.visible = task.completed

            if not task.completed:
                count += 1

        self.items_left.value = f"{count} {self.translations['item(s) left']}"

    def edit_clicked(self):
        self.update()

    def save_clicked(self):
        self.update()


todo_app = None


def main(page: ft.Page):
    global todo_app

    page.title = "ToDo App"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE

    def language_changed(e):
        global todo_app
        # 1) 現在のタスクをまるごと保持
        old_tasks = todo_app.tasks.controls[:] if todo_app else []
        # 2) ページから古いアプリを削除
        if todo_app and todo_app in page.controls:
            page.remove(todo_app)
        # 3) 新しい言語設定でアプリを再生成
        new_app = TodoApp(lang=language_dropdown.value)
        # 4) 古い Task インスタンスをそのまま新アプリに追加（状態も保持）
        for task in old_tasks:
            new_app.tasks.controls.append(task)
        # 5) ページに追加して更新
        page.add(new_app)
        todo_app = new_app
        page.update()

    language_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option("ja"), ft.dropdown.Option("en")],
        value="ja",
        on_change=language_changed,
    )

    page.appbar = ft.AppBar(
        title=ft.Text("ToDo App"),
        actions=[language_dropdown],
    )

    # 初回起動
    todo_app = TodoApp(lang="ja")
    page.add(todo_app)


if __name__ == "__main__":
    ft.app(main)  # pragma: no cover
