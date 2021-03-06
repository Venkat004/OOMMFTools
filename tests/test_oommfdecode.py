from future import standard_library
standard_library.install_aliases()
import sys, os
import io
import tempfile

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
sys.path.insert(0, PROJECT_DIR)

import unittest
from oommftools.fnameutil import filterOnExtensions
import scipy.io as spio
import pickle as pickle
import struct
import numpy as np
import oommftools.core.oommfdecode as oommfdecode


class Test_oommfdecode_text(unittest.TestCase):
    def setUp(self):
        self.test_files_folder = 'testfiles'
        self.vector_file_text = os.path.join(TEST_DIR, 
                                        self.test_files_folder,
                                        'dw_edgefield_cut_cell4_160.ohf')
        self.headers_test = {'ystepsize': 4e-09, 'xnodes': 1250.0, 'valuemultiplier': 258967.81743932367, 'xbase': 2e-09, 'zstepsize': 8e-09, 'znodes': 1.0, 'zbase': 4e-09, 'ynodes': 40.0, 'ybase': 2e-09, 'xstepsize': 4e-09}
        self.extraCaptures_test =  {'MIFSource': 'C:/programs/oommf_old/simus/DW-150-8-transverse/DW_edgefield/dw_edgefield.mif', 'Iteration': 0.0, 'SimTime': 0.0, 'Stage': 0.0}
        self.vector_file_binary = os.path.join(TEST_DIR, 
                                        self.test_files_folder,
                                        'h2h_leftedge_40x4.ohf')

        self.targetarray_pickle = os.path.join(TEST_DIR, 
                                        self.test_files_folder,
                                        'targetarray_text.npy')
    def test_unpackFile_text_targetarray(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_text)
        #np.save(self.targetarray_pickle, targetarray)
        np.testing.assert_array_equal(targetarray, np.load(self.targetarray_pickle))
        
    def test_unpackFile_text_headers(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_text)
        self.assertEqual(headers, self.headers_test)

    def test_unpackFile_headers_keys(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_text)
        self.assertEqual(list(headers.keys()).sort(), list(self.headers_test.keys()).sort())
        
    def test_unpackFile_text_extracaptures(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_text)
        self.assertEqual(extraCaptures, self.extraCaptures_test)

class Test_oommfdecode_binary(unittest.TestCase):
    def setUp(self):
        self.test_files_folder = 'testfiles'
        self.vector_file_binary = os.path.join(TEST_DIR, 
                                        self.test_files_folder,
                                        'h2h_leftedge_40x4.ohf')
        self.headers_test = {'ystepsize': 1e-08, 'xnodes': 160.0, 'valuemultiplier': 1.0, 'xbase': 5e-09, 'zstepsize': 1e-08, 'znodes': 4.0, 'zbase': 5e-09, 'ynodes': 40.0, 'ybase': 5e-09, 'xstepsize': 1e-08}
        
        self.extraCaptures_test =  {'MIFSource': '/local/home/donahue/oommf/app/oxs/examples/h2h_edgefield.mif', 'Iteration': 0.0, 'SimTime': 0.0, 'Stage': 0.0}
                                        
        self.targetarray_pickle = os.path.join(TEST_DIR, 
                                        self.test_files_folder,
                                        'targetarray_binary.npy')                                        
    def test_unpackFile_binary_targetarray(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_binary)
        #np.save(self.targetarray_pickle, targetarray)
        np.testing.assert_array_equal(targetarray, np.load(self.targetarray_pickle))
        
    def test_unpackFile_binary_headers(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_binary)
        self.assertEqual(headers, self.headers_test)
        
    def test_unpackFile_binary_extraCaptures(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_binary)
        self.assertEqual(extraCaptures, self.extraCaptures_test)
        
        
class Test_pickleArray(unittest.TestCase):
    def setUp(self):
        self.array = np.array([1., 2., 3.])
        self.headers = {'Name': 'Headers', 'Value': 1}
        self.extraCaptures = {'Capture1': 1, 'Capture2': 'two'}
        self.filename = os.path.join(tempfile.gettempdir(),
                                        'test.npy')
        
    def test_pickle_array(self):
        oommfdecode.pickleArray(self.array, self.headers, self.extraCaptures, self.filename)
        with open(self.filename, "rb") as input_file:
            e = pickle.load(input_file)
        np.testing.assert_array_equal(e[0], np.array([1., 2., 3.]))
        self.assertEqual(e[1], dict(list(self.headers.items()) + list(self.extraCaptures.items())))
 
class Test_matlabifyArray(unittest.TestCase):
    def setUp(self):
        self.array = np.array([1., 2., 3.])
        self.headers = {'xstepsize': 1, 'ystepsize': 2, 'zstepsize': 3}
        self.extraCaptures = {'Capture1': 1, 'Capture2': 'two'}
        self.filename = os.path.join(tempfile.gettempdir(),
                                        'test.mat')
        
    def test_matlabify_array(self):
        oommfdecode.matlabifyArray(self.array, self.headers, self.extraCaptures, self.filename)
        e = spio.loadmat(self.filename)
        np.testing.assert_array_equal(e['OOMMFData'], np.array([[1., 2., 3.]]))
        self.assertEqual(e['Capture2'], np.array(['two']))
        self.assertEqual(e['Capture1'], np.array([[1]]))
        np.testing.assert_array_equal(e['GridSize'], np.array([[1., 2., 3.]]))
        
