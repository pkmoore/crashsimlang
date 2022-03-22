echo "!!!! ---- Setup ---- !!!!"
RUNS=100
git restore ./compression.port
echo "!!!! ---- Compression Programs ---- !!!!"
echo "==== gzip compress file ===="
sed -i.bak -E 's/^inname.*/inname <- "test.pdf";/' compression.port
sed -i.bak -E 's/^outname.*/outname <- "test.pdf.gz";/' compression.port
port build -c ./compression.port
wc -l ./compression/gzip_compress_file.strace
multitime -n $RUNS port run strace -d ../syscall_definitions.pickle -s ./compression/gzip_compress_file.strace -a ./compression.auto

echo "==== gzip decompress file ===="
sed -i.bak -E 's/^inname.*/inname <- "test.pdf.gz";/' compression.port
sed -i.bak -E 's/^outname.*/outname <- "test.pdf";/' compression.port
port build -c ./compression.port
wc -l ./compression/gzip_decompress_file.strace
multitime -n $RUNS port run strace -d ../syscall_definitions.pickle -s ./compression/gzip_decompress_file.strace -a ./compression.auto

echo "==== rar compress file ===="
sed -i.bak -E 's/^inname.*/inname <- "hash_tables.py";/' compression.port
sed -i.bak -E 's/^outname.*/outname <- "files.rar";/' compression.port
port build -c ./compression.port
wc -l ./compression/rar_compress_file.strace
multitime -n $RUNS port run strace -d ../syscall_definitions.pickle -s ./compression/rar_compress_file.strace -a ./compression.auto

echo "====  rar decompress file ===="
sed -i.bak -E 's/^inname.*/inname <- "files.rar";/' compression.port
sed -i.bak -E 's/^outname.*/outname <- "hash_tables.py";/' compression.port
port build -c ./compression.port
wc -l ./compression/rar_decompress_file.strace
multitime -n $RUNS port run strace -d ../syscall_definitions.pickle -s ./compression/rar_decompress_file.strace -a ./compression.auto

echo "==== bzip decompress file ===="
sed -i.bak -E 's/^inname.*/inname <- "hash_tables.py.bz2";/' compression.port
sed -i.bak -E 's/^outname.*/outname <- "hash_tables.py";/' compression.port
port build -c ./compression.port
wc -l ./compression/bzip_decompress_file.strace
multitime -n $RUNS port run strace -d ../syscall_definitions.pickle -s ./compression/bzip_decompress_file.strace -a ./compression.auto

echo "!!!! ---- Network Programs ---- !!!!"
echo "==== ncat server ===="
port build -c ./server.port
wc -l ./network/ncat.strace
multitime -n $RUNS port run strace -d ../syscall_definitions.pickle -s ./network/ncat.strace -a ./server.auto

echo "==== socat server ===="
port build -c ./server.port
wc -l ./network/socat.strace
multitime -n $RUNS port run strace -d ../syscall_definitions.pickle -s ./network/socat.strace -a ./server.auto

echo "==== http.server server ===="
port build -c ./server.port
wc -l ./network/http.server.strace
multitime -n $RUNS port run strace -d ../syscall_definitions.pickle -s ./network/http.server.strace -a ./server.auto

echo "==== rsync client ===="
port build -c ./client.port
wc -l ./network/rsync_remote.strace
multitime -n $RUNS port run strace -d ../syscall_definitions.pickle -s ./network/rsync_remote.strace -a ./client.auto

echo "==== ssh client ===="
port build -c ./client.port
wc -l ./network/ssh_success.strace
multitime -n $RUNS port run strace -d ../syscall_definitions.pickle -s ./network/ssh_success.strace -a ./client.auto

echo "==== ftp client ===="
port build -c ./client.port
wc -l ./network/ftp_success.strace
multitime -n $RUNS port run strace -d ../syscall_definitions.pickle -s ./network/ftp_success.strace -a ./client.auto

echo "==== scp client ===="
port build -c ./client.port
wc -l ./network/scp_download.strace
multitime -n $RUNS port run strace -d ../syscall_definitions.pickle -s ./network/scp_download.strace -a ./client.auto

echo "==== telnet client ===="
port build -c ./client.port
wc -l ./network/telnet_remote.strace
multitime -n $RUNS port run strace -d ../syscall_definitions.pickle -s ./network/telnet_remote.strace -a ./client.auto

echo "!!!! ---- USB Streams ---- !!!!"
echo "==== BADUSB ===="
port build -c ./usbtest.port
wc -l ./usbjson.json
multitime -n $RUNS port run usbjson  -u ./usbjson.json -a ./usbtest.auto

echo "==== ID Conflict ===="
port build -c ./idconflict.port
wc -l ./idconflict.json
multitime -n $RUNS port run usbjson -u ./idconflict.json -a ./idconflict.auto

echo "!!!! ---- Teardown ---- !!!!"
git restore ./compression.port
rm compression.port.bak
