import pandas as pd

def scrape():
    print("Running scrape_1.py...")
    data = {"Name": ["Alice", "Bob"], "Age": [25, 30]}
    df = pd.DataFrame(data)
    df.to_csv("data/scrape_1.csv", index=False)
    print("Scrape 1 completed: Data saved.")

if __name__ == "__main__":
    scrape()
