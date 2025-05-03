import flet
from flet import IconButton, Page, Row, TextField, icons, ElevatedButton

def main(page: Page):
    page.title = "Flet Calculator"
    page.vertical_alignment = "center"

    # Text field to display the input and result
    txt_result = TextField(value="0", text_align="right", width=300)

    # Store the expression
    expression = ""

    # Function to handle button clicks
    def button_clicked(e):
        nonlocal expression
        button_text = e.control.text
        if button_text == "=":
            try:
                result = str(eval(expression))
                txt_result.value = result
                expression = result
            except Exception as e:
                txt_result.value = "Error"
                expression = ""
        elif button_text == "C":
            expression = ""
            txt_result.value = "0"
        else:
            expression += button_text
            txt_result.value = expression
        page.update()

    # Define buttons
    buttons = [
        "7", "8", "9", "/",
        "4", "5", "6", "*",
        "1", "2", "3", "-",
        "0", ".", "=", "+",
        "C"
    ]

    # Create rows of buttons
    rows = []
    for i in range(0, len(buttons), 4):
        row_buttons = buttons[i:i+4]
        row = Row(alignment="center")
        for button_text in row_buttons:
             row.controls.append(
                ElevatedButton(
                    text=button_text,
                    on_click=button_clicked,
                )
            )
        rows.append(row)

    # Add controls to the page
    page.add(
        txt_result,
        *rows,
    )

flet.app(target=main)
