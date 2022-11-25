# Use Case for marking items as served
## Server has served all items to the customers and want to notify the system
### *preconditions:* The Server is logged into the system and the restaurant view is visible. restaurant view is on Table View.
1. The server selects the button labeled "Items Served".
2. The system will change the state of all items ordered at the table to served
3. The system will remove the button labeled "Items Served" and replace it with three buttons saying "One Bill", "Separate Bills" and "Combine Bills"

### *Alternates and exceptions:*
1. For step 1 the Server could have pressed the button labeled "done" returning them to restaurant view