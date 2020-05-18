/*
    This file is included during the FreeRTOS kernel built. 
    It is left empty, and the fett tool fills it up with the assets data.
    A list of the assets can be found defined in `$REPO/fett/base/utils/setupEnv.json`, in `freertosAssets`.
    The file are converted to C byte arrays.
    Also, the following is defined:
        - MACRO: "asset_files": the number of assets
        - static size_t asset_sizes[asset_files]: sizes of each asset
        - static const char * const asset_names[asset_files]: file names of each asset to be stored in the FAT system
        - static const uint8_t * const asset_data[asset_files]: the data of each asset
*/

