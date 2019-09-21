# pynvme

## Buffer
```python
Buffer(self, /, *args, **kwargs)
```
Buffer class allocated in DPDK memzone,so can be used by DMA. Data in buffer is clear to 0 in initialization.

__Attributes__

- `size (int)`: the size (in bytes) of the buffer. Default: 4096
- `name (str)`: the name of the buffer. Default: 'buffer'
- `pvalue (int)`: data pattern value. Default: 0
- `Different pattern type has different value definition`:
- `0`: 1-bit pattern: 0 for all-zero data, 1 for all-one data
- `32`: 32-bit pattern: 32-bit value of the pattern
- `0xbeef`: random data: random data compression percentage rate
- `else`: not supported
- `ptype (int)`: data pattern type. Default: 0
- `0`: 1-bit pattern
- `32`: 32-bit pattern
- `0xbeef`: random data
- `else`: not supported

- `Examples`:
```python
    >>> b = Buffer(1024, 'example')
    >>> b[0] = 0x5a
    >>> b[1:3] = [1, 2]
    >>> b[4:] = [10, 11, 12, 13]
    >>> b.dump(16)
    example
    00000000  5a 01 02 00 0a 0b 0c 0d  00 00 00 00 00 00 00 00   Z...............
    >>> b[:8:2]
    b'Z\x02\n\x0c'
    >>> b.data(2) == 2
    True
    >>> b[2] == 2
    True
    >>> b.data(2, 0) == 0x02015a
    True
    >>> len(b)
    1024
    >>> b
    <buffer name: example>
    >>> b[8:] = b'xyc'
    example
    00000000  5a 01 02 00 0a 0b 0c 0d  78 79 63 00 00 00 00 00   Z.......xyc.....
    >>> b.set_dsm_range(1, 0x1234567887654321, 0xabcdef12)
    >>> b.dump(64)
    buffer
    00000000  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  ................
    00000010  00 00 00 00 12 ef cd ab  21 43 65 87 78 56 34 12  ........!Ce.xV4.
    00000020  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  ................
    00000030  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00   ................
```

### data
```python
Buffer.data(self, byte_end, byte_begin, type)
```
get field in the buffer. Little endian for integers.

__Attributes__

- `byte_end (int)`: the end byte number of this field, which is specified in NVMe spec. Included.
- `byte_begin (int)`: the begin byte number of this field, which is specified in NVMe spec. It can be omitted if begin is the same as end when the field has only 1 byte. Included. Default: None, means only get 1 byte defined in byte_end
- `type (type)`: the type of the field. It should be int or str. Default: int, convert to integer python object

__Returns__

`(int or str)`: the data in the specified field

### dump
```python
Buffer.dump(self, size)
```
get the buffer content

__Attributes__

- `size`: the size of the buffer to print,. Default: None, means to print the whole buffer

### set_dsm_range
```python
Buffer.set_dsm_range(self, index, lba, lba_count)
```
set dsm ranges in the buffer, for dsm/deallocation (a.ka trim) commands

__Attributes__

- `index (int)`: the index of the dsm range to set
- `lba (int)`: the start lba of the range
- `lba_count (int)`: the lba count of the range

## config
```python
config(verify, fua_read=False, fua_write=False)
```
config driver global setting

__Attributes__

- `verify (bool)`: enable inline checksum verification of read
- `fua_read (bool)`: enable FUA of read. Default: False
- `fua_write (bool)`: enable FUA of write. Default: False

__Returns__

    None

## Controller
```python
Controller(self, /, *args, **kwargs)
```
Controller class. Prefer to use fixture "nvme0" in test scripts.

__Attributes__

- `addr (bytes)`: the bus/device/function address of the DUT, for example:
- `b'01`:00.0' (PCIe BDF address);
                  b'127.0.0.1' (TCP IP address).

