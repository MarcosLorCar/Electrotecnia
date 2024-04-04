import math
from tkinter import *
from tkinter import ttk
from typing import Optional

ELEMENT_WIDTH: int = 100
ELEMENT_PADDING: int = 10
VIEW_MODE = 'VIEW'  # EDIT or VIEW


class Complex:
    def __init__(self, expr: str = None, freq: float = 50):
        self.real: float = 0.0
        self.complex: float = 0.0
        if expr[0] in ('(', '['):
            # Compound
            depth: int = 0
            value: str = ""
            values: list[Complex] = []
            for c in expr[1:-1]:
                if c == '+' and depth == 0:
                    values.append(Complex(value, freq))
                    value = ""
                elif c in ('(', '['):
                    depth += 1
                    value += c
                elif c in (')', ']'):
                    depth -= 1
                    value += c
                else:
                    value += c
            values.append(Complex(value, freq))

            # Add up values
            if expr[0] == '(':
                for other in values:
                    self.real += other.real
                    self.complex += other.complex
            elif expr[0] == '[':
                adm_real: float = 0
                adm_complex: float = 0
                for other in values:
                    new_mag = 1 / math.sqrt(other.real ** 2 + other.complex ** 2)
                    new_arg = -math.atan2(other.complex, other.real)
                    adm_real += new_mag * math.cos(new_arg)
                    adm_complex += new_mag * math.sin(new_arg)
                imp_mag = 1 / math.sqrt(adm_real ** 2 + adm_complex ** 2)
                imp_arg = -math.atan2(adm_complex, adm_real)
                self.real += imp_mag * math.cos(imp_arg)
                self.complex += imp_mag * math.sin(imp_arg)
        else:
            # Value
            unit = expr[-1].lower()
            value: float = eval(expr[:-1])
            if unit == 'o':
                self.real += value
            elif unit == 'h':
                self.complex += 2 * math.pi * freq * value
            elif unit == 'f':
                self.complex += -1 / (2 * math.pi * freq * value)


class Element:
    def __init__(self, parent, element_type: str = None):
        self.parent: Element = parent
        self.type: str = element_type
        self.value: Optional[str] = None
        self.values: list[Element] = []

    def calc_width(self) -> float:
        if self.value is not None:
            return ELEMENT_WIDTH + ELEMENT_PADDING * 2

        if self.type == 'chain':
            total_width = 0.0
            for e in self.values:
                total_width += e.calc_width()
            return (total_width + ELEMENT_WIDTH / 2 + ELEMENT_PADDING * 2) if (VIEW_MODE == 'EDIT') else total_width

        # if branch
        max_width = 0.0
        for e in self.values:
            new_width = e.calc_width()
            if new_width > max_width:
                max_width = new_width
        return max_width

    def calc_width_count(self) -> float:
        if self.value is not None:
            return 1

        if self.type == 'chain':
            total_width_count = 0
            for e in self.values:
                total_width_count += e.calc_width_count()
            return total_width_count

        # if branch
        max_width_count = 0
        for e in self.values:
            new_width_count = e.calc_width_count()
            if new_width_count > max_width_count:
                max_width_count = new_width_count
        return max_width_count

    def calc_height(self) -> float:
        if self.value is not None:
            return ELEMENT_WIDTH / 2 + ELEMENT_PADDING * 2

        if self.type == 'branch':
            total_height = 0.0
            for e in self.values:
                total_height += e.calc_height()
            return (total_height + ELEMENT_WIDTH / 2 + ELEMENT_PADDING * 2) if VIEW_MODE == 'EDIT' else total_height

        # if branch
        max_height = 0.0
        for e in self.values:
            new_height = e.calc_height()
            if new_height > max_height:
                max_height = new_height
        return max_height

    def calc_height_count(self) -> float:
        if self.value is not None:
            return 1

        if self.type == 'branch':
            total_height_count = 0
            for e in self.values:
                total_height_count += e.calc_height_count()
            return total_height_count

        # if branch
        max_height_count = 0
        for e in self.values:
            new_height_count = e.calc_height_count()
            if new_height_count > max_height_count:
                max_height_count = new_height_count
        return max_height_count

    def add_value(self, value: str) -> 'Element':
        new_element: Element = Element(self)
        new_element.type = 'value'
        new_element.value = value
        self.values.append(new_element)
        update_canvas()
        return self

    def add_branch(self) -> 'Element':
        new_element: Element = Element(self)
        new_element.type = 'branch'
        self.values.append(new_element)
        update_canvas()
        return new_element

    def add_chain(self) -> 'Element':
        new_element: Element = Element(self)
        new_element.type = 'chain'
        self.values.append(new_element)
        update_canvas()
        return new_element

    def to_string(self) -> str:
        if self.value is not None:
            element_type = self.value[-1]
            element_value = self.value[0:-2]
            if element_type == 'Ω':
                return element_value + 'o'
            elif element_type == 'H':
                return element_value + 'h'
            elif element_type == 'F':
                return element_value + 'f'

        if self.type == 'branch':
            return "[" + "+".join([value.to_string() for value in self.values]) + "]"
        elif self.type == 'chain':
            return "(" + "+".join([value.to_string() for value in self.values]) + ")"


