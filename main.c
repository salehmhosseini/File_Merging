// File Concatenator 
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <dirent.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <time.h>

#define MAX_PATH 1024
#define OUTPUT_FILE "output.txt"
#define FULL_LOG_FILE "full_log.log"

typedef struct {
    char filepath[MAX_PATH];
    FILE *local_log;
    char pid_chain[512];
    const char *root_path;
    int depth;
} ThreadArg;

pthread_mutex_t file_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t full_log_mutex = PTHREAD_MUTEX_INITIALIZER;
FILE *output_file;
FILE *full_log_file;

// Calculate depth of a file relative to root
int calculate_depth(const char *root, const char *path) {
    int depth = 0;
    const char *sub = path + strlen(root);
    for (int i = 0; sub[i]; i++) {
        if (sub[i] == '/') depth++;
    }
    return depth;
}

// Format mtime to readable timestamp
void format_mtime(time_t mod_time, char *buffer, size_t size) {
    struct tm *timeinfo = localtime(&mod_time);
    strftime(buffer, size, "%Y-%m-%d %H:%M:%S", timeinfo);
}

// Print file tree to terminal
void print_tree_line(int depth, const char *label, const char *type, pid_t pid_or_tid) {
    for (int i = 0; i < depth; i++) printf("    ");
    printf("|-- [%s %ld] %s\n", type, (long)pid_or_tid, label);
}

// Thread function
void *read_and_write_file(void *arg) {
    ThreadArg *targ = (ThreadArg *)arg;
    FILE *fp = fopen(targ->filepath, "r");
    if (!fp) {
        perror("Failed to open text file");
        return NULL;
    }

    pthread_t tid = pthread_self();

    struct stat sb;
    if (stat(targ->filepath, &sb) == -1) {
        perror("stat failed");
        fclose(fp);
        return NULL;
    }

    char mtime_str[64];
    format_mtime(sb.st_mtime, mtime_str, sizeof(mtime_str));

    // Print thread tree entry
    print_tree_line(targ->depth + 1, targ->filepath, "THREAD", tid);

    // Write to local log
    fprintf(targ->local_log, "[THREAD %lu] read file: %s\n", tid, targ->filepath);

    // Write to full log
    pthread_mutex_lock(&full_log_mutex);
    fprintf(full_log_file,
            "FILE: %s\n"
            "  Depth: %d\n"
            "  Thread ID: %lu\n"
            "  PID Chain: %s\n"
            "  Last Modified: %s\n\n",
            targ->filepath, targ->depth, tid, targ->pid_chain, mtime_str);
    pthread_mutex_unlock(&full_log_mutex);

    // Write to output.txt
    char buffer[1024];
    pthread_mutex_lock(&file_mutex);
    fprintf(output_file, "----- Start of %s -----\n", targ->filepath);
    while (fgets(buffer, sizeof(buffer), fp)) {
        fputs(buffer, output_file);
    }
    fprintf(output_file, "----- End of %s -----\n\n", targ->filepath);
    pthread_mutex_unlock(&file_mutex);

    fclose(fp);
    return NULL;
}

// Recursive directory processor
void process_directory(const char *path, const char *root_path, const char *pid_chain) {
    DIR *dir = opendir(path);
    if (!dir) {
        perror("Failed to open directory");
        exit(1);
    }

    // Create local log file
    char log_path[MAX_PATH];
    const char *folder_name = strrchr(path, '/');
    snprintf(log_path, sizeof(log_path), "%s/%s.log", path, folder_name ? folder_name + 1 : path);
    FILE *local_log = fopen(log_path, "w");
    if (!local_log) {
        perror("Failed to create local log file");
        closedir(dir);
        exit(1);
    }

    pid_t current_pid = getpid();
    char new_pid_chain[512];
    snprintf(new_pid_chain, sizeof(new_pid_chain), "%s>%d", pid_chain, current_pid);

    // Print process tree entry
    int depth = calculate_depth(root_path, path);
    print_tree_line(depth, path, "PROCESS", current_pid);

    fprintf(local_log, "[PROCESS %d] entered directory: %s\n", current_pid, path);

    struct dirent *entry;
    pthread_t threads[100];
    ThreadArg args[100];
    int thread_count = 0;

    while ((entry = readdir(dir)) != NULL) {
        if (!strcmp(entry->d_name, ".") || !strcmp(entry->d_name, "..")) continue;

        char full_path[MAX_PATH];
        snprintf(full_path, sizeof(full_path), "%s/%s", path, entry->d_name);

        struct stat statbuf;
        if (stat(full_path, &statbuf) == -1) continue;

        if (S_ISDIR(statbuf.st_mode)) {
            pid_t pid = fork();
            if (pid == 0) {
                process_directory(full_path, root_path, new_pid_chain);
                fclose(local_log);
                exit(0);
            }
        } else if (S_ISREG(statbuf.st_mode) && strstr(entry->d_name, ".txt")) {
            strcpy(args[thread_count].filepath, full_path);
            args[thread_count].local_log = local_log;
            strcpy(args[thread_count].pid_chain, new_pid_chain);
            args[thread_count].root_path = root_path;
            args[thread_count].depth = depth;
            pthread_create(&threads[thread_count], NULL, read_and_write_file, &args[thread_count]);
            thread_count++;
        }
    }

    for (int i = 0; i < thread_count; i++) {
        pthread_join(threads[i], NULL);
    }

    while (wait(NULL) > 0);
    fclose(local_log);
    closedir(dir);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <root_directory>\n", argv[0]);
        return 1;
    }

    output_file = fopen(OUTPUT_FILE, "w");
    if (!output_file) {
        perror("Failed to create output file");
        return 1;
    }

    full_log_file = fopen(FULL_LOG_FILE, "w");
    if (!full_log_file) {
        perror("Failed to create full log file");
        fclose(output_file);
        return 1;
    }

    char root_path[MAX_PATH];
    realpath(argv[1], root_path);

    char initial_pid_chain[64];
    snprintf(initial_pid_chain, sizeof(initial_pid_chain), "%d", getpid());

    printf("\n========== Process & Thread Tree =========\n");
    process_directory(root_path, root_path, initial_pid_chain);

    fclose(full_log_file);
    fclose(output_file);
    return 0;
}
