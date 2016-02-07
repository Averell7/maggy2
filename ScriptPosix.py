#!/usr/local/bin/python
# coding: utf-8 -*-

# Version 1.95 - Two new functions: recordFilenames() and VerifyDiscSpace() - Apr 10th, 2012
# Version 1.94 - Correction of minor bugs and integration in 1.94 revision
# Version 1.89.6 - Bug fix in gauge display of compressed and crypted files
# Version 1.89.5 - New fileCopy() algorithm (for write protected files)
# Version 1.89.4 - New gauge process in copy functions
# Version 1.89.2 - copyFile() function reworked
# Version 1.7.0 - New name Archeotes
# Version 1.6.7 - utf-8 support
# Version 1.4.5 - bugfix
# Version 1.4.4 - updated str2sql function
# Version 1.4.2 - added unCompFile function

###########################################################################
# SYSTEM LIBS #############################################################
###########################################################################

import os
import sys
import stat
import signal
import threading
import socket
import shutil
import gzip
import bz2
import base64
import re
import tempfile
#from ncrypt.digest import DigestType, Digest
#from ncrypt.cipher import *
from stat import *              # Aug 24th, 2011 - For os.chmod() function
#
#if os.name == "nt" :
#    import win32file

###########################################################################
#   CONFIGURATION  ########################################################
###########################################################################



fileLog = 0
fileErr = 0

###########################################################################
# ENUMS ###################################################################
###########################################################################

ok_e, warning_e, error_e = range(3)


###########################################################################
# CLASSES #################################################################
###########################################################################

