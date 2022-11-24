"""
Provides the controller layer for the OORMS system.

Submitting lab group: [your names here]
Submission date: [date here]

Original code by EEE320 instructors.
"""
from model import Bills


class Controller:

    def __init__(self, view, restaurant, bill):
        self.view = view
        self.restaurant = restaurant
        self.bill = bill


class RestaurantController(Controller):
    def __init__(self, view, restaurant, bill = Bills()):
        super().__init__(view, restaurant, bill)

    def create_ui(self):
        self.view.create_restaurant_ui()

    def table_touched(self, table_number):
        self.view.set_controller(TableController(self.view, self.restaurant, self.bill,
                                                 self.restaurant.tables[table_number]))
        self.view.update()


class TableController(Controller):

    def __init__(self, view, restaurant, bill, table):
        super().__init__(view, restaurant, bill)
        self.table = table

    def create_ui(self):
        self.view.create_table_ui(self.table)

    def seat_touched(self, seat_number):
        self.view.set_controller(OrderController(self.view, self.restaurant, self.bill, self.table, seat_number))
        self.view.update()

    def make_one_bill(self, printer):

        """
        tell model.table to get the table number and all of it's ordered items into an array 
        then, print the list and the total cost of the order from the table
        """

        # is now a list of orders that have been ordered
        printer.print(f'Table # {self.restaurant.tables.index(self.table)}')

        (items, total_cost) = self.bill.one_bill(table.orders)

        # print the name and price of each item
        for i in items:
            printer.print(f'\t {items[i][1]} * {i} : ${items[i][0]} \n')

        printer.print(f'\t Total : ${total_cost} \n')

        # clears the table
        self.table.clear_table()
        self.view.update()

    def make_separate_bills(self, printer):
        printer.print(f'Table # {self.restaurant.tables.index(self.table)}')

        seat_orders = self.table.separate_bills()

        seat_number_counter = 1
        for seat in seat_orders:
            if seat != 0:
                printer.print(f'\t Seat # {seat_number_counter}')
                for i in seat[0]:
                    printer.print(f'\t {seat[0][i][1]} * {i} : ${seat[0][i][0]} \n')
                printer.print(f'\t Total : ${seat[1]} \n \n')
            seat_number_counter += 1

        # clears the table
        self.table.clear_table()
        self.view.update()

    def done(self):
        self.view.set_controller(RestaurantController(self.view, self.restaurant))
        self.view.update()


class OrderController(Controller):

    def __init__(self, view, restaurant, bill, table, seat_number):
        super().__init__(view, restaurant, bill)
        self.table = table
        self.order = self.table.order_for(seat_number)

    def create_ui(self):
        self.view.create_order_ui(self.order)

    def add_item(self, menu_item):
        self.order.add_item(menu_item)
        self.restaurant.notify_views()

    def remove(self, order_item):
        self.order.remove_item(order_item)
        self.restaurant.notify_views()

    def update_order(self):
        self.order.place_new_orders()
        self.view.set_controller(TableController(self.view, self.restaurant, self.bill, self.table))
        self.restaurant.notify_views()

    def cancel_changes(self):
        self.order.remove_unordered_items()
        self.view.set_controller(TableController(self.view, self.restaurant, self.bill, self.table))
        self.restaurant.notify_views()

