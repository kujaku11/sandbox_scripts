#!/usr/bin/env python3
"""
image2geotiff.py

Object-oriented conversion from a jet-colored image to single-band, georeferenced GeoTIFF(s).
- Two NoData masking modes: 'bw' (grayscale removal) or 'colormap' (distance in Lab to jet_r).
- NoData policy: 'nan' (masked pixels are NoData) or 'zero' (masked pixels become 0.0, valid).
- Optional interpolation across NoData: 'none', 'nearest', 'linear', 'cubic', 'idw'.
- NEW: Spatial median pre-clean before interpolation to remove stray pixels not caught by the mask.
- Writes PNG previews: mask preview + color-mapped PNG for each GeoTIFF.

CRS: EPSG:4326 (lon/lat)
Georeferencing: rasterio.transform.from_bounds(lon_min, lat_min, lon_max, lat_max)
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple
import numpy as np
import cv2
from matplotlib import cm
from matplotlib import pyplot as plt
from skimage.color import rgb2lab
from scipy.spatial import cKDTree
from scipy.interpolate import griddata
from scipy.ndimage import generic_filter
import rasterio
from rasterio.transform import from_bounds


@dataclass
class Image2Geotiff:
    # --- Required georeferencing & input ---
    image: str
    lon_min: float
    lat_min: float
    lon_max: float
    lat_max: float

    # --- Value mapping (colormap calibration) ---
    vmin: float = 35.0  # numeric value at red end (low)
    vmax: float = 155.0  # numeric value at blue end (high)
    cmap: str = "jet_r"  # use 'jet_r' since red=low, blue=high

    # --- Optional preprocessing ---
    smooth_lab: int = 3  # median filter kernel in Lab (odd; 0/1 disables)

    # --- NoData masking ---
    nodata_mode: str = "bw"  # 'bw' or 'colormap'
    dist_thresh: float = 8.0  # Lab distance threshold if nodata_mode='colormap'

    # Grayscale thresholds for 'bw' mode (masking neutral tones from black->white)
    gray_s_thresh: int = 25  # HSV saturation threshold (0-255)
    gray_chroma_thresh: float = 10.0  # Lab chroma threshold (~6..12 typical)

    # --- NoData policy in outputs ---
    nodata_policy: str = "nan"  # 'nan' -> NoData; 'zero' -> set to 0.0 as valid data
    nodata_value: float = -9999.0  # explicit NoData value when nodata_policy='nan'

    # --- Output filenames ---
    output_raw: str = "map_raw.tif"
    output_filled: str = "map_filled.tif"
    raw_png: str = "map_raw.png"  # PNG visualization of raw GeoTIFF
    filled_png: str = "map_filled.png"  # PNG visualization of filled GeoTIFF
    preview_mask: str = "mask_preview.png"  # PNG showing NoData (red) vs kept (green)

    # --- Interpolation across NoData ---
    interp: str = "none"  # 'none' | 'nearest' | 'linear' | 'cubic' | 'idw'
    idw_power: float = 2.0
    idw_k: int = 12

    # --- Spatial median pre-clean BEFORE interpolation ---
    preclean_enable: bool = True
    preclean_kernel: int = 3  # odd window size (e.g., 3, 5)
    preclean_abs_thresh: Optional[float] = (
        5.0  # absolute deviation threshold (data units)
    )
    preclean_z_thresh: Optional[float] = (
        3.0  # z-threshold using MAD (robust); None to disable
    )
    preclean_iterations: int = 1  # number of passes

    # --- Rendering options for PNGs ---
    png_cmap: Optional[str] = None  # default: use self.cmap
    png_alpha_nodata: float = 0.0  # transparency alpha for NoData pixels in PNG
    png_alpha_data: float = 1.0  # transparency alpha for data pixels in PNG

    # --- Internals (populated during run) ---
    _bgr: Optional[np.ndarray] = field(default=None, init=False, repr=False)
    _alpha: Optional[np.ndarray] = field(default=None, init=False, repr=False)
    _img_lab: Optional[np.ndarray] = field(default=None, init=False, repr=False)
    _nodata_mask: Optional[np.ndarray] = field(default=None, init=False, repr=False)
    _values_raw: Optional[np.ndarray] = field(default=None, init=False, repr=False)
    _values_filled: Optional[np.ndarray] = field(default=None, init=False, repr=False)

    # -------------------------------
    # Public API
    # -------------------------------
    def run(self) -> None:
        """Executes the full pipeline and writes GeoTIFF(s) and PNG(s)."""
        self._read_image()
        self._to_lab(smooth_kernel=self.smooth_lab)

        # Build mask
        self._build_nodata_mask()

        # Preview mask: red=NoData, green=kept
        self._write_mask_preview()

        # Map colors -> scalar values
        self._map_colors_to_values()

        # Apply NoData policy and write RAW GeoTIFF + PNG
        self._write_raw_outputs()

        # Pre-clean & interpolate (if applicable), then write FILLED GeoTIFF + PNG
        self._write_filled_outputs_if_applicable()

    # -------------------------------
    # Internal helpers
    # -------------------------------
    def _read_image(self) -> None:
        img = cv2.imread(self.image, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise FileNotFoundError(f"Cannot read image: {self.image}")

        has_alpha = img.ndim == 3 and img.shape[2] == 4
        if has_alpha:
            self._bgr = img[..., :3]
            self._alpha = img[..., 3]
        else:
            self._bgr = img
            self._alpha = None

        h, w = self._bgr.shape[:2]
        print(f"[Image2Geotiff] Loaded image: {w}x{h}, alpha={has_alpha}")

    def _to_lab(self, smooth_kernel: int = 3) -> None:
        img_rgb = cv2.cvtColor(self._bgr, cv2.COLOR_BGR2RGB) / 255.0
        img_lab = rgb2lab(img_rgb)
        if smooth_kernel and smooth_kernel >= 3 and smooth_kernel % 2 == 1:
            img_lab = (
                cv2.medianBlur((img_lab * 10).astype(np.float32), smooth_kernel) / 10.0
            )
        self._img_lab = img_lab

    def _build_colormap_tree(self, n: int = 2048) -> Tuple[cKDTree, int, np.ndarray]:
        cmap = plt.get_cmap(self.cmap, n)
        rgb = cmap(np.linspace(0, 1, n))[:, :3]
        lab = rgb2lab(rgb.reshape(1, -1, 3)).reshape(-1, 3)
        tree = cKDTree(lab)
        return tree, n, lab

    def _detect_nodata_mask_bw(self) -> np.ndarray:
        """
        Grayscale NoData mask: mark any pixels from black->white with low colorfulness as NoData.
        Combines low HSV saturation and low Lab chroma; includes alpha==0.
        """
        hsv = cv2.cvtColor(self._bgr, cv2.COLOR_BGR2HSV)
        s = hsv[..., 1].astype(np.uint8)
        gray_by_s = s < np.uint8(self.gray_s_thresh)

        lab = self._img_lab
        a = lab[..., 1]
        b = lab[..., 2]
        chroma = np.sqrt(a * a + b * b)
        gray_by_chroma = chroma < float(self.gray_chroma_thresh)

        nodata = gray_by_s | gray_by_chroma
        if self._alpha is not None:
            nodata = nodata | (self._alpha == 0)
        return nodata

    def _detect_nodata_mask_colormap(
        self, dist_thresh: float = 8.0, n: int = 2048
    ) -> np.ndarray:
        cmap = plt.get_cmap(self.cmap, n)
        rgb = cmap(np.linspace(0, 1, n))[:, :3]
        lab = rgb2lab(rgb.reshape(1, -1, 3)).reshape(-1, 3)
        tree = cKDTree(lab)

        flat_lab = self._img_lab.reshape(-1, 3)
        dists, _ = tree.query(flat_lab)
        dist_img = dists.reshape(self._img_lab.shape[:2])

        hsv = cv2.cvtColor(self._bgr, cv2.COLOR_BGR2HSV)
        white = (hsv[..., 1] < 15) & (hsv[..., 2] > 245)
        black = hsv[..., 2] < 20
        nodata = (dist_img > dist_thresh) | white | black
        if self._alpha is not None:
            nodata = nodata | (self._alpha == 0)
        return nodata

    def _build_nodata_mask(self) -> None:
        if self.nodata_mode == "bw":
            nodata = self._detect_nodata_mask_bw()
            print("[Image2Geotiff] NoData mode: bw (grayscale removal)")
        elif self.nodata_mode == "colormap":
            nodata = self._detect_nodata_mask_colormap(dist_thresh=self.dist_thresh)
            print(
                f"[Image2Geotiff] NoData mode: colormap-aware (dist_thresh={self.dist_thresh})"
            )
        else:
            raise ValueError("nodata_mode must be 'bw' or 'colormap'")

        self._nodata_mask = nodata
        frac = float(np.mean(nodata))
        print(f"[Image2Geotiff] Fraction NoData: {frac:.3f}")

    def _write_mask_preview(self) -> None:
        rgb_vis = cv2.cvtColor(self._bgr, cv2.COLOR_BGR2RGB)
        overlay = rgb_vis.copy()
        overlay[self._nodata_mask] = (255, 0, 0)  # red = NoData
        overlay[~self._nodata_mask] = (0, 255, 0)  # green = kept
        cv2.imwrite(self.preview_mask, cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
        print(f"[Image2Geotiff] Wrote mask preview: {self.preview_mask}")

    def _map_colors_to_values(self) -> None:
        tree, n, _ = self._build_colormap_tree(n=2048)
        values = np.full(self._img_lab.shape[:2], np.nan, dtype=np.float32)

        valid_pixels = ~self._nodata_mask
        flat_lab_valid = self._img_lab[valid_pixels]

        _, idxs = tree.query(flat_lab_valid)
        frac = idxs.astype(np.float32) / (n - 1)  # 0..1 along cmap
        vals = self.vmin + frac * (self.vmax - self.vmin)
        values[valid_pixels] = vals

        self._values_raw = values
        valid_fraction = float(np.mean(~np.isnan(values)))
        print(f"[Image2Geotiff] Valid fraction after mapping: {valid_fraction:.3f}")

    def _write_geotiff(
        self,
        path: str,
        values: np.ndarray,
        nodata_value: Optional[float],
        mask_valid: Optional[np.ndarray],
    ) -> None:
        h, w = values.shape
        transform = from_bounds(
            self.lon_min, self.lat_min, self.lon_max, self.lat_max, w, h
        )
        profile = {
            "driver": "GTiff",
            "height": h,
            "width": w,
            "count": 1,
            "dtype": "float32",
            "crs": "EPSG:4326",
            "transform": transform,
            "compress": "deflate",
            "tiled": True,
            "blockxsize": 256,
            "blockysize": 256,
        }
        if nodata_value is not None:
            profile["nodata"] = float(nodata_value)

        data = values.astype(np.float32).copy()
        if nodata_value is not None and np.isnan(data).any():
            data[np.isnan(data)] = nodata_value

        with rasterio.open(path, "w", **profile) as dst:
            dst.write(data, 1)
            if mask_valid is not None:
                dst.write_mask((mask_valid.astype(np.uint8) * 255))
        print(f"[Image2Geotiff] Wrote GeoTIFF: {path}")

    def _array_to_png(
        self,
        arr: np.ndarray,
        out_png: str,
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
    ) -> None:
        """Render a scalar array to PNG using a colormap; NoData becomes transparent."""
        cmap_name = self.png_cmap or self.cmap
        cmap = plt.get_cmap(cmap_name)

        # Normalize
        if vmin is None:
            vmin = np.nanmin(arr)
        if vmax is None:
            vmax = np.nanmax(arr)
        norm = (arr - vmin) / (vmax - vmin + 1e-12)

        rgba = cmap(np.clip(norm, 0, 1))
        alpha = np.where(np.isnan(arr), self.png_alpha_nodata, self.png_alpha_data)
        rgba[..., 3] = alpha

        plt.imsave(out_png, rgba)
        print(f"[Image2Geotiff] Wrote PNG: {out_png}")

    def _write_raw_outputs(self) -> None:
        if self.nodata_policy == "zero":
            # Treat masked pixels as 0.0 valid data
            values = self._values_raw.copy()
            values[self._nodata_mask] = 0.0
            mask_valid = np.ones_like(values, dtype=bool)
            nodata_value = None
            print("[Image2Geotiff] NoData policy: zero (masked -> 0.0, valid data)")
        elif self.nodata_policy == "nan":
            # Masked remain NaN -> explicit NoData
            values = self._values_raw.copy()
            mask_valid = ~np.isnan(values)
            nodata_value = self.nodata_value
            print(
                f"[Image2Geotiff] NoData policy: nan (explicit NoData={nodata_value})"
            )
        else:
            raise ValueError("nodata_policy must be 'nan' or 'zero'")

        # Write GeoTIFF + PNG
        self._write_geotiff(self.output_raw, values, nodata_value, mask_valid)
        self._array_to_png(values, self.raw_png, vmin=self.vmin, vmax=self.vmax)

    # ---------- NEW: Spatial median pre-clean ----------
    def _preclean_with_median(self, values: np.ndarray) -> np.ndarray:
        """
        Run a masked spatial median pass to flag outliers not caught by the NoData mask.
        - Computes local median and MAD ignoring NaNs.
        - Marks pixels as NaN if they deviate from local median beyond thresholds.
        - Runs for `preclean_iterations` passes.
        """
        cleaned = values.copy()
        nodata = np.isnan(cleaned)

        def local_median(x):
            return np.nanmedian(x)

        def local_mad(x):
            med = np.nanmedian(x)
            return np.nanmedian(np.abs(x - med))

        for it in range(self.preclean_iterations):
            med = generic_filter(
                cleaned, local_median, size=self.preclean_kernel, mode="nearest"
            )
            mad = generic_filter(
                cleaned, local_mad, size=self.preclean_kernel, mode="nearest"
            )
            diff = np.abs(cleaned - med)

            outlier = np.zeros_like(cleaned, dtype=bool)
            # Absolute threshold
            if self.preclean_abs_thresh is not None:
                outlier |= diff > float(self.preclean_abs_thresh)
            # Robust MAD threshold
            if self.preclean_z_thresh is not None:
                sigma = 1.4826 * mad  # MAD->sigma
                outlier |= (diff > self.preclean_z_thresh * sigma) & (sigma > 1e-9)

            # Only flag currently valid pixels
            outlier &= ~nodata

            # Update cleaned: set outliers to NaN
            cleaned[outlier] = np.nan
            nodata = np.isnan(cleaned)  # update mask for next iteration

            print(
                f"[Image2Geotiff] Pre-clean iteration {it+1}: flagged {outlier.sum()} pixels as NaN"
            )

        return cleaned

    # ---------- Interpolation & filled outputs ----------
    def _idw_fill(
        self,
        values: np.ndarray,
        nodata_mask: np.ndarray,
        power: float = 2.0,
        k: int = 12,
    ) -> np.ndarray:
        h, w = values.shape
        valid_mask = ~nodata_mask & ~np.isnan(values)
        if valid_mask.sum() == 0 or nodata_mask.sum() == 0:
            return values

        yy, xx = np.indices((h, w))
        coords_valid = np.column_stack(np.nonzero(valid_mask))
        vals_valid = values[valid_mask]
        tree = cKDTree(coords_valid)

        coords_nan = np.column_stack(np.nonzero(nodata_mask))
        dists, idxs = tree.query(coords_nan, k=min(k, len(coords_valid)))
        eps = 1e-12
        filled = values.copy()

        for i, (dist_row, idx_row) in enumerate(zip(dists, idxs)):
            if np.any(dist_row < eps):
                filled[coords_nan[i, 0], coords_nan[i, 1]] = vals_valid[
                    idx_row[dist_row.argmin()]
                ]
                continue
            wts = 1.0 / np.power(dist_row + eps, power)
            v = np.sum(wts * vals_valid[idx_row]) / np.sum(wts)
            filled[coords_nan[i, 0], coords_nan[i, 1]] = v

        return filled

    def _write_filled_outputs_if_applicable(self) -> None:
        if self.interp == "none":
            print("[Image2Geotiff] Interpolation disabled; skipping filled outputs.")
            return
        if self.nodata_policy == "zero":
            print(
                "[Image2Geotiff] nodata_policy='zero' -> no NoData to fill; skipping filled outputs."
            )
            return

        # Start from RAW values and pre-clean if enabled
        values = self._values_raw.copy()
        if self.preclean_enable:
            print(
                "[Image2Geotiff] Running spatial median pre-clean before interpolation..."
            )
            values = self._preclean_with_median(values)

        nodata_where = np.isnan(values)
        if np.mean(~nodata_where) <= 0.0:
            print(
                "[Image2Geotiff] No valid pixels to interpolate from; skipping filled outputs."
            )
            return

        print(f"[Image2Geotiff] Interpolating across NoData with method: {self.interp}")
        if self.interp == "idw":
            filled = self._idw_fill(
                values, nodata_where, power=self.idw_power, k=self.idw_k
            )
        else:
            # griddata (nearest/linear/cubic)
            yy, xx = np.indices(values.shape)
            valid_mask = ~nodata_where
            pts = np.column_stack((xx[valid_mask], yy[valid_mask]))
            vls = values[valid_mask]
            grid_pts = np.column_stack((xx[nodata_where], yy[nodata_where]))
            filled_vals = griddata(pts, vls, grid_pts, method=self.interp)
            filled = values.copy()
            filled[nodata_where] = filled_vals
            # Patch remaining NaNs with nearest
            if np.isnan(filled).any():
                print(
                    "[Image2Geotiff] Linear/cubic left NaNs; patching with nearest..."
                )
                filled_vals_nn = griddata(pts, vls, grid_pts, method="nearest")
                mask_nan_after = np.isnan(filled[nodata_where])
                filled[nodata_where] = np.where(
                    mask_nan_after, filled_vals_nn, filled[nodata_where]
                )

        self._values_filled = filled

        # Write filled GeoTIFF + PNG
        mask_valid_filled = ~np.isnan(filled)
        self._write_geotiff(
            self.output_filled, filled, self.nodata_value, mask_valid_filled
        )
        self._array_to_png(filled, self.filled_png, vmin=self.vmin, vmax=self.vmax)

        print("[Image2Geotiff] Filled outputs written.")


# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    # Adapt to your paths/parameters
    converter = Image2Geotiff(
        image=r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\manuscript\figures\laveander_lab_depth_cropped.png",
        lon_min=-125,
        lat_min=32,
        lon_max=-102.5,
        lat_max=49,
        vmin=30,
        vmax=155,
        cmap="jet_r",
        smooth_lab=3,
        # Masking
        nodata_mode="bw",  # or "colormap"
        dist_thresh=8.0,
        gray_s_thresh=5,
        gray_chroma_thresh=15.0,
        # NoData policy & outputs
        nodata_policy="nan",  # or "zero"
        nodata_value=-9999.0,
        output_raw="map_raw.tif",
        output_filled="map_filled.tif",
        raw_png="map_raw.png",
        filled_png="map_filled.png",
        preview_mask="mask_preview.png",
        # Pre-clean & interpolation
        preclean_enable=True,
        preclean_kernel=9,
        preclean_abs_thresh=4.0,  # tune to your data units (range 35..155 here)
        preclean_z_thresh=2.0,  # robust threshold via MAD
        preclean_iterations=1,
        interp="idw",  # 'none'|'nearest'|'linear'|'cubic'|'idw'
        idw_power=2.0,
        idw_k=12,
        # PNG rendering
        png_cmap=None,  # default: same as self.cmap
        png_alpha_nodata=0.0,
        png_alpha_data=1.0,
    )
    converter.run()