class ScriptPosix(object) :
    """
    interface to posix operating system
    """

    # ---- enums ----

    # os
    (
    linux_e,
    windows_e
    ) = range(2)

    # compress type
    (
    noCompress_e,
    gzip_e,
    bzip2_e
    ) = range(3)

    # ---- constants ----

    # os
    _posix_cs = "posix" # unix like os

    # file sizes
    _kiloByte_c = 1024
    _megaByte_c = 1024 * _kiloByte_c
    _gigaByte_c = 1024 * _megaByte_c

    # units
    _byte_cs = "B"
    _kiloByte_cs = "K"
    _megaByte_cs = "M"
    _gigaByte_cs = "G"

    # local ip
    _localIp_cs = "127.0.0.1"
    _localHost_cs = "localhost"

    # default values
    _bufferSize_c = 256 * _kiloByte_c

    # ---- static methods ----

    @staticmethod
    def str2regexp(
            str_s) :
        """
        convert jokers into regexp
        @param str_s : joker expressions
        @return regexp_s : converted expression
        """
        tmp1_s = str_s.replace(".", "\\.")
        tmp2_s = tmp1_s.replace("?", ".")
        tmp3_s = tmp2_s.replace("*", ".*")
        return(tmp3_s)

    @staticmethod
    def str2sql(
            string_s) :
        """
        convert a filter into sql like syntax
        @param string_s : filter expression
        @return regexp_s : converted expression ready to be used in a where clause
        """

        #  Replace strings in "" to prevent difficulties in parsing files
        #+ like "Documents and settings" which contains "and", "or" and so on
        x = re.findall('".*?"', string_s)

        i = 0
        quotes_a = []
        for a in x :
            string_s = string_s.replace(a, "{" + str(i) + "}", 1)
            quotes_a += [a]
            i += 1

        # Suppress spaces before and after =<>
        string_s = re.sub(r'\s*([=<>])\s*', r"\1", string_s)

        # Now all filters should be solid blocks without space.
        # They are ready to be detected
        filters_a = re.findall('[a-z]*[=<>][^(),\s]*', string_s)


        # Extract the logic structure
        i = 0
        for a in filters_a :
            string_s = string_s.replace(a, "{" + str(i) + "}", 1)
            i += 1
        logic_s = string_s.replace(",", " or ")    # the comma is equivalent to OR

        # replace back what was replaced in the first steps to restore the filters
        i = 0
        for a in quotes_a :
            for b in filters_a :
                if -1 < b.find("{" + str(i) + "}") :
                    temp_s = b.replace("{" + str(i) + "}", quotes_a[i])
                    filters_a[i] = temp_s
                    i += 1
                    continue

        #  Now we have separate filters, convert them to slq syntax which means :
        #+ Replace = by like for strings
        #+ Add quotes when necessary
        #+ Replace * by % and ? by _
        #+ Replace values in K, M? G by an integer.

        i = 0
        filter2_a = []

        for filter_s in   filters_a :

            result_t = re.findall('([a-z]*)([=<>]*)(.*)', filter_s)
            (type_s, operator_s, value_s) = result_t[0]


            if type_s == BackupDefine._size_cs :
                value_s = ScriptPosix.str2size(value_s)
                value_s = str(value_s)

            if type_s == BackupDefine._path_cs :
                type_s = BackupDefine._fullpath_cs

            if type_s in [ BackupDefine._fullpath_cs,
                             BackupDefine._name_cs,
                             BackupDefine._ext_cs ] :
                operator_s = " like "
                if value_s[0:1] in [ "'", '"' ] :
                    pass
                else :
                    value_s = '"' + value_s + '"'
                tmp1_s = value_s.replace("?", "_")
                value_s = tmp1_s.replace("*", "%")


            filter2_a += [type_s + operator_s + value_s]
            i += 1

        # Recombine the complete filter
        where_s = logic_s
        for i in range(len(filter2_a)) :
            where_s = where_s.replace("{" + str(i) + "}", filter2_a[i], 1)
        return where_s


    @staticmethod
    def str2size(
            str_s) :
        # ----
        # convert size string into integer
        # ----
        if 0 == len(str_s) :
            return(0)
        if str_s.isdigit() :
            return(int(str_s))
        unit_s = str_s[-1].upper()
        value_s = str_s[:-1]
        if ScriptPosix._byte_cs == unit_s :
            return(int(value_s))
        elif ScriptPosix._kiloByte_cs == unit_s :
            return(int(value_s) * ScriptPosix._kiloByte_c)
        elif ScriptPosix._megaByte_cs == unit_s :
            return(int(value_s) * ScriptPosix._megaByte_c)
        elif ScriptPosix._gigaByte_cs == unit_s :
            return(int(value_s) * ScriptPosix._gigaByte_c)
        else :
            raise ScriptRt("unit \"%s\" is unknown" % (unit_s))

    @staticmethod
    def size2str(
            size_i) :
        # ----
        # convert size into short string
        # ----
        if 0 == size_i :
            return(0)

        if size_i > ScriptPosix._gigaByte_c :
            temp1 = float(size_i) / ScriptPosix._gigaByte_c
            value_s = "%.1f" % temp1 + _(" GB")     # give the value with one decimal
        elif size_i > ScriptPosix._megaByte_c :
            temp1 = float(size_i) / ScriptPosix._megaByte_c
            if temp1 < 10 :
                value_s = "%.1f" % temp1 + _(" MB")     # give the value with one decimal
            else :
                value_s = str(int(temp1)) + _(" MB")
        elif size_i > ScriptPosix._kiloByte_c :
            value_s = str(int(size_i / ScriptPosix._kiloByte_c)) + " KB"
        else :
            value_s = str(size_i) + " Bytes"
        return value_s



    @staticmethod
    def quotes(
            str_s) :
        # Remove quotes
        # TODO : deprecated. Should be replaced by remove_quotes below.
        if str_s[0:1] == '"' :
            str_s = str_s[1:]
        if str_s[-1:] == '"' :
            str_s = str_s[:-1]
        return str_s

    @staticmethod
    def remove_quotes(
            str_s,
            both = False,
            trailing_slash = False) :
        # Remove quotes in the beginning and end of a chain.
        # Improved copy of the "quotes" function above, renamed for clarity.
        # Parameter : both : If set to True, quotes will be removed only if begin and end quotes match
        # returns : The string either with quotes removed, or unmodified if conditions where not met

        if both == False :
            if str_s[0:1] == '"' or str_s[0:1] == "'" :
                str_s = str_s[1:]
            if str_s[-1:] == '"' or str_s[-1:] == "'" :
                str_s = str_s[:-1]

        else :
            if ((str_s[0:1] == '"' and str_s[-1:] == '"')
                  or (str_s[0:1] == "'" and str_s[-1:] == "'")) :
                str_s = str_s[1:-1]

        if trailing_slash :
            if str_s[-1:] == "/" or str_s[-1:] == "\\" :
                str_s = str_s[:-1]

        return str_s

    @staticmethod
    def add_quotes(
                str_s,
                quote_s = '"') :
        # Checks if string is quoted. If not, quotes it.
        # parameters : quote_s : The string to check
        #               quote_s : The quote to use
        str_s = str_s.strip()
        if str_s[0:1] == '"' and str_s[-1:] == '"' :    # Quotes already present
            return
        if str_s[0:1] == "'" and str_s[-1:] == "'" :    # Quotes already present
            return

        else :
            str_s = quote_s + str_s + quote_s

        return str_s

    @staticmethod
    def printExcept() :
        a,b,c = sys.exc_info()
        for d in traceback.format_exception(a,b,c) :
            print d,

    # ---- ctors ----

    def __init__(
            self) :
        """
        ctor
        @param logging : loging layer
        """

        # ---- data ----


        # login
        self._euid_s = ""
        self._user_s = ""
        self._pid = 0
        # current hostname
        self._hostname_s = socket.gethostname()
        # os dependent
        self._tmpDir_s = "/tmp"
        self._sep_s = "/"
        self._isWin32 = False
        self._encodelist = []
        self._decodelist = {}
        self._key_s = ""
        self.data_dir = {}
        self.fileCnt = 0

        # ---- code ----

        # check os
        if ScriptPosix._posix_cs != os.name :
            self._isWin32 = True
            self._os = ScriptPosix.windows_e
