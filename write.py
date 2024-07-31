import os
import time

SECTOR_SIZE = 512
BUFFER_SIZE = 1024 * 1024

def find_next_free_sector(disk, total_size):
    disk.seek(SECTOR_SIZE)
    buffer = disk.read(SECTOR_SIZE)
    sector_num = 1

    while buffer:
        if buffer.strip(b'\x00'):
            disk.seek(SECTOR_SIZE, os.SEEK_CUR)
        else:
            return sector_num
        
        sector_num += 1
        buffer = disk.read(SECTOR_SIZE)

    return -1

def file_exists(disk, file_name, total_size):
    disk.seek(SECTOR_SIZE)
    buffer = disk.read(SECTOR_SIZE)
    sector_num = 1

    while buffer:
        if buffer.strip(b'\x00'):
            metadata = buffer.decode(errors='ignore').strip()
            if metadata.startswith(f"FILE={file_name};"):
                return True

            disk.seek(SECTOR_SIZE, os.SEEK_CUR)
        else:
            disk.seek(SECTOR_SIZE, os.SEEK_CUR)
        
        sector_num += 1
        buffer = disk.read(SECTOR_SIZE)

    return False

def write_file_to_disk(disk, file_path, start_sector):
    with open(file_path, 'rb') as file:
        file_data = file.read()
        num_sectors = (len(file_data) + SECTOR_SIZE - 1) // SECTOR_SIZE

        file.seek(0)
        for i in range(0, len(file_data), BUFFER_SIZE):
            buffer = file.read(BUFFER_SIZE)
            disk.seek((start_sector + i // SECTOR_SIZE) * SECTOR_SIZE)
            disk.write(buffer)
        
    return num_sectors

def write_metadata(disk, file_name, num_sectors, start_sector):
    end_sector = start_sector + num_sectors - 1
    timestamp = int(time.time())
    metadata = f"FILE={file_name};{num_sectors};{start_sector};{end_sector};{timestamp};\n"

    metadata_sector = start_sector + num_sectors
    disk.seek(metadata_sector * SECTOR_SIZE)
    disk.write(metadata.encode())

def main():
    disk_path = "./disk.img"

    try:
        with open(disk_path, 'r+b') as disk:
            total_size = os.path.getsize(disk_path)

            file_name = input("Enter the name of the file: ")
            file_path = input("Enter the path to the file: ")

            if not os.path.isfile(file_path):
                print("File does not exist.")
                return

            if file_exists(disk, file_name, total_size):
                print("A file with this name already exists.")
                return

            start_sector = find_next_free_sector(disk, total_size)
            if start_sector == -1:
                print("No free sector found.")
                return

            num_sectors = write_file_to_disk(disk, file_path, start_sector)
            write_metadata(disk, file_name, num_sectors, start_sector)
            print(f"File '{file_name}' written successfully.")

    except IOError as e:
        print(f"Failed to process disk image: {e}")

if __name__ == "__main__":
    main()
