import paramiko
import time
import curses
import re
def get_ssh_connection(hostname, username, password):
    """Establishes an SSH connection to the specified host"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)
    return ssh

# Get the SSH connection details
hostname = input("Enter the hostname or IP address: ")
username = input("Enter the SSH username: ")
password = input("Enter the SSH password: ")

logo = r'''Created by LuckyWay1337
 ____  _     _ _    ____          _     _____         _
/ ___|| |__ (_) |_ / ___|___   __| | __|_   _|__  ___| |__
\___ \| '_ \| | __| |   / _ \ / _` |/ _ \| |/ _ \/ __| '_ \
 ___) | | | | | |_| |__| (_) | (_| |  __/| |  __/ (__| | | |
|____/|_| |_|_|\__|\____\___/ \__,_|\___||_|\___|\___|_| |_|
'''



# Connect to the remote host over SSH
ssh = get_ssh_connection(hostname, username, password)

# Initialize curses
stdscr = curses.initscr()
curses.start_color()
curses.noecho()
curses.cbreak()
stdscr.keypad(True)

# Split the logo into lines and get its dimensions
lines = logo.strip().split("\n")
height = len(lines)
width = max(len(line) for line in lines)

# Calculate the coordinates of the top-left corner of the logo
x = (curses.COLS - width) // 2
y = (curses.LINES - height) // 2

# Write the logo to the screen
for i, line in enumerate(lines):
    stdscr.addstr(y+i+5, x, line, curses.color_pair(6))

# Define colors for the text
curses.start_color()
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_color(6, 206, 209, curses.COLOR_BLACK)
curses.init_pair(6, 206, curses.COLOR_BLACK)

# Define the display layout
stdscr.addstr(0, 0,"Shutdown - 1\nReboot - 2\nClose - Ctrl-C")
stdscr.addstr(5, 2, "CPU Load:", curses.color_pair(1))
stdscr.addstr(6, 2, "Memory Load:", curses.color_pair(2))
stdscr.addstr(7, 2, "HDD Total/Used/Free:", curses.color_pair(3))
stdscr.addstr(8, 2, "Actual Time:", curses.color_pair(4))
stdscr.addstr(9, 2, "Uptime:", curses.color_pair(4))
stdscr.addstr(10, 2, "Network Connections:", curses.color_pair(5))
stdscr.addstr(12, 2, "TCP Connections...", curses.color_pair(5))
stdscr.refresh()

# Run monitoring commands remotely in an infinite loop
while True:
    try:
        stdin, stdout, stderr = ssh.exec_command('htop')
        htop_pid = stdout.channel.recv_exit_status()

        # attach to htop process in curses mode
        stdin, stdout, stderr = ssh.exec_command("top -bn1 | grep 'load average:' | awk '{printf \"%.2f\", $(NF-2)}'")
        cpu_load = stdout.read().decode('utf-8').strip()
        total_cpu = re.findall(r'\d+\.\d+', cpu_load)[0]
        total_cpu = round(float(total_cpu) * 100)
        if total_cpu >= 100:
            total_cpu = 100
            stdscr.addstr(5, 14, f"{total_cpu}%", curses.color_pair(1))
        else:
            stdscr.addstr(5, 14, f"{total_cpu}%", curses.color_pair(1))

        stdin, stdout, stderr = ssh.exec_command("free -m | awk 'NR==2{printf \"%.2f%%\", $3*100/$2 }'")
        mem_load = stdout.read().decode('utf-8').strip()
        stdscr.addstr(6, 17, mem_load, curses.color_pair(2))

        stdin, stdout, stderr = ssh.exec_command("df -h / | awk '/\\//{printf \"%s/%s/%s\", $4, $3, $4}'")
        hdd_usage = stdout.read().decode('utf-8').strip()
        stdscr.addstr(7, 22, hdd_usage, curses.color_pair(3))

        stdin, stdout, stderr = ssh.exec_command("date '+%Y-%m-%d %H:%M:%S'")
        current_time = stdout.read().decode('utf-8').strip()
        stdscr.addstr(8, 18, current_time, curses.color_pair(4))

        stdin, stdout, stderr = ssh.exec_command("uptime | awk '{print $3,$4,$5}'")
        uptime = stdout.read().decode('utf-8').strip()
        stdscr.addstr(9, 12, uptime, curses.color_pair(4))

        stdin, stdout, stderr = ssh.exec_command("netstat -an | grep ESTABLISHED | wc -l")
        established_connections = stdout.read().decode('utf-8').strip()
        stdscr.addstr(10, 22, established_connections, curses.color_pair(5))

        stdin, stdout, stderr = ssh.exec_command('netstat -tun | grep ESTABLISHED')
        output = stdout.read().decode()
        tcp_connections = []
        '''for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 5:
                local_address = parts[3]
                remote_address = parts[4]
                state = parts[5]
                tcp_connections.append((local_address, remote_address, state))
        for i, conn in enumerate(tcp_connections):
            stdscr.addstr(12 + i, 4, conn[0], curses.color_pair(5))
            stdscr.addstr(12 + i, 22, conn[1], curses.color_pair(5))
            stdscr.addstr(12 + i, 42, conn[2], curses.color_pair(5)'''

        stdin, stdout, stderr = ssh.exec_command("netstat -ant | awk 'NR>2{print $4,$5,$6}'")
        tcp_connections = stdout.read().decode('utf-8').strip()
        stdscr.addstr(11, 0, tcp_connections, curses.color_pair(5))
        #print(tcp_connections)

        # Get the key pressed by the user
        key = stdscr.getch()

        # Check if the key is '1', and perform some action if it is
        if key == ord('1'):
            stdscr.addstr("\nAre you sure you want to shut down? (Y/N)\n", curses.color_pair(1))
            response = stdscr.getch()  # Wait for user input
            if response == ord('y') or response == ord('Y'):
                stdscr.addstr("Shutting down...")
                ssh.exec_command("sudo /home/fuckthat/123.sh -s")
                curses.endwin()
                ssh.close()
                break
        if key == ord('2'):
            stdscr.addstr("\nAre you sure you want to reboot? (Y/N)\n")
            response = stdscr.getch()  # Wait for user input
            if response == ord('y') or response == ord('Y'):
                stdscr.addstr("Rebooting...")
                ssh.exec_command("sudo /home/fuckthat/123.sh -r")
                curses.endwin()
                ssh.close()
                break
        stdscr.refresh()




    except KeyboardInterrupt:
        # Handle Ctrl+C to exit gracefully
        curses.endwin()
        ssh.close()
        print("Exiting...")
        break
