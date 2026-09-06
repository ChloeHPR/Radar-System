import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import find_peaks
from scipy.ndimage import uniform_filter1d

def acquisition_treatment(filepath):
    fs, data = wavfile.read(filepath)
    Sigrampe, Sigradar = data[:, 0], data[:, 1]
    
    Fe = fs
    c = 3e8
    Tr = 5e-3       
    Tt = 10e-3      
    fstart = 2281.15e6
    fstop  = 2590e6
    BW = fstop - fstart
    fc = (fstart + fstop) / 2
    lambda_c = c / fc
    N = int(round(Tr * Fe))

    # Detection and cutting
    peaks, _ = find_peaks(-Sigrampe, distance=int(N * 0.8))
    start_index = peaks[0]
    
    Sigradar_cut = Sigradar[start_index:]
    Nrampes = len(Sigradar_cut) // N
    Sigradar_final = Sigradar_cut[:Nrampes * N]
    imgradar = Sigradar_final.reshape((Nrampes, N))

    # seoparation of up and down ramps
    rampe_up = imgradar[0::2]
    rampe_down = imgradar[1::2]
    Ncycles = min(len(rampe_up), len(rampe_down))
    rampe_up = rampe_up[:Ncycles]
    rampe_down = rampe_down[:Ncycles]

    # range processing
    win = np.hanning(N)
    avg_up_r = np.mean(rampe_up, axis=0, keepdims=True)
    mat_up_r = (rampe_up - avg_up_r) * win
    
    N_FFT_RANGE = 2 * N
    half_n_r = N_FFT_RANGE // 2
    fft_up_r = np.fft.fft(mat_up_r, n=N_FFT_RANGE, axis=1)
    fft_mag_up_r = np.abs(fft_up_r[:, :half_n_r])
    
    freqs_r = np.fft.fftfreq(N_FFT_RANGE, 1 / Fe)[:half_n_r]
    dist_axis_r = freqs_r * c * Tr / (2 * BW)
    time_axis_rti = np.arange(Ncycles) * Tt

    fft_mag_smooth = uniform_filter1d(fft_mag_up_r, size=5, axis=0)
    vdB = 20 * np.log10(fft_mag_smooth + 1e-9)
    vdB_norm = vdB - np.max(vdB)

    # RTI plot
    mask_d = (dist_axis_r >= 0.0) & (dist_axis_r <= 10.0)
    fig, ax = plt.subplots(figsize=(8, 6))
    pm = ax.pcolormesh(dist_axis_r[mask_d], time_axis_rti, vdB_norm[:, mask_d], shading='gouraud', cmap='jet', vmin=-20, vmax=0)
    fig.colorbar(pm, ax=ax, label="Normalized Amplitude (dB)")
    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("time (s)")
    ax.set_title("Graphe of the RTI (Range-Time Intensity)")
    plt.tight_layout()
    plt.show()