def render(element: Element, x, y) -> None:
    width = element.calc_width()
    height = element.calc_height()
    if element.type == 'value':
        circuitCanvas.create_line(x - width / 2, y, x + width / 2, y)
        circuitCanvas.create_rectangle(
            x - (width / 2 - ELEMENT_PADDING),
            y - (height / 2 - ELEMENT_PADDING),
            x + (width / 2 - ELEMENT_PADDING),
            y + (height / 2 - ELEMENT_PADDING),
            fill='white'
        )
        if VIEW_MODE == 'EDIT':
            circuitCanvas.create_window(
                x,
                y,
                width=ELEMENT_WIDTH,
                height=ELEMENT_WIDTH / 2,
                window=Button(mainframe, text=element.value, command=lambda: change_menu(element), relief='raised')
            )
        else:
            circuitCanvas.create_text(x, y, text=element.value)
    elif element.type == 'chain':
        acc_w = 0.0
        if element.values:
            for child in element.values:
                acc_w += child.calc_width() / 2
                render(child, x - width / 2 + acc_w, y)
                acc_w += child.calc_width() / 2
        # button
        if VIEW_MODE == 'EDIT':
            circuitCanvas.create_line(
                x - width / 2 + acc_w,
                y,
                x - width / 2 + acc_w + ELEMENT_PADDING * 2 + ELEMENT_WIDTH / 2,
                y
            )
            circuitCanvas.create_window(
                x - width / 2 + acc_w + ELEMENT_PADDING + ELEMENT_WIDTH / 4,
                y,
                width=ELEMENT_WIDTH / 2,
                height=ELEMENT_WIDTH / 2,
                window=ttk.Button(circuitCanvas, text='+', command=lambda: add_menu('chain', element)),
            )
    elif element.type == 'branch':
        acc_h = 0.0
        for child in element.values:
            acc_h += child.calc_height() / 2
            circuitCanvas.create_line(
                x - width / 2,
                y - height / 2 + acc_h,
                x - child.calc_width() / 2,
                y - height / 2 + acc_h,
            )
            circuitCanvas.create_line(
                x + child.calc_width() / 2,
                y - height / 2 + acc_h,
                x + width / 2,
                y - height / 2 + acc_h,
            )
            render(child, x, y - height / 2 + acc_h)
            acc_h += child.calc_height() / 2
        if element.values:
            acc_h -= element.values[-1].calc_height() / 2
            circuitCanvas.create_line(
                x - width / 2,
                y - height / 2 + element.values[0].calc_height() / 2,
                x - width / 2,
                y - height / 2 + acc_h,
            )
            circuitCanvas.create_line(
                x + width / 2,
                y - height / 2 + element.values[0].calc_height() / 2,
                x + width / 2,
                y - height / 2 + acc_h,
            )
            acc_h += element.values[-1].calc_height() / 2
        if VIEW_MODE == 'EDIT':
            if element.values:
                circuitCanvas.create_line(
                    x - width / 2,
                    y - height / 2 + element.values[0].calc_height() / 2,
                    x - width / 2,
                    y - height / 2 + acc_h + ELEMENT_PADDING + ELEMENT_WIDTH / 4,
                )
                circuitCanvas.create_line(
                    x + width / 2,
                    y - height / 2 + element.values[0].calc_height() / 2,
                    x + width / 2,
                    y - height / 2 + acc_h + ELEMENT_PADDING + ELEMENT_WIDTH / 4,
                )
                circuitCanvas.create_line(
                    x - width / 2,
                    y + height / 2 - ELEMENT_PADDING - ELEMENT_WIDTH / 4,
                    x + width / 2,
                    y + height / 2 - ELEMENT_PADDING - ELEMENT_WIDTH / 4,
                )
            circuitCanvas.create_window(
                x,
                y - height / 2 + acc_h + ELEMENT_PADDING + ELEMENT_WIDTH / 4,
                width=ELEMENT_WIDTH / 2,
                height=ELEMENT_WIDTH / 2,
                window=ttk.Button(circuitCanvas, text='+', command=lambda: add_menu('branch', element)),
            )