- `Example`:
```python
    >>> n = Controller(b'01:00.0')
    >>> hex(n[0])     # CAP register
    '0x28030fff'
    >>> hex(n[0x1c])  # CSTS register
    '0x1'
    >>> n.id_data(23, 4, str)
    'TW0546VPLOH007A6003Y'
    >>> n.supports(0x18)
    False
    >>> n.supports(0x80)
    True
    >>> id_buf = Buffer()
    >>> n.identify().waitdone()
    >>> id_buf.dump(64)
    buffer
    00000000  a4 14 4b 1b 54 57 30 35  34 36 56 50 4c 4f 48 30  ..K.TW0546VPLOH0
    00000010  30 37 41 36 30 30 33 59  43 41 33 2d 38 44 32 35  07A6003YCA3-8D25
    00000020  36 2d 51 31 31 20 4e 56  4d 65 20 4c 49 54 45 4f  6-Q11 NVMe LITEO
    00000030  4e 20 32 35 36 47 42 20  20 20 20 20 20 20 20 20   N 256GB
    >>> n.cmdlog(2)
    driver.c:1451:log_cmd_dump: *NOTICE*: dump qpair 0, latest tail in cmdlog: 1
    driver.c:1462:log_cmd_dump: *NOTICE*: index 0, 2018-10-14 14:52:25.533708
    nvme_qpair.c: 118:nvme_admin_qpair_print_command: *NOTICE*: IDENTIFY (06) sqid:0 cid:0 nsid:1 cdw10:00000001 cdw11:00000000
    driver.c:1469:log_cmd_dump: *NOTICE*: index 0, 2018-10-14 14:52:25.534030
    nvme_qpair.c: 306:nvme_qpair_print_completion: *NOTICE*: SUCCESS (00/00) sqid:0 cid:95 cdw0:0 sqhd:0142 p:1 m:0 dnr:0
    driver.c:1462:log_cmd_dump: *NOTICE*: index 1, 1970-01-01 07:30:00.000000
    nvme_qpair.c: 118:nvme_admin_qpair_print_command: *NOTICE*: DELETE IO SQ (00) sqid:0 cid:0 nsid:0 cdw10:00000000 cdw11:00000000
    driver.c:1469:log_cmd_dump: *NOTICE*: index 1, 1970-01-01 07:30:00.000000
    nvme_qpair.c: 306:nvme_qpair_print_completion: *NOTICE*: SUCCESS (00/00) sqid:0 cid:0 cdw0:0 sqhd:0000 p:0 m:0 dnr:0
```

### abort
```python
Controller.abort(self, cid, sqid, cb)
```
abort admin commands

__Attributes__

- `cid (int)`: command id of the command to be aborted
- `sqid (int)`: sq id of the command to be aborted. Default: 0, to abort the admin command
- `cb (function)`: callback function called at completion. Default: None

__Returns__

    self (Controller)

### aer
```python
Controller.aer(self, cb)
```
asynchorous event request admin command.

Not suggested to use this command in scripts because driver manages to send and monitor aer commands. Scripts should register an aer callback function if it wants to handle aer, and use the fixture aer.

__Attributes__

- `cb (function)`: callback function called at completion. Default: None

__Returns__

    self (Controller)

### cap
64-bit CAP register of NVMe
### cmdlog
```python
Controller.cmdlog(self, count)
```
print recent commands and their completions.

__Attributes__

- `count (int)`: the number of commands to print. Default: 0, to print the whole cmdlog

### cmdname
```python
Controller.cmdname(self, opcode)
```
get the name of the admin command

__Attributes__

- `opcode (int)`: the opcode of the admin command

__Returns__

`(str)`: the command name

### disable_hmb
```python
Controller.disable_hmb(self)
```
disable HMB function
### downfw
```python
Controller.downfw(self, filename, slot, action)
```
firmware download utility: by 4K, and activate in next reset

__Attributes__

- `filename (str)`: the pathname of the firmware binary file to download
- `slot (int)`: firmware slot field in the command. Default: 0, decided by device
- `cb (function)`: callback function called at completion. Default: None

__Returns__


### dst
```python
Controller.dst(self, stc, nsid, cb)
```
device self test (DST) admin command

__Attributes__

- `stc (int)`: selftest code (stc) field in the command
- `nsid (int)`: nsid field in the command. Default: 0xffffffff
- `cb (function)`: callback function called at completion. Default: None

__Returns__

    self (Controller)

### enable_hmb
```python
Controller.enable_hmb(self)
```
enable HMB function
### format
```python
Controller.format(self, lbaf, ses, nsid, cb)
```
format admin command

__Attributes__

- `lbaf (int)`: lbaf (lba format) field in the command. Default: 0
- `ses (int)`: ses field in the command. Default: 0, no secure erase
- `nsid (int)`: nsid field in the command. Default: 1
- `cb (function)`: callback function called at completion. Default: None

__Returns__

    self (Controller)

