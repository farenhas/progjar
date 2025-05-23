import socket
import json
import base64
import logging
import os

server_address = ('0.0.0.0', 7777)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        sock.sendall((command_str + "\r\n\r\n").encode())  # Mengirim dengan akhiran "\r\n\r\n"
        data_received = ""  # empty string
        while True:
            data = sock.recv(4096)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break
        hasil = json.loads(data_received)  # Pastikan hasil dalam format JSON
        logging.warning("data received from server:")
        return hasil
    except:
        logging.warning("error during data receiving")
        return False

def print_json(response):
    """Menampilkan hasil response dalam format JSON yang mudah dibaca di terminal."""
    try:
        json_formatted_str = json.dumps(response, indent=4)
        print(json_formatted_str)
    except Exception as e:
        print(f"[ERROR] Gagal menampilkan JSON: {str(e)}")

def remote_list():
    command_str = "LIST"
    hasil = send_command(command_str)
    if hasil and hasil['status'] == 'OK':
        print("Daftar file:")
        print_json(hasil)
        return True
    else:
        print("Gagal")
        return False

def remote_get(filename=""):
    command_str = f"GET {filename}"
    hasil = send_command(command_str)
    if hasil and hasil['status'] == 'OK':
        namafile = hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        with open(namafile, 'wb+') as fp:
            fp.write(isifile)
        print_json(hasil)  # Menampilkan hasil dalam format JSON
        return True
    else:
        print("Gagal")
        return False

def remote_upload(filepath=""):
    try:
        with open(filepath, 'rb') as f:
            filedata = base64.b64encode(f.read()).decode()
        filename = os.path.basename(filepath)
        command_str = f"UPLOAD {filename} {filedata}"
        hasil = send_command(command_str)
        if hasil and hasil['status'] == 'OK':
            print(f"Upload berhasil:")
            print_json(hasil)
        else:
            print(f"Upload gagal:")
            print_json(hasil)
    except FileNotFoundError:
        print("File tidak ditemukan")
    except Exception as e:
        print(f"Gagal upload: {str(e)}")

def remote_delete(filename=""):
    command_str = f"DELETE {filename}"
    hasil = send_command(command_str)
    if hasil and hasil['status'] == 'OK':
        print(f"Delete berhasil:")
        print_json(hasil)
    else:
        print(f"Delete gagal:")
        print_json(hasil)

def show_help():
    print("Perintah yang dapat dilakukan:")
    print("1. LIST - Menampilkan daftar file")
    print("2. GET <filename> - Mengambil file dengan nama <filename>")
    print("3. UPLOAD <filepath> - Mengupload file dari path <filepath>")
    print("4. DELETE <filename> - Menghapus file dengan nama <filename>")

if __name__ == '__main__':
    server_address = ('172.16.16.101', 6666)
    show_help()
    while True:
        cmd = input("Masukkan perintah: ").split(" ")
        if cmd[0] == "GET":
            if len(cmd) < 2:
                print("[ERROR] No filename provided!")
                continue
            remote_get(cmd[1])
        elif cmd[0] == "LIST":
            remote_list()
        elif cmd[0] == "DELETE":
            remote_delete(cmd[1])
        elif cmd[0] == "UPLOAD":
            remote_upload(cmd[1])
        elif cmd[0] == "QUIT":
            break
        else:
            print("[ERROR] Invalid command!")
            show_help()
