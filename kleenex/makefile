all: stat64_simulate_S_IFBLK.bin fstat64_simulate_S_IFBLK.bin time_simulate_reverse_time.bin poll_simulate_long_timeout.bin

stat64_simulate_S_IFBLK.bin: stat64_simulate_S_IFBLK.kex
	kexc compile stat64_simulate_s_IFBLK.kex --out stat64_simulate_S_IFBLK.bin

fstat64_simulate_S_IFBLK.bin: fstat64_simulate_S_IFBLK.kex
	kexc compile fstat64_simulate_S_IFBLK.kex --out fstat64_simulate_S_IFBLK.bin

time_simulate_reverse_time.bin: time_simulate_reverse_time.kex
	kexc compile time_simulate_reverse_time.kex --out time_simulate_reverse_time.bin

poll_simulate_long_timeout.bin: poll_simulate_long_timeout.kex
	kexc compile poll_simulate_long_timeout.kex --out poll_simulate_long_timeout.bin

clean:
	- rm *.pdf
	- rm *.bin
