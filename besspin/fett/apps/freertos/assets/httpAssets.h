/*
    This file is included during the FreeRTOS kernel built. 
    It is left empty, and the besspin tool fills it up with the assets data.
    A list of the assets can be found defined in `$REPO/besspin/base/utils/setupEnv.json`, in `freertosAssets`.
    The files are converted to C bytes arrays.
    Also, the following is defined:
        - MACRO: "asset_files": the number of assets
        - static size_t asset_sizes[asset_files]: sizes of each asset
        - static const char * const asset_names[asset_files]: file names of each asset to be stored in the FAT system
        - static const uint8_t * const asset_data[asset_files]: the data of each asset
*/

