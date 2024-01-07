import os.path
import socket
from zlib import crc32

SYN = 0
SYN_ACK = 1
NACK = 3
FIN  = 4
FIN_ACK = 5
SQN1 = 6
SQN2 = 7
SQN1_ACK = 8
SQN2_ACK = 9
SWITCH = 10
SWITCH_ACK = 11
FILE = 12
FILE_ACK = 13
last_sqn = SQN2



class Fragment:
    checksum = 0
    size = 0
    flag = 0
    data: bytearray = None

    def __init__(self, message, flag=None):
        if flag is None:
            self.from_message(message)
        else:
            self.flag = flag
            self.checksum = crc32(message)
            self.data = bytearray(message)

    def from_message(self, message):
        self.checksum = int.from_bytes(message[0:4], "big")
        self.flag = message[4]
        self.data = bytearray(message[5:])

    def as_message(self):
        message = self.data
        message.insert(0, self.flag)
        message = self.checksum.to_bytes(4, "big") + message
        return message


def server():

    localIP = input("Zadaj IP adresu: ")

    localPort = int(input("Zadaj port: "))

    bufferSize = 1467

    # vytvorenie socketu

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # bind na IP adresu

    UDPServerSocket.bind((localIP, localPort))

    print("Prijimatel je pripaveny a pocuva")

    # Listen for incoming datagrams
    arr = bytearray()
    file_data = bytearray()
    counter = 1
    transfered_size = 0
    global last_sqn
    is_file = 0
    while True:
        try:
            message, address = UDPServerSocket.recvfrom(bufferSize + 5)
            fragment = Fragment(message)
            flag = NACK
            #print(str(counter) + ":" + str(fragment.__dict__))
            if fragment.checksum != crc32(fragment.data):
                flag = NACK
                print(str(counter) + ":  Prisiel mi nespravny checksum, odpovedam NACK")
                print("Velkost fragmentu: " + str(len(fragment.data)))

            else:
                if fragment.flag == SYN:
                    print(str(counter) + ":  Dostal som SYN, Odpovedam SYN ACK")
                    print("Velkost fragmentu: " + str(len(fragment.data)))
                    flag = SYN_ACK
                    arr = fragment.data
                    if is_file == 0:
                        transfered_size += len(fragment.data)

                if (fragment.flag == SQN2 and last_sqn == SQN2) or (fragment.flag == SQN1 and last_sqn == SQN1):
                    print(str(counter) + ":  Prislo mi nespravne SQN, odpovedam NACK")
                    print("Velkost fragmentu: " + str(len(fragment.data)))


                if fragment.flag == SQN1 and last_sqn == SQN2:
                    print(str(counter) + ":  Dostal som SQN1, Odpovedam SQN1 ACK")
                    print("Velkost fragmentu: " + str(len(fragment.data)))
                    flag = SQN1_ACK
                    arr += fragment.data
                    last_sqn = SQN1
                    if is_file == 0:
                        transfered_size += len(fragment.data)

                if fragment.flag == SQN2 and last_sqn == SQN1:
                    print(str(counter) + ":  Dostal som SQN2, Odpovedam SQN2 ACK")
                    print("Velkost fragmentu: " + str(len(fragment.data)))
                    flag = SQN2_ACK
                    arr += fragment.data
                    last_sqn = SQN2
                    if is_file == 0:
                        transfered_size += len(fragment.data)

                if fragment.flag == FIN:
                    print(str(counter) +": Dostal som FIN, Odpovedam FIN ACK")
                    print("Velkost fragmentu: " + str(len(fragment.data)))
                    flag = FIN_ACK
                    arr += fragment.data
                    if is_file == 0:
                        transfered_size += len((fragment.data))
                    print("\nposielana sprava/subor: " + arr.decode())
                    print("Pocet prijatych fragmentov: " + str(counter))
                    print("Velkost posielanej spravy/suboru: " + str(transfered_size) + "B\n")
                    counter = 0
                    transfered_size = 0
                    is_file = 0

                    if len(file_data) > 0:
                        file = open(arr.decode("utf-8"), "wb+")
                        file.write(file_data)
                        file.close()
                        file_data = bytearray()
                        file_path = str(arr.decode())
                        full_path = os.path.abspath(file_path)
                        print("subor sa ulozil na ceste:  " + full_path)

                if fragment.flag == SWITCH:
                    print(str(counter) + ":  Dostal som SWITCH, Odpovedam SWITCH ACK")
                    print("Velkost fragmentu: " + str(len(fragment.data)))
                    flag = SWITCH_ACK
                    frag_out = Fragment("".encode(), flag)
                    UDPServerSocket.sendto(frag_out.as_message(), address)
                    return

                if fragment.flag == FILE:
                    print(str(counter) + ":  Dostal som FILE, Odpovedam FILE ACK")
                    print("Velkost fragmentu: " + str(len(fragment.data)))
                    flag = FILE_ACK
                    arr += fragment.data
                    file_data += arr
                    if is_file == 0:
                        transfered_size += len(fragment.data)


            counter += 1

            # Posielam odpoved klientovi
            frag_out = Fragment("".encode(), flag)
            UDPServerSocket.sendto(frag_out.as_message(), address)
            UDPServerSocket.settimeout(60)

        except:
            print("Odosielatel nekomunikuje, ostavam pocuvat")
            continue


