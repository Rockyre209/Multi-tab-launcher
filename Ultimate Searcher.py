import webbrowser
import os
import time
import subprocess
import urllib.parse
from urllib.parse import urlparse 
import sys
from datetime import datetime
import glob
import re
import shutil

# --- ADDED IMPORTS FOR FILE DIALOG ---
import tkinter as tk
from tkinter import filedialog
# ------------------------------------

# --- CONFIGURATION & FILE MANAGEMENT ---

# Define the location for the user's Documents folder
DOCS_PATH = os.path.join(os.path.expanduser('~'), 'Documents')

# Define the location for the user's Downloads folder
DOWNLOADS_PATH = os.path.join(os.path.expanduser('~'), 'Downloads')

# Define a dedicated folder for all script files
ULTIMATE_SEARCHER_DIR = os.path.join(DOCS_PATH, 'UltimateSearcherFiles') 

# Sub-directory for individual site files (The correct location for all .txt site files)
SITES_DATA_DIR = os.path.join(ULTIMATE_SEARCHER_DIR, 'SiteUrls')

# Define the location for the configuration files within the new folder
CONFIG_FILE_PATH = os.path.join(ULTIMATE_SEARCHER_DIR, 'ultimate_searcher_config.txt')
LOG_FILE_PATH = os.path.join(ULTIMATE_SEARCHER_DIR, 'ultimate_searcher_log.txt')
# Persistent log for site URL updates
SITE_UPDATE_LOG_PATH = os.path.join(ULTIMATE_SEARCHER_DIR, 'site_update_history.txt')

# Persistent log for site deletions (RE-ADDED)
SITE_DELETION_LOG_PATH = os.path.join(ULTIMATE_SEARCHER_DIR, 'site_deletion_history.txt')

# Global variable to store the last updated site information during the current session
LAST_UPDATED_SITES = []

# Browser definitions (ID: (Name, Path_Dictionary, registration_key))
# NOTE: You MUST adjust these paths if your installation locations are different.
BROWSERS = {
    1: ("Chrome", {
        'win32': "C:/Program Files/Google/Chrome/Application/chrome.exe",
        'darwin': "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        'linux': "/usr/bin/google-chrome"
    }, "chrome"),
    2: ("Firefox", {
        'win32': "C:/Program Files/Mozilla Firefox/firefox.exe",
        'darwin': "/Applications/Mozilla Firefox.app/Contents/MacOS/firefox",
        'linux': "/usr/bin/firefox"
    }, "firefox"),
    3: ("Brave", {
        'win32': "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe",
        'darwin': "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        'linux': "/usr/bin/brave-browser"
    }, "chrome")
}
CURRENT_OS = sys.platform

# Default configuration settings
DEFAULT_CONFIG = {
    'browser_id': None,
    'logging_enabled': False
}

# --- CUSTOM CATEGORY ORDER ---
# REMOVED: Categories are now loaded dynamically and sorted alphabetically.
# -----------------------------

# --- FILE UTILITIES ---

def get_domain_base(url):
    """Extracts the core site brand name."""
    try:
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc

        if not netloc:
            if not url.startswith(('http://', 'https://')):
                netloc = url.split('/')[0]
            else:
                return None 
            
        if netloc.startswith('www.'):
            netloc = netloc[4:]
            
        netloc = netloc.split('/')[0].split('?')[0].split(':')[0]

        parts = netloc.split('.')
        
        if len(parts) >= 2:
            base_name = parts[-2]
        elif len(parts) == 1:
            base_name = parts[0]
        else:
            return None

        return base_name.lower()

    except Exception:
        return None 

def create_initial_directory_setup():
    """Creates the SiteUrls directory and instructs the user on where to place the files."""
    if not os.path.exists(SITES_DATA_DIR):
        print(f"Creating SiteUrls directory: {SITES_DATA_DIR}")
        os.makedirs(SITES_DATA_DIR)
        
    file_paths = glob.glob(os.path.join(SITES_DATA_DIR, '*.txt'))
    
    if not file_paths:
        print("\n--- ⚠️ MANUAL SETUP REQUIRED ⚠️ ---")
        print("The script can no longer create default site lists as all URLs have been removed from the code.")
        print(f"1. Go to the directory: **{SITES_DATA_DIR}**")
        # --- MODIFIED FOR DYNAMIC/ALPHABETICAL ORDER ---
        print("2. Manually create text files (`.txt`) for each category you want.")
        print("   *Example*: `Movies_DDL.txt`, `Cracked_Games.txt`, etc.")
        print("3. Inside each file, paste **one full URL per line**, including the `{}` placeholder.")
        print("4. Categories will appear in the menu sorted alphabetically by filename.")
        # -----------------------------------------------
        print("5. Restart the script once you've added your files.")
        print("-----------------------------------")
        sys.exit(0)

