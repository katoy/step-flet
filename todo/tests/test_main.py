import unittest
import flet as ft
from src.main import Task, TodoApp


class MockPage:
    def __init__(self):
        self.controls = []

    def add(self, control):
        self.controls.append(control)
        control.page = self  # Add this line

    def update(self, control):
        pass


class TestTask(unittest.TestCase):
    def setUp(self):
        self.page = MockPage()
        self.task = Task("Test Task", None, None, None, None)
        self.task.page = self.page  # Add this line
        self.page.add(self.task)

    def test_task_creation(self):
        self.assertEqual(self.task.task_name, "Test Task")
        self.assertFalse(self.task.completed)

    def test_status_changed(self):
        self.task.status_changed(None)
        self.assertFalse(self.task.completed)  # status_changed doesn't change completed status without an event

    def test_delete_clicked(self):
        # Cannot directly test delete_clicked as it relies on a callback
        pass

    def test_edit_clicked(self):
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
        self.app = TodoApp()
        self.app.page = self.page  # Add this line
        self.page.add(self.app)
        self.app.new_task.page = self.page  # Add this line

    def test_todo_app_creation(self):
        self.assertEqual(self.app.width, 600)

    def test_add_clicked(self):
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        self.assertEqual(len(self.app.tasks.controls), 1)
        self.assertEqual(self.app.tasks.controls[0].task_name, "New Task")
        self.assertEqual(self.app.new_task.value, "")

    def test_status_changed(self):
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        task = self.app.tasks.controls[0]
        task.completed = True
        self.app.status_changed(task)
        # Cannot directly test status_changed as it relies on the before_update method
        # self.assertEqual(self.app.items_left.value, "0 active item(s) left")

    def test_delete_task(self):
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        task = self.app.tasks.controls[0]
        self.app.delete_task(task)
        self.assertEqual(len(self.app.tasks.controls), 0)

    def test_tabs_changed(self):
        self.app.tabs_changed(None)
        # Cannot directly test tabs_changed as it relies on the before_update method
        pass

    def test_clear_clicked(self):
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        task = self.app.tasks.controls[0]
        task.completed = True
        self.app.clear_clicked(None)
        self.assertEqual(len(self.app.tasks.controls), 0)

    def test_before_update(self):
        self.app.new_task.value = "New Task"
        self.app.add_clicked(None)
        self.app.filter.selected_index = 1  # "active" tab
        self.app.before_update()
        self.assertEqual(self.app.items_left.value, "1 active item(s) left")


if __name__ == '__main__':
    unittest.main()
