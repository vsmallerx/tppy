#!/usr/bin/env python
import nibabel as nib
import numpy as np
import argparse
import os
import gzip
import collections
try:
    import nrrd
except:
    print("Error importing pynrrd package, please install first\n")
    raise


def main():
    #-----------------
    # Parse arguments
    #-----------------
    parser = argparse.ArgumentParser(
        description="Convert tractography denisity image (TDI) from MRtrix format to a 3DSlicer readable file. NEED TO KNOW: Present code not support target image, also generated NRRD file space in 3DSlicer is not same with original Nifti file.",
        epilog="Written by Jianzhong He, vsmallerx@gmail.com")
    parser.add_argument("-v", "--version",
        action="version", default=argparse.SUPPRESS,
        version='1.0',
        help="Show program's version number and exit")
    parser.add_argument(
        'InputFile',
        help='A tractography denisity image (.nii or .nii.gz)')
    parser.add_argument(
        'OutputFile',
        help='Output an NRRD file.')
    parser.add_argument(
        '-target', action='store', type=str,
        help='Output file header is the same as target image header')
    args = parser.parse_args()
    
    def ConvertHeader(filename):
        """Convert Nifti Header to Nrrd Header"""
    
        image = nib.load(filename)
        header = image.header
        
        # dimension
        dimensions = len(header.get_data_shape())
        
        # sizes
        size = list(header.get_data_shape())
        sizes = size[0:3]; sizes.insert(0,size[3])
        sizes = np.array(sizes)

        # space
        if header['qform_code'] == 1:
            space = 'scanner-xyz'
        else:
            space = 'right-anterior-superior'
        
        # kinds
        kinds = ['3-color', 'domain', 'domain', 'domain']
        
        # endian
        endian = 'little'
        
        # encoding
        encoding = 'gzip'
        
        # measurement frame
        aff_diag = np.diag(image.affine); IJK2RAS_Matrix = np.zeros(aff_diag.shape)
        IJK2RAS_Matrix[aff_diag<0] = -1; IJK2RAS_Matrix[aff_diag>0]=1
        frame = np.diag(IJK2RAS_Matrix[0:3])
        
        # space units
        space_units= ['mm', 'mm', 'mm']
        
        # space directions
        nan_matrix = np.zeros([1,3]); nan_matrix[:] = np.nan
        pixdim = header['pixdim'][1:4]
        coordinates = np.diag(pixdim)
        coordinates = np.concatenate((nan_matrix, coordinates), axis=0)

        # space origin
        origin= header.get_sform()[0:3,3]
        
        # type
        dtype= str(header.get_data_dtype())
        
        # Nrrd Header
        nrrdheader = collections.OrderedDict()
        nrrdheader['dimension'] = dimensions
        nrrdheader['encoding'] = encoding 
        nrrdheader['endian'] = endian 
        nrrdheader['kinds'] = kinds 
        nrrdheader['measurement frame'] = frame
        nrrdheader['sizes'] = sizes 
        nrrdheader['space'] = space 
        nrrdheader['space directions'] = coordinates
        nrrdheader['space origin'] = origin
        nrrdheader['type'] = 'float'

        return nrrdheader

    # File path
    finput = args.InputFile
    ftarget = args.target
    foutput = args.OutputFile

    # Convert header
    print('Create a NRRD header.')
    header = ConvertHeader(finput)
    # tar_img = nib.load(ftarget)
    # header = tar_img.header
    # affine = tar_img.affine

    # Convert data shape
    print('Reshape data')
    img = nib.load(finput)
    data = img.dataobj
    data_reshape = np.transpose(data,(3,0,1,2))
    
    # Write nrrd file
    nrrd.write(foutput, data_reshape, header)
    # nib.save(nib.Nifti1Image(data_reshape, affine, header),foutput)
    print('Done!')
    
if __name__ == '__main__':
    main()