import flet
from flet import IconButton, Page, Row, TextField, Icons

def main(page: Page):
    page.title = "Flet Counter Example"
    page.vertical_alignment = "center"

    txt_number = TextField(value="0", text_align="right", width=100)

    def minus_click(e):
        txt_number.value = str(int(txt_number.value) - 1)
        page.update()

    def plus_click(e):
        txt_number.value = str(int(txt_number.value) + 1)
        page.update()

    page.add(
        Row(
            [
                IconButton(Icons.REMOVE, on_click=minus_click),
                txt_number,
                IconButton(Icons.ADD, on_click=plus_click),
            ],
            alignment="center",
        )
    )

flet.app(target=main)
