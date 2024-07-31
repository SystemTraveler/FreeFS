import os

SECTOR_SIZE = 512

def read_metadata(disk, file_name, total_size):
    disk.seek(SECTOR_SIZE)  # Пропускаем первый сектор
    buffer = disk.read(SECTOR_SIZE)
    sector_num = 1  # Начинаем с 1

    while buffer:
        if buffer.strip(b'\x00'):
            metadata = buffer.decode(errors='ignore').strip()
            if metadata.startswith(f"FILE={file_name};"):
                parts = metadata.split(';')
                return {
                    'file_name': parts[0].split('=')[1],
                    'num_sectors': int(parts[1]),
                    'start_sector': int(parts[2]),
                    'end_sector': int(parts[3]),
                    'timestamp': int(parts[4])
                }
            
            disk.seek(SECTOR_SIZE, os.SEEK_CUR)
        else:
            disk.seek(SECTOR_SIZE, os.SEEK_CUR)
        
        sector_num += 1
        buffer = disk.read(SECTOR_SIZE)

    return None

def read_file_from_disk(disk, file_metadata):
    start_sector = file_metadata['start_sector']
    num_sectors = file_metadata['num_sectors']
    file_data = bytearray()

    for i in range(num_sectors):
        disk.seek((start_sector + i) * SECTOR_SIZE)
        file_data.extend(disk.read(SECTOR_SIZE))

    return file_data

def main():
    disk_path = "./disk.img"

    try:
        with open(disk_path, 'r+b') as disk:
            total_size = os.path.getsize(disk_path)

            file_name = input("Enter the name of the file to read: ")

            file_metadata = read_metadata(disk, file_name, total_size)
            if file_metadata is None:
                print("File not found.")
                return

            file_data = read_file_from_disk(disk, file_metadata)

            # Записываем содержимое файла в out.aif
            with open(file_name, 'wb') as out_file:
                out_file.write(file_data)
            
            print(f"File '{file_name}' has been written to 'out.aif'.")

    except IOError as e:
        print(f"Failed to process disk image: {e}")

if __name__ == "__main__":
    main()
