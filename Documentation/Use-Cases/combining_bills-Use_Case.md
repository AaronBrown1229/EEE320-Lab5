# Use Case for Combining Bills
## Server wants to move the cost of one seat to the cost of another seat
### *preconditions:* The Server is logged into the system and the restaurant view is visible. restaurant view is on Table View.
1. The server selects the button labeled "Combine Bills".
2. The system then displays the table
3. The server will select the seat that they wish to move a bill to
4. The system will display the colour of the clicked seat as green
5. The server will select the seat that they wish to move the bill from
6. The system will move the bill and display `Table View`

### *Alternates and exceptions:*
1. For step 1 if not all items at the table are served the button labeled "Combine Bills" should not be visible
2. For step 3 through 5 the Server could instead press the button labeled "cancel" and it will return to `Table View`