#           self._tmpDir_s = self.getEnviron("TMP")
            self._tmpDir_s = "\\tmp"  # Gaston - March 26th, 2012
            self._sep_s = "\\"
            self._euid_s = "0"
        else :
            self._os = ScriptPosix.linux_e
            self._euid_s = "%d" % (os.geteuid())

        # catch signals
        thId_s = threading.currentThread().getName()

        # extract path
        (self._prog_s, self._pwd_s, self._base_s) = self.extractBase()


        self._pid = os.getpid()

    # ---- methods ----

    def nameEncode(
            self,
            string,
            basekey) :
        out = ""
        i = 0
        for a in string :
            if a in self._decodelist :

                key = basekey[i % len(basekey)]
                i += 1
                start = self._decodelist[a]
                delta = self._decodelist[key]
                shift = (start + delta) % len(self._decodelist)
                stop = self._encodelist[shift]
                out += stop
            else :
                out += a
        return out

    def nameDecode(
            self,
            string,
            basekey) :
        out2 = ""
        i = 0
        for a in string:
            if a in self._decodelist :
                key = basekey[i % len(basekey)]
                i += 1
                start = self._decodelist[a]
                delta = self._decodelist[key]
                shift = (start - delta) % len(self._decodelist)
                stop = self._encodelist[shift]
                out2 += stop
            else :
                out2 += a
        return out2

    def generateKey(
            self,
            cryptkey,
            text) :

        key_s = cryptkey._key_s
        iv_s = cryptkey._iv_s
        mode_s = cryptkey._mode_s
        algo_s = cryptkey._algo_s
        ct = CipherType(
                    algo_s,
                    mode_s)
        enc = EncryptCipher(
                        ct,
                        key_s,
                        iv_s)
        # crypt body
        c1 = enc.update(text)
        # crypt footer
        c2 = enc.finish()

        md5_s = ScriptPosix.stringMd5(
                self,
                c1 + c2)
        keyA = base64.b32encode(md5_s)[:-4]

        return keyA

    def createCryptList(
            self) :
        cryptlist = [40, 41, 45, 95]                   # -_()
        cryptlist = cryptlist + range(48, 58)        # 0-9
        cryptlist = cryptlist + range(65, 91)        # A-Z
        cryptlist = cryptlist + range(97, 123)       # a-z

        limit = len(cryptlist)
        self._encodelist = [ i for i in range(limit) ]
        self._decodelist = {}
        for i in range(limit) :
            self._encodelist[i] = chr(cryptlist[i])
            self._decodelist[chr(cryptlist[i])] = i
        return(True)

    def convertPath(
            self,
            path,
            osType = 0) :
        if 1 == osType :
            path = path.replace(":","")
        path = path.replace("\\","/")
        path = path.replace("//","/")
        return(path)

    def setKey(
            self,
            key_s) :
        """
        set file key
        """
        self._log.dispTitle("setting new key")
        self._key_s = key_s
        self._log.dispLog("ok, done")
        return(True)

    def cryptFile(
            self,
            algo_i,
            scriptKey,
            input_u,
            output_u,
            view = 1,
            realInput_u = "",
            originalSize_i = 0) :
        """
        crypt file
        """
        st = os.stat(input_u)
        size_i = st.st_size
        if view == 2 :
            # in case of compressed and encrypted file, the file is considered already treated at 50%
            processedSize_i = originalSize_i / 2
            # We must take in consideration that we are encrypting a compressed file, which size is different from the original
            ratio_l = (float(originalSize_i) / size_i) / 2
        else :
            processedSize_i = 0

        deleteFile_b = False

        try :
            fileIn = open(input_u, "rb")
            fileOut = open(output_u, "wb")
            try :
                # init
                cT = CipherType(
                    scriptKey._algo_s,
                    scriptKey._mode_s)
                enc = EncryptCipher(
                        cT,
                        scriptKey._key_s,
                        scriptKey._iv_s)
                # crypt body
                while True :
                    fileBuffer = fileIn.read(
                            ScriptPosix._bufferSize_c)
                    # check eof
                    if not fileBuffer :
                        break
                    # process buffer
                    cryptedBuffer = enc.update(
                            fileBuffer)
                    fileOut.write(cryptedBuffer)

                    if self.BFSGui.cancelState == 1 :       # Handle cancel button
                        deleteFile_b = True
                        break

                    #Update the gauge
                    if view == 1 :
                        processedSize_i += len(fileBuffer)
                        self.BFSGui.ShowBigFilesProgress(size_i, processedSize_i, input_u)
                    elif view == 2 :
                        # in case of compressed and encrypted file, we update the gauge using the values of the original file
                        processedSize_i += int(len(fileBuffer) * ratio_l)
                        self.BFSGui.ShowBigFilesProgress(originalSize_i, processedSize_i, realInput_u)

                # crypt footer
                cryptedBuffer = enc.finish()
                fileOut.write(cryptedBuffer)
            except CipherError, CEInst :
                raise ScriptRt(repr(CEInst))
            finally :
                fileIn.close()
                fileOut.close()
                if deleteFile_b == True :       # if process was interrupted, delete the partially copied file
                    os.remove(output_u)
                    return (False)

        except IOError, IOInst :
            raise ScriptRt(repr(IOInst))
        return(True)

    def compressFile(
            self,
            input_u,
            output_u,
            compressType,
            view = 1) :
        """
        compress file
        """
        st = os.stat(input_u)
        size_i = st.st_size
        processedSize_i = 0
        deleteFile_b = False

        try :
            fileIn = open(input_u, "rb")
            if ScriptPosix.gzip_e == compressType :
                regularFile = open(output_u,"wb")
                zipFilename_u = os.path.split(output_u)[1]
                zipFilename_s = zipFilename_u.encode("utf-8")
                fileOut = gzip.GzipFile(zipFilename_s, "wb", 9, regularFile)  # todo filename
            elif ScriptPosix.bzip2_e == compressType :
                fileOut = bz2.BZ2File(output_u, "wb")
            else :
                raise ScriptRt("compression type")
            try :
                while True :
                    fileBuffer = fileIn.read(ScriptPosix._bufferSize_c)
                    # check eof
                    if not fileBuffer :
                        break
                    # process buffer
                    fileOut.write(fileBuffer)


