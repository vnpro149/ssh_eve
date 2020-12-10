from multiprocessing import Process,Queue
import re
import os, sys, time
import subprocess
try:
    from netmiko import ConnectHandler
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install',
'netmiko>'])
from netmiko import ConnectHandler


list_ip = []
def screen_clear():
    # for mac and linux(here, os.name is 'posix')
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        # for windows platfrom
        _ = os.system('cls')
def device_list(ip,sl):
    devices = []
    device = {
        'device_type':'cisco_ios_telnet',
        'ip':ip,
        'port':"32769",
        'secret':'321',
        'global_delay_factor': 2
    }
    for i in range (0,sl):
        device_copy=device.copy()                       
        device_copy["port"]=str(int(device["port"])+i)
        devices.append(device_copy)
    return devices
def config_ssh(device):
    ssh = ConnectHandler(**device)
    ssh.enable()
    cmd1 = [
        'int e0/0',
        'no sw',
        'ip add dhcp',
        'no shut'
    ]
    cmd2 = [
        'hostname vnpro',
        'ip domain-name vnpro.org',
        'cryp key ge rsa modul 1024',
        'username admin password 123',
        'enable password 321',
        'line vty 0 4',
        'login local',
        'transport input all'
    ]
    ssh.send_config_set(cmd1)
    ssh.send_config_set(cmd2)
    ssh.disconnect()
def show_int(device):
    try:
        ssh = ConnectHandler(**device)
        data = ssh.send_command('show ip int br')
        ip_regex = re.search(r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}',data)
        with open('ip.csv','a') as file_ip:
            file_ip.write("{0},{1},admin,123,321\n".format(device['port'],ip_regex.group()))
            #file_ip.write(device['port']+','+ip_regex.group()+'\n')
        ssh.disconnect()
    except AttributeError:
        with open('ip.csv','a') as file_ip:
            file_ip.write("{0},No IP Address,admin,123,321\n".format(device['port']))
def main():
    screen_clear()
    while True:
        ip = input('Nhập IP của Server EVE-ng (A.B.C.D): ')
        if re.search(r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}',ip) != None:
            break
        else:
            print("Sai định dạng IP. Vui lòng nhập lại")
            continue    
    sl = input('Nhập Số lượng thiết bị: ')
    screen_clear()
    print("############ Server EVE-NG {} ###############".format(ip))
    devices = device_list(ip,int(sl))
    while True:
        print('1.Cấu hình SSH cho {} thiết bị'.format(sl))
        print('2.Lấy IP toàn bộ {} thiết bị'.format(sl))
        print('0.Thoát chương trình')
        choice = input("Nhập lựa chọn của bạn: ")
        if choice == '1':
            for item in devices:
                my_proc = Process(target=config_ssh, args=(item,))
                my_proc.start()
            time.sleep(5)
            print("Hoàn tất công việc")
            input("Nhấn Enter để tiếp tục...")
            screen_clear()
        elif choice == '2':
            procs=[]
            with open('ip.csv','w') as file_ip:
                file_ip.write('Device Port,IP Address,Username,Password,Enable Password\n')
            for item in devices:
                my_proc = Process(target=show_int, args=(item,))
                my_proc.start()
                procs.append(my_proc)
            for a_proc in procs:
                a_proc.join()
            print("Kiểm tra file ip.csv để xem danh sách IP\n")
            input("Nhấn Enter để tiếp tục...")
            screen_clear()
        elif choice =='3':
            pass
        elif choice == '0':
            sys.exit()
        else:
            print('Wrong input\n')
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nThoát khỏi chương trình")
    except SystemExit:
        print("\nThoát khỏi chương trình")
    except:
        print('Kiểm tra kết nối đến Server và các thiết bị')