### fw_commit
```python
Controller.fw_commit(self, slot, action, cb)
```
firmware commit admin command

__Attributes__

- `slot (int)`: firmware slot field in the command
- `action (int)`: action field in the command
- `cb (function)`: callback function called at completion. Default: None

__Returns__

    self (Controller)

### fw_download
```python
Controller.fw_download(self, buf, offset, size, cb)
```
firmware download admin command

__Attributes__

- `buf (Buffer)`: the buffer to hold the firmware data
- `offset (int)`: offset field in the command
- `size (int)`: size field in the command. Default: None, means the size of the buffer
- `cb (function)`: callback function called at completion. Default: None

__Returns__

    self (Controller)

### getfeatures
```python
Controller.getfeatures(self, fid, cdw11, cdw12, cdw13, cdw14, cdw15, sel, buf, cb)
```
getfeatures admin command

__Attributes__

- `fid (int)`: feature id
- `cdw11 (int)`: cdw11 in the command. Default: 0
- `sel (int)`: sel field in the command. Default: 0
- `buf (Buffer)`: the buffer to hold the feature data. Default: None
- `cb (function)`: callback function called at completion. Default: None

__Returns__

    self (Controller)

### getlogpage
```python
Controller.getlogpage(self, lid, buf, size, offset, nsid, cb)
```
getlogpage admin command

__Attributes__

- `lid (int)`: Log Page Identifier
- `buf (Buffer)`: buffer to hold the log page
- `size (int)`: size (in byte) of data to get from the log page,. Default: None, means the size is the same of the buffer
- `offset (int)`: the location within a log page
- `nsid (int)`: nsid field in the command. Default: 0xffffffff
- `cb (function)`: callback function called at completion. Default: None

__Returns__

    self (Controller)

### id_data
```python
Controller.id_data(self, byte_end, byte_begin, type, nsid, cns)
```
get field in controller identify data

__Attributes__

- `byte_end (int)`: the end byte number of this field, which is specified in NVMe spec. Included.
- `byte_begin (int)`: the begin byte number of this field, which is specified in NVMe spec. It can be omitted if begin is the same as end when the field has only 1 byte. Included. Default: None, means only get 1 byte defined in byte_end
- `type (type)`: the type of the field. It should be int or str. Default: int, convert to integer python object

__Returns__

`(int or str)`: the data in the specified field

### identify
```python
Controller.identify(self, buf, nsid, cns, cb)
```
identify admin command

__Attributes__

- `buf (Buffer)`: the buffer to hold the identify data
- `nsid (int)`: nsid field in the command. Default: 0
- `cns (int)`: cns field in the command. Default: 1
- `cb (function)`: callback function called at completion. Default: None

__Returns__

    self (Controller)

### mdts
max data transfer size
### register_aer_cb
```python
Controller.register_aer_cb(self, func)
```
register aer callback to driver.

It is recommended to use fixture aer(func) in pytest scripts.
When aer is triggered, the python callback function will
be called. It is unregistered by aer fixture when test finish.

__Attributes__

- `func (function)`: callback function called at aer completion

### reset
```python
Controller.reset(self)
```
controller reset: cc.en 1 => 0 => 1

__Notices__

    Test scripts should delete all io qpairs before reset!

### sanitize
```python
Controller.sanitize(self, option, pattern, cb)
```
sanitize admin command

__Attributes__

- `option (int)`: sanitize option field in the command
- `pattern (int)`: pattern field in the command for overwrite method. Default: 0x5aa5a55a
- `cb (function)`: callback function called at completion. Default: None

__Returns__

    self (Controller)

### send_cmd
```python
Controller.send_cmd(self, opcode, buf, nsid, cdw10, cdw11, cdw12, cdw13, cdw14, cdw15, cb)
```
send generic admin commands.

This is a generic method. Scripts can use this method to send all kinds of commands, like Vendor Specific commands, and even not existed commands.

__Attributes__

- `opcode (int)`: operate code of the command
- `buf (Buffer)`: buffer of the command. Default: None
- `nsid (int)`: nsid field of the command. Default: 0
- `cb (function)`: callback function called at completion. Default: None

__Returns__

    self (Controller)

### setfeatures
```python
Controller.setfeatures(self, fid, cdw11, cdw12, cdw13, cdw14, cdw15, sv, buf, cb)
```
setfeatures admin command

__Attributes__

