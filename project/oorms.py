"""
Provides the user interface for the Object-oriented Restaurant Management
application (OORMS). This includes the server's view and a window simulating
the tape of a bill printer.
Submitting lab group: [your names here]
Submission date: [date here]
Original code by EEE320 instructors.
"""

import math
import tkinter as tk
from abc import ABC

from constants import *
from controller import RestaurantController
from model import Restaurant


class RestaurantView(tk.Frame, ABC):

    def __init__(self, master, restaurant, window_width, window_height, controller_class):
        super().__init__(master)
        self.grid()
        self.canvas = tk.Canvas(self, width=window_width, height=window_height,
                                borderwidth=0, highlightthickness=0)
        self.canvas.grid()
        self.canvas.update()
        self.restaurant = restaurant
        self.restaurant.add_view(self)
        self.controller = controller_class(self, restaurant)
        self.controller.create_ui()

    def make_button(self, text, action, size=BUTTON_SIZE, location=BUTTON_BOTTOM_RIGHT,
                    rect_style=BUTTON_STYLE, text_style=BUTTON_TEXT_STYLE):
        w, h = size
        x0, y0 = location
        box = self.canvas.create_rectangle(x0, y0, x0 + w, y0 + h, **rect_style)
        label = self.canvas.create_text(x0 + w / 2, y0 + h / 2, text=text, **text_style)
        self.canvas.tag_bind(box, '<Button-1>', action)
        self.canvas.tag_bind(label, '<Button-1>', action)

    def update(self):
        self.controller.create_ui()

    def set_controller(self, controller):
        self.controller = controller


class ServerView(RestaurantView):

    def __init__(self, master, restaurant, printer_window):
        super().__init__(master, restaurant, SERVER_VIEW_WIDTH, SERVER_VIEW_HEIGHT, RestaurantController)
        self.printer_window = printer_window

    def create_restaurant_ui(self):
        self.canvas.delete(tk.ALL)
        view_ids = []
        for ix, table in enumerate(self.restaurant.tables):
            table_id, seat_ids = self.draw_table(table, scale=RESTAURANT_SCALE)
            view_ids.append((table_id, seat_ids))
        for ix, (table_id, seat_ids) in enumerate(view_ids):
            # §54.7 "extra arguments trick" in Tkinter 8.5 reference by Shipman
            # Used to capture current value of ix as table_index for use when
            # handler is called (i.e., when screen is clicked).
            def table_touch_handler(_, table_number=ix):
                self.controller.table_touched(table_number)

            self.canvas.tag_bind(table_id, '<Button-1>', table_touch_handler)
            for seat_id in seat_ids:
                self.canvas.tag_bind(seat_id, '<Button-1>', table_touch_handler)

    def create_table_ui(self, table):
        self.canvas.delete(tk.ALL)
        table_id, seat_ids = self.draw_table(table, location=SINGLE_TABLE_LOCATION)
        for ix, seat_id in enumerate(seat_ids):
            def handler(_, seat_number=ix):
                self.controller.seat_touched(seat_number)

            self.canvas.tag_bind(seat_id, '<Button-1>', handler)
        self.make_button('Done', action=lambda event: self.controller.done())
        # removed the Create Bills button and put three buttons to create the bills insted
        # this removes the need for a bill controller
        if table.has_any_active_orders():
            #makes the Separate Bills
            self.make_button('Separate Bills',
                action=lambda event: self.controller.make_separate_bills(self.printer_window),
                location=BUTTON_BOTTOM_LEFT)
            #makes the Split Bills button
            self.make_button('Split Bills',
                             action=lambda event: self.controller.make_split_bills(self.printer_window),
                             location=BUTTON_BOTTOM_LEFT_HIGHER1)
            #makes the One Bill button
            self.make_button('One Bill',
                             action=lambda event: self.controller.make_one_bill(self.printer_window),
                             location=BUTTON_BOTTOM_LEFT_HIGHER2)

    def create_MoveBill_ui(self, table):
        pass

    def draw_table(self, table, location=None, scale=1):
        offset_x0, offset_y0 = location if location else table.location
        seats_per_side = math.ceil(table.n_seats / 2)
        table_height = SEAT_DIAM * seats_per_side + SEAT_SPACING * (seats_per_side - 1)
        table_x0 = SEAT_DIAM + SEAT_SPACING
        table_bbox = scale_and_offset(table_x0, 0, TABLE_WIDTH, table_height,
                                      offset_x0, offset_y0, scale)
        table_id = self.canvas.create_rectangle(*table_bbox, **TABLE_STYLE)
        far_seat_x0 = table_x0 + TABLE_WIDTH + SEAT_SPACING
        seat_ids = []
        for ix in range(table.n_seats):
            seat_x0 = (ix % 2) * far_seat_x0
            seat_y0 = (ix // 2 * (SEAT_DIAM + SEAT_SPACING) +
                       (table.n_seats % 2) * (ix % 2) * (SEAT_DIAM + SEAT_SPACING) / 2)
            seat_bbox = scale_and_offset(seat_x0, seat_y0, SEAT_DIAM, SEAT_DIAM,
                                         offset_x0, offset_y0, scale)
            style = FULL_SEAT_STYLE if table.has_order_for(ix) else EMPTY_SEAT_STYLE
            seat_id = self.canvas.create_oval(*seat_bbox, **style)
            seat_ids.append(seat_id)
        return table_id, seat_ids

    def create_order_ui(self, order):
        self.canvas.delete(tk.ALL)
        for ix, item in enumerate(self.restaurant.menu_items):
            w, h, margin = MENU_ITEM_SIZE
            x0 = margin
            y0 = margin + (h + margin) * ix

            def handler(_, menuitem=item):
                self.controller.add_item(menuitem)

            self.make_button(item.name, handler, (w, h), (x0, y0))
        self.draw_order(order)
        self.make_button('Cancel', lambda event: self.controller.cancel_changes(), location=BUTTON_BOTTOM_LEFT)
        self.make_button('Update Order', lambda event: self.controller.update_order())

    def draw_order(self, order):
        x0, h, m = ORDER_ITEM_LOCATION
        for ix, item in enumerate(order.items):
            y0 = m + ix * h
            self.canvas.create_text(x0, y0, text=item.details.name,
                                    anchor=tk.NW)
            dot_style = ORDERED_STYLE if item.has_been_ordered() else NOT_YET_ORDERED_STYLE
            self.canvas.create_oval(x0 - DOT_SIZE - DOT_MARGIN, y0, x0 - DOT_MARGIN, y0 + DOT_SIZE, **dot_style)
            if item.can_be_cancelled():

                def handler(_, cancelled_item=item):
                    self.controller.remove(cancelled_item)

                self.make_button('X', handler, size=CANCEL_SIZE, rect_style=CANCEL_STYLE,
                                 location=(x0 - 2*(DOT_SIZE + DOT_MARGIN), y0))
        self.canvas.create_text(x0, m + len(order.items) * h,
                                text=f'Total: {order.total_cost():.2f}',
                                anchor=tk.NW)


