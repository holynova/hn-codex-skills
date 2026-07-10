# Raster Variant Contract

Record the requested matrix before transforming the master.

| Filename | Width | Height | Format | Crop/Fit | Alpha | Quality |
|---|---:|---:|---|---|---|---|
| example.png | 512 | 512 | PNG | contain | required | lossless |

## Input Checks

- Master file opens successfully.
- Source dimensions are sufficient for the largest requested output.
- Color mode, alpha channel, and orientation metadata are known.
- Crop anchor or fit rule is explicit.
- Output directory does not overwrite the master.

## Output Checks

- Every matrix row produced exactly one file.
- Filenames, dimensions, formats, and alpha requirements match the contract.
- No output is zero-byte, corrupt, unexpectedly upscaled, or produced through repeated lossy conversion.
- Representative smallest and largest variants were inspected for clipping, blur, padding, and transparency halos.
