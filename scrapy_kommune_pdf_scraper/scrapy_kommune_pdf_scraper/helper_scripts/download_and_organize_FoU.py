import os
import json
import requests
import typer
from datetime import datetime

import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict
import shutil
import time


app = typer.Typer()



def generateFileTargetPath(file_url: str, parent_item: dict, data_dir: str):
    parent_folder = parent_item.get('projectNumber')
    if not parent_folder or parent_folder == "N/A":
        parent_folder = f"missing-projectnumber/{generate_safe_folder_name(parent_item.get('projectEndDate'))}"
        # if not parent_folder:
        #     raise ValueError("Missing both title and project number for these documents: "+ ", ".join(file_links))

    # Create directory for the project number if it doesn't exist
    project_dir = os.path.join(data_dir, str(parent_folder))
    os.makedirs(project_dir, exist_ok=True)

                
    # Get the filename by splitting and taking the last part of the URL
    file_name = os.path.basename(file_url)

    # Construct the file path
    file_path = os.path.join(project_dir, file_name)

    return file_path, file_name, project_dir


def generate_safe_folder_name(js_style_time_string):
    try:
        # Parse the JavaScript-style time string
        dt = datetime.fromisoformat(js_style_time_string.replace('Z', '+00:00'))  # Ensure correct timezone handling

        # Format the datetime object into a string suitable for folders
        safe_folder_name = dt.strftime('%Y-%m-%d_%H-%M-%S')

        return safe_folder_name
    except ValueError as e:
        print(f"Error parsing date: {e}")
        return None


@app.command(help="Download files from URLs specified in the JSON file.")
def download_files(
    json_path: str = typer.Argument(..., help="Path to the JSON file containing file links."),
    data_dir: str = typer.Argument(..., help="Directory to store downloaded files.")
):
    # Read the JSON file
    with open(json_path, 'r', encoding="utf-8") as file:
        data = json.load(file).get("results", [])

    # Iterate over each object in the array
    for item in data:
        file_links = item.get('file_links', [])

        for file_url in file_links:
            file_path, file_name, project_dir = generateFileTargetPath(file_url, item, data_dir)

            # Check if the file already exists
            if os.path.exists(file_path):
                print(f"Skipped {file_name}: Already exists in {project_dir}")
                continue

            try:
                # Download the file and save it
                response = requests.get(file_url)
                response.raise_for_status()  # Check that the request was successful

                with open(file_path, 'wb') as f:
                    f.write(response.content)
                    
                print(f"Downloaded {file_name} to {project_dir}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to download {file_url}: {e}")


@app.command(help="Organize PDF documents by theme tags into specified target directory.")
def organize_by_theme(
    json_path: str = typer.Argument(..., help="Path to the JSON file containing data."),
    data_dir: str = typer.Argument(..., help="Directory containing downloaded files."),
    target_dir: str = typer.Argument(..., help="Target directory to organize theme tag folders.")
):
    missing_files = []

    with open(json_path, 'r', encoding="utf-8") as file:
        data = json.load(file).get("results", [])

    for item in data:
        theme_tags = item.get('themeTags', [])
        file_links = item.get('file_links', [])

        for file_url in file_links:
            file_path, file_name, _ = generateFileTargetPath(file_url, item, data_dir)
            
            if not file_name.lower().endswith('.pdf'):
                continue
            
            if not os.path.exists(file_path):
                missing_files.append(file_name)
                continue

            for theme_tag in theme_tags:
                theme_folder = os.path.join(target_dir, theme_tag)
                os.makedirs(theme_folder, exist_ok=True)
                
                dest_file_path = os.path.join(theme_folder, file_name)
                if not os.path.exists(dest_file_path):
                    shutil.copy(file_path, dest_file_path)
                    print(f"Copied {file_name} to {theme_folder}")
                else:
                    print(f"File {file_name} already exists in {theme_folder}")

    if missing_files:
        report_path = os.path.join(target_dir, 'missing_files_report.txt')
        with open(report_path, 'w') as report_file:
            report_file.write("Missing Files:\n")
            for missing_file in missing_files:
                report_file.write(f"{missing_file}\n")
        print(f"Report generated for missing files at {report_path}")

    verify_pdf_counts_for_themes_org(json_path, target_dir)


