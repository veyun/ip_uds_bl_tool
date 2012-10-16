import threading
import myutils

class UDS():
    """Unified Diagnostic Services"""
    def __init__(self, cantp):
        self.cantp = cantp
        self.can_tx_rdy = True
        self.active = False
        self.addressAndLengthFormatIdentifier = 0
        self.dataFormatIdentifier = 0
        cantp.event_sink = self.on_rcv_data
        self.routines = { 'ERASE_MEMORY' : 0xFF00, 'CHECK_ROUTINE' : 0x0202 }
        self.control_type = { 'START':1, 'STOP':2, 'GET_RESULTS': 3 }
        self.timedout = False
        self.rcv_timer = None

    def xmit(self, data):
        self.timedout = False
        self.cantp.xmit(data)
        #self.rcv_timer = threading.Timer(0.1, self.on_rcv_tout) # 0.1 min
        #self.rcv_timer.start()

    def on_rcv_tout(self):
        self.rcv_timer.cancel()
        self.rcv_timer = None        
        self.timedout = True

    def on_rcv_data(self):
        if self.rcv_timer <> None:
            self.rcv_timer.cancel()
            self.rcv_timer = None
        myutils.debug_print(0x1, 'UDS::on_rcv_data')
        self.event_sink()
   
    def TransferData(self, data):
        """ Transfers at the most 4095 bytes of data """
        myutils.debug_print(1, "UDS::TransferData")
        self.blockSequenceCounter = (self.blockSequenceCounter + 1) % 255
        self.cantp.Init()
        uds_data = [0x36, self.blockSequenceCounter]
        uds_data.extend(data)
        self.xmit(uds_data)
        

    def RequestDownload(self, address, data_size_bytes):
        myutils.debug_print(1, "UDS::RequestDownload")
        self.cantp.Init()
        self.blockSequenceCounter = 0
        uds_data = [0x34]
        uds_data.extend([self.dataFormatIdentifier, self.addressAndLengthFormatIdentifier])
        uds_data.extend(myutils.long_to_list(address))
        uds_data.extend(myutils.long_to_list(data_size_bytes))                        
        self.xmit(uds_data)

    def RequestTransferExit(self):
        myutils.debug_print(1, "UDS::RequestTransferExit")
        self.cantp.Init()
        self.xmit([0x37])

    def RoutineControl(self, routine_control_type, routine_id, op):
        myutils.debug_print(1, "UDS::RoutineControl")
        self.cantp.Init()
        uds_data = [0x31]
        uds_data.append(routine_control_type)
        uds_data.append((routine_id >> 8) & 0xFF)
        uds_data.append(routine_id & 0xFF)
        uds_data.extend(op)
        self.xmit(uds_data)