class Printer(tk.Frame):
    """
    Simulates a physical printer with a monospaced font, a maximum of 40 characters
    wide. To print, call the print() method passing the desired text as a parameter.
    The text may include \n (newline) characters to indicate line breaks.
    """

    def __init__(self, master):
        super().__init__(master)
        self.grid()
        scrollbar = tk.Scrollbar(self)
        scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.tape = tk.Text(self, wrap=None, bd=0, yscrollcommand=scrollbar.set,
                            font=TAPE_FONT, state=tk.DISABLED,
                            width=TAPE_WIDTH, height=VISIBLE_LINES)
        self.tape.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
        scrollbar.config(command=self.tape.yview)

    def print(self, text):
        self.tape['state'] = tk.NORMAL
        self.tape.insert(tk.END, text)
        self.tape.insert(tk.END, '\n')
        self.tape['state'] = tk.DISABLED
        self.tape.see(tk.END)


def scale_and_offset(x0, y0, width, height, offset_x0, offset_y0, scale):
    return ((offset_x0 + x0) * scale,
            (offset_y0 + y0) * scale,
            (offset_x0 + x0 + width) * scale,
            (offset_y0 + y0 + height) * scale)


if __name__ == "__main__":
    root = tk.Tk()

    printer_window = tk.Toplevel()
    printer_proxy = Printer(printer_window)
    printer_window.title('Printer Tape')
    printer_window.wm_resizable(0, 0)

    restaurant_info = Restaurant()
    ServerView(root, restaurant_info, printer_proxy)
    root.title('Server View v2')
    root.wm_resizable(0, 0)

    # nicely align the two windows
    root.update_idletasks()
    ph = printer_window.winfo_height()
    pw = printer_window.winfo_width()
    sw = root.winfo_width()
    sx = root.winfo_x()
    sy = root.winfo_y()
    printer_window.geometry(f'{pw}x{ph}+{sx+sw+10}+{sy}')

    root.mainloop()