def verify_pdf_counts_for_themes_org(
    json_path: str,
    target_dir: str
):
    with open(json_path, 'r', encoding="utf-8") as file:
        filters = json.load(file).get("filters", {})
    
    expected_counts = {tag['name']: tag['count'] for tag in filters}

    actual_counts = {tag: len([name for name in os.listdir(os.path.join(target_dir, tag))
                               if name.lower().endswith('.pdf')])
                     for tag in expected_counts}

    # Generate and print discrepancies
    print(f"{'Tag':<30}{'Expected':<10}{'Actual':<10}{'Discrepancy':<10}")
    print('-' * 60)
    for tag, expected_count in expected_counts.items():
        actual_count = actual_counts.get(tag, 0)
        discrepancy = expected_count - actual_count
        print(f"{tag:<30}{expected_count:<10}{actual_count:<10}{discrepancy:<10}")



def count_entries(data):
    # Initialize dictionaries to hold counts
    theme_tag_counts = defaultdict(int)
    year_counts = defaultdict(int)
    executive_environment_counts = defaultdict(int)

    # Iterate over each entry in the JSON data
    for entry in data:
        # Count themeTag occurrences
        theme_tags = entry.get('themeTags', [])
        for tag in theme_tags:
            theme_tag_counts[tag] += 1
        
        # Count occurrences per year derived from date string
        date_string = entry.get('projectEndDate', '')
        if date_string:
            try:
                date_object = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                year_counts[date_object.year] += 1
            except ValueError:
                print(f"Invalid date format: {date_string}")

        # Count occurrences for executiveEnvironment
        executive_environment = entry.get('executiveEnvironment', '')
        if executive_environment:
            executive_environment_counts[executive_environment] += 1

    return {
        'themeTagCounts': dict(theme_tag_counts),
        'yearCounts': dict(year_counts),
        'executiveEnvironmentCounts': dict(executive_environment_counts),
    }

def display_counts(counts):
    print("Theme Tag Counts:", counts['themeTagCounts'])
    print("Year Counts:", counts['yearCounts'])
    print("Executive Environment Counts:", counts['executiveEnvironmentCounts'])


def visualize_data(counts):
    # Configure subplots with ample space for each plot
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Visualisering av mengde rapporter (ikke mengde dokumenter)")

    # Theme Tag visualization
    theme_tags = counts['themeTagCounts']
    axs[0].bar(theme_tags.keys(), theme_tags.values(), color='skyblue', width=0.6)
    axs[0].set_xticklabels(theme_tags.keys(), rotation=45, ha='right', fontsize=9)
    axs[0].set_xlabel('Theme Tags', fontsize=10)
    axs[0].set_ylabel('Count', fontsize=10)
    axs[0].set_title('Counts per Theme Tag', fontsize=12)
    axs[0].tick_params(axis='x', labelsize=7)
    axs[0].grid(True, linestyle='--', alpha=0.7)

    # Increase space between x labels and plot
    plt.subplots_adjust(bottom=0.3)

    # Year visualization
    years = counts['yearCounts']
    sorted_years = sorted(years.items())
    sorted_year_keys = [year for year, count in sorted_years]
    sorted_year_values = [count for year, count in sorted_years]
    axs[1].plot(sorted_year_keys, sorted_year_values, marker='o', color='orange')
    axs[1].set_xlabel('Year', fontsize=10)
    axs[1].set_ylabel('Count', fontsize=10)
    axs[1].set_title('Counts per Year', fontsize=12)
    axs[1].grid(True, linestyle='--', alpha=0.7)

    # Adjust layout
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.show()


@app.command(help="Count entries in the JSON file and visualize the data.")
def count(
    json_path: str = typer.Argument(..., help="Path to the JSON file containing data.")
):
    with open(json_path, 'r', encoding="utf-8") as file:
        json_data = json.load(file).get("results", [])
    counts = count_entries(json_data)
    visualize_data(counts)

if __name__ == "__main__":
    app()
