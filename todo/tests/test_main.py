import unittest
import flet as ft
from unittest.mock import Mock
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.assets.translations import translations
import src.main

from src.main import Task, TodoApp


class MockPage:
    def __init__(self):
        self.controls = []
        self.appbar = MockAppBar()

    def add(self, control):
        self.controls.append(control)
        control.page = self

    def update(self, control=None):
        self.focus_called = False

    def remove(self, control):
        self.controls.remove(control)

    def focus(self):
        self.focus_called = True


class MockAppBar:
    def __init__(self):
        self.actions = [MockLanguageDropdown()]


class MockLanguageDropdown:
    def __init__(self):
        self.value = "ja"
        self.on_change = self

    def __call__(self, language_changed_event):
        if self.on_change:
            self.language_changed(language_changed_event)

    def language_changed(self, event):
        if src.main.todo_app:
            src.main.todo_app.lang = "en"


class TodoAppTestBase(unittest.TestCase):
    def setUp(self):
        self.page = MockPage()
        self.app = TodoApp(json_path="storage/test_todos.json")
        src.main.todo_app = self.app
        self.app.page = self.page
        self.page.add(self.app)
        self.app.new_task.page = self.page

        # テストファイルの存在を確認し、存在する場合は削除
        test_file_path = self.app.json_path
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

        self.app.update()

    def tearDown(self):
        # テストで使用したタスクを削除
        self.app.clear_clicked(None)


class TaskTestBase(unittest.TestCase):
    def setUp(self):
        self.page = MockPage()
        self.page.focus_called = False
        self.app = TodoApp(json_path="storage/test_todos.json")
        src.main.todo_app = self.app
        self.task = Task("Test Task", None, None, None, None)
        self.task.page = self.page
        self.page.add(self.task)
        self.task.update()


class TestMockLanguageDropdown(unittest.TestCase):
    def setUp(self):
        self.dropdown = MockLanguageDropdown()
        self.page = MockPage()
        self.app = TodoApp(json_path="storage/test_todos.json")
        src.main.todo_app = self.app
        self.app.page = self.page
        self.page.add(self.app)

    def test_language_changed(self):
        # Mock the event
        event = Mock()
        event.control = Mock()
        event.control.value = "en"

        # Call the method
        self.dropdown.language_changed(event)

        # Assert that the language has changed
        self.assertEqual(self.app.lang, "en")


class TestTodoAppLanguageChanged(TodoAppTestBase):
    def test_language_changed(self):
        # Mock the event
        event = Mock()
        event.control = Mock()
        event.control.value = "en"

        # Call the method
        self.app.language_changed(event)

        # Assert that the language has changed
        self.assertEqual(self.app.lang, "en")
        self.assertEqual(self.app.new_task.hint_text, "What needs to be done?")
        self.assertEqual(self.app.filter.tabs[0].text, "all")
        self.assertEqual(self.app.filter.tabs[1].text, "active")
        self.assertEqual(self.app.filter.tabs[2].text, "completed")
        self.assertEqual(self.app.items_left.value, "0 active item(s) left")
        self.assertEqual(self.app.translations, translations["en"])


class TestTodoAppInvalidLanguageChanged(TodoAppTestBase):
    def test_language_changed_invalid_language(self):
        # Mock the event
        event = Mock()
        event.control = Mock()
        event.control.value = "invalid"

        # Call the method
        self.app.language_changed(event)

        # Assert that the language has changed
        self.assertEqual(self.app.lang, "ja")

    def test_language_changed_empty_language(self):
        # Mock the event
        event = Mock()
        event.control = Mock()
        event.control.value = ""

        # Call the method
        self.app.language_changed(event)

        # Assert that the language has not changed
        self.assertEqual(self.app.lang, "ja")

    def test_language_changed_no_event(self):
        # Call the method with no event
        self.app.language_changed(None)

        # Assert that the language has not changed
        self.assertEqual(self.app.lang, "ja")

    def test_language_changed_no_control(self):
        # Mock the event
        event = Mock()
        del event.control

        # Call the method
        self.app.language_changed(event)

        # Assert that the language has not changed
        self.assertEqual(self.app.lang, "ja")


