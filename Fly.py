@@ -1482,8 +1482,8 @@ def CheckCLI(argv):
        #-------------------------------------------------------------------------------------------
        # Defaults for yaw angle PIDs
        #-------------------------------------------------------------------------------------------
        cli_yrp_gain = 80.0
        cli_yri_gain = 0.8
        cli_yrp_gain = 50.0
        cli_yri_gain = 5.0
        cli_yrd_gain = 0.0


@@ -1715,7 +1715,7 @@ def __init__(self, quadcopter, fp_FaDeD):
                                float(fp_row[self.PERIOD]),
                                fp_row[self.NAME].strip()))
            else:
                self.fp.append((0.0, 0.0, -0.25, 5.0, "LANDING"))
                self.fp.append((0.0, 0.0, -0.25, 5.0, "LANDING")) # Extended landed for safety
                self.fp.append((0.0, 0.0, 0.0, 0.0, "STOP"))
                return

@@ -2288,7 +2288,7 @@ def AutopilotProcessor(sweep_installed, gps_installed, compass_installed, initia
    takeoff_fp.append((0.0, 0.0, 0.5, 3.0, "TAKEOFF"))
    takeoff_fp.append((0.0, 0.0, 0.0, 0.5, "HOVER"))

    landing_fp.append((0.0, 0.0, -0.25, 6.0, "LANDING"))
    landing_fp.append((0.0, 0.0, -0.25, 7.0, "LANDING")) #  # Extended landed for safety

    #-----------------------------------------------------------------------------------------------
    # Build the initial post-takeoff GPS flight plan as a minutes hover pending GPS satellite acquisition.
@@ -3023,8 +3023,9 @@ def __init__(self):
        self.server = socket.socket()
        addr = "192.168.42.1"
        port = 31415
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((addr, port))
        self.server.listen(0)
        self.server.listen(5)

    def connect(self):
        pack_format = "=?"
@@ -3360,6 +3361,8 @@ def __init__(self):
        #    processing which is mostly handled by the GPU.
        # -  aahana is a B3 with 4 CPUs.  As a result she can run the four and a bit process required
        #    for all features to be enabled.
        # -  teotia is a B3+ with 4 CPUs.  As a result she can run the four and a bit process required
        #    for all features to be enabled.
        #-------------------------------------------------------------------------------------------
        X8 = False
        if i_am_shivangi:
@@ -4008,7 +4011,7 @@ def fly(self, cli_parms):
        if i_am_shivangi:
            eftoh = 0.04 # meters
        elif i_am_teotia:
            eftoh = 0.13 # meters
            eftoh = 0.18 # meters
        else:
            assert i_am_aahana, "Hey, I'm not supported"
            eftoh = 0.23 # meters
@@ -4039,7 +4042,7 @@ def fly(self, cli_parms):
            elif i_am_aahana:      # RPi 3B
                frame_width = 320    # an exact multiple of mb_size (16)
            elif i_am_shivangi:           # RPi 0W
                frame_width = 160    # an exact multiple of mb_size (16)
                frame_width = 240    # an exact multiple of mb_size (16)
            frame_height = frame_width
            frame_rate = fusion_rate

