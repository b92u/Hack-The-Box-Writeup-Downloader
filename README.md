**Note: For this script to work, you must have a VIP/VIP+ account on Hack the Box to access the writeup files.** 

## Prerequisites
- Python 3
- `requests` library
- `tqdm` library for progress bars

## Instructions
1. Ensure Python 3 is installed on your system.
2. Install the required Python packages:
   ```bash
   pip install requests tqdm
   ```
3. Clone the repo or keep the *ignore_list* file in the same directory as *downloader.py* 
4. Go to your account settings page on Hack the Box and generate a token with *CREATE APP TOKEN*. Run the script from the command line with the required arguments:

```bash
./downloader.py [TOKEN] [OUTPUT_DIR]
```

- `[TOKEN]`: Your authentication token for the API.
- `[OUTPUT_DIR]`: The directory where the downloaded files will be saved.

5. Official writeups will be downloaded to the specified directory named just like machines are in Hack the Box. 