- `fid (int)`: feature id
- `cdw11 (int)`: cdw11 in the command. Default: 0
- `sv (int)`: sv field in the command. Default: 0
- `buf (Buffer)`: the buffer to hold the feature data. Default: None
- `cb (function)`: callback function called at completion. Default: None

__Returns__

    self (Controller)

### supports
```python
Controller.supports(self, opcode)
```
check if the admin command is supported

__Attributes__

- `opcode (int)`: the opcode of the admin command

__Returns__

`(bool)`: if the command is supported

### timeout
timeout value of this controller in milli-seconds.

It is configurable by assigning new value in milli-seconds.

### waitdone
```python
Controller.waitdone(self, expected)
```
sync until expected commands completion

__Attributes__

- `expected (int)`: expected commands to complete. Default: 1

__Notices__

    Do not call this function in commands callback functions.

## DotDict
```python
DotDict(self, *args, **kwargs)
```
utility class to access dict members by . operation
## Namespace
```python
Namespace(self, /, *args, **kwargs)
```
Namespace class. Prefer to use fixture "nvme0n1" in test scripts.

__Attributes__

- `nvme (Controller)`: controller where to create the queue
- `nsid (int)`: nsid of the namespace

### capacity
bytes of namespace capacity
### close
```python
Namespace.close(self)
```
close namespace to release it resources in host memory.

Notice:
    Release resources explictly, del is not garentee to call __dealloc__.
    Fixture nvme0n1 uses this function, and prefer to use fixture in scripts, instead of calling this function directly.

### cmdname
```python
Namespace.cmdname(self, opcode)
```
get the name of the IO command

__Attributes__

- `opcode (int)`: the opcode of the IO command

__Returns__

`(str)`: the command name

### compare
```python
Namespace.compare(self, qpair, buf, lba, lba_count, io_flags, cb)
```
compare IO command

__Attributes__

- `qpair (Qpair)`: use the qpair to send this command
- `buf (Buffer)`: the data buffer of the command, meta data is not supported.
- `lba (int)`: the starting lba address, 64 bits
- `lba_count (int)`: the lba count of this command, 16 bits. Default: 1
- `io_flags (int)`: io flags defined in NVMe specification, 16 bits. Default: 0
- `cb (function)`: callback function called at completion. Default: None

__Returns__

`qpair (Qpair)`: the qpair used to send this command, for ease of chained call

__Raises__

- `SystemError`: the command fails

__Notices__

    buf cannot be released before the command completes.

### dsm
```python
Namespace.dsm(self, qpair, buf, range_count, attribute, cb)
```
data-set management IO command

__Attributes__

- `qpair (Qpair)`: use the qpair to send this command
- `buf (Buffer)`: the buffer of the lba ranges. Use buffer.set_dsm_range to prepare the buffer.
- `range_count (int)`: the count of lba ranges in the buffer
- `attribute (int)`: attribute field of the command. Default: 0x4, as deallocation/trim
- `cb (function)`: callback function called at completion. Default: None

__Returns__

`qpair (Qpair)`: the qpair used to send this command, for ease of chained call

__Raises__

- `SystemError`: the command fails

__Notices__

    buf cannot be released before the command completes.

### flush
```python
Namespace.flush(self, qpair, cb)
```
flush IO command

__Attributes__

- `qpair (Qpair)`: use the qpair to send this command
- `cb (function)`: callback function called at completion. Default: None

__Returns__

`qpair (Qpair)`: the qpair used to send this command, for ease of chained call

__Raises__

- `SystemError`: the command fails

### format
```python
Namespace.format(self, data_size, meta_size, ses)
```
change the format of this namespace

__Attributes__

- `data_size (int)`: data size. Default: 512
- `meta_size (int)`: meta data size. Default: 0
- `ses (int)`: ses field in the command. Default: 0, no secure erase

__Returns__

`(int or None)`: the lba format has the specified data size and meta data size

__Notices__

    this facility not only sends format admin command, but also updates driver to activate new format immediately

### get_lba_format
```python
Namespace.get_lba_format(self, data_size, meta_size)
```
find the lba format by its data size and meta data size

__Attributes__

- `data_size (int)`: data size. Default: 512
- `meta_size (int)`: meta data size. Default: 0

__Returns__

`(int or None)`: the lba format has the specified data size and meta data size

