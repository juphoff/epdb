#
# Copyright (c) SAS Institute, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from __future__ import unicode_literals
from unittest import TestCase
import mock

from epdb import epdb_server


class TelnetServerTest(TestCase):
    def _new_server_protocol_handler(self):
        """
        Convenience function for setting up a TelnetServerProtocolHandler
        object
        """
        socket = mock.MagicMock()
        socket.fileno.return_value = 42
        local = mock.MagicMock()
        return epdb_server.TelnetServerProtocolHandler(socket, local)

    @mock.patch("epdb.epdb_server.os.write")
    def test_process_IAC__DO(self, _write):
        IAC, WILL, TM = epdb_server.IAC, epdb_server.WILL, epdb_server.TM
        phand = self._new_server_protocol_handler()
        sock = mock.MagicMock()
        phand.process_IAC(sock, epdb_server.DO, None)
        _write.assert_not_called()
        phand.process_IAC(sock, epdb_server.DO, TM)
        _write.assert_called_once_with(phand.remote, IAC + WILL + TM)

    @mock.patch("epdb.epdb_server.os.write")
    def test_process_IAC__IP(self, _write):
        phand = self._new_server_protocol_handler()
        sock = mock.MagicMock()
        phand.process_IAC(sock, epdb_server.IP, None)
        _write.assert_called_once_with(phand.local,
                                       b'\x03')

    @mock.patch("epdb.epdb_server.fcntl.ioctl")
    def test_process_IAC__SE(self, _ioctl):
        phand = self._new_server_protocol_handler()
        sock = mock.MagicMock()

        # Not NAWS, ioctl should not be called
        phand.sbdataq = b'X'
        phand.process_IAC(sock, epdb_server.SE, None)
        _ioctl.assert_not_called()

        phand.sbdataq = b'\x1f\x50\x19'
        _ioctl.reset_mock()
        phand.process_IAC(sock, epdb_server.SE, None)
        _ioctl.assert_called_once_with(
            phand.local, epdb_server.termios.TIOCSWINSZ,
            b'\x19\x00\x50\x00\x00\x00\x00\x00')

    @mock.patch("epdb.epdb_server.os.write")
    def test_process_IAC__SB_DONT(self, _write):
        phand = self._new_server_protocol_handler()
        sock = mock.MagicMock()
        for cmd in [epdb_server.SB, epdb_server.DONT, object()]:
            phand.process_IAC(sock, cmd, None)
            _write.assert_not_called()
