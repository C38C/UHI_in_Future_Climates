"""
Code to parse results and put in a spreadsheet compatable with analysis / dataframe tools.

"""

import os
import time

output_filename = 'results.csv'

directory = "s:\\UHI\\Simulations\\"	

epws = {'tmyx_1950_2018': os.path.normpath(directory + 'CAN_ON_Toronto-Pearson.Intl.AP.716240_TMYx_GHRadCorrected.1950-2018.epw'), 
		'tmyx_1950_2018__2020': os.path.normpath(directory + 'CAN_Toronto-Pearson.Intl.AP_HadCM3-A2-2020.1950-2018.epw'), 
		'tmyx_1950_2018__2050': os.path.normpath(directory + 'CAN_Toronto-Pearson.Intl.AP_HadCM3-A2-2050.1950-2018.epw'),
		'tmyx_1950_2018__2080': os.path.normpath(directory + 'CAN_Toronto-Pearson.Intl.AP_HadCM3-A2-2080.1950-2018.epw'),
		'tmyx_2004_2018': os.path.normpath(directory + 'CAN_ON_Toronto-Pearson.Intl.AP.716240_TMYx_GHRadCorrected_B.2005-2018.epw'), 
		'tmyx_2004_2018__2020': os.path.normpath(directory + 'CAN_Toronto.Pearson.Intl.AP_HadCM3-A2-2020.2005-2018.epw'), 
		'tmyx_2004_2018__2050': os.path.normpath(directory + 'CAN_Toronto.Pearson.Intl.AP_HadCM3-A2-2050.2005-2018.epw'),
		'tmyx_2004_2018__2080': os.path.normpath(directory + 'CAN_Toronto.Pearson.Intl.AP_HadCM3-A2-2080.2005-2018.epw'),
        'tmyx_old': os.path.normpath(directory + 'CAN_ON_Toronto-Pearson.Intl.AP.716240_TMYx_old.epw')        }

list_morphed_weather = ['tmyx_old', 'tmyx_2004_2018', 'tmyx_2004_2018__2020', 'tmyx_2004_2018__2050', 'tmyx_2004_2018__2080']

def uwg_results(base, morphed):
	def get_temp(epw):
		dbt = []
		rh = []
		
		with open(epw, 'r') as f:
			for line in f:
				if 'DATA PERIODS' in line:
					break
			for line in f:
				parts = line.split(',')
				this_dbt = float(parts[6])
				this_rh = float(parts[8])
				
				dbt.append(this_dbt)
				rh.append(this_rh)
		
		return dbt, rh
	
	base_dbt, base_rh = get_temp(base)
	morphed_dbt, morphed_rh = get_temp(morphed)
	
	max_uhi = -999.0
	gt_30 = 0
	lt_5 = 0

	
	for i in range(8760):
		uhi = morphed_dbt[i] - base_dbt[i]
		if uhi > max_uhi:
			max_uhi = uhi
		if morphed_dbt[i] > 30:
			gt_30 += 1
		if morphed_dbt[i] < 5:
			lt_5 += 1	
	
	
	index = 0
	daily_max_uhi = []
	for d in range(365):
		day_max_uhi = -999
		for h in range(24):
			uhi = morphed_dbt[index] - base_dbt[index]
			if uhi > day_max_uhi:
				day_max_uhi = uhi
			index += 1
		daily_max_uhi.append(day_max_uhi)
	mean_uhi = sum(daily_max_uhi) / 365.0
	
	
	index = 0
	max_daytime = -999.0
	max_nighttime = -999.0
	daytime_schedule = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
	for d in range(365):
		for h in daytime_schedule:
			if h: # day time
				if morphed_dbt[index] > max_daytime:
					max_daytime = morphed_dbt[index]
			else: # night time
				if morphed_dbt[index] > max_nighttime:
					max_nighttime = morphed_dbt[index]
			index += 1
	
	
	return (max_uhi, mean_uhi, gt_30, lt_5, max_daytime, max_nighttime)

with open(output_filename, 'w') as f:
	f.write('n,epw,height,scr,fsr,gcr,tcr,type,type_num,vegroof,material,albedo,name,max_uhi_base,mean_uhi_base,gt_30_base,lt_5_base,max_daytime,max_nighttime\n')
	
	n = 0
	
	for epw_class in list_morphed_weather:
		for height in [5, 35, 65, 95]: #range(5,95+1, 30):
			for scr in [0.15, 0.35, 0.55]:
				for fsr in [0.2, 1.4, 2.5, 3.7]:
					for gcr in [0.0, 0.3, 0.6]:
						tcr = gcr / 1.7
						for veg_roof_fraction in [0.0, 0.3, 0.6]:
							for material_upgrade in [1.0, 1.5, 2.0]:
								for tnum,type in enumerate(['commercial', 'residential', 'mixed']):
									for albedo in [0.2, 0.5, 0.8]: # 0.5 already calculated 
										if albedo == 0.5:
											name = '%s_height%i_scr%.1f_fsr%.1f_gcr%.1f_tcr%.1f_vegroof%.1f_mat%s_%s' % (epw_class, height, scr, fsr, gcr, tcr, veg_roof_fraction, material_upgrade, type)
										else:
											name = '%s_height%i_scr%.1f_fsr%.1f_gcr%.1f_tcr%.1f_vegroof%.1f_mat%s_alb%.1f_%s' % (epw_class, height, scr, fsr, gcr, tcr, veg_roof_fraction, material_upgrade, albedo, type)
										
										
										fullpath = directory + "%s\\%s.epw" % (name, name)
										xml_path = directory + "%s\\%s.xml" % (name, name)
										
										if fsr / scr < 14.0:
											max_uhi, mean_uhi, gt_30, lt_5, max_daytime, max_nighttime = uwg_results(epws[epw_class], fullpath)
														
											f.write('%i,%s,%i,%.2f,%.2f,%.2f,%.2f,%s,%i,%.2f,%.2f,%.2f,%s,%.6f,%.6f,%i,%i,%.6f,%.6f\n' % (n, epw_class, height, scr, fsr, gcr, tcr, type, tnum, veg_roof_fraction, material_upgrade, albedo, name, max_uhi, mean_uhi, gt_30, lt_5, max_daytime, max_nighttime) )
										

