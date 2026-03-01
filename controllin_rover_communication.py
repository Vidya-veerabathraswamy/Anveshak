CODE: 
import csv
import pandas as pd

def main():
    df = pd.read_csv("can_frames .csv")
    crc_polynomial = ['1','1','0','0','0','1','0','1','1','0','0','1','1','0','0','1']

    for i in range(0, len(df)):          
        crc_data = []
        value = "true"

        for j in range(1, 6):
            if j == 1:
                a = df.iloc[i, j]
                a = int(str(a)[2:], 16)
                if a > 2047:
                    print("The can frame check is a failiure:(error:bad_id), the given error is bad_id")
                    value = "false"
                    break
                else:
                    binary_a = []
                    temp = a
                    while temp != 0:
                        binary_a.append(str(temp % 2))
                        temp = temp // 2
                    binary_a = binary_a[::-1]
                    while len(binary_a) < 11:
                        binary_a = ['0'] + binary_a

            elif j == 5:
                if pd.isna(df.iloc[i, 5]):
                    binary_a = []
                else:
                    a = str(df.iloc[i, j])
                    a = a.split()
                    binary_a = []
                    for k in a:
                        k = int(str(k), 16)
                        binary_k = []
                        temp = k
                        while temp != 0:
                            binary_k.append(str(temp % 2))
                            temp = temp // 2
                        binary_k = binary_k[::-1]
                        while len(binary_k) < 8:
                            binary_k = ['0'] + binary_k
                        binary_a.extend(binary_k)

            elif j == 4:
                a = int(float(df.iloc[i, 4]))
                if int(a) > 8:
                    print("The can frame check is a failiure:(error:bad_dlc), the given error is bad_dlc")
                    value = "false"
                    break
                if pd.isna(df.iloc[i, 5]):
                    data_bytes = []
                    binary_a = []
                else:
                    data_bytes = str(df.iloc[i, 5]).strip().split()
                if len(data_bytes) != a:
                    print("the CAN frame check is a failiure:error(Mismatch of dlc and length of data, the given error is mismatch of dlc and length of data")
                    value = "false"
                    break
                else:
                    binary_a = []
                    temp = a
                    while temp != 0:
                        binary_a.append(str(temp % 2))
                        temp = temp // 2
                    binary_a = binary_a[::-1]
                    while len(binary_a) < 4:
                        binary_a = ['0'] + binary_a

            else:
                if j == 2:
                    binary_a = []
                else: 
                    rtr = str(int(float(df.iloc[i, 3])))
                    ide = str(int(float(df.iloc[i, 2])))
                    binary_a = [rtr, ide, '0']   # RTR + IDE + r0

            crc_data.extend(binary_a)

        if value == "true":
            for x in range(0, len(crc_data)):
                if crc_data[x] == '1':
                    crc_data = crc_data[x::]
                    break

            crc_data = crc_data + ['0'] * 15

            while len(crc_data) >= 16:
                for y in range(0, 16):
                    crc_data[y] = str(int(crc_data[y]) ^ int(crc_polynomial[y]))
                if all(b == '0' for b in crc_data):
                    crc_data = ['0'] * 15
                    break
                else:
                    found = False
                    for x in range(0, len(crc_data)):
                        if crc_data[x] == '1':
                            crc_data = crc_data[x::]
                            found = True
                            break
                    if not found:
                        crc_data = ['0'] * 15
                        break

            output = df.iloc[i, 6]
            output = int(output, 16)
            out_b = []
            temp = output
            while temp != 0:
                out_b.append(str(temp % 2))
                temp = temp // 2
            out_b = out_b[::-1]

            while len(out_b) < len(crc_data):
                out_b = ['0'] + out_b
            while len(crc_data) < len(out_b):
                crc_data = ['0'] + crc_data

            if out_b == crc_data:
                print('The CAN frame check is a success:(error:none), the given error is none')
            else:
                print('The CAN frame check is a failiure:(error:bad_crc), the given error is bad_crc')

    return 0

main()