##                    if self.BFSGui.cancelState == 1 :
##                        deleteFile_b = True
##                        break

                    #Update the gauge
                    if view == 1 :
                        processedSize_i += int(len(fileBuffer))
                        self.BFSGui.ShowBigFilesProgress(size_i, processedSize_i, input_u)

            except :
                os.unlink(output_u)
                raise ScriptRt("compressing file")
            finally :
                fileIn.close()
                fileOut.close()
                regularFile.close()
                if deleteFile_b == True :       # if process was interrupted, delete the partially copied file
                    os.remove(output_u)
                    return (False)
                return (True)
        except IOError, IOInst :
            raise ScriptRt(repr(IOInst))

    def cryptCompFile(
            self,
            algo_i,
            scriptKey,
            input_u,
            output_u,
            compressType,
            view = 1) :
        """
        crypt and compress file
        """
        st = os.stat(input_u)
        size_i = st.st_size
        processedSize_i = 0
        ok_b = True

        if ScriptPosix.noCompress_e != compressType :
            # first compress file
            tmpOutput_s = "." + os.path.join( #@@@@@@@@ The "." + is mandatory (".\tmp\xxxxxxx.yyy) !!!
                    self._tmpDir_s,
                    "ScriptPosix%d" % self._pid)
            try :
                fileIn = open(input_u, "rb")
                if ScriptPosix.gzip_e == compressType :
                    fileOut = gzip.GzipFile(tmpOutput_s, "wb")
                elif ScriptPosix.bzip2_e == compressType :
                    fileOut = bz2.BZ2File(tmpOutput_s, "wb")
                else :
                    raise ScriptRt("compression type")
                try :
                    while True :
                        fileBuffer = fileIn.read(ScriptPosix._bufferSize_c)
                        # check eof
                        if not fileBuffer :
                            break
                        # process buffer
                        fileOut.write(fileBuffer)

                        if self.BFSGui.cancelState == 1 :
                            ok_b = False
                            break

                        #Update the gauge
                        if view == 1 :
                            processedSize_i += int(len(fileBuffer) / 2)
