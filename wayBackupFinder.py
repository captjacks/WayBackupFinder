import os
import requests
from colorama import init
from termcolor import colored

def print_ascii_art():
    ascii_art = r'''
    .  .      .__       .          .___      .      
    |  | _.  .[__) _. _.;_/. .._   [__ *._  _| _ ._.
    |/\|(_]\_|[__)(_](_.| \(_|[_)  |   |[ )(_](/,[  
           ._|                |                     
    '''
    print(ascii_art)

print_ascii_art()

def load_extensions_from_file(file_path='extensions.txt'):
    try:
        with open(file_path, 'r') as f:
            extensions = [line.strip() for line in f.readlines() if line.strip()]
        return extensions
    except FileNotFoundError:
        print(colored(f"{file_path} not found. Proceeding with no extensions.", "red"))
        return []

def load_domains_from_file(file_path):
    try:
        with open(file_path, 'r') as f:
            domains = [line.strip() for line in f.readlines() if line.strip()]
        return domains
    except FileNotFoundError:
        print(colored(f"{file_path} not found. Exiting.", "red"))
        exit()

def fetch_urls(target, file_extensions):
    print(f"\nFetching URLs from The Time Machine Lite for {target}...")
    archive_url = f'https://web.archive.org/cdx/search/cdx?url=*.{target}/*&output=txt&fl=original&collapse=urlkey'
    
    try:
        response = requests.get(archive_url)
        response.raise_for_status()
        url_list = response.text.splitlines()
        print(colored(f"Fetched {len(url_list)} URLs from archive.", "green"))
    except Exception as e:
        print(colored(f"Error fetching URLs: {e}", "red"))
        return []
    
    print("\nFiltering URLs by file extensions...")
    extension_stats = {ext: [] for ext in file_extensions}
    
    for url in url_list:
        for ext in file_extensions:
            if url.lower().endswith(ext.lower()):
                extension_stats[ext].append(url)
    
    # Print stats for extensions that have URLs
    for ext, urls in extension_stats.items():
        if urls:
            print(f"Extension {ext} found: {len(urls)} URLs")
    
    return extension_stats

def check_wayback_snapshot(url):
    wayback_url = f'https://archive.org/wayback/available?url={url}'
    
    try:
        response = requests.get(wayback_url)
        response.raise_for_status()
        data = response.json()
        
        if "archived_snapshots" in data and "closest" in data["archived_snapshots"]:
            snapshot_url = data["archived_snapshots"]["closest"].get("url")
            if snapshot_url:
                print(f"Found possible backup: {colored(snapshot_url, 'green')}")
        else:
            print(f"No archived snapshot found for {url}.")
    except Exception as e:
        print(f"Error checking Wayback snapshot for {url}: {e}")

def save_urls(target, extension_stats, file_suffix="_filtered_urls.txt"):
    folder = f"content/{target}"
    os.makedirs(folder, exist_ok=True)
    
    all_filtered_urls = []
    for ext, urls in extension_stats.items():
        if urls:
            file_path = os.path.join(folder, f"{target}_{ext.strip('.')}"+file_suffix)
            with open(file_path, 'w') as file:
                file.write("\n".join(urls))
            all_filtered_urls.extend(urls)
            print(f"Filtered URLs for {ext} saved to: {colored(file_path, 'green')}")
    
    return all_filtered_urls

def process_domain(target, file_extensions):
    extension_stats = fetch_urls(target, file_extensions)
    all_filtered_urls = save_urls(target, extension_stats)
    for url in all_filtered_urls:
        check_wayback_snapshot(url)

if __name__ == "__main__":
    init()
    print(colored('    Coded with Love by Anmol K Sachan @Fr13ND0x7f\n', 'green'))

    # Input: Single or multiple domains
    mode = input("Select mode (1: Single Domain, 2: Multiple Domains): ").strip()
    if mode == "1":
        # Single Domain
        target = input("\nEnter the target domain (e.g., example.com): ").strip()
        if not target:
            print(colored("Target domain is required. Exiting.", "red"))
            exit()
        domains = [target]
    elif mode == "2":
        # Multiple Domains
        domain_file = input("\nEnter the path to the file containing domain list: ").strip()
        domains = load_domains_from_file(domain_file)
        print(f"Loaded {len(domains)} domains from {colored(domain_file, 'green')}.")
    else:
        print(colored("Invalid choice. Exiting.", "red"))
        exit()

    # Load default extensions from file
    default_extensions = load_extensions_from_file()

    # Ask user whether to use default extensions or input custom ones
    choice = input(f"Would you like to use custom file extensions or load from extensions.txt? (custom/load): ").strip().lower()

    if choice == "custom":
        file_extensions = input("Enter file extensions to filter (comma-separated, e.g., .zip,.pdf,.jpg): ").strip()
        file_extensions = [ext.strip() for ext in file_extensions.split(",") if ext.strip()]
        if not file_extensions:
            print(colored("No valid file extensions provided. Exiting.", "red"))
            exit()
    elif choice == "load" and default_extensions:
        file_extensions = default_extensions
        print(f"Loaded extensions from {colored('extensions.txt', 'green')}: {', '.join(file_extensions)}")
    else:
        print(colored("No extensions found. Exiting.", "red"))
        exit()

    # Process each domain
    for target in domains:
        print(colored(f"\nProcessing domain: {target}", "blue"))
        process_domain(target, file_extensions)

    print(colored("\nProcess complete for all domains.", "green"))

