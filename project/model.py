"""
Provides the model classes representing the state of the OORMS
system.

Submitting lab group: [your names here]
Submission date: [date here]

Original code by EEE320 instructors.
"""

from constants import TABLES, MENU_ITEMS


class Restaurant:

    def __init__(self):
        super().__init__()
        self.tables = [Table(seats, loc) for seats, loc in TABLES]
        self.menu_items = [MenuItem(name, price) for name, price in MENU_ITEMS]
        self.views = []

    def add_view(self, view):
        self.views.append(view)

    def notify_views(self):
        for view in self.views:
            view.update()


class Table:

    def __init__(self, seats, location):
        self.n_seats = seats
        self.location = location
        self.orders = [Order() for _ in range(seats)]

    def has_any_active_orders(self):
        for order in self.orders:
            for item in order.items:
                if item.has_been_ordered() and not item.has_been_served():
                    return True
        return False

    def has_order_for(self, seat):
        return bool(self.orders[seat].items)

    def order_for(self, seat):
        return self.orders[seat]

    def one_bill(self):

        # make a list of seats that have orders
        # make an outer for loop with that list
        # the nested loop will be to cycle through the items orderd by each seat

        item_array = []
        item_cost = []

        for i in self.orders:
            for j in i.items:
                item_array.append(j.details.name)
                item_cost.append(j.details.price)
        return item_array, item_cost

class Order:

    def __init__(self):
        self.items = []

    def add_item(self, menu_item):
        item = OrderItem(menu_item)
        self.items.append(item)

    def remove_item(self, order_item):
        self.items.remove(order_item)

    def place_new_orders(self):
        for item in self.unordered_items():
            item.mark_as_ordered()

    def remove_unordered_items(self):
        for item in self.unordered_items():
            self.items.remove(item)

    def unordered_items(self):
        return [item for item in self.items if not item.has_been_ordered()]

    def total_cost(self):
        return sum((item.details.price for item in self.items))


class OrderItem:

    # TODO: need to represent item state, not just 'ordered', all methods will need modifying
    def __init__(self, menu_item):
        self.details = menu_item
        self.ordered = False

    def mark_as_ordered(self):
        self.ordered = True

    def has_been_ordered(self):
        return self.ordered

    def has_been_served(self):
        # TODO: correct implementation based on item state
        return False

    def can_be_cancelled(self):
        # TODO: correct implementation based on item state
        return True


class MenuItem:

    def __init__(self, name, price):
        self.name = name
        self.price = price