#                           print "a : ", processedSize_i
                            self.BFSGui.ShowBigFilesProgress(size_i, processedSize_i, input_u)

                except :
                    os.unlink(tmpOutput_s)
                    raise ScriptRt("compressing file")
                finally :
                    fileIn.close()
                    fileOut.close()
            except IOError, IOInst :
                raise ScriptRt(repr(IOInst))
        else :
            tmpOutput_s = input_u
        # then encrypt file
        if self.BFSGui.cancelState == 0 :
            ok_b =self.cryptFile(
                        algo_i,
                        scriptKey,
                        tmpOutput_s,
                        output_u,
                        2,
                        input_u,
                        size_i)

        if ScriptPosix.noCompress_e != compressType :
            os.unlink(
                    tmpOutput_s)

        if ok_b == False :
            return (False)

        return(True)

    def uncryptFile(
            self,
            scriptKey,
            input_s,
            output_s) :

        try :
            fileIn = open(input_s, "rb")
            fileOut = open(output_s, "wb") #@@@@@@@ must be "tmp\xxxxxxxx.yyy" instead of ".\tmp\xxxxxxxx.yyy"
            try :
                # init
                enc = DecryptCipher(
                        scriptKey._ct,
                        scriptKey._key_s,
                        scriptKey._iv_s)
                # crypt body
                while True :
                    fileBuffer = fileIn.read(
                            ScriptPosix._bufferSize_c)
                    # check eof
                    if not fileBuffer :
                        break
                    # process buffer
                    uncryptedBuffer = enc.update(
                            fileBuffer)
                    fileOut.write(uncryptedBuffer)
                # crypt footer
                uncryptedBuffer = enc.finish()
                fileOut.write(uncryptedBuffer)
            except CipherError, CEInst :
                raise ScriptRt(repr(CEInst))
            finally :
                fileIn.close()
                fileOut.close()
        except IOError, IEInst :
            raise ScriptRt(repr(IEInst))
        return(True)

    def uncryptCompFile(
            self,
            scriptKey,
            input_s,
            output_s,
            compressType) :
        """
        crypt and compress file
        """
        if ScriptPosix.noCompress_e != compressType :
            tmpOutput_s = os.path.join(
                    self._tmpDir_s,
                    "ScriptPosix%d" % self._pid)
        else :
            tmpOutput_s = output_s
        # first uncrypt file
        self.uncryptFile(
                scriptKey,
                input_s,
                tmpOutput_s)
        if ScriptPosix.noCompress_e != compressType :
            # then uncompress file
            self.unCompFile(
                    tmpOutput_s,
                    output_s,
                    compressType)
            os.unlink(
                    tmpOutput_s)