def change_menu(element: Element):
    popup_window = Toplevel(root, padx=10, pady=10)

    def change_value():
        try:
            element.value = (str(float(entry_value.get())) + " " + type_value.get())
            update_canvas()
            popup_window.destroy()
        except ValueError:
            pass

    def remove_value():
        element.parent.values.remove(element)
        update_canvas()
        popup_window.destroy()

    # widgets
    button_value = ttk.Button(popup_window, text='Change', command=change_value)
    entry_value = ttk.Entry(popup_window, width=10, justify='center')
    entry_value.insert(0, "100.0")
    type_value = ttk.Combobox(popup_window, values=('Ω', 'H', 'F'), width=2)
    type_value.insert(0, 'Ω')

    remove_button = ttk.Button(popup_window, text='Remove', command=remove_value)

    # layout
    remove_button.pack(ipady=10, pady=10)
    entry_value.pack(side='left', fill='both', pady=10)
    type_value.pack(side='left', fill='both', pady=10)
    button_value.pack(side='top', fill='both', ipady=10, pady=10)

    center_window(popup_window)


def add_menu(disable: str, parent: Element):
    popup_window = Toplevel(root)

    # button actions
    def add_branch():
        parent.add_branch().add_value('100.0 Ω')
        popup_window.destroy()

    def add_chain():
        parent.add_chain().add_value('100.0 Ω')
        popup_window.destroy()

    def add_value():
        try:
            parent.add_value(str(float(entry_value.get())) + " " + type_value.get())
            popup_window.destroy()
        except ValueError:
            pass

    # widgets
    composite_frame = ttk.Frame(popup_window, padding='10 10 10 10')
    value_frame = ttk.Frame(popup_window, padding='10 10 10 10')

    button_branch = ttk.Button(composite_frame, text="Branch", command=add_branch)
    button_chain = ttk.Button(composite_frame, text="Chain", command=add_chain)

    button_value = ttk.Button(value_frame, text='Value', command=add_value)
    entry_value = ttk.Entry(value_frame, width=10, justify='center')
    entry_value.insert(0, "100.0")
    type_value = ttk.Combobox(value_frame, values=('Ω', 'H', 'F'), width=2)
    type_value.insert(0, 'Ω')

    # layout
    composite_frame.grid(column=0, row=0)
    value_frame.grid(column=0, row=1)
    entry_value.pack(side='left', fill='both')
    type_value.pack(side='left', fill='both')

    if disable != "branch":
        button_branch.pack(side='left', fill='both', ipady=10)
    if disable != "chain":
        button_chain.pack(side='left', fill='both', ipady=10)
    button_value.pack(fill='both', ipady=10)

    center_window(popup_window)