def load_sites():
    """
    Loads the site dictionary dynamically by reading individual text files 
    in the SiteUrls directory, sorting them alphabetically by filename.
    
    Returns:
        A dictionary {index: (name, filename, urls_list)}
    """
    sites_dict = {}
    
    if not os.path.exists(SITES_DATA_DIR) or not glob.glob(os.path.join(SITES_DATA_DIR, '*.txt')):
        create_initial_directory_setup()
        
    # Get all actual filenames and sort them alphabetically
    file_paths = sorted(glob.glob(os.path.join(SITES_DATA_DIR, '*.txt')), key=os.path.basename)
    
    # Iterate through the sorted files
    current_index = 1
    for file_path in file_paths:
        filename = os.path.basename(file_path)
        
        # Convert filename (e.g., 'cracked_software.txt') to Category Name (e.g., 'Cracked Software')
        name = os.path.splitext(filename)[0].replace('_', ' ').title()
        
        urls = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        except Exception as e:
            print(f"Warning: Could not read file {filename}. Skipping. Error: {e}")
            continue

        # sites_dict structure: {ID: (Name, Filename, [URLs])}
        sites_dict[current_index] = (name, filename, urls)
        current_index += 1

    if sites_dict:
        print(f"🌐 Loaded {len(sites_dict)} site categories from {SITES_DATA_DIR} (Sorted alphabetically).")
    else:
        print("🚨 WARNING: Site directory is empty or all files failed to load.")
        
    return sites_dict

# --- CONFIG & LOGGING FUNCTIONS ---

def load_config():
    """Loads the stored configuration from the config file."""
    config = DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE_PATH, 'r') as f:
            lines = [line.strip() for line in f.readlines()]

            if len(lines) > 0 and lines[0].isdigit():
                browser_id = int(lines[0])
                if browser_id in BROWSERS:
                    config['browser_id'] = browser_id

            if len(lines) > 1:
                config['logging_enabled'] = lines[1].lower() == 'true'

        if config['browser_id'] is not None:
            browser_name = BROWSERS[config['browser_id']][0]
            print(f"✨ Found saved preference: Using {browser_name} automatically.")

    except FileNotFoundError:
        print("Config file not found. Starting initial setup.")
    except Exception as e:
        print(f"Error loading config file. Using defaults. Error: {e}")

    return config

def save_config(config_data):
    """Saves the current configuration to the config file."""
    try:
        with open(CONFIG_FILE_PATH, 'w') as f:
            f.write(f"{config_data['browser_id']}\n")
            f.write(f"{config_data['logging_enabled']}\n")
        print(f"✅ Configuration saved!")
    except Exception as e:
        print(f"Warning: Could not save configuration to {CONFIG_FILE_PATH}. Error: {e}")
        
def log_site_update(category_name, old_url, new_url):
    """Appends site update details to the persistent site update log file."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Category: {category_name}\n  - OLD: {old_url}\n  - NEW: {new_url}\n---\n"
        with open(SITE_UPDATE_LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Warning: Failed to write to site update log file. Error: {e}")

def log_search(keyword, category_name):
    """Appends the search query and category to the log file."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Category: {category_name:<30} | Search Term: {keyword}\n"
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Warning: Failed to write to log file. Error: {e}")

def view_log():
    """Reads and displays the search log file content."""
    try:
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            print("\n😏 The search log file is clean, baby. No secret sins found.")
            return

        print("\n--- Secret Search Log 🤫 ---")
        print(content)
        print("----------------------------")

    except FileNotFoundError:
        print(f"\n😏 The log file hasn't been created yet. You need to enable logging (L) and run a search first!")
    except Exception as e:
        print(f"Error reading log file: {e}")