##        if ScriptPosix.noCompress_e != compressType :
##            try :
##                if ScriptPosix.gzip_e == compressType :
##                    fileIn = gzip.GzipFile(tmpOutput_s, "rb")
##                elif ScriptPosix.bzip2_e == compressType :
##                    fileIn = bz2.BZ2File(tmpOutput_s, "rb")
##                else :
##                    raise ScriptRt("compression type")
##                fileOut = open(output_s, "wb")
##                try :
##                    while True :
##                        fileBuffer = fileIn.read(
##                                ScriptPosix._bufferSize_c)
##                        # check eof
##                        if not fileBuffer :
##                            break
##                        fileOut.write(
##                                fileBuffer)
##                except :
##                    raise ScriptRt("uncrypting file")
##                finally :
##                    fileIn.close()
##                    fileOut.close()
##                    if ScriptPosix.noCompress_e != compressType :
##                        os.unlink(
##                                tmpOutput_s)
##            except IOError, IOInst :
##                raise ScriptRt(repr(IOInst))
        # done
        return(True)

    def unCompFile(
            self,
            input_s,
            output_s,
            compressType) :
        """
        crypt and compress file
        """

        # uncompress file
        if ScriptPosix.noCompress_e != compressType :
            try :
                if ScriptPosix.gzip_e == compressType :
                    fileIn = gzip.GzipFile(input_s, "rb")
                elif ScriptPosix.bzip2_e == compressType :
                    fileIn = bz2.BZ2File(input_s, "rb")
                else :
                    raise ScriptRt("compression type")
                fileOut = open(output_s, "wb")
                try :
                    while True :
                        fileBuffer = fileIn.read(
                                ScriptPosix._bufferSize_c)
                        # check eof
                        if not fileBuffer :
                            break
                        fileOut.write(
                                fileBuffer)
                except :
                    raise ScriptRt("uncompressing file")
                finally :
                    fileIn.close()
                    fileOut.close()

            except IOError, IOInst :
                raise ScriptRt(repr(IOInst))
        # done
        return(True)



    def stringMd5(
            self,
            data)  :
        md5Type = DigestType('MD5')
        d = Digest(md5Type)
        d.update(data)
        md5_s = ""
        for val in d.digest() :
            md5_s += "%02x" % ord(val)
        return md5_s

    def copyFile(
            self,
            from_u,
            to_u,
            mode = 0700,
            view = 1) :
        """
        copy file
        @param from_u : from file path
        @param to_u : to file path
        @param mode : dir path creation rights
        @param view : if set to 0 prevents call to BFSGui (this parameter is used by RestoreFS)
        @return ret : True if successful, False otherwise
        """
        try :
            toDir_u = os.path.dirname(
                    to_u)
            if not os.path.isdir(
                    toDir_u) :
                os.makedirs(
                        toDir_u,
                        mode)

            """Copy data from src to dst"""

            st = os.stat(from_u)
            size_i = st.st_size
            processedSize_i = 0
            deleteFile_b = False

            with open(from_u, 'rb') as fsrc:
                try :
                    fdst = open(to_u, 'wb')
                except :
                    os.chmod(to_u,S_IWRITE)     # In case destination file is write protected - Aug 24th, 2011
                    os.remove(to_u)             # In case destination file is write protected - Aug 24th, 2011
                    fdst = open(to_u, 'wb')     # In case destination file is write protected - Aug 24th, 2011

                while 1:
                    buf = fsrc.read(ScriptPosix._bufferSize_c)
                    if not buf:
                        break
                    fdst.write(buf)

                    if view == 1 :  # BFSGui does not exist when this function is called by RestoreFS.py
                        self.pauseScript(self.BFSGui)       # handle pause button

                        if self.BFSGui.cancelState == 1 :   # handle cancel button
                            deleteFile_b = True
                            break

                        #Update the gauge
                        processedSize_i += len(buf)
                        self.BFSGui.ShowBigFilesProgress(size_i, processedSize_i, from_u)

#               End of "while 1:"
                fdst.close()

