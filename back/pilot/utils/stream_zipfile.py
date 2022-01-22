import zipfile, zlib, binascii, struct, time


class BufferedZipFile(zipfile.ZipFile):
    def write_s3_streaming_body(self, arcname, streaming_body):
        zinfo = zipfile.ZipInfo(
            filename=arcname,
            date_time=time.localtime(time.time())[:6]
        )
        zinfo.compress_type = self.compression
        zinfo._compresslevel = self.compresslevel
        if zinfo.filename[-1] == '/':
            zinfo.external_attr = 0o40775 << 16   # drwxrwxr-x
            zinfo.external_attr |= 0x10           # MS-DOS directory flag
        else:
            zinfo.external_attr = 0o600 << 16     # ?rw-------

        if not self.fp:
            raise ValueError(
                "Attempt to write to ZIP archive that was already closed")
        if self._writing:
            raise ValueError(
                "Can't write to ZIP archive while an open writing handle exists."
            )

        zinfo.file_size = int(streaming_body._content_length)            # Uncompressed size
        with self._lock:
            with self.open(zinfo, mode='w') as dest:
                while True:
                    data = streaming_body.read(1024 * 8)
                    if not data:
                        break
                    dest.write(data)

    """
    Inspired by :
    https://stackoverflow.com/questions/297345/create-a-zip-file-from-a-generator-in-python/299830#299830
    """
    def write_buffered(self, zinfo_or_arcname, buffer):
        if not isinstance(zinfo_or_arcname, zipfile.ZipInfo):
            zinfo = zipfile.ZipInfo(
                filename=zinfo_or_arcname,
                date_time=time.localtime(time.time())[:6]
            )
            zinfo.compress_type = self.compression
            zinfo._compresslevel = self.compresslevel
            if zinfo.filename[-1] == '/':
                zinfo.external_attr = 0o40775 << 16   # drwxrwxr-x
                zinfo.external_attr |= 0x10           # MS-DOS directory flag
            else:
                zinfo.external_attr = 0o600 << 16     # ?rw-------
        else:
            zinfo = zinfo_or_arcname

        zinfo.file_size = file_size = 0
        zinfo.flag_bits = 0x00
        zinfo.header_offset = self.fp.tell()

        self._writecheck(zinfo)
        self._didModify = True

        zinfo.CRC = CRC = 0
        zinfo.compress_size = compress_size = 0
        self.fp.write(zinfo.FileHeader())
        if zinfo.compress_type == zipfile.ZIP_DEFLATED:
            cmpr = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -15)
        else:
            cmpr = None

        while True:
            buf = buffer.read(1024 * 8)
            if not buf:
                break

            file_size = file_size + len(buf)
            CRC = binascii.crc32(buf, CRC) & 0xffffffff
            if cmpr:
                buf = cmpr.compress(buf)
                compress_size = compress_size + len(buf)

            self.fp.write(buf)

        if cmpr:
            buf = cmpr.flush()
            compress_size = compress_size + len(buf)
            self.fp.write(buf)
            zinfo.compress_size = compress_size
        else:
            zinfo.compress_size = file_size

        zinfo.CRC = CRC
        zinfo.file_size = file_size

        position = self.fp.tell()
        self.fp.seek(zinfo.header_offset + 14, 0)
        self.fp.write(struct.pack("<LLL", zinfo.CRC, zinfo.compress_size, zinfo.file_size))
        self.fp.seek(position, 0)
        self.filelist.append(zinfo)
        self.NameToInfo[zinfo.filename] = zinfo