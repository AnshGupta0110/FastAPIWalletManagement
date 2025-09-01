# FastAPIWalletManagement
This is a backend API system built with FastAPI for managing user wallets and transactions.

## What this does

This API lets you:
1. Get a list of all users and their wallet balances
2. Add or subtract money from any user's wallet  
3. See all transactions for any specific user

## The APIs

### Get all users
- **URL:** GET /users
- Shows name, email, phone and wallet balance for all users

### Update wallet  
- **URL:** PUT /wallet/update
- Send: user_id and amount (positive to add money, negative to subtract)
- Example: {"user_id": 1, "amount": 100} adds $100 to user 1

### Get transactions
- **URL:** GET /transactions/1 (replace 1 with user ID)
- Shows all transactions for that user

## Test data

When you start the app, it creates 3 test users:
- John Doe (john@example.com) - $1000 balance
- Jane Smith (jane@example.com) - $500 balance  
- Mike Wilson (mike@example.com) - $750 balance

## Files
- App.py - The main code file
- requirements.txt - List of packages needed


You can test all the APIs using the Swagger interface at /docs after starting the server.
