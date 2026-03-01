import serial
import numpy as np
import threading
import time
import struct
import zlib

port_sender = "/dev/pts/1"  
port_receiver = "/dev/pts/2" 

BYTE_RESET_PROBABLITY = 0.005

def send_data(ser: serial.Serial, data: np.ndarray) -> None:

    data_to_send = []
    
    for value in data:
        data_to_send.append(int(value) & 0xFF)
        raw_bytes = bytes(data_to_send)
        checksum = zlib.crc32(raw_bytes)
    
    checksum_bytes = list(struct.pack('I',checksum))
    data_to_send.extend(checksum_bytes)

    for byte in data_to_send:
        ser.write(bytes([byte]))


def receive_data(ser: serial.Serial) -> tuple[np.ndarray, bool]:
    received_pwm_data = []
    acknowledgement = False #sending acknowledgement message 
    for i in range(100):
        byte = ser.read(1)
        if len(byte) == 0:
            return np.array(received_pwm_data), False
        received_pwm_data.append(byte[0])

    checksum_bytes = b'' #crc check 
    for i in range(4):
        byte = ser.read(1)
        if len(byte) == 0:
            return np.array(received_pwm_data), False
        checksum_bytes += byte

    received_checksum = struct.unpack('I', checksum_bytes)[0]
    calculated_checksum = zlib.crc32(bytes(received_pwm_data))

    if received_checksum == calculated_checksum:
        acknowledgement = True
    else:
        acknowledgement = False

    return np.array(received_pwm_data), acknowledgement

def receive_thread_task(received_data: list, no_of_success: int):
    no_of_tries = 0
    try:
        with serial.Serial(port_receiver, 9600, timeout=0.2) as ser:   #timer without which all motors will turn off
            while len(received_data) < 100 and no_of_tries < 150:
                print(f"[RECIEVER] [{no_of_tries}] Trying to Recieve Data")

                received_arr, acknowledgement = receive_data(ser)
                
                if np.any(received_arr) or acknowledgement:
                    received_data.append(received_arr)
                    if acknowledgement:
                        print(f"[RECEIVER] [{len(received_data)}] SUCCESS")
                        no_of_success[0] += 1
                    else: 
                        print(f"[RECEIVER] [{len(received_data)}] FAILED")
                no_of_tries += 1
                time.sleep(0.01) 
            else: 
                print(f"[RECEIVER] Time Out")
    except Exception as e:
        print(f"Receiver Thread Error: {e}")

def send_thread_task(all_data):
    try: 
        with serial.Serial(port_sender, 9600) as ser:
            for i, data in enumerate(all_data):
                send_data(ser, data)
                print(f"[SENDER]   [{i+1}] Packet Sent")
                time.sleep(0.15) 
    except Exception as e:
        print(f"Sender Thread Error: {e}")

def generate_pwm():

    pwm = np.random.randint(0, 255, size=(100,))
    return pwm

def main():

    pwm_data = [generate_pwm() for i in range(100)]
    received_data = []
    no_of_success = [0]

    receiver_thread = threading.Thread(target=receive_thread_task, args=(received_data, no_of_success))
    receiver_thread.daemon = True
    receiver_thread.start()

    time.sleep(1)

    sender_thread = threading.Thread(target=send_thread_task, args=(pwm_data,))
    sender_thread.daemon = True
    sender_thread.start()

    time.sleep(1)

    sender_thread.join(timeout=30)
    receiver_thread.join(timeout=30)

    print(f"Total Successful: {no_of_success[0]}/100")

if __name__ == "__main__":
    main()