def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))


def update_canvas():
    global ELEMENT_WIDTH
    width = circuitCanvas.winfo_width()
    height = circuitCanvas.winfo_height()
    element_width_count = circuit.calc_width_count()
    element_height_count = circuit.calc_height_count()
    if VIEW_MODE == 'EDIT':
        ELEMENT_WIDTH = min(100.0, width / (element_width_count + 1) - ELEMENT_PADDING * 2)
        element_height = min(50.0, height / (element_height_count + 1) - ELEMENT_PADDING * 2)
    else:
        ELEMENT_WIDTH = min(100.0, width / element_width_count - ELEMENT_PADDING * 2)
        element_height = min(50.0, height / element_height_count - ELEMENT_PADDING * 2)
    if circuit.calc_height() > height:
        ELEMENT_WIDTH = element_height * 2
    circuitCanvas.delete('all')
    render(circuit, width / 2, height / 2)


def calc_imp():
    string = circuit.to_string()
    imp_total = Complex(string, float(freq_entry.get()))
    popup_window = Toplevel(root)

    label_real = ttk.Label(popup_window, text=imp_total.real, padding='10 10 10 10', justify='center')
    label_complex = ttk.Label(popup_window, text=str(imp_total.complex)+'j', padding='10 10 10 10', justify='center')
    label_polar = ttk.Label(popup_window, text=str(math.sqrt(imp_total.real**2+imp_total.complex**2))+" @ "+str(math.atan2(imp_total.complex, imp_total.real))+"º")
    ok_button = ttk.Button(popup_window, text='Ok', padding='10 10 10 10', command=lambda: popup_window.destroy())

    label_real.pack()
    label_complex.pack()
    label_polar.pack()
    ok_button.pack()

    center_window(popup_window)

if __name__ == '__main__':
    circuit: Element = Element(None, 'chain')

    # boilerplate
    root = Tk()
    root.title("Electrotecnia")
    root.state('zoomed')

    mainframe = ttk.Frame(root)
    mainframe.pack(expand=True, fill='both')


    def change_mode(mode: str):
        global VIEW_MODE
        if mode == 'edit':
            VIEW_MODE = 'EDIT'
            view_button['state'] = 'default'
            edit_button['state'] = 'disabled'
        elif mode == 'view':
            VIEW_MODE = 'VIEW'
            edit_button['state'] = 'default'
            view_button['state'] = 'disabled'
        update_canvas()


    def clear_circuit():
        global circuit
        circuit = Element(None, 'chain')
        circuit.add_value('100.0 Ω')
        update_canvas()


    # widgets
    circuitCanvas = Canvas(mainframe)
    edit_button = ttk.Button(mainframe, text='Edit', command=lambda: change_mode('edit'))
    clear_button = ttk.Button(mainframe, text='Clear', command=lambda: clear_circuit())
    view_button = ttk.Button(mainframe, text='View', command=lambda: change_mode('view'), state='disabled')
    calc_button = ttk.Button(mainframe, text='Calc', command=lambda: calc_imp())
    freq_frame = ttk.Frame(mainframe)
    freq_entry = ttk.Entry(freq_frame)
    freq_entry.insert(0, "50")

    # layout
    circuitCanvas.pack(side='left', expand=True, fill='both')
    edit_button.pack(fill='both', ipady=10)
    view_button.pack(fill='both', ipady=10)
    clear_button.pack(fill='both', ipady=10)
    calc_button.pack(fill='both', ipady=10)
    freq_frame.pack()
    ttk.Label(freq_frame, text='Hz').pack(side='right')
    freq_entry.pack(side='right', fill='both')
    

    circuitCanvas.bind("<Configure>",
                       lambda x: update_canvas())

    circuit.add_value('100.0 Ω')

    root.mainloop()