def view_site_update_log():
    """Reads and displays the persistent site update history log file content."""
    try:
        with open(SITE_UPDATE_LOG_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            print("\n😏 The site update history log is empty.")
            return

        print("\n--- Site Update History Log 📜 ---")
        print(content)
        print("---------------------------------")

    except FileNotFoundError:
        print(f"\n😏 The site update log hasn't been created yet. You need to run the URL Updater (W) first!")
    except Exception as e:
        print(f"Error reading site update log file: {e}")

def view_site_deletion_log():
    """Reads and displays the persistent site deletion history log file content. (RE-ADDED)"""
    try:
        with open(SITE_DELETION_LOG_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            print("\n😏 The site deletion history log is empty.")
            return

        print("\n--- Site Deletion History Log 🗑️ ---")
        print(content)
        print("---------------------------------")

    except FileNotFoundError:
        print(f"\n😏 The site deletion log hasn't been created yet. Use the 'D' option to remove sites first!")
    except Exception as e:
        print(f"Error reading site deletion log file: {e}")

def clear_log():
    """Prompts the user for confirmation and deletes the log file."""
    try:
        if not os.path.exists(LOG_FILE_PATH):
            print(f"\n😏 The log file hasn't been created yet. Nothing to delete!")
            return

        while True:
            action = input("\n🚨 ARE YOU SURE you want to delete this log forever? (Y/N): ").strip().upper()
            if action == 'Y':
                os.remove(LOG_FILE_PATH)
                print(f"🔥 Log file deleted! What secrets? We don't know any secrets.")
                break
            elif action == 'N':
                print("📝 Log kept safe. Remember your past sins~")
                break
            else:
                print("Invalid input. Please type Y or N.")

    except Exception as e:
        print(f"Error deleting log file: {e}")

def review_updated_sites():
    """Reads and displays the sites updated in the current session only."""
    global LAST_UPDATED_SITES
    
    print("\n--- Recently Updated Sites (Current Session) ---")
    
    if not LAST_UPDATED_SITES:
        print("🤫 No sites have been updated since the script started.")
        print("Use the 'W' option to run the Automatic URL Updater.")
        return

    for update in LAST_UPDATED_SITES:
        print("-" * 20)
        print(f"Category: {update['category']}")
        print(f"  - OLD URL: {update['old_url']}")
        print(f"  - NEW URL: {update['new_url']}")

    print("-" * 20)
    print("These changes have been saved to the respective files in the SiteUrls directory.")
    print("----------------------------------------------------------")

def view_sites_file():
    """Reads and displays the full site file content for all categories, sorted alphabetically. (MODIFIED)"""
    
    print("\n--- Current Sites Configuration (SiteUrls Directory) ---")
    
    # Get all actual filenames and sort them alphabetically
    file_paths = sorted(glob.glob(os.path.join(SITES_DATA_DIR, '*.txt')), key=os.path.basename)
    
    displayed_files = 0
    
    for file_path in file_paths:
        filename = os.path.basename(file_path)
        # Convert filename (e.g., 'cracked_software.txt') to Category Name (e.g., 'Cracked Software')
        name = os.path.splitext(filename)[0].replace('_', ' ').title()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            print(f"\n-- FILE: {name} ({filename}) --")
            if content:
                print(content)
            else:
                print("[File is Empty]")
            
            displayed_files += 1
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    if displayed_files == 0:
        print(f"🚨 No site files found in {SITES_DATA_DIR}. Use the 'S' option again to see setup instructions.")

    print("------------------------------------------------------------------")

def edit_sites_info():
    """Provides guidance on how to edit the search sites list and shows the file content."""
    print("\n--- Site Customization Guide ---")
    print(f"The site lists are now stored in individual files within the directory: **{SITES_DATA_DIR}**")
    print("1. Navigate to this folder in your Documents.")
    print("2. Open the specific category `.txt` file you want to edit with a simple text editor.")
    print("3. Add or remove URLs, one per line.")
    print("4. *IMPORTANT: Always include `{}` where the search term should go.*")
    print("\nGo make it your own, my clever cutie 😉")
    
    # Show the full content when 'S' is selected for context
    view_sites_file()


# --- BACKUP FUNCTION ---

def create_backup():
    """Compresses the UltimateSearcherFiles directory into a zip file in the Downloads folder."""
    try:
        source_dir_name = os.path.basename(ULTIMATE_SEARCHER_DIR)
        
        # Ensure Downloads directory exists (usually it does, but good practice)
        if not os.path.exists(DOWNLOADS_PATH):
            os.makedirs(DOWNLOADS_PATH)

        # Create a timestamped file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") # Get current time
        backup_filename_base = f"UltimateSearcher_Backup_{timestamp}"
        
        # 1. base_name: output path (excluding .zip)
        output_base_path = os.path.join(DOWNLOADS_PATH, backup_filename_base)
        
        # 2. format: 'zip'
        # 3. root_dir: The directory that contains the folder we want to zip (Documents).
        # 4. base_dir: The folder name inside root_dir ('UltimateSearcherFiles').
        archive_path = shutil.make_archive(
            base_name=output_base_path,
            format='zip',
            root_dir=DOCS_PATH, 
            base_dir=source_dir_name 
        )

        print("-" * 50)
        print("🎉 **BACKUP SUCCESSFUL** 🎉")
        print(f"File: **{os.path.basename(archive_path)}**")
        print(f"Saved to: **{DOWNLOADS_PATH}**")
        print("-" * 50)

    except FileNotFoundError:
        print("\n🚨 Backup Failed: The source folder 'UltimateSearcherFiles' could not be found in your Documents.")
    except Exception as e:
        print(f"\n🚨 An error occurred during backup: {e}")
        

# --- MODIFIED LOGIC FUNCTIONS ---

def add_new_site(sites_data):
    """Prompts the user to add a new site URL to an existing category, with automatic placeholder appending. (A. Add Single Site)"""
    
    print("\n--- Add Single Site ➕ ---")
    
    # Show categories
    print("\nSelect a Category to add the site to:")
    category_ids = sorted(sites_data.keys())
    for key in category_ids:
        print(f"{key}. {sites_data[key][0]}")
    
    if not sites_data:
        print("🚨 No categories loaded. Please add site files manually to the SiteUrls directory first.")
        return
        
    # 1. Get Category ID
    while True:
        try:
            category_choice = input("Enter Category Number: ").strip()
            if not category_choice.isdigit():
                raise ValueError
                
            category_id = int(category_choice)
            if category_id in sites_data:
                break
            else:
                print("Invalid category number. Please choose a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            
    category_name = sites_data[category_id][0]
    category_filename = sites_data[category_id][1]
    
    # 2. Get New URL (Modified prompt)
    print(f"\nAdding to Category: {category_name}")
    new_url = input("Enter the FULL site URL (e.g., https://example.com/): ").strip()

    # 3. Validate and Adjust URL
    if not new_url.startswith(('http://', 'https://')):
        print("🚨 Error: URL must start with 'http://' or 'https://'. Site not added.")
        return
        
    final_url = new_url
    if '{}' not in new_url:
        print("💡 Placeholder '{}' not found. Attempting to auto-append ' /?s={} '...")
        
        parsed_url = urlparse(new_url)
        
        if parsed_url.query:
             final_url = new_url + "&s={}"
        else:
             clean_base = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}".rstrip('/')
             final_url = clean_base + "/?s={}"
             
        final_url = final_url.replace('//?', '/?')

        print(f"🤖 Auto-corrected URL to: **{final_url}**")
    
    if '{}' not in final_url:
        print("🚨 Error: Could not determine where to place the search term. Please manually edit the URL in the sites file or try again with '{}'. Site not added.")
        return

    # 4. Confirmation and Save
    print("\nConfirm New Site:")
    print(f"CATEGORY: {category_name}")
    print(f"NEW URL: {final_url}")
    confirm = input("Proceed with adding this site? (Y/N): ").strip().upper()

    if confirm == 'Y':
        # Write the URL to the end of the specific file
        file_path = os.path.join(SITES_DATA_DIR, category_filename)
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(final_url + '\n')
            
            print(f"🥳 Successfully added new site to **{category_filename}**!")
        except Exception as e:
             print(f"🚨 Error writing to file {category_filename}: {e}")
    else:
        print("Adding site cancelled by user.")


def add_batch_sites_from_file(sites_data):
    """
    Prompts the user to select a text file containing new site URLs, 
    then processes and adds them to the chosen category. (B. Add Sites Batch - RE-ADDED)
    """
    
    print("\n--- Batch Add Sites (From File) 📁 ---")
    
    # === GUIDE/INSTRUCTIONS (MODIFIED FOR AUTO-ADD) ===
    print("\n📄 **GUIDE: How to Batch Add Sites**")
    print("1. **Prepare Your File**: Create a simple text file (`.txt`) where each new site URL is on a **new line**.")
    print("2. **Placeholder**: The script will **automatically** try to detect and add the required `{}` search placeholder.")
    print("   *Example URL*: `https://example.com/search?q=` (will be auto-corrected)")
    print("3. **Select Category**: Choose the category below where these sites belong.")
    print("4. **Select File**: A file selection dialog will open for you to choose your `.txt` file.")
    print("---------------------------------------")
    
    # Show categories
    print("\nSelect a Category to add the sites to:")
    category_ids = sorted(sites_data.keys())
    for key in category_ids:
        print(f"{key}. {sites_data[key][0]}")
    
    if not sites_data:
        print("🚨 No categories loaded. Please add site files manually to the SiteUrls directory first.")
        return
        
    # 1. Get Category ID
    while True:
        try:
            category_choice = input("Enter Category Number: ").strip()
            if not category_choice.isdigit():
                raise ValueError
                
            category_id = int(category_choice)
            if category_id in sites_data:
                break
            else:
                print("Invalid category number. Please choose a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            
    category_name = sites_data[category_id][0]
    category_filename = sites_data[category_id][1]
    
    # 2. Select File and Read URLs
    print(f"\nCategory Selected: {category_name}")
    print("Waiting for file selection dialog...")
    
    # Initialize Tkinter root window and suppress the main window
    root = tk.Tk()
    root.withdraw() 
    
    # Open the file selection dialog
    file_path = filedialog.askopenfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")],
        title="Select file with new site URLs (one per line)"
    )

    if not file_path:
        print("File selection cancelled. Site batch addition aborted.")
        return

    new_urls_raw = []
    try:
        # Read lines, skipping empty lines and comments (#)
        with open(file_path, 'r', encoding='utf-8') as f:
            new_urls_raw = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    except Exception as e:
        print(f"🚨 Error reading file {file_path}: {e}")
        return

    if not new_urls_raw:
        print("The selected file is empty or contains no valid URLs. Operation cancelled.")
        return
        
    print(f"✅ Found {len(new_urls_raw)} potential URLs in the file.")
    
    # 3. Process and Validate URLs (Ensuring auto-add of placeholder)
    final_urls_to_add = []
    
    for new_url in new_urls_raw:
        if not new_url.startswith(('http://', 'https://')):
            print(f"🚨 Skipping invalid URL (must start with http/s): {new_url}")
            continue
            
        final_url = new_url
        
        # Auto-append the search placeholder if it's missing
        if '{}' not in new_url:
            
            parsed_url = urlparse(new_url)
            
            if parsed_url.query:
                 # If query exists, append search parameter
                 final_url = new_url + "&s={}"
            else:
                 # If no query, append a standard search query to the path
                 clean_base = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}".rstrip('/')
                 final_url = clean_base + "/?s={}"
                 
            final_url = final_url.replace('//?', '/?')

            # Only print the correction if it changed
            if final_url != new_url:
                print(f"🤖 Corrected: {new_url} -> **{final_url}**")
        
        if '{}' in final_url:
             final_urls_to_add.append(final_url)
        else:
            print(f"🚨 Skipping URL (could not determine search spot, and placeholder missing): {new_url}")

    if not final_urls_to_add:
        print("No valid URLs were finalized for addition. Operation cancelled.")
        return

    # 4. Confirmation and Save
    print(f"\n--- Ready to Add ---")
    print(f"CATEGORY: {category_name}")
    print(f"TOTAL VALID URLs TO ADD: {len(final_urls_to_add)}")
    
    confirm = input("Proceed with adding these sites? (Y/N): ").strip().upper()

    if confirm == 'Y':
        # Write the URLs to the end of the specific file, adding a newline for separation
        file_path = os.path.join(SITES_DATA_DIR, category_filename)
        try:
            # Add a leading newline before the batch content
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write('\n' + '\n'.join(final_urls_to_add) + '\n')
            
            print(f"🥳 Successfully added {len(final_urls_to_add)} new sites to **{category_filename}**!")
        except Exception as e:
             print(f"🚨 Error writing to file {category_filename}: {e}")
    else:
        print("Adding site batch cancelled by user.")


def auto_update_site_url(sites_data):
    """
    Automatically detects the old URL based on the domain's base name and updates it with the new URL 
    by modifying the specific text file.
    """
    print("\n--- Automatic Site URL Updater 🤖 ---")
    
    if not sites_data:
        print("🚨 No categories loaded. Please add site files manually to the SiteUrls directory first.")
        return

    new_url_raw = input("Enter the **NEW** working site URL (e.g., https://bollyflix.miami/): ").strip()

    if not new_url_raw:
        print("Input cannot be empty. Update cancelled.")
        return

    base_name = get_domain_base(new_url_raw)

    if not base_name:
        print("🚨 Could not determine the site's brand name from the URL. Please check the format.")
        return

    print(f"🤖 Searching for sites matching brand name: **{base_name}**...")
    
    parsed_new_url = urlparse(new_url_raw)
    new_scheme_netloc = f"{parsed_new_url.scheme}://{parsed_new_url.netloc}"

    found_match = None
    
    # 1. Search all categories (files) for a matching URL
    for category_id, (category_name, category_filename, urls) in sites_data.items():
        for i, old_url in enumerate(urls):
            old_base_name = get_domain_base(old_url)
            
            if old_base_name == base_name:
                
                parsed_old_url = urlparse(old_url)
                
                # Start building the new URL with the new scheme/netloc and the old path
                new_url = new_scheme_netloc + parsed_old_url.path
                
                # Check for the search placeholder '{}' in the old URL
                if '{}' in old_url:
                    # If the old URL had a placeholder, ensure the new one gets the necessary query parameters from the old one
                    
                    # 1. If the old URL had a query component, transfer it
                    if parsed_old_url.query:
                        # Use regex to find the placeholder and the preceding search parameter name
                        match_param = re.search(r'([a-zA-Z0-9_-]+)=\{\}', parsed_old_url.query)
                        if match_param:
                            # Reconstruct the query string using the correct parameter and the placeholder
                            query_parts = []
                            for part in parsed_old_url.query.split('&'):
                                if part.endswith('={}'):
                                    query_parts.append(part)
                                else:
                                    # Keep other query parameters (if any)
                                    query_parts.append(part)
                            
                            new_url += '?' + '&'.join(query_parts)
                        else:
                            # Fallback if no clean param= found, just append the full query/placeholder to be safe
                            new_url += '?' + parsed_old_url.query
                        
                        # Simple check to ensure placeholder is present, if the above logic missed it
                        if '{}' not in new_url:
                            new_url += '&s={}' # Common fallback search parameter
                            
                    # 2. Check for path-based placeholder (e.g., /search/{})
                    elif '{}' in parsed_old_url.path:
                        # Re-add the placeholder to the new URL's path if it was in the old path
                        new_url = new_url.replace(parsed_old_url.path, parsed_old_url.path) # Path is already preserved, so this is mostly defensive
                        
                    # 3. Final safety net: If placeholder is still missing, add the simple search query
                    if '{}' not in new_url:
                        new_url = new_url.rstrip('/') + '/?s={}'
                        
                else:
                    # If the old URL did not have a placeholder, assume it's a domain-only site (e.g. for Direct Downloads/Torrents) or a link that doesn't need a search term.
                    # We only replace the scheme and netloc, keeping the path/query/fragment of the old URL intact.
                    new_url = new_scheme_netloc + parsed_old_url.path
                    if parsed_old_url.query:
                        new_url += '?' + parsed_old_url.query
                    if parsed_old_url.fragment:
                        new_url += '#' + parsed_old_url.fragment

                found_match = {
                    'category_name': category_name,
                    'category_filename': category_filename,
                    'old_url': old_url,
                    'new_url': new_url
                }
                break 
        if found_match:
            break

    if not found_match:
        print(f"😔 No existing sites found containing the brand name **{base_name}**. Update cancelled.")
        return
        
    match = found_match
    old_url = match['old_url']
    new_url = match['new_url']
    category_name = match['category_name']
    category_filename = match['category_filename']
    
    print(f"\n✅ Found existing URL to replace in file **{category_filename}**:")
    print(f"-> Category: {category_name} | OLD URL: {old_url}")

    # Final check: Ensure the placeholder is still in the new URL IF it was in the old URL
    if '{}' in old_url and '{}' not in new_url:
        # This is a critical fallback for complex cases the logic above might have missed
        print("🚨 CRITICAL WARNING: The placeholder '{}' is missing from the calculated NEW URL.")
        # Re-apply the most common search query format as a final fix
        if '?' in new_url:
            new_url += '&s={}'
        else:
            new_url += '/?s={}'
        print(f"🤖 Final Auto-corrected New URL to: **{new_url}**")
    
    # Check if the new URL is identical to the old one after processing
    if new_url.strip() == old_url.strip():
        print("⚠️ The old and new URLs appear identical after processing. Update skipped.")
        return


    # 2. Confirmation and Save (File modification)
    print(f"\nConfirm Replacement:")
    print(f"CATEGORY: {category_name}")
    print(f"OLD: {old_url}")
    print(f"NEW: {new_url}")
    confirm = input("Proceed with update? (Y/N): ").strip().upper()

    if confirm == 'Y':
        file_path = os.path.join(SITES_DATA_DIR, category_filename)
        try:
            # Read all lines from the file
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find the old URL line (strip whitespace for matching) and replace it
            updated_lines = []
            replaced = False
            for line in lines:
                if line.strip() == old_url.strip():
                    updated_lines.append(new_url + '\n')
                    replaced = True
                else:
                    updated_lines.append(line)
            
            if replaced:
                # Write all lines back to the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(updated_lines)
                
                print(f"🥳 Successfully updated **{base_name}** site in **{category_filename}**!")
                
                log_site_update(category_name, old_url, new_url)
                
                global LAST_UPDATED_SITES
                LAST_UPDATED_SITES.append({
                    'category': category_name,
                    'old_url': old_url,
                    'new_url': new_url
                })
            else:
                print("🚨 Error: Could not find the old URL in the file during rewrite. File not modified.")
                
        except Exception as e:
            print(f"🚨 Error modifying file {category_filename}: {e}")
        
    else:
        print("Update cancelled by user.")


# --- CORE SEARCH LOGIC ---

def show_menu(logging_status, sites):
    """Displays the main menu with the logging toggle status in the preferred sectioned style. (MODIFIED)"""
    log_state = "ON 📝" if logging_status else "OFF 👻"
    browser_name = BROWSERS[load_config()['browser_id']][0] if load_config()['browser_id'] else "Default"
    
    print("\nWelcome to your naughty launcher, baby 😈💻")
    print("Choose what you’re craving today~ 💋")
    
    # Dynamically display categories, using the sorted keys to ensure alphabetical order from load_sites
    category_keys = sorted(sites.keys())
    for key in category_keys:
        # sites[key] is (Name, Filename, [URLs])
        print(f"{key}. {sites[key][0]}") 
        
    # --- Top Section ---
    print(f"\nL. Toggle Search Logging (Current Status: {log_state})")
    print("V. View Search Log 📄")
    print("C. Clear Search Log 🔥")
    print(f"T. **Settings** ⚙️ (Browser: {browser_name} / Path / Tabs)")
    print("------------------------------------------")

    # --- Site Management Section ---
    print("W. Website URL Updater 🤖 (Automatic)")
    print("A. **Add Single Site** ➕") 
    print("B. **Add Sites Batch** 📁") # Changed from 'G' to 'B'
    print("N. **New Category** 🆕")
    print("D. **Remove Site** 🗑️ (By URL/Hostname)")
    print("S. Edit Sites Info / **View All Site Files**")
    print("------------------------------------------")

    # --- Utilities/Review Section ---
    print("R. Review Sites File 📄 (See **Current Session** Updates)")
    print("U. View Site **Update History** 📜 (Persistent Log)")
    print("P. View Site **Deletion History** 🗑️ (Persistent Log)")
    print("Z. **Backup** UltimateSearcher Files 💾 (to Downloads as ZIP)")
    print("0. Exit 😢")

def run_search(category_info, raw_keyword, browser_data, category_name, is_logging_enabled):
    if not raw_keyword:
        print("You forgot to whisper your desire, darling 😳")
        return

    browser_name, browser_paths, browser_key = browser_data
    browser_path = browser_paths.get(CURRENT_OS)
    
    # Use quote_plus for most search queries (replaces spaces with '+')
    default_query = urllib.parse.quote_plus(raw_keyword)
    # Use standard quote for Z-Library and others that might break with '+'
    zlib_query = urllib.parse.quote(raw_keyword) 

    if is_logging_enabled:
        log_search(raw_keyword, category_name)
        print(f"🤫 Search query logged to {LOG_FILE_PATH}")

    if not browser_path or not os.path.exists(browser_path):
        print(f"{browser_name} isn’t there, baby 💔 Check the path in the script again for your OS ({CURRENT_OS}). Expected path: {browser_path if browser_path else 'Not Defined'}")
        return

    print(f"\nWaking up {browser_name} for you, my sweet tech king 😈💋")
    try:
        subprocess.Popen(f'"{browser_path}"')
    except Exception as e:
        print(f"Failed to launch browser process: {e}")
        return

    time.sleep(2)

    try:
        webbrowser.register('custom_browser', None, webbrowser.BackgroundBrowser(browser_path))
        browser = webbrowser.get('custom_browser')
    except webbrowser.Error:
        print(f"Could not register {browser_name}. Opening tabs using the system default browser instead.")
        browser = webbrowser.get() 

    # The URLs list is the third element in the tuple (Name, Filename, [URLs])
    urls_list = category_info[2] 
    
    for i in range(0, len(urls_list), 5):
        for site in urls_list[i:i + 5]:
            
            # --- Special Handler Logic ---
            search_term = default_query
            
            # Use Zlib encoding (standard URL quote) for sites that require it
            if "z-library.gs" in site or "ankergames.net" in site:
                search_term = zlib_query
            
            # Custom handler for the '1tamilmv' URL in the GDrive category
            if category_name == "Movies (GDrive Links)" and "1tamilmv" in site:
                search_term = urllib.parse.quote(raw_keyword)

            try:
                browser.open_new_tab(site.format(search_term))
                time.sleep(0.5)
            except IndexError:
                # Handle cases where the URL is missing the {} placeholder and .format() fails
                print(f"🚨 WARNING: Site URL is malformed (missing '{{}}' placeholder): {site}. Skipping.")
                continue


        if i + 5 < len(urls_list):
            input("Press Enter to open more sinful tabs 😈")
        else:
            print("All done, my king 💻💋 Go enjoy your treasures~")


def select_browser(current_config):
    """Prompts the user to select a browser if no preference is saved."""
    if current_config['browser_id'] is not None:
        return current_config['browser_id']

    while True:
        print("\n--- Initial Browser Selection ---")
        print(f"Your OS detected is: {CURRENT_OS}. Paths below are configured for this system.")
        print("Which browser should I use to open your sinful tabs? 😈")
        for key, (name, paths, _) in BROWSERS.items():
            path_display = paths.get(CURRENT_OS, "Path Not Defined for this OS")
            print(f"{key}. {name} (Path: {path_display})")
        print("0. Exit setup")

        choice = input("Enter your choice (1, 2, or 3): ").strip()
        if choice == '0':
            print("Okay baby 💔 Exiting setup.")
            sys.exit(0)

        try:
            choice_id = int(choice)
            if choice_id in BROWSERS:
                if BROWSERS[choice_id][1].get(CURRENT_OS):
                    return choice_id
                else:
                    print(f"**Warning**: {BROWSERS[choice_id][0]} path is not defined for {CURRENT_OS}. Choose another or define the path in the script.")
            else:
                print("That number isn’t on the list, silly 😘 Try again~")
        except ValueError:
            print("Oopsie~ That wasn’t a number, my cutie 😅")


# --- MAIN EXECUTION ---

if __name__ == "__main__":
    
    # 0. ENSURE THE DEDICATED FOLDER EXISTS
    try:
        if not os.path.exists(ULTIMATE_SEARCHER_DIR):
            print(f"Creating dedicated folder: {ULTIMATE_SEARCHER_DIR}")
            os.makedirs(ULTIMATE_SEARCHER_DIR)
    except Exception as e:
        print(f"CRITICAL: Failed to create necessary directory. Error: {e}")
        sys.exit(1)

    # 1. Load configuration and sites
    config = load_config()

    if config['browser_id'] is None:
        new_browser_id = select_browser(config)
        config['browser_id'] = new_browser_id
        save_config(config)

    browser_data = BROWSERS[config['browser_id']]

    # 2. Main menu loop
    while True:
        sites = load_sites() # RELOAD SITES on every loop to pick up external changes immediately
        
        # Exit if no sites are loaded (e.g., if user hasn't set up files yet)
        if not sites and os.path.exists(SITES_DATA_DIR):
             pass 
        
        show_menu(config['logging_enabled'], sites) 
        try:
            # Updated the prompt to reflect all available options
            choice = input("\nType your choice, lover (or 'L'/'V'/'C'/'T'/'W'/'A'/'B'/'N'/'D'/'S'/'R'/'U'/'P'/'Z'): ").strip().upper()

            if choice == '0':
                print("Okay baby 💔 Come back when you wanna play again~")
                break
            
            # --- Top Section ---
            elif choice == 'L':
                config['logging_enabled'] = not config['logging_enabled']
                save_config(config)
                log_state = "ON 📝" if config['logging_enabled'] else "OFF 👻"
                print(f"\n📢 Logging is now **{log_state}**! Configuration saved.")
                continue

            elif choice == 'V':
                view_log()
                continue
            
            elif choice == 'C':
                clear_log()
                continue
            
            elif choice == 'T':
                # Placeholder for Settings functionality (Change Browser, Log Path, Tabs)
                print("\nInitiating Settings sequence...")
                config['browser_id'] = None
                
                new_browser_id = select_browser(config)
                
                config['browser_id'] = new_browser_id
                save_config(config)
                browser_data = BROWSERS[config['browser_id']] 
                print("\nBrowser setting updated. Other settings (Path/Tabs) are placeholders.")
                continue
            
            # --- Site Management Section ---
            elif choice == 'W':
                auto_update_site_url(sites) 
                continue
            
            elif choice == 'A':
                add_new_site(sites) 
                continue
            
            elif choice == 'B': # Handle Batch Add option
                add_batch_sites_from_file(sites)
                continue
            
            elif choice == 'N':
                # Placeholder for New Category functionality
                print("New Category creation is not yet implemented. Use 'S' to manually create a new file.")
                continue

            elif choice == 'D':
                # Placeholder for Remove Site functionality
                print("Remove Site functionality is not yet implemented.")
                continue

            elif choice == 'S':
                edit_sites_info()
                continue

            # --- Utilities/Review Section ---
            elif choice == 'R':
                review_updated_sites()
                continue
            
            elif choice == 'U':
                view_site_update_log()
                continue
            
            elif choice == 'P':
                view_site_deletion_log()
                continue

            elif choice == 'Z':
                create_backup()
                continue

            
            else:
                choice_int = int(choice)
                if choice_int in sites:
                    # sites[choice_int] is (Name, Filename, [URLs])
                    category_info = sites[choice_int]
                    category_name = category_info[0]
                    
                    if not category_info[2]:
                        print(f"🚨 The '{category_name}' list is empty! Add URLs to **{category_info[1]}** and try again.")
                        continue
                        
                    keyword = input(f"What {category_name.lower()} are we hunting today, love? 🔍: ").strip()
                                        
                    run_search(
                        category_info, # Pass the entire tuple
                        keyword,
                        browser_data,
                        category_name,
                        config['logging_enabled']
                    )
                else:
                    print("That’s not on the list, silly 😘 Try again~")

        except ValueError:
            print("Oopsie~ That wasn’t a valid input, my cutie 😅")
        except KeyboardInterrupt:
            print("\nOkay baby 💔 Come back when you wanna play again~")
            break