#           End of "with open(from_u, 'rb') as fsrc:"
            fsrc.close()

            if deleteFile_b == True :
                os.remove(to_u)
                return (False)
            else :
                shutil.copystat(from_u, to_u)

            # done
            return(True)

        except :
            #self.printExcept()
            from_s = from_u.encode("utf-8")
            to_s = to_u.encode("utf-8")
            raise ScriptRt("Copying from : %s \nto : %s" %
                    (from_s, to_s))


    def sigcatch(
            self,
            signum,
            frame) :
        self._log.dispLog("received signal %d" % (signum))
        return(True)

    def getEnviron(
            self,
            var_s) :
        """
        read env variable value
        @param var_s : environment variable
        @return val_s : environment value
        """
        if os.environ.has_key(var_s) :
            return(os.environ[var_s])
        else :
            return("")

    def setEnviron(
            self,
            var_s,
            val_s) :
        """
        set env variable value
        @param var_s : environment variable
        @param val_s : environment value
        """
        os.environ[var_s] = val_s
        return(True)

    def extractBase(
            self) :
        """
        extract absolute path to script
        @return prog_s : absolute program path
        @return pwd_s : current working dir
        @return base_s : dirname of prog_s
        """

        # read current dir
        prog_s = sys.argv[0]
        pwd_s = os.path.abspath(".")
        name_s = os.path.basename(prog_s)

        # extract program path
        # if path starts with \ or x:\ absolute path
        if self._sep_s == prog_s[0] or \
           (2 < len(prog_s) and \
            ":" == prog_s[1] and
            self._sep_s == prog_s[2]) :
            base_s = os.path.dirname(prog_s)
        # if it starts with ./  , relative path
        elif 1 < len(prog_s) and \
             "." == prog_s[0] and \
             self._sep_s == prog_s[1] :
            path_s = os.path.abspath(prog_s)
            base_s = os.path.dirname(path_s)
        # if it is in the active directory
        elif os.path.exists(os.path.join(pwd_s, prog_s)) or \
            os.path.exists(os.path.join(pwd_s, prog_s) + ".exe"):       # Necessary if the user starts the program without the extension (maggy, without .exe)
            path_s = os.path.join(pwd_s, prog_s)
            base_s = os.path.dirname(path_s)
        else :
            tab_a = os.environ["PATH"].split(":")
            limit = len(tab_a)
            found = False
            for scan in range(limit) :
                path_s = os.path.join(tab_a[scan], prog_s)
                if os.path.exists(path_s) :
                    base_s = os.path.dirname(path_s)
                    found = True
                    break
            if not found :
                raise ScriptRt("path to program is undefined")

        # application base import
        return(name_s, pwd_s, base_s)


    """ The os.walk function is slow on the network because it calls stat 3 or 4 times for each file, and stat is slow.
        This is the reason for which we have rewritten it here in a way which calls stat only once for each file.
        Os.walk is recursive. It would have been possible to use this approach here,
        but experience showed that this approach leads to a constant change of directory and much harder work
        for the disk. It is better to treat a full directory and then change to the following one.
        This is the reason for which we have preferred the stack approach.
    """

    def oswalk3(self, root, nosub_b = False) :

            stack = []
            activedir = root
            fileCnt = 0

            while True :

                data_dir = {}
                if isinstance(activedir, unicode) == False :
                    activedir = unicode(activedir,"utf-8")
                if activedir.endswith('/') == False :
                        activedir += u"/"

                try :
                    ldir = os.listdir(activedir)
                except :
                    print "Error reading", activedir

                for filename in ldir :
                    if isinstance(filename, unicode) == False :
                        filename = unicode(filename,"utf-8")
                    root2 = activedir + filename

                    try :

                        st = os.stat(root2)
                        filesize = st.st_size
                        filedate = int(st.st_mtime)
                        pathmode = st.st_mode
                        isdir_i = stat.S_ISDIR(pathmode)

                        if isdir_i :
                            if nosub_b == False:
                                stack.append(root2)
                        else :
                            data_dir[root2] = [filesize, filedate]
                            fileCnt += 1

                    except :
                        try:
                            if isinstance(root2, unicode) :
                                root2 = root2.encode("utf-8")
                            print " Error for : ", root2
                        except:
                            print "Error "


                # send data to the caller and continue
                yield data_dir

                if len(stack) == 0 :
                    break
                activedir = stack.pop(0)
            # End of while True


    def printExcept2(
              self) :
        a,b,c = sys.exc_info()
        for d in traceback.format_exception(a,b,c) :
            print d,
#
#------------- Functions moved from C++ to Python - @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#

    def recordFilenames(self,
                        text_s,
                        path_s) :
#
        global fileLog, fileErr
