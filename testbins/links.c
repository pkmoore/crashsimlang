#include <unistd.h>
#include<sys/types.h>
#include<sys/stat.h>
#include<stdio.h>
#include<stdlib.h>
#include<time.h>

void links(){
    //good link
    int i=link("al/ma/newfile.txt","al/sic/newest1.txt");

    //bad link
    int k=link("al/ma/newfile.txt","al/sic/");

    //good unlink
    int j=unlink("al/sic/newest1.txt");

    //bad unlink
    int s=unlink("al/sic/newest2.txt");
}

void dirs(){
mkdir("al/ma/new-dir1",0700);
    mkdir("al/ma/new-dir1",0700);
    rmdir("al/ma/new-dir1");
    rmdir("al/ma/new-dir1");
}

void bad_mount(){
mkdir("al/ma/newest",0700);
    mkdir("al/mnt",0700);
    mount("al/ma/newest","al/mnt",0);
    umount("al/mnt/");
}

void chdir_mod(){
    chdir("/home/almazhan/Desktop/res_tandon/posix-omni-parser/testbins");
    chmod("al/ma/newfile.txt",0644);

    //bad chdir and chmod
    chdir("/home/almazhan/Desktop/res_tandon/posix-omni-parser/testbins1");
    chmod("al/ma/newfile7.txt",0644);
}



int main(int argc , char *argv[]){
    //generate strace lines for link,unlink
    struct stat st={0};
    links();
    //generate strace lines for mkdir,rmdir
    dirs();


    bad_mount();
    
    chdir_mod();

    //time

    time_t current_time;
    char* c_time_string;

    current_time = time(NULL);

    if (current_time == ((time_t)-1))
    {
        exit(EXIT_FAILURE);
    }

    c_time_string = ctime(&current_time);

    if (c_time_string == NULL)
    {
        exit(EXIT_FAILURE);
    }

    (void) printf("Current time is %s", c_time_string);
    exit(EXIT_SUCCESS);

    return 1;
}