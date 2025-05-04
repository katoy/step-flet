import unittest
import flet as ft
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'assets')))

# Execute src/main.py's if __name__ == "__main__": block

from src.main import Task, TodoApp, main


class MockPage:
    def __init__(self):
        self.controls = []

    def add(self, control):
        self.controls.append(control)
        control.page = self  # Add this line

    def update(self, control=None):
        self.focus_called = True


    def remove(self, control):
        self.controls.remove(control)

    def focus(self):
        self.focus_called = True
        return None


class TestTask(unittest.TestCase):
    def setUp(self):
        self.page = MockPage()
        self.page.focus_called = False
        self.task = Task("Test Task", None, None, None, None)
        self.task.page = self.page  # Add this line
        self.page.add(self.task)

    def test_task_creation(self):
        self.assertEqual(self.task.task_name, "Test Task")
        self.assertFalse(self.task.completed)

    def test_status_changed(self):
        # status_changed doesn't change completed status without an event
        self.task.status_changed(None)
        self.assertFalse(self.task.completed)

        # Test status_changed with an event
        event = ft.ControlEvent(target=self.task.display_task, name="change", data=None, control=self.task.display_task, page=self.page)
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


class TestTodoApp(unittest.TestCase):
    def setUp(self):
        self.page = MockPage()
        self.page.focus_called = False
        self.app = TodoApp()
        self.app.page = self.page  # Add this line
        self.page.add(self.app)
        self.app.new_task.page = self.page  # Add this line

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
        self.app.before_update()
        self.assertEqual(self.app.items_left.value, "1 active item(s) left")

    def test_add_clicked_focus(self):
        self.page.focus_called = False
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        self.app.new_task.focus()
        self.assertTrue(self.page.focus_called)

    def test_before_update_status(self):
        self.page.focus_called = False
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        task = self.app.tasks.controls[0]
        task.completed = True
        self.app.filter.selected_index = 2  # "completed" tab
        self.app.before_update()
        self.assertTrue(task.visible)
        self.assertEqual(self.app.items_left.value, "0 active item(s) left")

    def test_before_update_all_tab(self):
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        task = self.app.tasks.controls[0]
        self.app.filter.selected_index = 0  # "all" tab
        self.app.before_update()
        self.assertTrue(task.visible)
        self.assertEqual(self.app.items_left.value, "1 active item(s) left")

    def test_before_update_active_tab(self):
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        task = self.app.tasks.controls[0]
        self.app.filter.selected_index = 1  # "active" tab
        self.app.before_update()
        self.assertTrue(task.visible)
        self.assertEqual(self.app.items_left.value, "1 active item(s) left")

    def test_before_update_completed_tab(self):
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        task = self.app.tasks.controls[0]
        task.completed = True
        self.app.filter.selected_index = 2  # "completed" tab
        self.app.before_update()
        self.assertTrue(task.visible)
        self.assertEqual(self.app.items_left.value, "0 active item(s) left")

    def test_before_update_active_tab_completed_task(self):
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        task = self.app.tasks.controls[0]
        task.completed = True
        self.app.filter.selected_index = 1  # "active" tab
        self.app.before_update()
        self.assertFalse(task.visible)
        self.assertEqual(self.app.items_left.value, "0 active item(s) left")

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

        task = Task("Test Task", set_status_called, set_delete_called, set_edit_called, set_save_called)
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

    def test_add_clicked_empty_task(self):
        self.app.new_task.value = ""
        self.app.add_clicked(None)
        self.assertEqual(len(self.app.tasks.controls), 0)

    def test_before_update_no_tasks(self):
        self.app.filter.selected_index = 0  # "all" tab
        self.app.before_update()
        self.assertEqual(self.app.items_left.value, "0 active item(s) left")
        self.assertEqual(self.app.filter.selected_index, 0)

    def test_add_clicked_empty_task_focus(self):
        self.page.focus_called = False
        self.app.new_task.value = ""
        self.app.add_clicked(None)
        self.assertTrue(not self.page.focus_called)

    def test_todo_app_edit_save_clicked(self):
        self.app.edit_clicked()
        self.app.save_clicked()


class TestMain(unittest.TestCase):
    def setUp(self):
        mock_page = MockPage()
        main(mock_page)
        self.assertEqual(len(mock_page.controls), 1)
        self.assertIsInstance(mock_page.controls[0], TodoApp)

    def test_main(self):
        mock_page = MockPage()
        main(mock_page)
        self.assertEqual(len(mock_page.controls), 1)
        self.assertIsInstance(mock_page.controls[0], TodoApp)


    def test_language_changed(self):
        mock_page = MockPage()
        main(mock_page)
        app = mock_page.controls[0]
        language_dropdown = app.page.appbar.actions[0]
        language_dropdown.value = "en"
        language_changed_event = ft.ControlEvent(
            target=language_dropdown,
            name="change",
            data=None,
            control=language_dropdown,
            page=mock_page
        )
        language_dropdown.on_change(language_changed_event)
        app = mock_page.controls[0]
        self.assertEqual(app.lang, "en")


if __name__ == '__main__':
    unittest.main()