#
        if text_s[0:1] != "@" :                           # It is for the log file
            if fileLog == 0 :
                fileLog = open("Archeotes_FileList.txt","w")
                fileLog.write(chr(239) + chr(187) + chr(191)) # Writes the BOM
            if (text_s != "") :
                recordLog_s = "%s: %s\n" %(text_s,path_s)
                fileLog.write(recordLog_s)
            return
#
        if text_s[0:1] == "@" :                           # It is for the error file
            if fileErr == 0 :
                fileErr = open("Archeotes_ErrorList.txt","w")
                fileErr.write(chr(239) + chr(187) + chr(191)) # Writes the BOM
            recordErr_s = "%s: %s\n" %(text_s[1:],path_s) # Skips the '@' prefix
            fileErr.write(recordErr_s)
            return

    def CloserecordFilenames(self) :
#
        global fileLog, fileErr
#
        if fileErr != 0 :
            fileErr.close()
        if fileLog != 0 :
            fileLog.close()

    def VerifyDiscSpace(self,
                szDestination,
                szRequiredSize) :

        requestedSize_i = int(szRequiredSize)
        if os.name == "nt" :
            sizes = win32file.GetDiskFreeSpace(szDestination)
            availableSize_i = sizes[0] * sizes[1] * sizes[2]
        else :
            disk = os.statvfs(szDestination)
            requestedSize_i = int(szRequiredSize)
            availableSize_i = disk.f_bsize * disk.f_bavail
        if availableSize_i > requestedSize_i :
            return "OK"
        else :
            return "KO"



###########################################################################
# EXCEPTIONS ##############################################################
###########################################################################

class ScriptRt(Exception) :
    """
    general purpose runtime errors
    """

    # ---- ctors ----

    def __init__(
            self,
            reason_s) :
        """
        ctor
        @param reason_s : exception description
        """

        if isinstance(reason_s, unicode) :
            reason_s = reason_s.encode("utf-8")
        # ---- super ----

        Exception.__init__(
                self)

        # ---- data ----

        # error description
        self._reason_s = ""

        # ---- code ----

        self._reason_s = reason_s

    def __str__(
            self) :
        """
        operator const char*()
        """
        return(self._reason_s)

class ScriptIo(ScriptRt) :
    """
    operating system error
    """

    # ---- ctors ----

    def __init__(
            self,
            reason_s,
            errno) :
        """
        ctor
        @param reason_s : exception description
        @param errno : error number
        """

        # ---- super ----

        ScriptRt.__init__(
                self,
                reason_s)

        # ---- data ----

        self._errno = errno

    def __str__(
            self) :
        """
        operator const char*()
        """
        return("Echec(errno=%d): %s\n%s" %
                (self._errno, os.strerror(self._errno), self._reason_s))

class ScriptSg(ScriptRt) :
    """
    signal error
    """

    # ---- ctors ----

    def __init__(
            self,
            signum,
            reason_s) :
        """
        ctor
        @param signum : signal number
        @param reason_s : exception description
        """

        # ---- super ----

        ScriptRt.__init__(
                self,
                reason_s)

        # ---- data ----

        # caught signal number
        self._signum = signum

        # ---- code ----

        self._signum = signum

    def __str__(
            self) :
        """
        operator const char*()
        """
        return("Echec(signal=%d): %s" % (self._signum, self._reason_s))

class ScriptDbg(Exception) :
    """
    debug purpose runtime errors (not catched)
    """

    # ---- ctors ----

    def __init__(
            self,
            reason_s) :
        """
        ctor
        @param reason_s : exception description
        """

        # ---- super ----

        Exception.__init__(
                self)

        # ---- data ----

        # error description
        self._reason_s = ""

        # ---- code ----

        self._reason_s = reason_s

    def __str__(
            self) :
        """
        operator const char*()
        """
        return(self._reason_s)


class ScriptCancel(Exception) :
    """
    general purpose runtime errors
    """

    # ---- ctors ----

    def __init__(
            self,
            reason_s) :
        """
        ctor
        @param reason_s : exception description
        """

        # ---- super ----

        Exception.__init__(
                self)

        # ---- data ----

        # error description
        self._reason_s = ""

        # ---- code ----

        self._reason_s = reason_s

    def __str__(
            self) :
        """
        operator const char*()
        """
        return(self._reason_s)