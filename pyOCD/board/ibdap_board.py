import sys, os
import logging, array

from time import sleep
from board import Board
from pyOCD.pyDAPAccess import DAPAccess

IBDAP_VID = 0x1fc9
IBDAP_PID = 0x0081

class IBDAPBoard(Board):
    def __init__(self, link, target, frequency=1000000):
        super(IBDAPBoard, self).__init__(target, target, link, frequency)
        self.target_type = target

    def getTargetType(self):
        """
        Return the type of the board
        """
        return self.target_type

    def getInfo(self):
        """
        Return info on the board
        """
        return "[" + self.target_type + "]"

    @staticmethod
    def listConnectedBoards(dap_class=DAPAccess):
        """
        List the connected board info
        """
        all_mbeds = IBDAPBoard.getAllConnectedBoards(dap_class, close=True,
                                                     blocking=False)
        index = 0
        if len(all_ibdaps) > 0:
            for ibdap in all_ibdaps:
                print("%d => %s" % (index, ibdap.getInfo().encode('ascii', 'ignore')))
                index += 1
        else:
            print("No available boards are connected")

    @staticmethod
    def getAllConnectedBoards(dap_class=DAPAccess, close=False, blocking=True,
                              target_override=None, frequency=1000000):
        """
        Return an array of all mbed boards connected
        """

        ibdap_list = []
        while True:
            connected_daps = dap_class.get_connected_devices(IBDAP_VID, IBDAP_PID)
            for dap_access in connected_daps:
                new_ibdap = IBDAPBoard(dap_access, target_override, frequency)
                ibdap_list.append(new_ibdap)

            #TODO - handle exception on open
            if not close:
                for dap_access in connected_daps:
                    dap_access.open(IBDAP_VID, IBDAP_PID)

            if not blocking:
                break
            elif len(ibdap_list) > 0:
                break
            else:
                sleep(0.01)
            assert len(ibdap_list) == 0

        return ibdap_list

    @staticmethod
    def useTarget(target_override, dap_class=DAPAccess, blocking=True,
                  frequency=1000000, init_board=True):
        """
        Allow you to select a board among all boards connected
        """
        all_ibdaps = IBDAPBoard.getAllConnectedBoards(dap_class, False, blocking,
                                                    target_override, frequency)

        # Return if no boards are connected
        if all_ibdaps == None or len(all_ibdaps) <= 0:
            print("No connected IBDAPs")
            return None

        # Select first board and close others if True
        for i in range(1, len(all_ibdaps)):
            all_ibdaps[i].link.close()
        all_mbeds = all_ibdaps[0:1]

        assert len(all_mbeds) == 1
        ibdap = all_ibdaps[0]
        if init_board:
            try:
                ibdap.init()
            except:
                ibdap.link.close()
                raise
        return ibdap