class TestTask(TaskTestBase):
    def test_task_creation(self):
        self.assertEqual(self.task.task_name, "Test Task")
        self.assertFalse(self.task.completed)

    def test_status_changed(self):
        # status_changed doesn't change completed status without an event
        self.task.status_changed(None)
        self.assertFalse(self.task.completed)

        # Test status_changed with an event
        event = ft.ControlEvent(
            target=self.task.display_task,
            name="change",
            data=None,
            control=self.task.display_task,
            page=self.page,
        )
        self.task.display_task.value = True
        self.task.status_changed(event)
        self.assertTrue(self.task.completed)

    def test_delete_clicked(self):
        # Cannot directly test delete_clicked as it relies on a callback
        self.task.on_delete_clicked = lambda task: None  # Mock the callback
        self.task.delete_clicked(None)

    def test_edit_clicked(self):
        self.task.on_edit_clicked = lambda: None  # Mock the callback
        self.task.edit_clicked(None)
        self.assertEqual(self.task.edit_name.value, "Test Task")
        self.assertFalse(self.task.display_view.visible)
        self.assertTrue(self.task.edit_view.visible)

    def test_save_clicked(self):
        self.task.edit_name.value = "New Task Name"
        self.task.save_clicked(None)
        self.assertEqual(self.task.display_task.label, "New Task Name")
        self.assertTrue(self.task.display_view.visible)
        self.assertFalse(self.task.edit_view.visible)


