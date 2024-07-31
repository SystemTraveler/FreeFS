import os
import sys

SECTOR_SIZE = 512

def format_disk(disk_path, total_size):
    with open(disk_path, 'wb') as disk:
        signature = 'FreeFS'.encode()
        disk.write(signature)
        disk.write(bytearray(SECTOR_SIZE - len(signature)))

        remaining_size = total_size - SECTOR_SIZE
        sectors = remaining_size // SECTOR_SIZE
        progress_step = sectors // 100

        for i in range(sectors):
            disk.write(bytearray(SECTOR_SIZE))
            if i % progress_step == 0:
                percent_complete = (i // progress_step)
                sys.stdout.write(f"\rFormatting disk: {percent_complete}% complete")
                sys.stdout.flush()

        disk.seek(total_size - SECTOR_SIZE)
        end_marker = 'END'.encode()
        disk.write(end_marker)
        disk.write(bytearray(SECTOR_SIZE - len(end_marker)))

    print("\nDisk formatted successfully.")
    print(f"Cleared {total_size} bytes.")
    print("Wrote 'FreeFS' signature to the first sector.")
    print("Wrote 'END' marker to the last sector.")

def main():
    disk_path = "./disk.img"
    total_size = 64 * 1024 * 1024
    format_disk(disk_path, total_size)

if __name__ == "__main__":
    main()
