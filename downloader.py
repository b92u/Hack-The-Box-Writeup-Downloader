#!/usr/bin/env python3

import sys, os, re, time, requests
from tqdm import tqdm

RED = "\033[1;31m"
GREEN = "\033[1;32m"
BLUE = "\033[1;34m"
YELLOW = "\033[1;33m"
RESET = "\033[0m"

def read_ids_to_ignore(filename):
    try:
        with open(filename, 'r') as file:
            return {int(line.strip()) for line in file if line.strip()}
    except FileNotFoundError:
        print(f"File {filename} not found. No ID will be ignored.")
        return set()

def sanitize_path(input_path):
    clean_path = re.sub(r'[^\w\s/-]', '', input_path) 
    clean_path = os.path.abspath(clean_path)
    return clean_path

def sanitize_filename(filename):
    return re.sub(r'[^\w\s-]', '', filename).strip()

def get_headers(token):
    return {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'curl/8.5.0'
    }

def get_machine_name(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['info']['name']
    else:
        print(f'Failed to get machine name: {response.status_code}')
        return None

def download_file(url, output_dir, machine_name, headers, failed_downloads, max_retries=3, wait_seconds=10):
    s_output_dir = sanitize_path(output_dir)
    s_machine_name = sanitize_filename(machine_name) 
    output_path = os.path.join(s_output_dir, f'{s_machine_name}.pdf')
   
    if not os.access(output_dir, os.W_OK):
        print(f"{RED}You cannot write in '{output_dir}'. Insufficient permissions.{RESET}")
        return

    for _ in range(max_retries):
        response = requests.get(url, headers=headers, stream=True)

        if response.status_code == 200:
            try:
                with open(output_path, 'wb') as file, tqdm(
                        total=int(response.headers.get('content-length', 0)),
                        unit='iB',
                        unit_scale=True,
                        bar_format="{l_bar}%s{bar}%s{r_bar}" % (BLUE, RESET)
                    ) as progress_bar:
                    for data in response.iter_content(1024):
                        progress_bar.update(len(data))
                        file.write(data)
                print(f'{YELLOW}File saved to: {output_path}{RESET}')
                return
            except Exception as e:
                print(f"{RED}ERROR, someting went wrong during file saving: {e}{RESET}")
                break
                
        elif response.status_code == 429:
            print(f'Rate limit reached. Retrying in {wait_seconds} seconds...')
            time.sleep(wait_seconds)
        else:
            print(f'{RED}Failed to download the file: {response.status_code}{RESET}')
            failed_downloads.append(machine_name)
            break
    print(f"{RED}Max retries reached. Failed to download the file.{RESET}")

def main():
    if len(sys.argv) < 3:
        print("Usage: ./downloader.py [TOKEN] [OUTPUT_DIR]")
        sys.exit(1)

    token = sys.argv[1]
    output_dir = sys.argv[2]
    max_id = 578
    failed_downloads = []
    headers = get_headers(token)
    ids_to_ignore = read_ids_to_ignore('ignore_list')

    if not os.path.isdir(output_dir):
        print(f"Error: The directory '{output_dir}' does not exist.")
        sys.exit(1)

    for machine_id in range(1, max_id + 1):
        if machine_id in ids_to_ignore:
            continue
        if machine_id % 6 == 0:
            print("Waiting 10 seconds to avoid rate limiting...")
            time.sleep(10)

        name_url = f'https://labs.hackthebox.com/api/v4/machine/profile/{machine_id}'
        machine_name = get_machine_name(name_url, headers)
        if not machine_name:
            print(f'Skipping ID {machine_id}: Machine name not found.')
            failed_downloads.append(machine_name)
            continue

        print(f'Downloading writeup for machine: {machine_name}')
        writeup_url = f'https://labs.hackthebox.com/api/v4/machine/writeup/{machine_id}'
        download_file(writeup_url, output_dir, machine_name, headers, failed_downloads)
    
    if failed_downloads:
        print("Download failed for the following machines: ")
        for machine_id in failed_downloads:
            print(f"{RED}https://app.hackthebox.com/machines/{machine_id}/writeups{RESET}")
        
if __name__ == "__main__":
    main()