### id_data
```python
Namespace.id_data(self, byte_end, byte_begin, type)
```
get field in namespace identify data

__Attributes__

- `byte_end (int)`: the end byte number of this field, which is specified in NVMe spec. Included.
- `byte_begin (int)`: the begin byte number of this field, which is specified in NVMe spec. It can be omitted if begin is the same as end when the field has only 1 byte. Included. Default: None, means only get 1 byte defined in byte_end
- `type (type)`: the type of the field. It should be int or str. Default: int, convert to integer python object

__Returns__

`(int or str)`: the data in the specified field

### ioworker
```python
Namespace.ioworker(self, io_size, lba_align, lba_random, read_percentage, time, qdepth, region_start, region_end, iops, io_count, lba_start, qprio, pvalue, ptype, output_io_per_second, output_percentile_latency)
```
workers sending different read/write IO on different CPU cores.

User defines IO characteristics in parameters, and then the ioworker
executes without user intervesion, until the test is completed. IOWorker
returns some statistic data at last.

User can start multiple IOWorkers, and they will be binded to different
CPU cores. Each IOWorker creates its own Qpair, so active IOWorker counts
is limited by maximum IO queues that DUT can provide.

Each ioworker can run upto 24 hours.

__Attributes__

- `io_size (short)`: IO size, unit is LBA
- `lba_align (short)`: IO alignment, unit is LBA
- `lba_random (bool)`: True if sending IO with random starting LBA
- `read_percentage (int)`: sending read/write mixed IO, 0 means write only, 100 means read only
- `time (int)`: specified maximum time of the IOWorker in seconds, up to 24*3600. Default:0, means no limit
- `qdepth (int)`: queue depth of the Qpair created by the IOWorker, up to 1024. Default: 64
- `region_start (long)`: sending IO in the specified LBA region, start. Default: 0
- `region_end (long)`: sending IO in the specified LBA region, end but not include. Default: 0xffff_ffff_ffff_ffff
- `iops (int)`: specified maximum IOPS. IOWorker throttles the sending IO speed. Default: 0, means no limit
- `io_count (long)`: specified maximum IO counts to send. Default: 0, means no limit
- `lba_start (long)`: the LBA address of the first command. Default: 0, means start from region_start
- `qprio (int)`: SQ priority. Default: 0, as Round Robin arbitration
- `pvalue (int)`: data pattern value. Refer to class Buffer. Default: 0
- `ptype (int)`: data pattern type. Refer to class Buffer. Default: 0
- `output_io_per_second (list)`: list to hold the output data of io_per_second. Default: None, not to collect the data
- `output_percentile_latency (dict)`: dict of io counter on different percentile latency. Dict key is the percentage, and the value is the latency in ms. Default: None, not to collect the data

__Returns__

    ioworker object

### nsid
id of the namespace
### read
```python
Namespace.read(self, qpair, buf, lba, lba_count, io_flags, cb)
```
read IO command

__Attributes__

- `qpair (Qpair)`: use the qpair to send this command
- `buf (Buffer)`: the data buffer of the command, meta data is not supported.
- `lba (int)`: the starting lba address, 64 bits
- `lba_count (int)`: the lba count of this command, 16 bits. Default: 1
- `io_flags (int)`: io flags defined in NVMe specification, 16 bits. Default: 0
- `cb (function)`: callback function called at completion. Default: None

__Returns__

`qpair (Qpair)`: the qpair used to send this command, for ease of chained call

__Raises__

- `SystemError`: the read command fails

__Notices__

    buf cannot be released before the command completes.

### send_cmd
```python
Namespace.send_cmd(self, opcode, qpair, buf, nsid, cdw10, cdw11, cdw12, cdw13, cdw14, cdw15, cb)
```
send generic IO commands.

This is a generic method. Scripts can use this method to send all kinds of commands, like Vendor Specific commands, and even not existed commands.

__Attributes__

- `opcode (int)`: operate code of the command
- `qpair (Qpair)`: qpair used to send this command
- `buf (Buffer)`: buffer of the command. Default: None
- `nsid (int)`: nsid field of the command. Default: 0
- `cb (function)`: callback function called at completion. Default: None

__Returns__

`qpair (Qpair)`: the qpair used to send this command, for ease of chained call

### supports
```python
Namespace.supports(self, opcode)
```
check if the IO command is supported

__Attributes__

- `opcode (int)`: the opcode of the IO command

__Returns__