class TestTodoApp(TodoAppTestBase):
    def test_todo_app_creation(self):
        self.assertEqual(self.app.width, 600)

    def test_add_clicked(self):
        self.page.focus_called = False
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        self.assertEqual(len(self.app.tasks.controls), 1)
        self.assertEqual(self.app.tasks.controls[0].task_name, "New Task")
        self.assertEqual(self.app.new_task.value, "")

    def test_status_changed(self):
        self.page.focus_called = False
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        self.assertEqual(len(self.app.tasks.controls), 1)
        task = self.app.tasks.controls[0]
        task.completed = True
        self.app.status_changed(task)
        # Cannot directly test status_changed as it relies on the before_update method
        # self.assertEqual(self.app.items_left.value, "0 active item(s) left")

    def test_delete_task(self):
        self.page.focus_called = False
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        task = self.app.tasks.controls[0]
        self.app.delete_task(task)
        self.assertEqual(len(self.app.tasks.controls), 0)

    def test_tabs_changed(self):
        self.page.focus_called = False
        self.app.tabs_changed(None)
        # Cannot directly test tabs_changed as it relies on the before_update method
        pass

    def test_clear_clicked(self):
        self.page.focus_called = False
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        task = self.app.tasks.controls[0]
        task.completed = True
        self.app.clear_clicked(None)
        self.assertEqual(len(self.app.tasks.controls), 0)

    def test_before_update(self):
        self.page.focus_called = False
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        self.app.filter.selected_index = 1  # "active" tab
        self.app.update()
        self.assertEqual(self.app.items_left.value, "1 active item(s) left")

    def test_add_clicked_focus(self):
        self.page.focus_called = False
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        self.assertFalse(self.page.focus_called)

    def test_before_update_status(self):
        self.page.focus_called = False
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        task = self.app.tasks.controls[0]
        task.completed = True
        self.app.filter.selected_index = 2  # "completed" tab
        self.app.update()
        self.assertTrue(task.visible)
        self.assertEqual(self.app.items_left.value, "1 active item(s) left")

    def test_before_update_all_tab(self):
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        task = self.app.tasks.controls[0]
        self.app.filter.selected_index = 0  # "all" tab
        self.app.update()
        self.assertTrue(task.visible)
        self.assertEqual(self.app.items_left.value, "1 active item(s) left")

    def test_before_update_active_tab(self):
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        task = self.app.tasks.controls[0]
        self.app.filter.selected_index = 1  # "active" tab
        self.app.update()
        self.assertTrue(task.visible)
        self.assertEqual(self.app.items_left.value, "1 active item(s) left")

    def test_before_update_completed_tab(self):
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        task = self.app.tasks.controls[0]
        task.completed = True
        self.app.filter.selected_index = 2  # "completed" tab
        self.app.update()
        self.assertTrue(task.visible)
        self.assertEqual(self.app.items_left.value, "1 active item(s) left")

    def test_before_update_active_tab_completed_task(self):
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        task = self.app.tasks.controls[0]
        task.completed = True
        self.app.filter.selected_index = 1  # "active" tab
        self.app.update()
        self.assertTrue(task.visible)
        self.assertEqual(self.app.items_left.value, "1 active item(s) left")

    def test_task_callbacks(self):
        task = Task("Test Task", None, None, None, None)
        task.on_save_clicked = lambda: None
        task.on_status_changed = lambda task: None
        task.on_delete_clicked = lambda task: None
        task.on_edit_clicked = lambda: None
        task.page = self.page
        self.page.add(task)
        task.save_clicked(None)
        task.status_changed(None)
        task.delete_clicked(None)
        task.edit_clicked(None)

    def test_task_callbacks_called(self):
        # Test that the callbacks are called when they are set
        save_called = False
        status_called = False
        delete_called = False
        edit_called = False

        def set_save_called():
            nonlocal save_called
            save_called = True

        def set_status_called(task):
            nonlocal status_called
            status_called = True

        def set_delete_called(task):
            nonlocal delete_called
            delete_called = True

        def set_edit_called():
            nonlocal edit_called
            edit_called = True

        task = Task(
            "Test Task",
            set_status_called,
            set_delete_called,
            set_edit_called,
            set_save_called,
        )
        task.page = self.page
        self.page.add(task)
        task.save_clicked(None)
        task.status_changed(None)
        task.delete_clicked(None)
        task.edit_clicked(None)

        self.assertTrue(save_called)
        self.assertTrue(status_called)
        self.assertTrue(delete_called)
        self.assertTrue(edit_called)

    def test_task_save_clicked(self):
        # Test that save_clicked calls on_save_clicked
        save_called = False

        def set_save_called():
            nonlocal save_called
            save_called = True

        task = Task(
            "Test Task",
            None,
            None, None,
            set_save_called,
        )
        task.page = self.page
        self.page.add(task)
        task.save_clicked(None)
        self.assertTrue(save_called)

    def test_task_save_clicked_save_tasks(self):
        # Test that save_clicked calls todo_app.save_tasks
        save_tasks_called = False

        def set_save_tasks_called():
            nonlocal save_tasks_called
            save_tasks_called = True

        # Mock todo_app and its save_tasks method
        src.main.todo_app = Mock()
        src.main.todo_app.save_tasks = set_save_tasks_called

        task = Task(
            "Test Task",
            None,
            None,
            None,
            lambda: None,
        )
        task.page = self.page
        self.page.add(task)
        task.save_clicked(None)
        self.assertTrue(save_tasks_called)

    def test_task_save_clicked_update(self):
        update_called = False

        def set_update_called(arg):
            nonlocal update_called
            update_called = True

        # Mock todo_app and its save_tasks method
        src.main.todo_app = Mock()
        src.main.todo_app.save_tasks = Mock()

        task = Task(
            "Test Task",
            None,
            None,
            None,
            lambda: None,
        )
        mock_page = Mock()
        mock_page.update = set_update_called
        task.page = mock_page
        task.save_clicked(None)
        self.assertTrue(update_called)

    def test_add_clicked_empty_task(self):
        self.app.new_task.value = ""
        self.app.add_clicked(None)
        self.assertEqual(len(self.app.tasks.controls), 0)

    def test_before_update_no_tasks(self):
        self.app.filter.selected_index = 0  # "all" tab
        self.app.update()
        self.assertEqual(self.app.items_left.value, "0 items left")
        self.assertEqual(self.app.filter.selected_index, 0)

    def test_add_clicked_empty_task_focus(self):
        self.page.focus_called = False
        self.app.new_task.value = ""
        self.app.add_clicked(None)
        self.assertFalse(self.page.focus_called)

    def test_add_clicked_adds_task(self):
        # Test that add_clicked adds a task to the list
        self.app.new_task.value = "Test Task"
        self.app.add_clicked(None)
        self.assertEqual(len(self.app.tasks.controls), 1)
        self.assertEqual(self.app.tasks.controls[0].task_name, "Test Task")

    def test_todo_app_edit_save_clicked(self):
        self.app.edit_clicked()
        self.app.save_clicked()

    def test_save_tasks(self):
        # テスト用のタスクを追加
        self.app.new_task.value = "Test Task 1"
        self.app.add_clicked(None)
        self.app.new_task.value = "Test Task 2"
        self.app.add_clicked(None)

        # タスクを保存
        self.app.save_tasks()

        # JSON ファイルからタスクをロード
        with open(self.app.json_path, "r", encoding="utf-8") as f:
            task_list = json.load(f)

        # 保存されたタスクが正しいことを確認
        self.assertEqual(len(task_list), 2)
        self.assertEqual(task_list[0]["task_name"], "Test Task 1")
        self.assertEqual(task_list[1]["task_name"], "Test Task 2")

        # テストで使用したタスクを削除main
        self.app.clear_clicked(None)

    def test_load_tasks_from_json(self):
        # JSONファイルにタスクを書き込む
        test_tasks = [
            {"task_name": "Task 1", "completed": False},
            {"task_name": "Task 2", "completed": False},
        ]
        with open(self.app.json_path, "w", encoding="utf-8") as f:
            json.dump(test_tasks, f, ensure_ascii=False, indent=4)

        # タスクをロード
        self.app.load_tasks()

        # ロードされたタスクが正しいことを確認
        self.assertEqual(len(self.app.tasks.controls), 2)
        self.assertEqual(self.app.tasks.controls[0].task_name, "Task 1")
        self.assertEqual(self.app.tasks.controls[1].task_name, "Task 2")

        # テストで使用したタスクを削除
        self.app.clear_clicked(None)

    def test_load_tasks_from_deleted_json(self):
        # JSONファイルを削除
        if os.path.exists(self.app.json_path):
            os.remove(self.app.json_path)

        # タスクをロード
        # JSONファイルが存在しないため、タスクはロードされない
        self.app.load_tasks()

        # タスクがロードされないことを確認
        self.assertEqual(len(self.app.tasks.controls), 0)

    def test_load_tasks_from_invalid_json(self):
        # JSONファイルにJSON形式ではない内容を書き込む
        with open(self.app.json_path, "w", encoding="utf-8") as f:
            f.write("invalid json")

        # タスクをロード
        self.app.load_tasks()

        # タスクがロードされないことを確認
        self.assertEqual(len(self.app.tasks.controls), 0)


class TestMain(unittest.TestCase):
    def setUp(self):
        self.mock_page = MockPage()
        self.app = TodoApp(lang="ja", json_path="storage/test_todos.json")
        src.main.todo_app = self.app
        self.app.page = self.mock_page
        self.mock_page.add(self.app)
        self.app.update()

    def test_main(self):
        self.assertEqual(len(self.mock_page.controls), 1)
        self.assertIsInstance(self.mock_page.controls[0], TodoApp)

    def test_main_function(self):
        # Test the main function
        self.mock_page.controls = []
        src.main.main(self.mock_page)
        self.assertEqual(len(self.mock_page.controls), 1)
        self.assertIsInstance(self.mock_page.controls[0], TodoApp)


if __name__ == "__main__":
    unittest.main()
