git restore ./compression.port
echo "==== gzip compress file ===="
sed -i.bak -E 's/^inname.*/inname <- "test.pdf";/' compression.port
sed -i.bak -E 's/^outname.*/outname <- "test.pdf.gz";/' compression.port
port build -c ./compression.port
wc -l ./compression/gzip_compress_file.strace
multitime -n 10 port run strace -d ../syscall_definitions.pickle -s ./compression/gzip_compress_file.strace -a ./compression.auto

echo "==== gzip decompress file ===="
sed -i.bak -E 's/^inname.*/inname <- "test.pdf.gz";/' compression.port
sed -i.bak -E 's/^outname.*/outname <- "test.pdf";/' compression.port
port build -c ./compression.port
wc -l ./compression/gzip_decompress_file.strace
multitime -n 10 port run strace -d ../syscall_definitions.pickle -s ./compression/gzip_decompress_file.strace -a ./compression.auto

echo "==== rar compress file ===="
sed -i.bak -E 's/^inname.*/inname <- "hash_tables.py";/' compression.port
sed -i.bak -E 's/^outname.*/outname <- "files.rar";/' compression.port
port build -c ./compression.port
wc -l ./compression/rar_decompress_file.strace
multitime -n 10 port run strace -d ../syscall_definitions.pickle -s ./compression/rar_compress_file.strace -a ./compression.auto

echo "====  rar decompress file ===="
sed -i.bak -E 's/^inname.*/inname <- "files.rar";/' compression.port
sed -i.bak -E 's/^outname.*/outname <- "hash_tables.py";/' compression.port
port build -c ./compression.port
wc -l ./compression/rar_decompress_file.strace
multitime -n 10 port run strace -d ../syscall_definitions.pickle -s ./compression/rar_decompress_file.strace -a ./compression.auto

echo "==== bzip decompress file ===="
sed -i.bak -E 's/^inname.*/inname <- "hash_tables.py.bz2";/' compression.port
sed -i.bak -E 's/^outname.*/outname <- "hash_tables.py";/' compression.port
port build -c ./compression.port
wc -l ./compression/bzip_decompress_file.strace
multitime -n 10 port run strace -d ../syscall_definitions.pickle -s ./compression/bzip_decompress_file.strace -a ./compression.auto
