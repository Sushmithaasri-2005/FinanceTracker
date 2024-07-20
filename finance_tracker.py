import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import csv

# Finance Tracker Class
class CSV:
    csv_file = 'finance_data.csv'
    COLUMNS = ["date", "amount", "category", "description"]
    FORMAT = "%d-%m-%Y"

    @classmethod
    def initialize_csv(cls):
        try:
            pd.read_csv(cls.csv_file)
        except FileNotFoundError:
            df = pd.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.csv_file, index=False)

    @classmethod
    def add_entry(cls, date, amount, category, description):
        new_entry = {
            "date": date,
            "amount": amount,
            "category": category,
            "description": description
        }
        with open(cls.csv_file, "a", newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV.COLUMNS)
            writer.writerow(new_entry)
        st.success("Entry added successfully")
    
    @classmethod
    def get_df(cls, start_date, end_date):
        df = pd.read_csv(cls.csv_file)
        df['date'] = pd.to_datetime(df['date'], format=cls.FORMAT)
        start_date = datetime.strptime(start_date, CSV.FORMAT)
        end_date = datetime.strptime(end_date, CSV.FORMAT)

        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            st.warning('No transactions found in the given interval')

        total_income = filtered_df[filtered_df["category"] == 'Income']["amount"].sum()
        total_expense = filtered_df[filtered_df["category"] == 'Expense']['amount'].sum()

        st.write("\n### Summary:")
        st.write(f"**Total Income**: {total_income:.2f}")
        st.write(f"**Total Expense**: {total_expense:.2f}")
        st.write(f"**Net Savings**: {(total_income - total_expense):.2f}")
        return filtered_df

    @classmethod
    def get_transactions(cls, start_date, end_date):
        df = cls.get_df(start_date, end_date)
        if not df.empty:
            st.write(f"Transactions from {start_date} to {end_date}")
            st.dataframe(df, width=800)

    
    
def save_and_display_plot(df):
    df['date'] = pd.to_datetime(df['date'], format=CSV.FORMAT)
    df.set_index("date", inplace=True)

    income_df = df[df["category"] == "Income"].resample("D").sum().reindex(df.index, fill_value=0)
    expense_df = df[df["category"] == "Expense"].resample("D").sum().reindex(df.index, fill_value=0)

    plt.figure(figsize=(10, 5))
    plt.plot(income_df.index, income_df["amount"], label="Income", color="g")
    plt.plot(expense_df.index, expense_df["amount"], label="Expense", color="r")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.title("Income and Expenses Over Time")
    plt.legend()
    plt.grid(True)
    
    # Save the plot as an image file
    image_path = 'plot.png'
    plt.savefig(image_path)
    
    # Display the saved image using Streamlit
    st.image(image_path)

# Streamlit App
def main():
    st.title("Finance Tracker")

    # Initialize CSV
    CSV.initialize_csv()

    # Sidebar for navigation
    menu = ["About","Add Transaction", "View Transactions", "Plot Transactions"]
    choice = st.sidebar.selectbox("Menu", menu)
    if choice=="About":
        st.subheader("About Finance Tracker")
        st.write("""
        Welcome to Finance Tracker! This web app is designed to help you manage your personal finances efficiently and effortlessly.
        
        With Finance Tracker, you can:
        - **Add Transactions**: Record your income and expenses with ease.
        - **View Transactions**: Filter and view your transactions within a specific date range.
        - **Summary and Insights**: Get a summary of your total income, expenses, and net savings.
        - **Visualize Data**: Generate and display graphical representations of your financial data for better insights.

        Our goal is to provide you with a simple yet powerful tool to track your finances and make informed decisions. Whether you're budgeting for the month or planning for the future, Finance Tracker is here to assist you every step of the way.
        """)

    elif choice == "Add Transaction":
        st.subheader("Add a new Transaction")

        # Add Transaction Form
        date = st.date_input("Date", datetime.today()).strftime(CSV.FORMAT)
        amount = st.number_input("Amount", min_value=1, step=1)
        category = st.selectbox("Category", ["Income", "Expense"])
        description = st.text_input("Description")

        if st.button("Add Transaction"):
            CSV.add_entry(date, amount, category, description)

    elif choice == "View Transactions":
        st.subheader("View Transactions")

        # Date Inputs
        start_date = st.date_input("Start Date").strftime(CSV.FORMAT)
        end_date = st.date_input("End Date").strftime(CSV.FORMAT)

        if st.button("View"):
            CSV.get_transactions(start_date, end_date)

            # if not df.empty and st.button("Show Plot"):
            #     save_and_display_plot(df)

    elif choice == "Plot Transactions":
        st.subheader("Transactions Chart")
        start_date = st.date_input("Start Date").strftime(CSV.FORMAT)
        end_date = st.date_input("End Date").strftime(CSV.FORMAT)
        if st.button("Plot"):
            df = CSV.get_df(start_date, end_date)
            save_and_display_plot(df)

        



if __name__ == "__main__":
    main()
