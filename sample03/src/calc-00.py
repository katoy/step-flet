import flet as ft

def main(page: ft.Page):
    page.title = "Calc App"
    # ── 状態変数 ─────────────────────────────────────────
    page.operand1 = 0.0
    page.operator = "+"
    page.new_operand = True

    # ── 画面に置くテキスト ─────────────────────────────────
    result = ft.Text(value="0", size=30, color=ft.Colors.WHITE)

    # ── ヘルパー関数 ───────────────────────────────────────
    def format_number(n):
        return int(n) if n == int(n) else n

    def calculate(op1, op2, op):
        if op == "+":
            return format_number(op1 + op2)
        if op == "-":
            return format_number(op1 - op2)
        if op == "*":
            return format_number(op1 * op2)
        if op == "/":
            return "Error" if op2 == 0 else format_number(op1 / op2)

    # ── ボタン押下時イベント ─────────────────────────────────
    def on_click(e: ft.ControlEvent):
        data = e.control.data

        # AC or Error → リセット
        if data == "AC" or result.value == "Error":
            page.operand1 = 0.0
            page.operator = "+"
            page.new_operand = True
            result.value = "0"

        # 数字・ドット
        elif data in "0123456789.":
            if result.value == "0" or page.new_operand:
                result.value = data
            else:
                result.value += data
            page.new_operand = False

        # 演算子
        elif data in "+-*/":
            try:
                curr = float(result.value)
            except:
                curr = 0.0
            res = calculate(page.operand1, curr, page.operator)
            result.value = str(res)
            page.operand1 = 0.0 if res == "Error" else float(res)
            page.operator = data
            page.new_operand = True

        # イコール
        elif data == "=":
            try:
                curr = float(result.value)
            except:
                curr = 0.0
            res = calculate(page.operand1, curr, page.operator)
            result.value = str(res)
            page.operand1 = 0.0
            page.operator = "+"
            page.new_operand = True

        # パーセント
        elif data == "%":
            try:
                curr = float(result.value)
                result.value = str(format_number(curr / 100))
            except:
                result.value = "Error"
            page.operand1 = 0.0
            page.operator = "+"
            page.new_operand = True

        # 符号反転
        elif data == "+/-":
            try:
                curr = float(result.value)
                result.value = str(-curr)
            except:
                pass

        result.update()

    # ── ボタン生成ユーティリティ ───────────────────────────
    def make_btn(txt, bg, fg, exp=1):
        return ft.ElevatedButton(
            text=txt,
            bgcolor=bg,
            color=fg,
            expand=exp,
            data=txt,
            on_click=on_click,
        )

    # ── レイアウト ─────────────────────────────────────────
    rows = [
        [("AC","BLUE_GREY_100"),("+/-","BLUE_GREY_100"),("%","BLUE_GREY_100"),("/","ORANGE")],
        [("7","WHITE24"),("8","WHITE24"),("9","WHITE24"),("*","ORANGE")],
        [("4","WHITE24"),("5","WHITE24"),("6","WHITE24"),("-","ORANGE")],
        [("1","WHITE24"),("2","WHITE24"),("3","WHITE24"),("+","ORANGE")],
        [("0","WHITE24",2),(".","WHITE24",1),("=","ORANGE",1)],
    ]

    controls = [ft.Row(controls=[result], alignment="end")]
    for row in rows:
        btns = []
        for spec in row:
            txt = spec[0]
            clr = getattr(ft.Colors, spec[1])
            exp = spec[2] if len(spec) == 3 else 1
            fg = ft.Colors.WHITE if txt not in ("AC","+/-","%") else ft.Colors.BLACK
            btns.append(make_btn(txt, clr, fg, exp))
        controls.append(ft.Row(controls=btns))

    container = ft.Container(
        width=300,
        bgcolor=ft.Colors.BLACK,
        border_radius=ft.border_radius.all(20),
        padding=10,
        content=ft.Column(controls=controls),
    )

    page.add(container)


if __name__ == "__main__":
    ft.app(target=main)
