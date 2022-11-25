"""
Test cases for the OORMS system.

Submitting lab group: [your names here]
Submission date: [date here]

Original code by EEE320 instructors.
"""

import unittest
from enum import Enum, auto
from controller import RestaurantController, TableController, OrderController
from model import Restaurant, OrderItem


class UI(Enum):
    restaurant = auto()
    table = auto()
    order = auto()
    MoveBill = auto()


class ServerViewMock:

    def __init__(self, restaurant):
        self.controller = None
        self.last_UI_created = None
        self.restaurant = restaurant
        restaurant.add_view(self)
        self.set_controller(RestaurantController(self, self.restaurant))

    def set_controller(self, controller):
        self.controller = controller
        self.controller.create_ui()

    def create_restaurant_ui(self):
        self.last_UI_created = UI.restaurant

    def create_table_ui(self, table):
        self.last_UI_created = (UI.table, table)

    def create_order_ui(self, order):
        self.last_UI_created = (UI.order, order)

    def create_MoveBill_ui(self, table):
        self.last_UI_created = (UI.MoveBill, table)

    def update(self):
        self.controller.create_ui()


class OORMSTestCase(unittest.TestCase):

    def setUp(self):
        self.restaurant = Restaurant()
        self.view = ServerViewMock(self.restaurant)

    def test_initial_state(self):
        self.assertEqual(UI.restaurant, self.view.last_UI_created)
        self.assertIsInstance(self.view.controller, RestaurantController)

    def test_restaurant_controller_touch_table(self):
        self.view.controller.table_touched(3)
        self.assertIsInstance(self.view.controller, TableController)
        self.assertEqual(self.view.controller.table, self.restaurant.tables[3])
        self.assertEqual((UI.table, self.restaurant.tables[3]), self.view.last_UI_created)

    def test_table_controller_done(self):
        self.view.controller.table_touched(5)
        self.view.controller.done()
        self.assertIsInstance(self.view.controller, RestaurantController)
        self.assertEqual(UI.restaurant, self.view.last_UI_created)

    def test_table_controller_seat_touched(self):
        self.view.controller.table_touched(4)
        self.view.controller.seat_touched(0)
        self.assertIsInstance(self.view.controller, OrderController)
        self.assertEqual(self.view.controller.table, self.restaurant.tables[4])
        the_order = self.restaurant.tables[4].order_for(0)
        self.assertEqual(self.view.controller.order, the_order)
        self.assertEqual((UI.order, the_order), self.view.last_UI_created)

    def order_an_item(self):
        """
        Starting from the restaurant UI, orders one instance of item 0
        for table 2, seat 4
        """
        self.view.controller.table_touched(2)
        self.view.controller.seat_touched(4)
        the_menu_item = self.restaurant.menu_items[0]
        self.view.last_UI_created = None
        self.view.controller.add_item(the_menu_item)
        return self.restaurant.tables[2].order_for(4), the_menu_item

    def test_order_controller_add_item(self):
        the_order, the_menu_item = self.order_an_item()
        self.assertIsInstance(self.view.controller, OrderController)
        self.assertEqual((UI.order, the_order), self.view.last_UI_created)
        self.assertEqual(1, len(the_order.items))
        self.assertIsInstance(the_order.items[0], OrderItem)
        self.assertEqual(the_order.items[0].details, the_menu_item)
        self.assertFalse(the_order.items[0].has_been_ordered())

    def test_order_controller_update_order(self):
        the_order, the_menu_item = self.order_an_item()
        self.view.last_UI_created = None
        self.view.controller.update_order()
        self.assertEqual((UI.table, self.restaurant.tables[2]), self.view.last_UI_created)
        self.assertEqual(1, len(the_order.items))
        self.assertIsInstance(the_order.items[0], OrderItem)
        self.assertEqual(the_order.items[0].details, the_menu_item)
        self.assertTrue(the_order.items[0].has_been_ordered())

    def test_order_controller_cancel(self):
        the_order, the_menu_item = self.order_an_item()
        self.view.last_UI_created = None
        self.view.controller.cancel_changes()
        self.assertEqual((UI.table, self.restaurant.tables[2]), self.view.last_UI_created)
        self.assertEqual(0, len(the_order.items))

    def test_order_controller_update_several_then_cancel(self):
        self.view.controller.table_touched(6)
        self.view.controller.seat_touched(7)
        the_order = self.restaurant.tables[6].order_for(7)
        self.view.controller.add_item(self.restaurant.menu_items[0])
        self.view.controller.add_item(self.restaurant.menu_items[3])
        self.view.controller.add_item(self.restaurant.menu_items[5])
        self.view.controller.update_order()

        def check_first_three_items(menu_items, items):
            self.assertEqual(menu_items[0], items[0].details)
            self.assertEqual(menu_items[3], items[1].details)
            self.assertEqual(menu_items[5], items[2].details)

        self.assertEqual(3, len(the_order.items))
        check_first_three_items(self.restaurant.menu_items, the_order.items)

        def add_two_more(menu_items, view):
            view.controller.seat_touched(7)
            view.controller.add_item(menu_items[1])
            view.controller.add_item(menu_items[2])

        add_two_more(self.restaurant.menu_items, self.view)
        self.view.controller.cancel_changes()

        self.assertEqual(3, len(the_order.items))
        check_first_three_items(self.restaurant.menu_items, the_order.items)

        add_two_more(self.restaurant.menu_items, self.view)
        self.view.controller.update_order()

        self.assertEqual(5, len(the_order.items))
        check_first_three_items(self.restaurant.menu_items, the_order.items)
        self.assertEqual(self.restaurant.menu_items[1], the_order.items[3].details)
        self.assertEqual(self.restaurant.menu_items[2], the_order.items[4].details)

    def test_bill_before_all_served(self):
        # make an order
        self.view.controller.table_touched(6)

        self.view.controller.seat_touched(0)
        self.view.controller.add_item(self.restaurant.menu_items[3])
        self.view.controller.add_item(self.restaurant.menu_items[6])
        the_order0 = self.view.controller.table.orders[0].items
        self.view.controller.update_order()
        self.assertEqual(2, len(the_order0))

        self.view.controller.seat_touched(1)
        the_order1 = self.view.controller.table.orders[1].items
        self.view.controller.add_item(self.restaurant.menu_items[3])
        self.view.controller.update_order()
        self.assertEqual(1, len(the_order1))

        self.view.controller.seat_touched(5)
        the_order5 = self.view.controller.table.orders[5].items
        self.view.controller.add_item(self.restaurant.menu_items[3])
        self.view.controller.update_order()
        self.assertEqual(1, len(the_order5))


        # mark as served
        self.view.controller.serve()

        # ensure the state of all items ordered are now served
        for i in self.view.controller.table.orders:
            for j in i.items:
                # j is item *inst of orderItem
                #check that each ordered item state is either 0 or 2
                self.assertEqual(j.ordered, 0 or 2)

    def test_make_one_bill(self):
        # make an order
        self.view.controller.table_touched(0)
        self.view.controller.seat_touched(3)
        the_order3 = self.restaurant.tables[0].order_for(3)
        self.view.controller.add_item(self.restaurant.menu_items[0])
        self.view.controller.update_order()
        self.assertEqual(1, len(the_order3.items))

        self.view.controller.seat_touched(4)
        the_order4 = self.restaurant.tables[0].order_for(4)
        self.view.controller.add_item(self.restaurant.menu_items[3])
        self.view.controller.update_order()
        self.assertEqual(1, len(the_order4.items))

        self.view.controller.seat_touched(5)
        the_order5 = self.restaurant.tables[0].order_for(5)
        self.view.controller.add_item(self.restaurant.menu_items[5])
        self.view.controller.update_order()
        self.assertEqual(1, len(the_order5.items))

        # mark all as served
        self.view.controller.serve()

        # gets list of items ordered and val of total cost from one_bill

        (items, total) = self.view.controller.bill.one_bill(self.view.controller.table.orders)

        # make dic of real_items and int of real_total cost and compare real to meathods
        real_items = {'House burger': [16, 1],'Fried Chicken' : [14.5, 1], 'Roasted Squash': [14, 1]}
        real_total = 44.5

        self.assertEqual(items,real_items)
        self.assertEqual(total, real_total)

    def test_make_separate_bills(self):
        # make an order
        self.view.controller.table_touched(0)
        self.view.controller.seat_touched(3)
        the_order3 = self.restaurant.tables[0].order_for(3)
        self.view.controller.add_item(self.restaurant.menu_items[0])
        self.view.controller.update_order()
        self.assertEqual(1, len(the_order3.items))

        self.view.controller.seat_touched(4)
        the_order4 = self.restaurant.tables[0].order_for(4)
        self.view.controller.add_item(self.restaurant.menu_items[3])
        self.view.controller.update_order()
        self.assertEqual(1, len(the_order4.items))

        self.view.controller.seat_touched(5)
        the_order5 = self.restaurant.tables[0].order_for(5)
        self.view.controller.add_item(self.restaurant.menu_items[5])
        self.view.controller.update_order()
        self.assertEqual(1, len(the_order5.items))

        # mark all as served
        self.view.controller.serve()

        # get dictionary from separate_bills
        table = self.view.controller.bill.separate_bills(self.view.controller.table.orders,
                                                         self.view.controller.table.n_seats)

        # make dictionary that contains all the values expected
        real_table = [0, 0, 0, [{'House burger': [16, 1]}, 16], [{'Fried Chicken' : [14.5, 1]}, 14.5],
                      [{'Roasted Squash': [14, 1]}, 14]]

        # compare the two
        self.assertEqual(table, real_table)

    def combine_bills_setup(self):
        self.view.controller.table_touched(6)
        self.view.controller.seat_touched(3)
        self.view.controller.add_item(self.restaurant.menu_items[3])
        self.view.controller.add_item(self.restaurant.menu_items[6])
        the_order3 = self.view.controller.table.orders[3].items
        self.view.controller.update_order()
        self.assertEqual(2, len(the_order3))

        self.view.controller.seat_touched(1)
        the_order1 = self.view.controller.table.orders[1].items
        self.view.controller.add_item(self.restaurant.menu_items[3])
        self.view.controller.update_order()
        self.assertEqual(1, len(the_order1))

        self.view.controller.seat_touched(5)
        the_order5 = self.view.controller.table.orders[5].items
        self.view.controller.update_order()
        self.assertEqual(0, len(the_order5))

        self.view.controller.serve()

        self.view.controller.combine_bills()

    def test_combine_bills1(self):
        self.combine_bills_setup()

        self.view.controller.seat_touched(3)
        self.view.controller.seat_touched(1)

        table = self.view.controller.bill.separate_bills(self.view.controller.table.orders,
                                                         self.view.controller.table.n_seats)
        real_table = [0, 0, 0, [{'Fried Chicken': [14.5, 2], 'Portabella Burger': [14, 1]}, 43.0], 0, 0, 0, 0]

        # compare the two
        self.assertEqual(table, real_table)

    def test_combine_bills2(self):
        self.combine_bills_setup()

        self.view.controller.seat_touched(1)
        self.view.controller.seat_touched(3)

        (items, total) = self.view.controller.bill.one_bill(self.view.controller.table.orders)

        real_items = {'Fried Chicken': [14.5, 2], 'Portabella Burger': [14, 1]}
        real_total = 43.0
        self.assertEqual(items, real_items)
        self.assertEqual(total, real_total)

    def test_combine_bills3(self):
        self.combine_bills_setup()

        self.view.controller.seat_touched(3)
        self.view.controller.seat_touched(0)

        table = self.view.controller.bill.separate_bills(self.view.controller.table.orders,
                                                         self.view.controller.table.n_seats)
        real_table = [0, [{'Fried Chicken': [14.5, 1]}, 14.5], 0,
                      [{'Fried Chicken': [14.5, 1], 'Portabella Burger': [14, 1]}, 28.5], 0, 0, 0, 0]

        # compare the two
        self.assertEqual(table, real_table)