class Test_textDecode(unittest.TestCase):
    def setUp(self):
        to_write = u'-0.80  0.52  0.00\n-0.35  0.27  0.00\n-0.21  0.17  0.00'
        self.output = io.StringIO(to_write)
        self.outArray = np.zeros((3, 3, 3, 3))
        self.headers = {'xnodes': 1.0, 'znodes': 1.0, 'ynodes'                   : 3.0, 'valuemultiplier': 2}
        self.extraCaptures = {'a': 1, 'b': 2, 'c': 3}
        self.test_array = np.array([[[[-1.6 ,  1.04,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[-0.7 ,  0.54,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[-0.42,  0.34,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]]],


                                   [[[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]]],


                                   [[[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]]]])
    def test_textDecode(self):
        (targetarray, headers, extraCaptures) = oommfdecode._textDecode(self.output, self.outArray, self.headers, self.extraCaptures)
        #self.assertEqual(targetarray.all(), np.array(1))
        np.testing.assert_array_equal(targetarray, self.test_array)

class Test_binaryDecode(unittest.TestCase):
    def setUp(self):
        self.outArray = np.zeros((3, 3, 3, 3))
        self.headers = {'xnodes': 3.0,
                        'znodes': 3.0,    
                        'ynodes' : 3.0, 
                        'valuemultiplier': 2}
        self.extraCaptures = {'a': 1, 'b': 2, 'c': 3}
        self.chunksize_4 = 4
        self.chunksize_8 = 8
        self.test_array = np.array([[[[-1.6 ,  1.04,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ]],

                                [[-0.7 ,  0.54,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ]],

                                [[-0.42,  0.34,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ]]],


                               [[[ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ]],

                                [[ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ]],

                                [[ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ]]],


                               [[[ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ]],

                                [[ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ]],

                                [[ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ]]]])
        self.output_little = io.BytesIO(struct.pack('<%sf' % self.test_array.size, *self.test_array.flatten('C')))
        self.output_little_8 = io.BytesIO(struct.pack('<%sd' % self.test_array.size, *self.test_array.flatten('C')))
        self.output_big = io.BytesIO(struct.pack('>%sf' % self.test_array.size, *self.test_array.flatten('C'))) 
        self.output_big_8 = io.BytesIO(struct.pack('>%sd' % self.test_array.size, *self.test_array.flatten('C')))         
        
    def test_binaryDecode_little_4(self):
        (targetarray, headers, extraCaptures) = oommfdecode._binaryDecode(self.output_little, 
                                  self.chunksize_4, 
                                  struct.Struct("<f"), 
                                  self.outArray, 
                                  self.headers, 
                                  self.extraCaptures)
        np.testing.assert_array_almost_equal(targetarray,2.0*self.test_array)

    def test_binaryDecode_little_8(self):
        (targetarray, headers, extraCaptures) = oommfdecode._binaryDecode(self.output_little_8, 
                                  self.chunksize_8, 
                                  struct.Struct("<d"), 
                                  self.outArray, 
                                  self.headers, 
                                  self.extraCaptures)
        np.testing.assert_array_almost_equal(targetarray,2.0*self.test_array)
        
    def test_binaryDecode_big_4(self):
        (targetarray, headers, extraCaptures) = oommfdecode._binaryDecode(self.output_big, 
                                  self.chunksize_4, 
                                  struct.Struct(">f"), 
                                  self.outArray, 
                                  self.headers, 
                                  self.extraCaptures)
        np.testing.assert_allclose(targetarray,2.0*self.test_array)
        
    def test_binaryDecode_big_8(self):
        output_big_8 = io.BytesIO(struct.pack('>%sd' % self.test_array.size, *self.test_array.flatten('C')))
        (targetarray, headers, extraCaptures) = oommfdecode._binaryDecode(filehandle=output_big_8, 
                                  chunksize=self.chunksize_8, 
                                  decoder=struct.Struct(">d"), 
                                  targetarray=self.outArray, 
                                  headers=self.headers, 
                                  extraCaptures=self.extraCaptures)
        np.testing.assert_allclose(targetarray,2.0*self.test_array)        
class Test_slowlyPainfullyMaximise(unittest.TestCase):
    def setUp(self):
        self.test_files_folder = 'testfiles'
        self.vector_file_text = os.path.join(TEST_DIR, 
                                        self.test_files_folder,
                                        'dw_edgefield_cut_cell4_160.ohf')

        self.vector_file_binary = os.path.join(TEST_DIR, 
                                        self.test_files_folder,
                                        'h2h_leftedge_40x4.ohf')
                                        
    def test_slowlyPainfullyMaximize_single_file(self):
        max_mag = oommfdecode.slowlyPainfullyMaximize([self.vector_file_text])
        np.testing.assert_almost_equal(max_mag, 258967.81743932364)
        
    def test_slowlyPainfullyMaximize_multifile(self):
        max_mag = oommfdecode.slowlyPainfullyMaximize([self.vector_file_text, self.vector_file_binary])
        np.testing.assert_almost_equal(max_mag, 349370.681891435)


class Test_sortBySimTime(unittest.TestCase):

    def test_sortBySimTime_basic_operation(self):
        self.arrays = [[1,1,1], [2,2,2]]
        self.extra = {'SimTime': [1, 2], 'MIFSource': [2], 'c': [3]}
        arrays, extra = oommfdecode.sortBySimTime(self.extra, self.arrays)
        self.assertEqual(arrays, ([1,1,1], [2,2,2]))
        self.assertEqual(extra, {'SimTime': (1, 2), 'MIFSource': (2,), 'c': (3,)})

    def test_sortBySimTime_reverse_order(self):
        self.arrays = [[1,1,1], [2,2,2]]
        self.extra = {'SimTime': [2, 1], 'MIFSource': [2], 'c': [3]}
        arrays, extra = oommfdecode.sortBySimTime(self.extra, self.arrays)
        self.assertEqual(arrays, ([2,2,2], [1,1,1]))
        self.assertEqual(extra, {'SimTime': (1, 2), 'MIFSource': (2,), 'c': (3,)})

    def test_sortBySimTime_no_extra_keys(self):
        self.arrays = [[1,1,1], [2,2,2]]
        self.extra = {'SimTime': [2, 1], 'MIFSource': [2]}
        arrays, extra = oommfdecode.sortBySimTime(self.extra, self.arrays)
        self.assertEqual(arrays, ([2,2,2], [1,1,1]))
        self.assertEqual(extra, {'SimTime': (1, 2), 'MIFSource': (2,)})

    def test_sortBySimTime_len_mif_source_not_one(self):
        self.arrays = ([1,1,1], [2,2,2])
        self.extra = {'SimTime': (2, 1), 'MIFSource': (1, 2)}
        arrays, extra = oommfdecode.sortBySimTime(self.extra, self.arrays)
        self.assertEqual(arrays, ([1,1,1], [2,2,2]))
        self.assertEqual(extra, {'SimTime': (2, 1), 'MIFSource': (1, 2)})

    def test_sortBySimTime_sim_time_minus_one(self):
        self.arrays = ([1,1,1], [2,2,2])
        self.extra = {'SimTime': (2, -1), 'MIFSource': (1, 1)}
        arrays, extra = oommfdecode.sortBySimTime(self.extra, self.arrays)
        self.assertEqual(arrays, ([1,1,1], [2,2,2]))
        self.assertEqual(extra, {'SimTime': (2, -1), 'MIFSource': (1, 1)})

    def test_sortBySimTime_extra_keys(self):
        self.arrays = ([1,1,1], [2,2,2])
        self.extra = {'SimTime': (2, -1), 
                      'MIFSource': (1, 1),
                      'Extra1': (1, 2),
                      'Extra2': ('1')}
        arrays, extra = oommfdecode.sortBySimTime(self.extra, self.arrays)
        self.assertEqual(arrays, ([1,1,1], [2,2,2]))
        self.assertEqual(extra, {'SimTime': (2, -1), 'MIFSource': (1, 1), 'Extra1': (1,2), 'Extra2':'1'})


    def test_sortBySimTime_numpy_array(self):        
        self.test_array = np.array([[[[-1.6 ,  1.04,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[-0.7 ,  0.54,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[-0.42,  0.34,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]]],


                                   [[[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]]],


                                   [[[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]]]])
        self.arrays = (self.test_array)
        self.extra = {'SimTime': (2, -1), 
                      'MIFSource': (1, 1),
                      'Extra1': (1, 2),
                      'Extra2': ('1')}
        arrays, extra = oommfdecode.sortBySimTime(self.extra, self.arrays)
        np.testing.assert_array_equal(arrays, self.arrays)
        self.assertEqual(extra, {'SimTime': (2, -1), 'MIFSource': (1, 1), 'Extra1': (1,2), 'Extra2':'1'})


    def test_sortBySimTime_two_numpy_arrays(self):        
        self.test_array = np.array([[[[-1.6 ,  1.04,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[-0.7 ,  0.54,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[-0.42,  0.34,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]]],


                                   [[[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]]],


                                   [[[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]]]])
        self.arrays = (self.test_array, self.test_array)
        self.extra = {'SimTime': (2, -1), 
                      'MIFSource': (1, 1),
                      'Extra1': (1, 2),
                      'Extra2': ('1')}
        arrays, extra = oommfdecode.sortBySimTime(self.extra, self.arrays)
        self.assertEqual(arrays, self.arrays)
        self.assertEqual(extra, {'SimTime': (2, -1), 'MIFSource': (1, 1), 'Extra1': (1,2), 'Extra2':'1'})