def check_buffer_size():
    while True:
        try:
            buffer_size = int(input("Zadaj velkost fragmentacie 1-1467B:"))
            if buffer_size >= 1 and buffer_size <= 1467:
                return buffer_size
            else:
                print("Zadal si nespravnu hodnotu!")

        except:
            print("Zadal si nespravnu hodnotu!")




def client ():

    ip_adress = input("Zadaj IP adresu servera: ")
    port = int(input("Zadaj port na ktorom chces komunikovat: "))

    serverAddressPort = (ip_adress, port)
    while True:
        print("Vyber si moznost co chces robit:\n 1 - odoslat spravu\n2 - odoslat subor\n3 - vymena\n4 - ukoncit program ")
        choice = input()
        simulate_error = 0
        if choice == "1":
            longmsg = input("Zadaj spravu ktoru chces poslat:")
            while True:

                try:
                    simulate_error = int(input("Chces simulovat chybu pri prenose(1-ano,0-nie)?"))

                    if simulate_error == 1 or simulate_error == 0:
                        buffer_size = check_buffer_size()
                        if send_message(buffer_size, longmsg, serverAddressPort, simulate_error) == -1:
                            return
                        break
                    else:
                        print("Zadal si nespravnu hodnotu!")

                except:
                    print("Zadal si nespravnu hodnotu!")


        elif choice == "2":
            file_to_send = input("zadaj nazov suboru na odoslanie:")
            file_name_to_save = input("zadaj nazov ako ho chces ulozit:")

            if file_name_to_save == "":

                if os.path.isabs(file_to_send):  # ak odosielam celu cestu chcem len filename
                    file_name_to_save = os.path.basename(file_to_send)

                else:
                    file_name_to_save = file_to_send

            if file_name_to_save.endswith(os.path.sep):  # ak zadam cielovu cestu ale bez nazvu suboru
                file_name_to_save += os.path.basename(file_to_send)

            while True:

                try:
                    simulate_error = int(input("Chces simulovat chybu pri prenose(1-ano,0-nie)?"))

                    if simulate_error == 1 or simulate_error == 0:
                        buffer_size = check_buffer_size()
                        file = open(file_to_send, "rb")
                        file_data = file.read()
                        file.close()
                        if send_message(buffer_size, file_data, serverAddressPort, simulate_error, True) == -1:
                            return
                        if send_message(buffer_size, file_name_to_save, serverAddressPort, simulate_error) == -1:
                            return
                        break
                    else:
                        print("Zadal si nespravnu hodnotu!")

                except:
                    print("Zadal si nespravnu hodnotu!")

            print("Subor sa odosielal z:  " + str(os.path.abspath(file_to_send)))

        elif choice == "3":
            switch(serverAddressPort)
            return

            #daco
        elif choice == "4":
            exit()
        else:
            print("Zadal si nespravnu moznost")


