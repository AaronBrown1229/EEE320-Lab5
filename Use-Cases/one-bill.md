# Use Case for when the server wants to print a tables bill
*preconditions:* The Server is logged into the system and the restaurant view is visible. restaurant view is on Table View, and all items ordered at a table are accounted for.
1. The server selsects the button labeled "One Bill".
2. The system adds the table number, all ordered items at the table and the total cost on to the printer tape.


*Alternates and exceptions:*
- At Step 1 the Server may select the button labeled "Split Bills". The system will then add the table number, all ordered items at the table, total cost and the total cost divided by size of party on to the printer tape.
- At Step 1 the server may select the button labeled "Separate Bills". The system will then add the table number, each seat number, all ordered items under the seat that ordered it and the total cost for each person.
