//Code by Almazhan K. for CSCI-UA 202
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <ctype.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <errno.h>
/*auxiliary functions*/
void printId();
void greet();
int main(int argc, char **argv)
{
//maximum number of characters
char cmdline[1000] = {};
while (1) //infinite loop
{
//read command line
printf("lab1>");
fflush(stdout);
//check for input errors
if ((fgets(cmdline, 1000, stdin) == NULL) && ferror(stdin))
{
fprintf(stdout, "%s\n", "fgets stdin error");
exit(1);
}
if (feof(stdin))
{
fflush(stdout);
exit(0);
}
char *argv[128]; //maximum number of arguments
char *cmd_ptr = cmdline; // pointer to the command line input
/*format command line input */
cmd_ptr[strlen(cmd_ptr) - 1] = ' ';
while (*cmd_ptr && (*cmd_ptr == ' ')) //ignore space character
cmd_ptr++;
int count = 0;
char *space = strchr(cmd_ptr, ' ');
while (space)
{
argv[count++] = cmd_ptr;
*space = '\0';
cmd_ptr = space + 1;
while (*cmd_ptr && (*cmd_ptr == ' '))
cmd_ptr++;
space = strchr(cmd_ptr, ' ');
}
argv[count] = NULL;
pid_t child;
int status;
/*Skip if line with no arguments*/
if (argv[0] == NULL){
continue;
} else { //print parent process id
printf("Parent Process %d\n", getpid());
}
/*Check if command is a built-in command*/
if (strcmp(argv[0], "printid") == 0){
printId();
} else if (strcmp(argv[0], "greet") == 0){
greet();
} else if (strcmp(argv[0], "exit") == 0){
exit(0);
}
/*If not a a built-in command, create a child process*/
else{
child = fork();
if (child < 0){
printf("fork error");
exit(1);
}
/*child process*/
else if (child == 0){
printf("Child process %d will execute the command %s\n", getpid(), argv[0]);
//first argument to execve
//format the input command string as "/bin/command_name" i.e. "/bin/ls"
char *str1 = "/bin/";
char *str2 = argv[0];
char *command = malloc(strlen(str1) + strlen(str2) + 1); // +1 for thenull-terminator
strcpy(command, str1);
strcat(command, str2);
//pass parameters to execve
execve(command, argv, NULL);
//if program ever reaches this point, then command is not found
printf("Command Not Found!\n");
exit(1);
}
else{
wait(&status);
}
}
fflush(stdout);
}
exit(0);
}
//au
void printId(){
printf("The ID of the current process is %d\n", getpid());
}
void greet(){
printf("Hello\n");
}

