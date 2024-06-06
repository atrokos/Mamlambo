# Mamlambo: Finance Management App

## Introduction
Mamlambo is a finance management application designed for personal use on PCs. It helps users manage their finances by allowing them to record, edit, and analyze their transactions efficiently.

## Installing Prerequisites
To use Mamlambo, ensure you have the following installed on your PC:
- Python 3.12

All necessary Python packages are listed in the `requirements.txt` file. To install them, run the following command in your terminal:
```sh
pip install -r requirements.txt
```

## Running the Application
To run Mamlambo, open a terminal and navigate to the directory where Mamlambo is located. Execute the following command:
```sh
python ./main.py
```

## Using the Application

### Initializing the Database
Upon launching Mamlambo, all buttons will be disabled because no database has been initialized. To initialize the database:
1. Click on `File` in the menu.
2. Select either `New` to create a new database or `Open` to import an existing one. Only header-less `CSV` files can be imported.

After initializing the database, all buttons except `Revert` and `Commit` will be enabled.

### Transactions

#### Transaction Data
A single transaction consists of the following fields:
- **Date:** in the YYYY-MM-DD format
- **Title**
- **Group:** a tag for better organization
- **Amount:** with a dot as the decimal separator
- **Currency:** the three-letter ISO code (e.g., CZK, USD)
- **Description:** an optional description

#### Adding a Transaction
1. Click on the `Add` button.
2. A new window will appear with fields for each data point (except Description, which is optional).
3. You can select a Template to pre-fill the fields with saved values.
4. To quickly fill out the current date, use its letter abbreviation (e.g., 25-MM-2024 will be translated to 25-06-2024 if the current month is June).
5. You can save the current fields as a new template.
6. Press `Confirm` when done.

#### Removing Transactions
1. Select the transaction(s) you want to remove by clicking on them in the view (hold CTRL to select multiple).
2. Press the `Remove` button.

#### Editing Transactions
1. Select the transaction(s) you want to edit by clicking on them in the view (hold CTRL to select multiple).
2. Press the `Edit` button.

### Filtering Transactions
1. Press the `Filter` button.
2. A new window will open where you can add filters for all properties as needed.
3. For example, to filter transactions with an amount greater than 50:
   - Select "Amount" from the dropdown menu.
   - Enter `> 50` in the field next to it.

### Ordering Transactions
1. Click on any of the column names to order by that property.
2. Click again to toggle between ascending and descending order.
3. Ordering by transaction's description is not supported.

### Committing Changes
After adding, editing, or removing transactions, changes must be committed. Press the `Commit` button to save changes.

### Reverting Changes
After committing, you can revert up to the last 10 commits by pressing the `Revert` button.

### Converting currencies
You can add your own currency conversions, simply add them in the `config.json` file. User added conversions
work both ways, so only one definition is sufficient. To convert between currencies:
1. Click on `Tools` in the menu.
2. Select `Convert currency`.

### Statistics
Mamlambo supports statistics for data with the same currency. Ensure that the data is filtered by a single currency before generating statistics.
1. Apply a filter for a single currency.
2. To access statistics, click on `Tools` in the menu.
3. Select `Statistics`.

## Saving the database
To save the database, press `File`, then `Save`.
By default, the data will be saved in a `CSV` file. To export the data to `JSON`, change the file type to `.json` when saving.