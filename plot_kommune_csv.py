import pandas as pd
import matplotlib.pyplot as plt

import typer

def process_csv(file_path):
    # Read the CSV file
    print("Loading csv...")
    df = pd.read_csv(file_path)
    
    print("")
    # Remove duplicates in the "url" field
    df = df.drop_duplicates(subset='pdf_link')
    
    # Count occurrences in the "Kommune" field
    kommune_counts = df['kommune_navn'].value_counts()
    
    # Plotting the counts in a bar chart
    plt.figure(figsize=(10, 6))
    ax = kommune_counts.plot(kind='bar', color='black')
    plt.title('Antall PDF dokumenter per kommune')
    plt.xlabel('Kommune')
    plt.ylabel('Antall PDF dokumenter')
    plt.xticks(rotation=45)

    # Annotating each bar with its count
    for p in ax.patches:
        ax.annotate(str(int(p.get_height())), 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center',
                    xytext=(0, 10), 
                    textcoords='offset points')


    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    typer.run(process_csv)
    # process_csv('./scrapy_kommune_pdf_scraper/finnmark.csv')