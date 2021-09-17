#include <unistd.h>
#include <string.h>

int main() {
    ssize_t len;
    int fd;
    int fd1;
    char data[128];
    char msg[128];
    char bad_msg[128];


    strcpy(msg,"Hello");
    strcpy(bad_msg,"Bad message");
    //if (read(0,data,128)<0)
       // write(2,"an error",31);
    
    //write
    if (write(0,msg,strlen(msg))<0)
        write(2,"an error",31);

    //bad write
    if (write(40,bad_msg,strlen(msg))<0)
        write(2,"an error",31);
    
    //execve
    char* argv[]={"jim","jams",NULL};
    char* envp[]={"some","environment",NULL};
    if (execve("./client",argv,envp) == -1)
        perror("Could not execve");
    
    char buf[256];
    int result = read(40, buf, 10);
    return result;
}

