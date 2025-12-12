
import numpy as np
import panel as pn
import holoviews as hv
from holoviews import opts
import json

hv.extension('bokeh')
pn.extension()

# Widgets
window_length = pn.widgets.IntInput(name='Window Length', value=1024, step=1)
sample_rate = pn.widgets.IntInput(name='Original Sample Rate', value=4096, step=1)
decimation_factor = pn.widgets.IntInput(name='Decimation Factor', value=4, step=1)
num_decimations = pn.widgets.IntInput(name='Number of Decimations', value=4, step=1)
bands_per_level = pn.widgets.IntInput(name='Bands per Decimation Level', value=3, step=1)
band_width = pn.widgets.IntInput(name='Band Width (Hz)', value=50, step=1)
save_button = pn.widgets.Button(name='Save Frequency Bands', button_type='primary')

# Function to compute frequency arrays
def compute_frequencies():
    freqs_by_level = []
    for level in range(num_decimations.value):
        rate = sample_rate.value / (decimation_factor.value ** level)
        freqs = np.fft.rfftfreq(window_length.value, d=1/rate)
        freqs_by_level.append(freqs)
    return freqs_by_level

# Plotting function
@pn.depends(window_length, sample_rate, decimation_factor, num_decimations, bands_per_level, band_width)
def generate_plots():
    freqs_by_level = compute_frequencies()
    plots = []
    for i, freqs in enumerate(freqs_by_level):
        curve = hv.Curve((freqs, np.ones_like(freqs)), label=f'Decimation Level {i}')
        curve.opts(opts.Curve(height=200, width=600, tools=['hover'], title=f'Decimation Level {i}', xlabel='Frequency (Hz)', ylabel='Amplitude'))
        plots.append(curve)
    return hv.Layout(plots).cols(1)

# Save function
def save_bands(event):
    freqs_by_level = compute_frequencies()
    bands = {}
    for i, freqs in enumerate(freqs_by_level):
        bands[f'Decimation_Level_{i}'] = []
        for b in range(bands_per_level.value):
            start = b * band_width.value
            end = start + band_width.value
            bands[f'Decimation_Level_{i}'].append({'min_freq': start, 'max_freq': end})
    with open('selected_frequency_bands.json', 'w') as f:
        json.dump(bands, f, indent=4)
    print("Frequency bands saved to selected_frequency_bands.json")

save_button.on_click(save_bands)

# Layout
controls = pn.Column(window_length, sample_rate, decimation_factor, num_decimations, bands_per_level, band_width, save_button)
app = pn.Row(controls, generate_plots)

# To run the app
app.servable()
