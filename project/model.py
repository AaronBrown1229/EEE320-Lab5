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
        self.bill = Bills()

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

    def clear_table(self):
        self.orders = [Order() for _ in range(self.n_seats)]


class Bills:
    # returns a dict of items matched to their price and the total cost
    def seat_bill(self, seat):
        # maybe make this return the number of times the item is ordered the price and the total cost
        # This will let the other methods create the list
        items = {}
        cost = 0

        for j in seat.items:
            if j.details.name in items:
                items[j.details.name] = [j.details.price, items[j.details.name][1] + 1]
            else:
                items[j.details.name] = [j.details.price, 1]
            cost += j.details.price

        return items, cost

    def one_bill(self, orders):
        # items is a dict whose keys are food items and the content is a list
        # in the list the first element is the cost of the item and the second element is the
        # number of times it was ordered
        items = {}
        cost = 0

        # steps through each seat at the table and fills items with the required info
        # also calculates the total cost of the bill
        for i in orders:
            for j in i.items:
                if j.details.name in items:
                    items[j.details.name] = [j.details.price, items[j.details.name][1] + 1]
                else:
                    items[j.details.name] = [j.details.price, 1]
                cost += j.details.price

        return items, cost

    def separate_bills(self, orders, n_seats):
        # stores the working chairs food and cost similar to one_bill
        items = {}
        # stores the working chairs total cost
        total = 0

        # stores the items and total
        seat = []
        # stores seats
        table = [0] * n_seats

        # used to print the seat number
        seat_counter = 0
        # cycles through each seat at the table
        for i in orders:
            # if the seat ordered anything
            if len(i.items) > 0:
                # creates the dict and the total cost ordered by the seat
                (items, total) = self.seat_bill(i)

                # sets up the return list
                seat.append(items)
                seat.append(total)
                table[seat_counter] = seat

                # clears for next iteration of the loop
                seat = []

            seat_counter += 1

        return table


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
