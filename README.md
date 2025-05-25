# Concatenator Project

This project recursively merges `.txt` files from a given root directory using **multi-processing** and **multi-threading** in C. It also generates detailed logs per directory and a global log file with file metadata. Additionally, it displays a visual tree of processes and threads in the terminal.

---

## 🔧 Features

* Uses `fork()` for process creation per subdirectory
* Uses `pthread_create()` for thread creation per `.txt` file
* Builds `output.txt` containing merged contents
* Logs:

  * Per-directory: `<directory_name>.log`
  * Global log: `full_log.log`
* Shows a live tree in terminal of all processes and threads

---

## 📁 Directory Structure Example

```
project_root/
├── subdir1/
│   ├── file1.txt
│   └── file2.txt
├── subdir2/
│   └── nested/
│       └── file3.txt
└── subdir2.log
```

---

##  How to Compile

Make sure you have GCC installed. Then compile the program with pthread support:

```bash
gcc -pthread -o concatenator concatenator.c
```

---

##  How to Run

Run the program with the root folder containing `.txt` files and subfolders:

```bash
.gcc -pthread -o concatenator main.c
./concatenator test/
```

---

## 📄 Output Files

* `output.txt`: Merged contents of all `.txt` files
* `full_log.log`: Global log with metadata (thread ID, PID chain, depth, last modified time)
* `<dirname>.log`: Each folder has its own log with basic process/thread activity

---

## 🌳 Terminal Tree Output

The terminal shows a tree like:

```
========== Process & Thread Tree =========
|-- [PROCESS 12345] /root
    |-- [THREAD 14054389] /root/file1.txt
    |-- [PROCESS 12346] /root/subdir
        |-- [THREAD 14054390] /root/subdir/file2.txt
```

This helps trace exactly how processes and threads managed the traversal and file handling.

---

##  Test Notes

* Supports nested folders
* Prioritizes deeper folders first in output
* Thread-safe access to shared files using mutex

---

##  Requirements

* Linux/Unix environment (uses `fork`, `pthread`, `stat`, `opendir`)
* C compiler (GCC)

---

##  Bonus

* GUI Viewer for logs is available as a separate Python tool

---

## 🧑‍💻 Authors

* Developed by: <  Saleh Mhosseini>
* For: Operating Systems University Course Project

