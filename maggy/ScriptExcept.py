#!/usr/bin/python
# coding: utf-8 -*-

# Version 1.92 - ScriptRt message converted in utf-8 if necessary
# Version 1.95 - Version alignment

###########################################################################
# SYSTEM LIBS #############################################################
###########################################################################

import os
import sys

###########################################################################
# APPLICATION LIBS ########################################################
###########################################################################

# import path
sys.path.append(os.getenv("PYLIB"))

###########################################################################
# ENUMS ###################################################################
###########################################################################

ok_e, warning_e, error_e = range(3)

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


# eof