`(bool)`: if the command is supported

### write
```python
Namespace.write(self, qpair, buf, lba, lba_count, io_flags, cb)
```
write IO command

__Attributes__

- `qpair (Qpair)`: use the qpair to send this command
- `buf (Buffer)`: the data buffer of the write command, meta data is not supported.
- `lba (int)`: the starting lba address, 64 bits
- `lba_count (int)`: the lba count of this command, 16 bits
- `io_flags (int)`: io flags defined in NVMe specification, 16 bits. Default: 0
- `cb (function)`: callback function called at completion. Default: None

__Returns__

`qpair (Qpair)`: the qpair used to send this command, for ease of chained call

__Raises__

- `SystemError`: the write command fails

__Notices__

    buf cannot be released before the command completes.

### write_uncorrectable
```python
Namespace.write_uncorrectable(self, qpair, lba, lba_count, cb)
```
write uncorrectable IO command

__Attributes__

- `qpair (Qpair)`: use the qpair to send this command
- `lba (int)`: the starting lba address, 64 bits
- `lba_count (int)`: the lba count of this command, 16 bits. Default: 1
- `cb (function)`: callback function called at completion. Default: None

__Returns__

`qpair (Qpair)`: the qpair used to send this command, for ease of chained call

__Raises__

- `SystemError`: the command fails

### write_zeroes
```python
Namespace.write_zeroes(self, qpair, lba, lba_count, io_flags, cb)
```
write zeroes IO command

__Attributes__

- `qpair (Qpair)`: use the qpair to send this command
- `lba (int)`: the starting lba address, 64 bits
- `lba_count (int)`: the lba count of this command, 16 bits. Default: 1
- `io_flags (int)`: io flags defined in NVMe specification, 16 bits. Default: 0
- `cb (function)`: callback function called at completion. Default: None

__Returns__

`qpair (Qpair)`: the qpair used to send this command, for ease of chained call

__Raises__

- `SystemError`: the command fails

## Pcie
```python
Pcie(self, /, *args, **kwargs)
```
Pcie class. Prefer to use fixture "pcie" in test scripts

__Attributes__

- `nvme (Controller)`: the nvme controller object of that subsystem

### cap_offset
```python
Pcie.cap_offset(self, cap_id)
```
get the offset of a capability

__Attributes__

- `cap_id (int)`: capability id

__Returns__

`(int)`: the offset of the register
    or None if the capability is not existed

### register
```python
Pcie.register(self, offset, byte_count)
```
access registers in pcie config space, and get its integer value.

__Attributes__

- `offset (int)`: the offset (in bytes) of the register in the config space
- `byte_count (int)`: the size (in bytes) of the register

__Returns__

`(int)`: the value of the register

### reset
```python
Pcie.reset(self)
```
reset this pcie device
## Qpair
```python
Qpair(self, /, *args, **kwargs)
```
Qpair class. IO SQ and CQ are combinded as qpairs.

__Attributes__

- `nvme (Controller)`: controller where to create the queue
- `depth (int)`: SQ/CQ queue depth
- `prio (int)`: when Weighted Round Robin is enabled, specify SQ priority here

### cmdlog
```python
Qpair.cmdlog(self, count)
```
print recent IO commands and their completions in this qpair.

__Attributes__

- `count (int)`: the number of commands to print. Default: 0, to print the whole cmdlog

### waitdone
```python
Qpair.waitdone(self, expected)
```
sync until expected commands completion

__Attributes__

- `expected (int)`: expected commands to complete. Default: 1

__Notices__

    Do not call this function in commands callback functions.

## Subsystem
```python
Subsystem(self, /, *args, **kwargs)
```
Subsystem class. Prefer to use fixture "subsystem" in test scripts.

__Attributes__

- `nvme (Controller)`: the nvme controller object of that subsystem

### power_cycle
```python
Subsystem.power_cycle(self, sec)
```
power off and on in seconds

__Attributes__

- `sec (int)`: the seconds between power off and power on

### reset
```python
Subsystem.reset(self)
```
reset the nvme subsystem through register nssr.nssrc
### shutdown_notify
```python
Subsystem.shutdown_notify(self, abrupt)
```
notify nvme subsystem a shutdown event through register cc.chn

__Attributes__

- `abrupt (bool)`: it will be an abrupt shutdown (return immediately) or clean shutdown (wait shutdown completely)
