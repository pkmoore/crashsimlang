for i in $(seq 1 $3); do 
  cslang run strace -a $1 -s $2 -d ../syscall_definitions.pickle;
done
