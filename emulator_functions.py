#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
emulator_functions.py
Created on 19/06/2023

This file includes all functions used to build, train and apply the emulator.

It is composed of 4 main classes :

Predictors: Pre-process the predictors to feed the network,
Target: prepare the target variable,
wrapModel : to train the Unet after building it,
Pred : to make the prediction. 



@author: Antoine Doury, Elizabeth Harader-Coustau
"""

import sys
import xarray as xr
import numpy as np
import random as rn
import netCDF4 as nc
import cftime
from datetime import datetime
from math import log2,pow,cos,sin,pi

import tensorflow as tf
from tensorflow.keras import backend as K

#To be activated only if GPU available
physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

from tensorflow.keras.models import load_model, Model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, UpSampling2D, Conv2DTranspose, Reshape, concatenate, BatchNormalization, Activation, Cropping2D
from tensorflow.keras.layers import Input,  LeakyReLU, Concatenate, Dropout, Conv1D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping, ModelCheckpoint
from tensorflow.keras.models import Sequential

# set of functions used accross the different classes

def launch_gpu(num=0):
    physical_devices = tf.config.experimental.list_physical_devices('GPU')
    print(physical_devices)
    tf.config.experimental.set_visible_devices(physical_devices[num], 'GPU')
    tf.config.experimental.set_memory_growth(physical_devices[num], True)

def rmse_k(y_true, y_pred):
    return K.sqrt(K.mean(K.square(y_pred - y_true), axis=-1))

def standardize(data,name):
    mean =  np.nanmean(data,axis=(1,2), keepdims=True)
    print(f'{sys._getframe().f_code.co_name} : shape of {name} mean after normalizing {mean.shape}')
    sd   =  np.nanstd(data,axis=(1,2), keepdims=True)
    print(f'{sys._getframe().f_code.co_name} : shape of {name} sd after normalizing {sd.shape}')
    ndata = (data - mean)/sd
    return (ndata)

def standardize2(data,ref,name):
    mean =  np.nanmean(ref,axis=(0,1,2), keepdims=True)
    print(f'{sys._getframe().f_code.co_name} : shape of {name} mean after normalizing {mean.shape}')
    sd   =  np.nanstd(data,axis=(0,1,2), keepdims=True)
    print(f'{sys._getframe().f_code.co_name} : shape of {name} sd after normalizing {sd.shape}')
    ndata = (data - mean)/sd
    return (ndata)


def mon2day(data):
    nbyrs=int(data.shape[0]/12)
    months=np.tile([31,28,31,30,31,30,31,31,30,31,30,31],nbyrs)
    daily = np.concatenate([np.transpose( np.tile(data[i,:,:,:],months[i]),[2,0,1]) for i in range(len(months)) ])
    return daily


#Let's define a basic CNN with few convolutions and MaxPooling
def block_conv(conv, filters):
    conv = Conv2D(filters, 3, padding='same')(conv)
    conv = BatchNormalization()(conv)
    conv = Activation('relu')(conv)
    conv = Conv2D(filters, 3, padding='same')(conv)
    conv = BatchNormalization()(conv)
    conv = Activation('relu')(conv)
    return conv

def block_up_conc(conv, filters,conv_conc):
    conv = Conv2DTranspose(filters, (3, 3), strides=(2, 2), padding='same', activation='relu')(conv)
    conv = concatenate([conv,conv_conc])
    conv = block_conv(conv, filters)
    return conv

def block_up(conv, filters):
    conv = Conv2DTranspose(filters, (3, 3), strides=(2, 2), padding='same', activation='relu')(conv)
    conv = block_conv(conv, filters)
    return conv

def highestPowerof2(n):
    res = 0
    for i in range(n, 0, -1):

        # If i is a power of 2
        if ((i & (i - 1)) == 0):
            res = i
            break

    return res

def wmae_gb_glob_quant(alpha,pbeta,quant):  # loss function fro precipitation emulator
    def wmae_gb(y_true,y_pred):
        gamma=tf.compat.v1.distributions.Gamma(alpha,pbeta)
        gamma_coef=tf.cast(gamma.cdf(tf.cast(tf.subtract(y_true,tf.cast(quant[None,:,:],tf.float32)),tf.float64))**2,tf.float64)
        beta = tf.cast(tf.where(tf.math.is_nan(gamma_coef),tf.zeros_like(gamma_coef),gamma_coef),tf.float32)
        ext=beta*tf.maximum(tf.zeros(y_true.shape[1:]),y_true-y_pred)
        return(tf.reduce_mean(tf.losses.mae(y_true,y_pred)+ext[:,:,:,0]))
    return(wmae_gb)

class Pred: 
    def __init__(self, 
                 domain: str,  # Target domain 
                 inputIn=[None], # list of Perdictors objects
                 filepath_grid= None, # path to a .nc file containing the grid informations to put in the output file
                 filepath_out=None, # path where to save the output file
                 filepath_model=None,  # path to the emulator file
                 target_var='precip', # variable to emulate 
                 # attributes=None #list of attributes to pass to the output file
                ):
        self.targetGrid = Grid(filepath_grid) 

        # Create a prediction for the inputs passed in inputIn for the model passed in 'filepath_model'
        # inputIn must be a list of Predictors objects 
        # This is so we can concatenate inputs together from different scenarios if desired 
        # DONT use Pred with raw numpy 1D/2D inputs, the concatenate function below will flatten the 
        # zeroeth dimension and cause the code to fail. 
        # NB : input2D/1D = numpy arrays, timeout = xr DataArray

        input2D = []
        input1D = []
        timeout = []

        for an_input in inputIn:
            input2D.append(an_input.input2D)
            input1D.append(an_input.input1D)
            timeout.append(an_input.timeout)

        self.ds = self.make(input2D, input1D, timeout,
                            filepath_out=filepath_out,
                            #filepath_mask=filepath_mask,
                            filepath_model=filepath_model
                            ,target_var=target_var,
                            )

    def make(self, input2D, input1D, timeout,
             filepath_out=None,
             filepath_model=None,
             target_var='precip',
             attributes=None):

        full_input=[np.concatenate(input2D, axis=0), np.concatenate(input1D, axis=0)]
        full_time=xr.concat(timeout, dim='time')

        reference_date = cftime.DatetimeNoLeap(1950, 1, 1)
        numeric_time = np.array([(t - reference_date).days for t in full_time.values], dtype=float)

        if target_var=='pr':
            l=wmae_gb_glob_quant(0.5,0.5,1)
            unet=load_model(filepath_model, custom_objects={l.__name__: l, 'rmse_k': rmse_k})
        else:
            unet=load_model(filepath_model, custom_objects={"rmse_k": rmse_k})
	
        unet.summary()        

        pred_temp=[]
        for k in range(int(full_input[0].shape[0] / 10) + 1):            
            pred_temp.append(unet.predict([full_input[0][10*k:10*(k+1),:,:,:], ]))
        
        pred = np.concatenate(pred_temp)
        K.clear_session()
        del full_input
        
        print(f"Pred shape: {pred.shape}")
        
        # Create a new NetCDF file with desired structure and metadata
        ds = nc.Dataset(filepath_out, 'w', format='NETCDF4')
        
        # Create dimensions
        ds.createDimension('time', None)  # Unlimited
        ds.createDimension('bnds', 2)
        ds.createDimension('rlon', len(self.targetGrid.rlon))
        ds.createDimension('rlat', len(self.targetGrid.rlat))
        ds.createDimension('height', 1)

        # Create variables
        time = ds.createVariable('time', 'f8', ('time',))
        time_bnds = ds.createVariable('time_bnds', 'f8', ('time', 'bnds'))
        lon = ds.createVariable('lon', 'f8', ('rlat', 'rlon'))
        lat = ds.createVariable('lat', 'f8', ('rlat', 'rlon'))
        rlon = ds.createVariable('rlon', 'f8', ('rlon',))
        rlat = ds.createVariable('rlat', 'f8', ('rlat',))
        height = ds.createVariable('height', 'f8', ('height',))
        rotated_pole = ds.createVariable('rotated_pole', 'i4')
        precip = ds.createVariable('precip', 'f4', ('time', 'height', 'rlat', 'rlon'), chunksizes=(1, 1, 121, 118), fill_value=-9999.0)

        # Add attributes to variables
        time.standard_name = "time"
        time.long_name = "time"
        time.bounds = "time_bnds"
        time.units = "days since 1950-01-01 00:00:00.0"
        time.calendar = "365_day"
        time.axis = "T"
        time._ChunkSizes = np.uint32(512)

        time_bnds._ChunkSizes = np.array([1, 2], dtype='uint32')

        lon.standard_name = "longitude"
        lon.long_name = "longitude"
        lon.units = "degrees_east"
        lon._CoordinateAxisType = "Lon"

        lat.standard_name = "latitude"
        lat.long_name = "latitude"
        lat.units = "degrees_north"
        lat._CoordinateAxisType = "Lat"

        rlon.standard_name = "projection_x_coordinate"
        rlon.long_name = "longitude in rotated pole grid"
        rlon.units = "degrees"
        rlon.axis = "X"

        rlat.standard_name = "projection_y_coordinate"
        rlat.long_name = "latitude in rotated pole grid"
        rlat.units = "degrees"
        rlat.axis = "Y"

        height.standard_name = "height"
        height.long_name = "height above the surface"
        height.units = "m"
        height.positive = "up"
        height.axis = "Z"

        rotated_pole.proj_parameters = "-m 57.295779506 +proj=ob_tran +o_proj=latlon +o_lat_p=18.0 +lon_0=-37.5"
        rotated_pole.projection_name = "rotated_latitude_longitude"
        rotated_pole.long_name = "projection details"
        rotated_pole.proj4_params = "-m 57.295779506 +proj=ob_tran +o_proj=latlon +o_lat_p=18.0 +lon_0=-37.5"
        rotated_pole.grid_north_pole_longitude = 142.5
        rotated_pole.grid_mapping_name = "rotated_latitude_longitude"
        rotated_pole.grid_north_pole_latitude = 18.0

        precip.standard_name = "precipitation_flux"
        precip.long_name = "Total Precipitative Flux"
        precip.units = "kg m-2 s-1"
        precip.grid_mapping = "rotated_pole"
        precip.coordinates = "lat lon"
        precip.cell_methods = "time: 24-hr averaged values"
        precip._ChunkSizes = np.array([1, 1, 121, 118], dtype='uint32')

        # Add data
        rlon[:] = self.targetGrid.rlon
        rlat[:] = self.targetGrid.rlat
        lon[:] = np.random.uniform(-180, 180, (len(self.targetGrid.rlat), len(self.targetGrid.rlon)))  # Example values
        lat[:] = np.random.uniform(-90, 90, (len(self.targetGrid.rlat), len(self.targetGrid.rlon)))  # Example values
        height[:] = [2]  # Example value, can be changed as needed
        time[:] = numeric_time  # Using full_time from xr.concat
        time_bnds[:, :] = np.column_stack((np.arange(len(full_time)), np.arange(1, len(full_time) + 1)))  # Example bounds
        precip[:, 0, :, :] = pred[:, :, :, 0]  # Assign predicted values

        if attributes:
            print('attr')
            for key, value in attributes.items():
                ds.setncattr(key, value)
        
        ds.close()
        print(f"Saved file to {filepath_out}, returning dataset")
        
        return xr.open_dataset(filepath_out)      

    # Example usage
    # Assuming the required parameters are correctly defined elsewhere in your code
    # pred = Pred(domain, inputIn, filepath_grid, filepath_out, filepath_model, target_var)
    # pred.create_nc_file(filepath_out)   





class wrapModel: 
    def __init__(self, inputIn = None, #predictor list
                 targetIn=None, #corresponding target list (supervised training)
                 target_var=None, # name of target variable
                 filepath_model=None, # path where to save the model
                 filepath_sftlf=None, # 
                 filepath_grid=None,
                 filepath_gamma_param=None,
                 batch_size=16, LR=0.005):

        # Build and train the emulator 
        # inputIn and tagretIn must be lists of Predictors and Targets objects  
        # This is so we can concatenate inputs together from different scenarios if desired 
        # DONT use Model with raw numpy 1D/2D inputs, the concatenate function below will flatten the 
        # zeroeth dimension and cause the code to fail. 

        input2D = []
        input1D = []

        print(f"LR: {LR}")	

        for an_input in inputIn:
            input2D.append(an_input.input2D)
            input1D.append(an_input.input1D)
   
        self.make(targetIn, input2D, input1D, target_var=target_var,
                  filepath_model = filepath_model, 
                  filepath_sftlf=filepath_sftlf, filepath_grid=filepath_grid, 
                  filepath_gamma_param=filepath_gamma_param, 
                  batch_size=batch_size, LR=LR)  
    

    
    def unet_maker(self, nb_inputs, size_target_domain, shape_inputs, filters):
        # draw the network according to the predictors and target shapes.
        
        inputs_list=[]
        size=np.min([highestPowerof2(shape_inputs[0][0]),highestPowerof2(shape_inputs[0][1])])

        print(f'nb_inputs: {nb_inputs}')
        print(f'extra: { highestPowerof2(shape_inputs[0][0])}, {highestPowerof2(shape_inputs[0][1])} ')            
        print(f'extra2: {size}')

        if nb_inputs==1:
            inputs = Input(shape = shape_inputs[0])
            
            print(f'nbinputs1: input layer: {shape_inputs[0]}')             
            conv_down=[]
            diff_lat=inputs.shape[1]-size+1
            diff_lon=inputs.shape[2]-size+1
            conv0=Conv2D(32, (diff_lat,diff_lon))(inputs)
            conv0=BatchNormalization()(conv0)
            conv0=Activation('relu')(conv0)
            prev=conv0
            for i in range(int(log2(size))):
                conv=block_conv(prev, min(filters*int(pow(2,i)),512))
                pool=MaxPooling2D(pool_size=(2,2), strides=(2,2), padding='same')(conv)
                conv_down.append(conv)
                prev=pool
            up=block_conv(prev, min(filters*int(pow(2,i)),512))
            k=log2(size)
            for i in range(1,int(log2(size_target_domain)+1)):
                if i<=k:
                    up=block_up_conc(up,min(filters*int(pow(2,k-i)),512),conv_down[int(k-i)])
                else :
                    up=block_up(up,filters)
            inputs_list.append(inputs)

        if nb_inputs==2:
            inputs = Input(shape = shape_inputs[0])
            print(f'nbinputs2: input layer: {shape_inputs[0]}')            
            conv_down=[]
            diff_lat=inputs.shape[1]-size+1
            diff_lon=inputs.shape[2]-size+1 
            print(f'diff_lat: {diff_lat}')
            print(f'diff_lon: {diff_lon}')
            conv0=Conv2D(32, (diff_lat,diff_lon))(inputs)
            conv0=BatchNormalization()(conv0)
            conv0=Activation('relu')(conv0)
            prev=conv0
            for i in range(int(log2(size))):
                conv=block_conv(prev, min(filters*int(pow(2,i)),512))
                pool=MaxPooling2D(pool_size=(2,2), strides=(2,2), padding='same')(conv)
                conv_down.append(conv)
                prev=pool

            last_conv=block_conv(prev, min(filters*int(pow(2,i)),512))
            inputs2 = Input(shape=shape_inputs[1])
            model2 = Dense(filters)(inputs2)
            for i in range(1,int(log2(size))):
                model2 = Dense(min(filters*int(pow(2,i)),512))(model2)

            merged = concatenate([last_conv,model2])
            up=merged
            k=log2(size)
            for i in range(1,int(log2(size_target_domain)+1)):
                if i<=k:
                    up=block_up_conc(up,min(filters*int(pow(2,k-i)),512),conv_down[int(k-i)])
                else :
                    conv=block_up(up,filters)
                    up=conv
            inputs_list.append(inputs)
            inputs_list.append(inputs2)        
        last = up
        lastconv = Conv2D(1, 1, padding='same')(last)
        # Apply UpSampling2D to achieve the target height and width
        upsampled = UpSampling2D(size=(2, 2))(lastconv)  # Upsample from (64, 64) to (128, 128)

        # Use Conv2D to correct the final output shape to (121, 118)
        final_output = Conv2D(1, (3, 3), padding='same')(upsampled)

        # Cropping to the exact target dimensions
        final_output = Cropping2D(cropping=((3, 4), (5, 5)))(final_output)  # Crop to (121, 118)

        # Add an activation function if needed
        final_output = Activation('sigmoid')(final_output)

        return (Model(inputs=inputs_list, outputs=final_output))

    
    def make(self, targetIn, input2D, input1D, target_var,
             filepath_model=None, 
             filepath_sftlf=None, filepath_grid=None,
             filepath_gamma_param=None,
             batch_size=16,LR=0.005):
        
        # if os.path.isfile(filepath_model) :
        #     print ( 'Model already trained.')
        #     return None 

        full_input=[np.concatenate(input2D,axis=0),np.concatenate(input1D,axis=0)]
        full_target=np.concatenate(targetIn ,axis=0)
        
        if np.any(np.isnan(full_target)):
            idx=np.unique(np.where(np.isnan(full_target))[0])
            full_target=np.delete(full_target,idx,axis=0)
            full_input=[np.delete(full_input[0],idx,axis=0),
                        np.delete(full_input[1],idx,axis=0)]
        
        print(f'fulltarget shape: {full_target.shape}') 
        print(f'fullinput0 shape: {full_input[0].shape}')
        print(f'fullinput1 shape: {full_input[1].shape}')
        
        rn.seed(123)
               
        idx_train=rn.sample(range(full_target.shape[0]), int(0.7*full_target.shape[0]))
        full_input_train=[full_input[k][idx_train,:,:,:] for k in range(len(full_input))]
        full_input_test=[np.delete(full_input[k],idx_train,axis=0) for k in range(len(full_input))]
        full_target_train=full_target[idx_train,:,:]
        full_target_test=np.delete(full_target,idx_train,axis=0)
        
        print("----")
        print(f'fullinputtrain0 shape: {full_input_train[0].shape}')
        print(f'fullinputtrain1 shape: {full_input_train[1].shape}')
        print(f'fulltargettrain shape: {full_target_train[:,:,:].shape}')
        # print(f'fulltargettrain none shape: {full_target_train[:,:,:,None].shape}')

        print("----")
        print(f'fullinputtest0 shape: {full_input_test[0].shape}')        
        print(f'fullinputtest1 shape: {full_input_test[1].shape}')        
        print(f'fulltargettrain shape: {full_target_train[:,:,:].shape}')
        # print(f'fulltargettest none shape: {full_target_test[:,:,:,None].shape}')
        
        del full_input, full_target    
    
        dataset_tr = tf.data.Dataset.from_tensor_slices(({"input_1": full_input_train[0]},
                                                            full_target_train[:,:,:])).batch(batch_size)
        dataset_ts = tf.data.Dataset.from_tensor_slices(({"input_1": full_input_test[0]},
                                                            full_target_test[:,:,:])).batch(batch_size)
        
        del full_input_train, full_target_train, full_input_test, full_target_test
        
        # sftlf_ds = xr.open_dataset(filepath_sftlf)
        # sftlf = matchLambert(grid_ds, sftlf_ds, 4)   

        grid_ds    = xr.open_dataset(filepath_grid, engine="netcdf4")     
        unet=self.unet_maker(nb_inputs=len(dataset_tr.element_spec[0]),
                            size_target_domain=dataset_tr.element_spec[1].shape[1],
                            shape_inputs=[tuple(dataset_tr.element_spec[0][A].shape[1:]) for A in dataset_tr.element_spec[0]],
                            filters = 64)

        unet.summary()
        epochs = 110
        
        if target_var=='pr':
            gamma_param=xr.open_dataset(filepath_gamma_param).sel(x=grid_ds.x,y=grid_ds.y)
            alpha=gamma_param.alpha.values
            beta=1/gamma_param.beta.values
            lvl=tf.zeros_like(alpha)+1
            l=wmae_gb_glob_quant(alpha,beta,lvl)
        else:
            l = 'mse'
        
        print(l)
        callbacks = [ReduceLROnPlateau(monitor='val_loss', factor=0.7, patience=4, verbose=1), EarlyStopping(monitor='val_loss', patience=20, verbose=1), ModelCheckpoint(filepath_model, monitor='val_loss', verbose=1, save_best_only=True)]
        
        unet.compile(optimizer=Adam(learning_rate=LR), loss=l, metrics=[tf.metrics.RootMeanSquaredError()])
        
        tf.config.run_functions_eagerly(True)

        now = datetime.now()
        print(f"Start of training: {now}")

        unet.fit(dataset_tr,
                epochs=epochs,   
                callbacks = callbacks,
                validation_data=dataset_ts)    
        K.clear_session()       
        del dataset_tr, dataset_ts 
        
        
    


class Predictors:
    #make the predictors following a set of parameters to define 
    def __init__(self,
                 domain: str,                     # output domain name, must be defined in the class Domain
                 # domain_size,                     # size of the input domain, can be integer or tuple, must be define in the class domain.  
                 var_list=[None],                 # List of predictors (2D)
                 filepath=None,                   # path to the input file, must be a .nc file containing all 2D variables used as predictors (except aerosols) 
                 filepath_ref=None,               # path to the file used to normalize the inputs, must be similar to 'filepath'
                 stand=2,                         # way to standardize the data, see strandardize functions upper
                 ref_period=['1960','1962'],      # reference periode to use for normalisation
                 means='r',stds='r',              # If stand = 1, to include or not ('n') the means and standard deviation
                 aero_ext=False,                  # Bool, to be True if aerosols variable is not in the input file 
                 filepath_aero=None,              # path to aerosol files (only if not in the input file)
                 aero_stdz=False,                 # Bool, to normalise or not the inputs
                 aero_var='aero',                  # name of aero variable in filepath_aero
                 filepath_forc=None,              # path to the .csv file containing external forcings (GHG, solar, ozone...)
                 opt_ghg='ONE',                   # Option for the ghg, each comoponent (CO2, CH4....) seperately ('MULTI') or concatenated ('ONE') in C02 equivalent. 
                 seas=True                       # Bool, to include or not a cosine&sine vector for the season
    ):  
        with tf.device("/cpu:0"):
            self.input2D, self.input1D, self.timeout = self.make(filepath, 
                                                                filepath_ref,
                                                                stand,
                                                                var_list,
                                                                ref_period,
                                                                filepath_aero=filepath_aero,
                                                                aero_var=aero_var,
                                                                aero_stdz=aero_stdz, aero_ext=aero_ext,   
                                                                filepath_forc=filepath_forc,
                                                                opt_ghg=opt_ghg,
                                                                means=means,stds=stds,
                                                                seas=seas) 

    def make(self, filepath, filepath_ref, stand, var_list,ref_period,
             aero_ext=None,filepath_aero=None,aero_stdz=None,aero_var=None,
             filepath_forc=None,opt_ghg=None,
             means=None,stds=None,seas=None):
        
        DATASET = xr.open_dataset(filepath)
        # DATASET_wleap = self.domain.applyDom(DATASET_wleap)

        # DATASET = DATASET_wleap.sel(time=~((DATASET_wleap.time.dt.month==2) & (DATASET_wleap.time.dt.day==29)))
        # del DATASET_wleap

        #Do the same thing for the reference dataset 
        DATASET_ref = xr.open_dataset(filepath_ref)
        # DATASET_ref_wleap = self.domain.applyDom(DATASET_ref_wleap)
        
        # years=np.asarray([y for y in to_datetime(DATASET_ref['time'].values).year])
        # Numpy where gives a 2 member tuple here composed of an array of indicies followed by a second empty value
        # b=np.where(years==ref_period[0])
        # e=np.where(years==ref_period[1]) 

        # Create an array with coordinates in order (time, y, x, variable)
        if 'tos' in var_list:
            DATASET['tos']=xr.where(np.isnan(DATASET['tos']),DATASET['tos'].mean(dim=['lon','lat']),DATASET['tos'])
            DATASET_ref['tos']=xr.where(np.isnan(DATASET_ref['tos']),DATASET_ref['tos'].mean(dim=['lon','lat']),DATASET_ref['tos'])
        
        INPUT_2D=DATASET[var_list].to_array().values.transpose((1,2,3,0))
        REF_ARRAY=DATASET_ref[var_list].to_array().values.transpose((1,2,3,0))
        # del DATASET_ref_wleap        
        print(f"Shape of INPUT2D: {INPUT_2D.shape}")
        # MV: Normalization of 2D variables happens below in the "standardize" functions
        
        if stand==1:
           INPUT_2D_SDTZ = standardize(INPUT_2D, "INPUT_2D")
           print(f'shape of ndata: {INPUT_2D_SDTZ.shape}')
        elif stand==2:
           INPUT_2D_SDTZ = standardize2(INPUT_2D,REF_ARRAY, "INPUT_2D")

        if aero_ext:
            aero_dataset= xr.open_dataset(filepath_aero)
            aero_dataset=aero_dataset.sel(time=DATASET.time,method='pad')
            aero_dataset=aero_dataset.sel(lon=DATASET.lon,lat=DATASET.lat,method='nearest')[aero_var]
            if aero_stdz:
                aero_array = standardize(aero_dataset.values[:,:,:,None], "AERO")
            else:
                aero_array = aero_dataset.values[:,:,:,None] 

            INPUT_2D_ARRAY=np.concatenate([INPUT_2D_SDTZ,aero_array],axis=3)
        else: 
            INPUT_2D_ARRAY=INPUT_2D_SDTZ
        nbdays=DATASET.time.groupby('time.year').count()[0].values
        '''
        MAKE THE 1D INPUT ARRAY
        CONTAINS MEANS, STD, GHG, SEASON IF ASKED
        '''
        INPUT_1D=[]

        # INPUT_1D.append(oz.values.reshape(INPUT_2D.shape[0],1,1,1))
        # INPUT_1D.append(oz.values.reshape(INPUT_2D.shape[0],1,1,1))

        vect_means = INPUT_2D.mean(axis=(1,2))
        vect_std = INPUT_2D.std(axis=(1,2))

        # MV: This if statement seems to not execute anything
        if means == 's' or stds == 's' :
            '''
            COMPUTE MEANS
            '''
            
            # For 's', we take the centered, reduced variable. The reshape at the end serves to add back two 
            # singleton lat/lon dimensions to the 1D input 
            # For INPUT_1D and 2D, dimensions are time, lat, lon, var 
       
        if means == 's':
            ref_means=REF_ARRAY.mean(axis=(1,2))
            ref_means_mean=ref_means.mean(axis=0)
            ref_means_std=ref_means.std(axis=0)
            vect_means_stdz = (vect_means - ref_means_mean)/ref_means_std
            INPUT_1D.append(vect_means_stdz.reshape(INPUT_2D.shape[0],1,1,INPUT_2D.shape[3])) 
        elif means=='r':
            INPUT_1D.append(vect_means.reshape(INPUT_2D.shape[0],1,1,INPUT_2D.shape[3]))
        if stds == 's':
            ref_stds=REF_ARRAY.std(axis=(1,2))
            ref_stds_mean=ref_stds.mean(axis=0)
            ref_stds_std=ref_stds.std(axis=0)
            vect_std_stdz = (vect_std -ref_stds_mean)/ref_stds_std
            INPUT_1D.append(vect_std_stdz.reshape(INPUT_2D.shape[0],1,1,INPUT_2D.shape[3]))
        elif stds=='r':
            INPUT_1D.append(vect_std.reshape(INPUT_2D.shape[0],1,1,INPUT_2D.shape[3]))
        
        if seas :
            cosvect = np.tile([cos(2*i*pi/nbdays)  for i in range(nbdays)],int(INPUT_2D.shape[0]/nbdays)) 
            sinvect = np.tile([sin(2*i*pi/nbdays)  for i in range(nbdays)],int(INPUT_2D.shape[0]/nbdays)) 

            INPUT_1D.append(cosvect.reshape(INPUT_2D.shape[0],1,1,1))
            INPUT_1D.append(sinvect.reshape(INPUT_2D.shape[0],1,1,1))

        # This reduces the 5D INPUT_1D array (time, singleton lat, singleton lon, var, appended array)
        # to a 4D array by concatenating to the var dimension. Please see graphing and notes for more information. 
        INPUT_1D_ARRAY= np.concatenate(INPUT_1D,axis=3)

        timeout = DATASET.time

        DATASET.close()
        return INPUT_2D_ARRAY,INPUT_1D_ARRAY,timeout
      


class Target:
    # Prepare target 
    def __init__(self,
                 target_var,            # target var name
                 filepath=None,         # path to a file containing the output variable on a domain including the output domain
                 filepath_grid=None     # path to a file containing the output file grid
                ):
        if filepath_grid:
            grid=xr.open_dataset(filepath_grid)
            ds = xr.open_dataset(filepath)
        else:
            ds = xr.open_dataset(filepath)
            grid=ds
        self.target = ds[target_var]
        # self.lat = grid['lat']   
        # self.lon = grid['lon'] 
        self.rlat = grid['rlat']
        self.rlon = grid['rlon']
        ds.close()


class Grid:
    def __init__(self,filepath=None):
        ds = xr.open_dataset(filepath)
        # self.lat = ds['lat']   
        # self.lon = ds['lon'] 
        self.rlat = ds['rlat']
        self.rlon = ds['rlon']
        ds.close()


                                                    ###             I just commented out this class, in case it would be needed later               ####

# class Domain:
#     def __init__(self, domain: str):
#         self.domainLims(domain)
#     def __repr__(self):
#         return f"[Domain object :lon_b {self.lon_b}, lon_e {self.lon_e}, lat_b {self.lat_b}, lat_e {self.lat_e}]" 
#     def domainLims(self, domain: str):        

#         #TODO:  The actual values do not contain negative numbers so I have to
#         #       manually write the limits

#         if domain == 'ST' :
#             print("chosen: ST")
#             # self.setLims(-58,-20,59,72)
#         if domain=='NT' :
#             print("chosen: NT")
#             # self.setLims(-74,-10,72,85)
            


#     def setLims(self,lon_b,lon_e,lat_b,lat_e):

#         print("setLims \n")
#         self.lon_b = lon_b
#         self.lon_e = lon_e
#         self.lat_b = lat_b
#         self.lat_e = lat_e

#         print(self.__repr__())
#     def applyDom(self, ds):
#         return ds.sel(lon=slice(self.lon_b,self.lon_e),lat=slice(self.lat_b,self.lat_e))  
