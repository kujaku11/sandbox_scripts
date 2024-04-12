import re
import numpy as np


class ZFile:
    def __init__(self, filename):
        # attempt to open file
        try:
            f = open(filename, "r")
        except IOError:
            raise IOError("File not found.")

        # skip header lines
        f.readline()
        f.readline()
        f.readline()

        # get station ID
        line = f.readline()
        if line.lower().startswith("station"):
            station = line.strip().split(":", 1)[1]
        else:
            station = line.strip()
        self.station = station

        # read coordinates and declination
        line = f.readline().strip().lower()
        re_match = re.match(
            r"\s*coordinate\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+"
            r"declination\s+(-?\d+\.?\d*)",
            line,
        )
        self.coordinates = (float(re_match.group(1)), float(re_match.group(2)))
        self.declination = float(re_match.group(3))

        # read number of channels and number of frequencies
        line = f.readline().strip().lower()
        re_match = re.match(
            r"\s*number\s+of\s+channels\s+(\d+)\s+number\s+of"
            r"\s+frequencies\s+(\d+)",
            line,
        )
        nchannels = int(re_match.group(1))
        nfreqs = int(re_match.group(2))

        # skip line
        f.readline()

        # read channel information
        self.orientation = np.zeros((nchannels, 2))
        self.channels = []
        for i in range(nchannels):
            line = f.readline().strip()
            re_match = re.match(
                r"\s*\d+\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+\w*\s+" r"(\w+)",
                line,
            )
            self.orientation[i, 0] = float(re_match.group(1))
            self.orientation[i, 1] = float(re_match.group(2))
            if len(re_match.group(3)) > 2:
                # sometimes the channel ID comes out with extra stuff
                self.channels.append(re_match.group(3)[:2].title())
            else:
                self.channels.append(re_match.group(3).title())

        # skip blank line
        f.readline()

        # initialize empty arrays for transfer functions
        # note that EMTF, and consequently this code, assumes two predictor
        #    channels (horizontal magnetics)
        # nchannels - 2 therefore is the number of predicted channels
        self.periods = np.zeros(nfreqs)
        self.transfer_functions = np.zeros(
            (nfreqs, nchannels - 2, 2), dtype=np.complex64
        )

        # residual covariance -- square matrix with dimension as number of
        # predicted channels
        self.sigma_e = np.zeros(
            (nfreqs, nchannels - 2, nchannels - 2), dtype=np.complex64
        )

        # inverse coherent signal power -- square matrix, with dimension as the
        #    number of predictor channels
        # since EMTF and this code assume N predictors is 2,
        #    this dimension is hard-coded
        self.sigma_s = np.zeros((nfreqs, 2, 2), dtype=np.complex64)

        # now read data for each period
        for i in range(nfreqs):
            # extract period
            line = f.readline().strip()
            self.periods[i] = float(
                re.match(
                    r"\s*period\s*:\s+(\d+\.?\d*)\s+" r"decimation\s+level",
                    line,
                ).group(1)
            )

            # skip two lines
            f.readline()
            f.readline()

            # read transfer functions
            for j in range(nchannels - 2):
                comp1_r, comp1_i, comp2_r, comp2_i = (
                    f.readline().strip().split()
                )
                self.transfer_functions[i, j, 0] = float(
                    comp1_r
                ) + 1.0j * float(comp1_i)
                self.transfer_functions[i, j, 1] = float(
                    comp2_r
                ) + 1.0j * float(comp2_i)

            # skip label line
            f.readline()

            # read inverse coherent signal power matrix
            val1_r, val1_i = f.readline().strip().split()
            val2_r, val2_i, val3_r, val3_i = f.readline().strip().split()
            self.sigma_s[i, 0, 0] = float(val1_r) + 1.0j * float(val1_i)
            self.sigma_s[i, 1, 0] = float(val2_r) + 1.0j * float(val2_i)
            self.sigma_s[i, 0, 1] = float(val2_r) - 1.0j * float(val2_i)
            self.sigma_s[i, 1, 1] = float(val3_r) + 1.0j * float(val3_i)

            # skip label line
            f.readline()

            # read residual covariance
            for j in range(nchannels - 2):
                values = f.readline().strip().split()
                for k in range(j + 1):
                    if j == k:
                        self.sigma_e[i, j, k] = float(
                            values[2 * k]
                        ) + 1.0j * float(values[2 * k + 1])
                    else:
                        self.sigma_e[i, j, k] = float(
                            values[2 * k]
                        ) + 1.0j * float(values[2 * k + 1])
                        self.sigma_e[i, k, j] = float(
                            values[2 * k]
                        ) - 1.0j * float(values[2 * k + 1])

            # val1_r, val1_i = f.readline().strip().split()
            # val2_r, val2_i, val3_r, val3_i = f.readline().strip().split()
            # val4_r, val4_i, val5_r, val5_i, val6_r, val6_i = f.readline().strip().split()
            # self.sigma_e[i, 0, 0] = float(val1_r) + 1.j * float(val1_i)
            # self.sigma_e[i, 1, 0] = float(val2_r) + 1.j * float(val2_i)
            # self.sigma_e[i, 0, 1] = float(val2_r) - 1.j * float(val2_i)
            # self.sigma_e[i, 1, 1] = float(val3_r) + 1.j * float(val3_i)
            # self.sigma_e[i, 2, 0] = float(val4_r) + 1.j * float(val4_i)
            # self.sigma_e[i, 0, 2] = float(val4_r) - 1.j * float(val4_i)
            # self.sigma_e[i, 2, 1] = float(val5_r) + 1.j * float(val5_i)
            # self.sigma_e[i, 1, 2] = float(val5_r) - 1.j * float(val5_i)
            # self.sigma_e[i, 2, 2] = float(val6_r) + 1.j * float(val6_i)

        f.close()

    def impedance(self, angle=0.0):
        # check to see if there are actually electric fields in the TFs
        if "Ex" not in self.channels and "Ey" not in self.channels:
            raise ValueError(
                "Cannot return apparent resistivity and phase "
                "data because these TFs do not contain electric "
                "fields as a predicted channel."
            )

        # transform the TFs first...
        # build transformation matrix for predictor channels
        #    (horizontal magnetic fields)
        hx_index = self.channels.index("Hx")
        hy_index = self.channels.index("Hy")
        u = np.eye(2, 2)
        u[hx_index, hx_index] = np.cos(
            (self.orientation[hx_index, 0] - angle) * np.pi / 180.0
        )
        u[hx_index, hy_index] = np.sin(
            (self.orientation[hx_index, 0] - angle) * np.pi / 180.0
        )
        u[hy_index, hx_index] = np.cos(
            (self.orientation[hy_index, 0] - angle) * np.pi / 180.0
        )
        u[hy_index, hy_index] = np.sin(
            (self.orientation[hy_index, 0] - angle) * np.pi / 180.0
        )
        u = np.linalg.inv(u)

        # build transformation matrix for predicted channels (electric fields)
        ex_index = self.channels.index("Ex")
        ey_index = self.channels.index("Ey")
        v = np.eye(
            self.transfer_functions.shape[1], self.transfer_functions.shape[1]
        )
        v[ex_index - 2, ex_index - 2] = np.cos(
            (self.orientation[ex_index, 0] - angle) * np.pi / 180.0
        )
        v[ey_index - 2, ex_index - 2] = np.sin(
            (self.orientation[ex_index, 0] - angle) * np.pi / 180.0
        )
        v[ex_index - 2, ey_index - 2] = np.cos(
            (self.orientation[ey_index, 0] - angle) * np.pi / 180.0
        )
        v[ey_index - 2, ey_index - 2] = np.sin(
            (self.orientation[ey_index, 0] - angle) * np.pi / 180.0
        )

        # matrix multiplication...
        rotated_transfer_functions = np.matmul(
            v, np.matmul(self.transfer_functions, u.T)
        )
        rotated_sigma_s = np.matmul(u, np.matmul(self.sigma_s, u.T))
        rotated_sigma_e = np.matmul(v, np.matmul(self.sigma_e, v.T))

        # now pull out the impedance tensor
        z = np.zeros((self.periods.size, 2, 2), dtype=np.complex64)
        z[:, 0, 0] = rotated_transfer_functions[
            :, ex_index - 2, hx_index
        ]  # Zxx
        z[:, 0, 1] = rotated_transfer_functions[
            :, ex_index - 2, hy_index
        ]  # Zxy
        z[:, 1, 0] = rotated_transfer_functions[
            :, ey_index - 2, hx_index
        ]  # Zyx
        z[:, 1, 1] = rotated_transfer_functions[
            :, ey_index - 2, hy_index
        ]  # Zyy

        # and the variance information
        var = np.zeros((self.periods.size, 2, 2))
        var[:, 0, 0] = np.real(
            rotated_sigma_e[:, ex_index - 2, ex_index - 2]
            * rotated_sigma_s[:, hx_index, hx_index]
        )
        var[:, 0, 1] = np.real(
            rotated_sigma_e[:, ex_index - 2, ex_index - 2]
            * rotated_sigma_s[:, hy_index, hy_index]
        )
        var[:, 1, 0] = np.real(
            rotated_sigma_e[:, ey_index - 2, ey_index - 2]
            * rotated_sigma_s[:, hx_index, hx_index]
        )
        var[:, 1, 1] = np.real(
            rotated_sigma_e[:, ey_index - 2, ey_index - 2]
            * rotated_sigma_s[:, hy_index, hy_index]
        )

        error = np.sqrt(var)

        return z, error

    def tippers(self, angle=0.0):
        # check to see if there is a vertical magnetic field in the TFs
        if "Hz" not in self.channels:
            raise ValueError(
                "Cannot return tipper data because the TFs do not "
                "contain the vertical magnetic field as a "
                "predicted channel."
            )

        # transform the TFs first...
        # build transformation matrix for predictor channels
        #    (horizontal magnetic fields)
        hx_index = self.channels.index("Hx")
        hy_index = self.channels.index("Hy")
        u = np.eye(2, 2)
        u[hx_index, hx_index] = np.cos(
            (self.orientation[hx_index, 0] - angle) * np.pi / 180.0
        )
        u[hx_index, hy_index] = np.sin(
            (self.orientation[hx_index, 0] - angle) * np.pi / 180.0
        )
        u[hy_index, hx_index] = np.cos(
            (self.orientation[hy_index, 0] - angle) * np.pi / 180.0
        )
        u[hy_index, hy_index] = np.sin(
            (self.orientation[hy_index, 0] - angle) * np.pi / 180.0
        )
        u = np.linalg.inv(u)

        # don't need to transform predicated channels (assuming no tilt in Hz)
        hz_index = self.channels.index("Hz")
        v = np.eye(
            self.transfer_functions.shape[1], self.transfer_functions.shape[1]
        )

        # matrix multiplication...
        rotated_transfer_functions = np.matmul(
            v, np.matmul(self.transfer_functions, u.T)
        )
        rotated_sigma_s = np.matmul(u, np.matmul(self.sigma_s, u.T))
        rotated_sigma_e = np.matmul(v, np.matmul(self.sigma_e, v.T))

        # now pull out tipper information
        tipper = np.zeros((self.periods.size, 2), dtype=np.complex64)
        tipper[:, 0] = rotated_transfer_functions[
            :, hz_index - 2, hx_index
        ]  # Tx
        tipper[:, 1] = rotated_transfer_functions[
            :, hz_index - 2, hy_index
        ]  # Ty

        # and the variance/error information
        var = np.zeros((self.periods.size, 2))
        var[:, 0] = np.real(
            rotated_sigma_e[:, hz_index - 2, hz_index - 2]
            * rotated_sigma_s[:, hx_index, hx_index]
        )  # Tx
        var[:, 1] = np.real(
            rotated_sigma_e[:, hz_index - 2, hz_index - 2]
            * rotated_sigma_s[:, hy_index, hy_index]
        )  # Ty
        error = np.sqrt(var)

        return tipper, error


# =============================================================================
# test
# =============================================================================
z_fn = r"c:\Users\jpeacock\OneDrive - DOI\mt\spectra_edis\s01_spectra.edi"
z_obj = ZFile(z_fn)