def send_message(buffer_size, longmsg, serverAddressPort, simulate_error, is_file=False):

    counter = 1
    #vytvorenie socketu
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    index = buffer_size
    last_index = 0
    is_comunication = False
    lastsqn = SQN2
    doimplementacia = True
    last = False  # premenna na poslanie prazdneho FIN ( Ak je buffer_size > len(msg) )

    if isinstance(longmsg, str):
        longmsg = longmsg.encode()

    while last_index < len(longmsg) or last:
        try:
            flag = SYN
            # pripravujem si flag na odoslanie
            if is_comunication:

                if lastsqn == SQN1:
                    if index != len(longmsg):
                        print(str(counter) + ": Posielam SQN2")
                    flag = SQN2
                    lastsqn = SQN2

                else:
                    if index != len(longmsg):
                        print(str(counter) +": Posielam SQN1")
                    flag = SQN1
                    lastsqn = SQN1

                if index == len(longmsg) and not is_file:  #odoslal som cely text
                    print(str(counter) +": Posielam FIN")
                    flag = FIN


                elif index == len(longmsg) and is_file:  # odoslal som cely subor, idem posielat filename
                    print(str(counter) +": Posielam FILE")
                    flag = FILE
            else:
                print(str(counter) +": Posielam SYN")

            if simulate_error == 1:
                if counter == 6:
                    counter += 1
                    print("simulujem zaroven chybu skipujem SQN (toto SQN sa neodošle)")
                    continue

            # odoslem a prijmem spravu
            fragment = Fragment(longmsg[last_index:index], flag)

            if simulate_error == 1:
                if counter == 2:
                    fragment.checksum = 0
                    print("simulujem zaroven chybu vkladam zly checksum")

            UDPClientSocket.sendto(fragment.as_message(), serverAddressPort)
            UDPClientSocket.settimeout(60)
            msgFromServer, _ = UDPClientSocket.recvfrom(buffer_size + 5)
            inc_f = Fragment(msgFromServer)
            print("Prislo mi: "+ str(inc_f.__dict__))

            # kontrolujem ci prijata prava ma spravnu hlavicku
            if inc_f.flag == NACK:
                counter += 1
                continue

            if flag == SYN and inc_f.flag == SYN_ACK:
                is_comunication = True
                last_index = index
                index += buffer_size

            if flag == SQN1 and inc_f.flag == SQN1_ACK or flag == SQN2 and inc_f.flag == SQN2_ACK:
                last_index = index
                index += buffer_size

            if flag == FIN and inc_f.flag == FIN_ACK and not is_file:
                is_comunication = False
                print("Pocet odosielanych fragmentov: " + str(counter))
                print("Velkost odosielanej spravy/suboru: " + str(len(longmsg)) + "B")
                break

            if flag == FILE and inc_f.flag == FILE_ACK and is_file:
                print("Pocet odosielanych fragmentov: " + str(counter))
                print("Velkost odosielanej spravy/suboru: " + str(len(longmsg)))
                break

            if index > len(longmsg):
                index = len(longmsg)

            if index < last_index:  # toto sa stane len vtedy ak index nastavime na buff size a potom sa index nastavi na len(msg)
                last = True
                last_index = index
            if index == len(longmsg):
                last = True

            counter += 1
        except:
            print("Prijimatel nekomunikuje, zatvaram spojenie")
            return -1



def switch(serverAddressPort):
    bufferSize = 1467
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    while True:
        flag = SWITCH
        fragment = Fragment("".encode(), flag)
        UDPClientSocket.sendto(fragment.as_message(), serverAddressPort)
        msgFromServer, _ = UDPClientSocket.recvfrom(bufferSize)
        inc_f = Fragment(msgFromServer)

        if inc_f.flag == SWITCH_ACK:
            return



def init():
    while True:
        print("1 pre odosielatela \n2 pre prijimatela \n3 pre exit\n")
        choice = input()

        if choice == "1":
            client()

        elif choice == "2":
            server()

        elif choice == "3":
            break


if __name__ == '__main__':
    init()

