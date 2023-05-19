"""
Code to automate urban and residential typologies using the UWG
Version 1 - 16 Dec 2019 - 	Initial meeting with VLB to define urban types.


Version 2 - *Unknown*   - 	Working version using Python Mackey script

Version 3 - *Unknown*   - 	Translated entire core to Matlab version of UWG
							Envelope upgrades implemented
							Albedo upgrades (building roof and walls) implemented

Version 4 - 17 May 2019 - 	Updated Toronto Pearson surroundings data
							Added TMYx (1950-2018) and TMYx (2004-2018) basis for A2 Scenario 2030, 2050, 2080 calcs
"""

import pp
import os
import time

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

# setup pp
num_servers = 30
job_server = pp.Server(num_servers, ppservers=())
jobs = []

def uwg_go(epw_class, height, scr, fsr, gcr, tcr, type, veg_roof_fraction, material_upgrade, albedo, name):
	start_time = time.time()
	
	
	class uwg_settings:
		# init variables
		path = ""
		folder = ""
		settings_fullpath = ""
		output_fullpath = ""

		##############
		# sim settings
		##############
		base_epw = ""
		
		#####################
		# urban type settings
		#####################
		height = 0 # m
		density = 0 # dimensionless, plan density
		vert_to_horiz = 0 # dimensionless, vert to horiz ratio
		
		h_mix = 0.5 # 50 to canyon by default
		char_length = 1000 # 1 km characteristic length 
		
		albedo_road = 0 # dimensionless
		thickness_road = 0.5 # m
		conductivity_road = 1 # W/m-K
		heat_capacity_road = 1600000 # J/m**3-K
		
		sensible_anthropogenic = 20 # (W/m^2)
		latent_anthropogenic = 2 # (W/m^2), NOT USED
		
		climate_zone = 0
		# Climate Zone (Eg. City)   Zone number
		# 1A(Miami)					1
		# 2A(Houston)				2
		# 2B(Phoenix)				3
		# 3A(Atlanta)				4
		# 3B-CA(Los Angeles)		5
		# 3B(Las Vegas)				6
		# 3C(San Francisco)			7
		# 4A(Baltimore)				8
		# 4B(Albuquerque)			9
		# 4C(Seattle)				10
		# 5A(Chicago)				11
		# 5B(Boulder)				12
		# 6A(Minneapolis)			13
		# 6B(Helena)				14
		# 7(Duluth)					15
		# 8(Fairbanks)				16
		
		vegetation_cover = 0 # dimensionless, fraction of urban ground covered in grass
		tree_cover = 0 # dimensionless, fraction of urban ground covered by tree canopy
		evapotranspiration_start = 4 # month leaves emerge
		evapotranspiration_end = 10 # month leaves drop
		vegetation_albedo = 0.25 # dimensionless
		latent_grass = 0.4 # dimensionless, latent heat absorption
		latent_tree = 0.6 # dimensionless, latent heat absorption
		rural_vegetation_cover = 0.9 # dimensionless, amount of rural coverage of vegetation 
		
		weekday_traffic = "0.2,0.2,0.2,0.2,0.2,0.4,0.7,0.9,0.9,0.6,0.6,0.6,0.6,0.6,0.7,0.8,0.9,0.9,0.8,0.8,0.7,0.3,0.2,0.2," # Weekday
		saturday_traffic = "0.2,0.2,0.2,0.2,0.2,0.3,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.6,0.7,0.7,0.7,0.7,0.5,0.4,0.3,0.2,0.2," # Saturday
		sunday_traffic = "0.2,0.2,0.2,0.2,0.2,0.3,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.3,0.3,0.2,0.2," # Sunday
		
		########################
		# building type settings
		########################
		# fraction of pre-80s, 80's-present, new buildings for each type
		# 4th element of tuple is percent envelope improvement over baseline
		office_percent = 0.0
		residential_percent = 0.0
		
		roof_albedo = 0.5 # dimensionless
		wall_albedo = 0.5 # dimensionless
		vegetated_roof = 0 # dimensionless, fraction of green roofs
		glazing_ratio = 0.4 # dimensionless, WWR
		shgc = 0.45 # dimensionless, fractional percentage of solar gains
		hvac = 0 # 0 = fully conditioned, 1 = mixed mode, 2 = unconditioned
		cooling_cop = 3.2 # not sure if possible to edit into py code.. will see
		heating_cop = 0.8 # not sure if possible to edit into py code.. will see
		
		# optional params
		# row[0] == "albRoof" or
		# row[0] == "vegRoof" or
		# row[0] == "glzR" or
		# row[0] == "hvac" or
		# row[0] == "albWall" or
		# row[0] == "SHGC"
		
		def __init__(self, path, folder):
			self.path = os.path.normpath(path)
			self.folder = folder
			self.fullpath = self.path + '\\' + self.folder
			
			if not os.path.isdir(self.fullpath):
				os.mkdir(self.fullpath)
			
			self.settings_fullpath = self.fullpath + '\\' + folder + '.xml'
			self.output_fullpath = self.fullpath + '\\' + folder + '.epw'

	def run_uwg(settings):
		epw_pieces = settings.base_epw.split("\\")
		epw_path = "\\".join(epw_pieces[:-1]) + '\\'
		epw_filename = epw_pieces[-1]
		
		settings_pieces = settings.settings_fullpath.split("\\")
		settings_path = "\\".join(settings_pieces[:-1]) + '\\'
		settings_filename = settings_pieces[-1]
		
		output_pieces = settings.output_fullpath.split("\\")
		output_path = "\\".join(output_pieces[:-1]) + '\\'
		output_filename = output_pieces[-1]
		
		if not os.path.isdir(output_path):
			os.mkdir(output_path)
		
		if not os.path.isdir(settings_path):
			os.mkdir(settings_path)
		
		f = open(settings_path + '\\run.bat', 'w')
		
		f.write('s:\n')
		f.write('cd ' + settings_path + '\\ \n')
		f.write('s:\\UHI\\UWG\\UWGEngine %s %s %s %s %s %s \n' % (epw_path, epw_filename, settings_path, settings_filename, output_path, output_filename))
		f.close()
		
		
		timeout = 12 * 60 # 12 minutes in seconds
		
		cmd = ['cmd', '/q', '/c', settings_path + '\\run.bat']
		proc = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		
		timer = threading.Timer(timeout, proc.kill)
		try:
			timer.start()
			proc.wait()
		finally:
			timer.cancel()
					
	def write_param_file(settings):
		f = open(settings.settings_fullpath, 'w')
		
		f.write('<?xml version="1.0" encoding="utf-8"?>' + '\n')
		f.write('<xml_input>' + '\n')
		
		if True: # Type 1
			# Type 1
			f.write('	<typology1 dist="%i" name="Office">' % settings.office_percent + '\n')
			f.write('		<dist>%i</dist>' % settings.office_percent + '\n')
			f.write('		<construction>' + '\n')
			f.write('		  <wall>' + '\n')
			f.write('			<albedo>%.2f</albedo>' % settings.wall_albedo + '\n')
			f.write('			<emissivity>0.9</emissivity>' + '\n')
			f.write('			<materials name="Exterior Wall">' + '\n')
			f.write('			  <names>' + '\n')
			f.write('				<item>heavyweight concrete</item>' + '\n')
			f.write('				<item>insulation</item>' + '\n')
			f.write('				<item>gypsum board</item>' + '\n')
			f.write('			  </names>' + '\n')
			f.write('			  <thermalConductivity>' + '\n') # partial R Af_out = 0.044
			f.write('			<item>1.442</item>' + '\n') # partial R concrete = 0.10402219140083217753120665742025
			f.write('				<item>0.025</item>' + '\n')
			f.write('				<item>0.16</item>' + '\n') # partial R gyp = 0.079375
			f.write('			  </thermalConductivity>' + '\n') # partial R Af_in = 0.12
									# total partial R = 0.30779719140083217753120665742025
									# remaining R = 3.7407858045505848265173763385312
			f.write('			  <volumetricHeatCapacity>' + '\n')
			f.write('				<item>2400000.0</item>' + '\n') # specific heat * density
			f.write('				<item>29400.0</item>' + '\n') # specific heat * density
			f.write('				<item>736000.0</item>' + '\n') # specific heat * density
			f.write('			  </volumetricHeatCapacity>' + '\n')
			f.write('			  <thickness>[0.1500, %.5f, 0.0127]</thickness>' % (0.09351964511376462066293440846328 * settings.material_upgrade) + '\n') # at material_upgrade = 1, R = 4.0485829959514170040485829959514
			f.write('			</materials>' + '\n')
			f.write('			<vegetationCoverage>0</vegetationCoverage>' + '\n')
			f.write('			<inclination>0.0</inclination>' + '\n')
			f.write('			<initialTemperature>15.6</initialTemperature>' + '\n')
			f.write('		  </wall>' + '\n')
			f.write('		  <roof>' + '\n')
			f.write('			<albedo>%.2f</albedo>' % settings.roof_albedo + '\n')
			f.write('			<emissivity>0.9</emissivity>' + '\n')
			f.write('			<materials name="Exterior Roof">' + '\n')
			f.write('			  <names>' + '\n')
			f.write('				<item>heavyweight concrete</item>' + '\n')
			f.write('				<item>insulation</item>' + '\n')
			f.write('				<item>acoustic tile</item>' + '\n')
			f.write('			  </names>' + '\n')
			f.write('			  <thermalConductivity>' + '\n') # partial R Af_out = 0.044
			f.write('				<item>1.442</item>' + '\n') # partial R concrete = 0.2080443828016643550624133148405
			f.write('				<item>0.025</item>' + '\n')
			f.write('				<item>0.06</item>' + '\n') # partial R ceiling_tile = 0.333
			f.write('			  </thermalConductivity>' + '\n') # partial R Af_in = 0.12
									# total partial R = 0.7050443828016643550624133148405
									# remaining R = 4.7594364915152755356479691988207
			f.write('			  <volumetricHeatCapacity>' + '\n')
			f.write('				<item>2400000.0</item>' + '\n') # specific heat * density
			f.write('				<item>29400.0</item>' + '\n') # specific heat * density
			f.write('				<item>217120.000000</item>' + '\n') # specific heat * density
			f.write('			  </volumetricHeatCapacity>' + '\n')
			f.write('			  <thickness>[0.3, %.5f, 0.02]</thickness>' % (0.11898591228788188839119922997052 * settings.material_upgrade) + '\n') # at material_upgrade = 1, R = 5.4644808743169398907103825136612
			f.write('			</materials>' + '\n')
			f.write('			<vegetationCoverage>%.2f</vegetationCoverage>' % settings.vegetated_roof + '\n')
			f.write('			<inclination>1.0</inclination>' + '\n')
			f.write('			<initialTemperature>15.6</initialTemperature>' + '\n')
			f.write('		  </roof>' + '\n')
			f.write('		  <mass>' + '\n')
			f.write('			<albedo>0.7</albedo>' + '\n')
			f.write('			<emissivity>0.9</emissivity>' + '\n')
			f.write('			<materials name="Interior Floor">' + '\n')
			f.write('			  <names>' + '\n')
			f.write('				<item>M11 100mm lightweight concrete</item>' + '\n')
			f.write('			  </names>' + '\n')
			f.write('			  <thermalConductivity>' + '\n')
			f.write('				<item>0.53</item>' + '\n')
			f.write('			  </thermalConductivity>' + '\n')
			f.write('			  <volumetricHeatCapacity>' + '\n')
			f.write('				<item>1075200.0</item>' + '\n')
			f.write('			  </volumetricHeatCapacity>' + '\n')
			f.write('			  <thickness>[0.1016]</thickness>' + '\n')
			f.write('			</materials>' + '\n')
			f.write('			<vegetationCoverage>0</vegetationCoverage>' + '\n')
			f.write('			<inclination>1</inclination>' + '\n')
			f.write('			<initialTemperature>15.6</initialTemperature>' + '\n')
			f.write('		  </mass>' + '\n')
			f.write('		  <glazing name="Exterior Window">' + '\n')
			f.write('			<glazingRatio>%.2f</glazingRatio>' % settings.glazing_ratio + '\n')
			f.write('			<windowUvalue>%.2f</windowUvalue>' % ( 2.2 / settings.material_upgrade )+ '\n')
			f.write('			<windowSHGC>%.2f</windowSHGC>' % settings.shgc + '\n')
			f.write('		  </glazing>' + '\n')
			f.write('		</construction>' + '\n')
			f.write('		<building name="Office_Building">' + '\n')
			f.write('		  <floorHeight>2.74</floorHeight>' + '\n')
			f.write('		  <dayInternalGains>28.78</dayInternalGains>' + '\n')
			f.write('		  <nightInternalGains>5.2</nightInternalGains>' + '\n')
			f.write('		  <radiantFraction>0.30</radiantFraction>' + '\n')
			f.write('		  <latentFraction>0.15</latentFraction>' + '\n')
			f.write('		  <infiltration>0.068712467</infiltration>' + '\n')
			f.write('		  <ventilation>0.517546733469037</ventilation>' + '\n')
			f.write('		  <coolingSystemType>air</coolingSystemType>' + '\n')
			f.write('		  <coolingCOP>%.2f</coolingCOP>' % settings.cooling_cop + '\n')
			f.write('		  <daytimeCoolingSetPoint>24.0</daytimeCoolingSetPoint>' + '\n')
			f.write('		  <nighttimeCoolingSetPoint>26.7</nighttimeCoolingSetPoint>' + '\n')
			f.write('		  <daytimeHeatingSetPoint>21.0</daytimeHeatingSetPoint>' + '\n')
			f.write('		  <nighttimeHeatingSetPoint>15.6</nighttimeHeatingSetPoint>' + '\n')
			f.write('		  <coolingCapacity>300</coolingCapacity>' + '\n')
			f.write('		  <heatingEfficiency>%.2f</heatingEfficiency>' % settings.heating_cop + '\n')
			f.write('		  <nightSetStart>22</nightSetStart>' + '\n')
			f.write('		  <nightSetEnd>6</nightSetEnd>' + '\n')
			f.write('		  <heatReleasedToCanyon>0.5</heatReleasedToCanyon>' + '\n')
			f.write('		  <initialT>15.6</initialT>' + '\n')
			f.write('		</building>' + '\n')
			f.write('	</typology1>' + '\n')
		
		if True: # Type 2
			# Type 2
			f.write('	<typology2 dist="%i" name="House">' % settings.residential_percent + '\n')
			f.write('		<dist>%i</dist>' % settings.residential_percent + '\n')
			f.write('		<construction>' + '\n')
			f.write('		  <wall>' + '\n')
			f.write('			<albedo>%.2f</albedo>' % settings.wall_albedo + '\n')
			f.write('			<emissivity>0.9</emissivity>' + '\n')
			f.write('			<materials name="Exterior Wall">' + '\n')
			f.write('			  <names>' + '\n')
			f.write('				<item>heavyweight concrete</item>' + '\n')
			f.write('				<item>insulation</item>' + '\n')
			f.write('				<item>gypsum board</item>' + '\n')
			f.write('			  </names>' + '\n')
			f.write('			  <thermalConductivity>' + '\n') # partial R Af_out = 0.044
			f.write('				<item>1.442</item>' + '\n') # partial R concrete = 0.10402219140083217753120665742025
			f.write('				<item>0.025</item>' + '\n')
			f.write('				<item>0.16</item>' + '\n') # partial R gyp = 0.079375
			f.write('			  </thermalConductivity>' + '\n') # partial R Af_in = 0.12
									# total partial R = 0.30779719140083217753120665742025
									# remaining R = 3.2893251107574412037637573713567
			f.write('			  <volumetricHeatCapacity>' + '\n')
			f.write('				<item>2400000.0</item>' + '\n') # specific heat * density
			f.write('				<item>29400.0</item>' + '\n') # specific heat * density
			f.write('				<item>736000.0</item>' + '\n') # specific heat * density
			f.write('			  </volumetricHeatCapacity>' + '\n')
			f.write('			  <thickness>[0.1500, %.5f, 0.0127]</thickness>' % (0.08223312776893603009409393428392 * settings.material_upgrade) + '\n') # at material_upgrade = 1, R = 3.597122302158273381294964028777
			f.write('			</materials>' + '\n')
			f.write('			<vegetationCoverage>0</vegetationCoverage>' + '\n')
			f.write('			<inclination>0.0</inclination>' + '\n')
			f.write('			<initialTemperature>15.6</initialTemperature>' + '\n')
			f.write('		  </wall>' + '\n')
			f.write('		  <roof>' + '\n')
			f.write('			<albedo>%.2f</albedo>' % settings.roof_albedo + '\n')
			f.write('			<emissivity>0.9</emissivity>' + '\n')
			f.write('			<materials name="Exterior Roof">' + '\n')
			f.write('			  <names>' + '\n')
			f.write('				<item>heavyweight concrete</item>' + '\n')
			f.write('				<item>insulation</item>' + '\n')
			f.write('				<item>acoustic tile</item>' + '\n')
			f.write('			  </names>' + '\n')
			f.write('			  <thermalConductivity>' + '\n') # partial R Af_out = 0.044
			f.write('				<item>1.442</item>' + '\n') # partial R concrete = 0.2080443828016643550624133148405
			f.write('				<item>0.025</item>' + '\n')
			f.write('				<item>0.06</item>' + '\n') # partial R ceiling_tile = 0.333
			f.write('			  </thermalConductivity>' + '\n') # partial R Af_in = 0.12
									# total partial R = 0.7050443828016643550624133148405
									# remaining R = 4.7594364915152755356479691988207
			f.write('			  <volumetricHeatCapacity>' + '\n')
			f.write('				<item>2400000.0</item>' + '\n') # specific heat * density
			f.write('				<item>29400.0</item>' + '\n') # specific heat * density
			f.write('				<item>217120.000000</item>' + '\n') # specific heat * density
			f.write('			  </volumetricHeatCapacity>' + '\n')
			f.write('			  <thickness>[0.3, %.5f, 0.02]</thickness>' % (0.11898591228788188839119922997052 * settings.material_upgrade) + '\n') # at material_upgrade = 1, R = 5.4644808743169398907103825136612
			f.write('			</materials>' + '\n')
			f.write('			<vegetationCoverage>%.2f</vegetationCoverage>' % settings.vegetated_roof + '\n')
			f.write('			<inclination>1.0</inclination>' + '\n')
			f.write('			<initialTemperature>15.6</initialTemperature>' + '\n')
			f.write('		  </roof>' + '\n')
			f.write('		  <mass>' + '\n')
			f.write('			<albedo>0.7</albedo>' + '\n')
			f.write('			<emissivity>0.9</emissivity>' + '\n')
			f.write('			<materials name="Interior Floor">' + '\n')
			f.write('			  <names>' + '\n')
			f.write('				<item>M11 100mm lightweight concrete</item>' + '\n')
			f.write('			  </names>' + '\n')
			f.write('			  <thermalConductivity>' + '\n')
			f.write('				<item>0.53</item>' + '\n')
			f.write('			  </thermalConductivity>' + '\n')
			f.write('			  <volumetricHeatCapacity>' + '\n')
			f.write('				<item>1075200.0</item>' + '\n')
			f.write('			  </volumetricHeatCapacity>' + '\n')
			f.write('			  <thickness>[0.1016]</thickness>' + '\n')
			f.write('			</materials>' + '\n')
			f.write('			<vegetationCoverage>0</vegetationCoverage>' + '\n')
			f.write('			<inclination>1</inclination>' + '\n')
			f.write('			<initialTemperature>15.6</initialTemperature>' + '\n')
			f.write('		  </mass>' + '\n')
			f.write('		  <glazing name="Exterior Window">' + '\n')
			f.write('			<glazingRatio>%.2f</glazingRatio>' % settings.glazing_ratio + '\n')
			f.write('			<windowUvalue>%.2f</windowUvalue>' % (2.2 / settings.material_upgrade) + '\n')
			f.write('			<windowSHGC>%.2f</windowSHGC>' % settings.shgc + '\n')
			f.write('		  </glazing>' + '\n')
			f.write('		</construction>' + '\n')
			f.write('		<building name="House_Building">' + '\n')
			f.write('		  <floorHeight>3.05</floorHeight>' + '\n')
			f.write('		  <dayInternalGains>6.41</dayInternalGains>' + '\n')
			f.write('		  <nightInternalGains>12.82</nightInternalGains>' + '\n')
			f.write('		  <radiantFraction>0.30</radiantFraction>' + '\n')
			f.write('		  <latentFraction>0.20</latentFraction>' + '\n')
			f.write('		  <infiltration>0.171013375184129</infiltration>' + '\n')
			f.write('		  <ventilation>0.451214301018868</ventilation>' + '\n')
			f.write('		  <coolingSystemType>air</coolingSystemType>' + '\n')
			f.write('		  <coolingCOP>%.2f</coolingCOP>' % settings.cooling_cop+ '\n')
			f.write('		  <daytimeCoolingSetPoint>23.9</daytimeCoolingSetPoint>' + '\n')
			f.write('		  <nighttimeCoolingSetPoint>23.9</nighttimeCoolingSetPoint>' + '\n')
			f.write('		  <daytimeHeatingSetPoint>21.1</daytimeHeatingSetPoint>' + '\n')
			f.write('		  <nighttimeHeatingSetPoint>21.1</nighttimeHeatingSetPoint>' + '\n')
			f.write('		  <coolingCapacity>300</coolingCapacity>' + '\n')
			f.write('		  <heatingEfficiency>%.2f</heatingEfficiency>' % settings.heating_cop + '\n')
			f.write('		  <nightSetStart>22</nightSetStart>' + '\n')
			f.write('		  <nightSetEnd>6</nightSetEnd>' + '\n')
			f.write('		  <heatReleasedToCanyon>0.5</heatReleasedToCanyon>' + '\n')
			f.write('		  <initialT>15.6</initialT>' + '\n')
			f.write('		</building>' + '\n')
			f.write('	</typology2>' + '\n')
			
		if True: # Blank Types 3 + 4
			# blank typologies 3 and 4
			f.write('	<typology3 dist="0" name="blankTypology3">' + '\n')
			f.write('		<dist>0</dist>' + '\n')
			f.write('		<construction>' + '\n')
			f.write('		  <wall>' + '\n')
			f.write('			<albedo>0.5</albedo>' + '\n')
			f.write('			<emissivity>0.9</emissivity>' + '\n')
			f.write('			<materials>' + '\n')
			f.write('			  <names>' + '\n')
			f.write('				<item>Wood Siding</item>' + '\n')
			f.write('			  </names>' + '\n')
			f.write('			  <thermalConductivity>' + '\n')
			f.write('				<item>0.11</item>' + '\n')
			f.write('			  </thermalConductivity>' + '\n')
			f.write('			  <volumetricHeatCapacity>' + '\n')
			f.write('				<item>658990</item>' + '\n')
			f.write('			  </volumetricHeatCapacity>' + '\n')
			f.write('			  <thickness>[0.2]</thickness>' + '\n')
			f.write('			</materials>' + '\n')
			f.write('			<vegetationCoverage>0</vegetationCoverage>' + '\n')
			f.write('			<inclination>0</inclination>' + '\n')
			f.write('			<initialTemperature>20</initialTemperature>' + '\n')
			f.write('		  </wall>' + '\n')
			f.write('		  <roof>' + '\n')
			f.write('			<albedo>0.25</albedo>' + '\n')
			f.write('			<emissivity>0.9</emissivity>' + '\n')
			f.write('			<materials name="Boston R Roof">' + '\n')
			f.write('			  <names>' + '\n')
			f.write('				<item>Insulation</item>' + '\n')
			f.write('			  </names>' + '\n')
			f.write('			  <thermalConductivity>' + '\n')
			f.write('				<item>0.5</item>' + '\n')
			f.write('			  </thermalConductivity>' + '\n')
			f.write('			  <volumetricHeatCapacity>' + '\n')
			f.write('				<item>221752</item>' + '\n')
			f.write('			  </volumetricHeatCapacity>' + '\n')
			f.write('			  <thickness>[0.1273]</thickness>' + '\n')
			f.write('			</materials>' + '\n')
			f.write('			<vegetationCoverage>0.2</vegetationCoverage>' + '\n')
			f.write('			<inclination>1</inclination>' + '\n')
			f.write('			<initialTemperature>20</initialTemperature>' + '\n')
			f.write('		  </roof>' + '\n')
			f.write('		  <mass>' + '\n')
			f.write('			<albedo>0.5</albedo>' + '\n')
			f.write('			<emissivity>0.9</emissivity>' + '\n')
			f.write('			<materials name="Boston R IM">' + '\n')
			f.write('			  <names>' + '\n')
			f.write('				<item>Concrete HW</item>' + '\n')
			f.write('			  </names>' + '\n')
			f.write('			  <thermalConductivity>' + '\n')
			f.write('				<item>1.31</item>' + '\n')
			f.write('			  </thermalConductivity>' + '\n')
			f.write('			  <volumetricHeatCapacity>' + '\n')
			f.write('				<item>1874432</item>' + '\n')
			f.write('			  </volumetricHeatCapacity>' + '\n')
			f.write('			  <thickness>[0.1]</thickness>' + '\n')
			f.write('			</materials>' + '\n')
			f.write('			<vegetationCoverage>0</vegetationCoverage>' + '\n')
			f.write('			<inclination>1</inclination>' + '\n')
			f.write('			<initialTemperature>20</initialTemperature>' + '\n')
			f.write('		  </mass>' + '\n')
			f.write('		  <glazing name="Boston R">' + '\n')
			f.write('			<glazingRatio>0.15</glazingRatio>' + '\n')
			f.write('			<windowUvalue>3.8</windowUvalue>' + '\n')
			f.write('			<windowSHGC>0.39</windowSHGC>' + '\n')
			f.write('		  </glazing>' + '\n')
			f.write('		</construction>' + '\n')
			f.write('		<building name="BOS Commericial">' + '\n')
			f.write('		  <floorHeight>3</floorHeight>' + '\n')
			f.write('		  <dayInternalGains>24.7145454545455</dayInternalGains>' + '\n')
			f.write('		  <nightInternalGains>5.58725274725274</nightInternalGains>' + '\n')
			f.write('		  <radiantFraction>0.5</radiantFraction>' + '\n')
			f.write('		  <latentFraction>0.09</latentFraction>' + '\n')
			f.write('		  <infiltration>0.176785714285714</infiltration>' + '\n')
			f.write('		  <ventilation>1</ventilation>' + '\n')
			f.write('		  <coolingSystemType>air</coolingSystemType>' + '\n')
			f.write('		  <coolingCOP>3.7</coolingCOP>' + '\n')
			f.write('		  <daytimeCoolingSetPoint>25</daytimeCoolingSetPoint>' + '\n')
			f.write('		  <nighttimeCoolingSetPoint>26</nighttimeCoolingSetPoint>' + '\n')
			f.write('		  <daytimeHeatingSetPoint>20</daytimeHeatingSetPoint>' + '\n')
			f.write('		  <nighttimeHeatingSetPoint>17</nighttimeHeatingSetPoint>' + '\n')
			f.write('		  <coolingCapacity>205</coolingCapacity>' + '\n')
			f.write('		  <heatingEfficiency>0.8</heatingEfficiency>' + '\n')
			f.write('		  <nightSetStart>19</nightSetStart>' + '\n')
			f.write('		  <nightSetEnd>5</nightSetEnd>' + '\n')
			f.write('		  <heatReleasedToCanyon>0</heatReleasedToCanyon>' + '\n')
			f.write('		  <initialT>20</initialT>' + '\n')
			f.write('		</building>' + '\n')
			f.write('	</typology3>' + '\n')
			f.write('	<typology4 dist="0" name="blankTypology4">' + '\n')
			f.write('		<dist>0</dist>' + '\n')
			f.write('		<construction>' + '\n')
			f.write('		  <wall>' + '\n')
			f.write('			<albedo>0.5</albedo>' + '\n')
			f.write('			<emissivity>0.9</emissivity>' + '\n')
			f.write('			<materials>' + '\n')
			f.write('			  <names>' + '\n')
			f.write('				<item>Wood Siding</item>' + '\n')
			f.write('			  </names>' + '\n')
			f.write('			  <thermalConductivity>' + '\n')
			f.write('				<item>0.11</item>' + '\n')
			f.write('			  </thermalConductivity>' + '\n')
			f.write('			  <volumetricHeatCapacity>' + '\n')
			f.write('				<item>658990</item>' + '\n')
			f.write('			  </volumetricHeatCapacity>' + '\n')
			f.write('			  <thickness>[0.2]</thickness>' + '\n')
			f.write('			</materials>' + '\n')
			f.write('			<vegetationCoverage>0</vegetationCoverage>' + '\n')
			f.write('			<inclination>0</inclination>' + '\n')
			f.write('			<initialTemperature>20</initialTemperature>' + '\n')
			f.write('		  </wall>' + '\n')
			f.write('		  <roof>' + '\n')
			f.write('			<albedo>0.25</albedo>' + '\n')
			f.write('			<emissivity>0.9</emissivity>' + '\n')
			f.write('			<materials name="Boston R Roof">' + '\n')
			f.write('			  <names>' + '\n')
			f.write('				<item>Insulation</item>' + '\n')
			f.write('			  </names>' + '\n')
			f.write('			  <thermalConductivity>' + '\n')
			f.write('				<item>0.5</item>' + '\n')
			f.write('			  </thermalConductivity>' + '\n')
			f.write('			  <volumetricHeatCapacity>' + '\n')
			f.write('				<item>221752</item>' + '\n')
			f.write('			  </volumetricHeatCapacity>' + '\n')
			f.write('			  <thickness>[0.1273]</thickness>' + '\n')
			f.write('			</materials>' + '\n')
			f.write('			<vegetationCoverage>0.2</vegetationCoverage>' + '\n')
			f.write('			<inclination>1</inclination>' + '\n')
			f.write('			<initialTemperature>20</initialTemperature>' + '\n')
			f.write('		  </roof>' + '\n')
			f.write('		  <mass>' + '\n')
			f.write('			<albedo>0.5</albedo>' + '\n')
			f.write('			<emissivity>0.9</emissivity>' + '\n')
			f.write('			<materials name="Boston R IM">' + '\n')
			f.write('			  <names>' + '\n')
			f.write('				<item>Concrete HW</item>' + '\n')
			f.write('			  </names>' + '\n')
			f.write('			  <thermalConductivity>' + '\n')
			f.write('				<item>1.31</item>' + '\n')
			f.write('			  </thermalConductivity>' + '\n')
			f.write('			  <volumetricHeatCapacity>' + '\n')
			f.write('				<item>1874432</item>' + '\n')
			f.write('			  </volumetricHeatCapacity>' + '\n')
			f.write('			  <thickness>[0.1]</thickness>' + '\n')
			f.write('			</materials>' + '\n')
			f.write('			<vegetationCoverage>0</vegetationCoverage>' + '\n')
			f.write('			<inclination>1</inclination>' + '\n')
			f.write('			<initialTemperature>20</initialTemperature>' + '\n')
			f.write('		  </mass>' + '\n')
			f.write('		  <glazing name="Boston R">' + '\n')
			f.write('			<glazingRatio>0.15</glazingRatio>' + '\n')
			f.write('			<windowUvalue>3.8</windowUvalue>' + '\n')
			f.write('			<windowSHGC>0.39</windowSHGC>' + '\n')
			f.write('		  </glazing>' + '\n')
			f.write('		</construction>' + '\n')
			f.write('		<building name="BOS Commericial">' + '\n')
			f.write('		  <floorHeight>3</floorHeight>' + '\n')
			f.write('		  <dayInternalGains>24.7145454545455</dayInternalGains>' + '\n')
			f.write('		  <nightInternalGains>5.58725274725274</nightInternalGains>' + '\n')
			f.write('		  <radiantFraction>0.5</radiantFraction>' + '\n')
			f.write('		  <latentFraction>0.09</latentFraction>' + '\n')
			f.write('		  <infiltration>0.176785714285714</infiltration>' + '\n')
			f.write('		  <ventilation>1</ventilation>' + '\n')
			f.write('		  <coolingSystemType>air</coolingSystemType>' + '\n')
			f.write('		  <coolingCOP>3.7</coolingCOP>' + '\n')
			f.write('		  <daytimeCoolingSetPoint>25</daytimeCoolingSetPoint>' + '\n')
			f.write('		  <nighttimeCoolingSetPoint>26</nighttimeCoolingSetPoint>' + '\n')
			f.write('		  <daytimeHeatingSetPoint>20</daytimeHeatingSetPoint>' + '\n')
			f.write('		  <nighttimeHeatingSetPoint>17</nighttimeHeatingSetPoint>' + '\n')
			f.write('		  <coolingCapacity>205</coolingCapacity>' + '\n')
			f.write('		  <heatingEfficiency>0.8</heatingEfficiency>' + '\n')
			f.write('		  <nightSetStart>19</nightSetStart>' + '\n')
			f.write('		  <nightSetEnd>5</nightSetEnd>' + '\n')
			f.write('		  <heatReleasedToCanyon>0</heatReleasedToCanyon>' + '\n')
			f.write('		  <initialT>20</initialT>' + '\n')
			f.write('		</building>' + '\n')
			f.write('	</typology4>' + '\n')
		
		# urban area parameters
		f.write('	<urbanArea>' + '\n')
		f.write('		<averageBuildingHeight>%i</averageBuildingHeight>' % settings.height + '\n')
		f.write('		<siteCoverageRatio>%.3f</siteCoverageRatio>' % settings.density + '\n')
		f.write('		<facadeToSiteRatio>%.3f</facadeToSiteRatio>' % settings.vert_to_horiz + '\n')
		f.write('		<treeCoverage>%.3f</treeCoverage>' % settings.tree_cover + '\n')
		f.write('		<nonBldgSensibleHeat>%i</nonBldgSensibleHeat>' % settings.sensible_anthropogenic + '\n')
		f.write('		<nonBldgLatentAnthropogenicHeat>%i</nonBldgLatentAnthropogenicHeat>' % settings.latent_anthropogenic + '\n')
		f.write('		<charLength>%i</charLength>' % settings.char_length + '\n')
		f.write('		<treeLatent>%.2f</treeLatent>' % settings.latent_tree + '\n')
		f.write('		<grassLatent>%.2f</grassLatent>' % settings.latent_grass + '\n')
		f.write('		<vegAlbedo>%.3f</vegAlbedo>' % settings.vegetation_albedo + '\n')
		f.write('		<vegStart>%i</vegStart>' % settings.evapotranspiration_start + '\n')
		f.write('		<vegEnd>%i</vegEnd>' % settings.evapotranspiration_end + '\n')
		f.write('		<daytimeBLHeight>1000</daytimeBLHeight>' + '\n')
		f.write('		<nighttimeBLHeight>80</nighttimeBLHeight>' + '\n')
		f.write('		<refHeight>150</refHeight>' + '\n')
		f.write('		<urbanRoad>' + '\n')
		f.write('		  <albedo>0.165</albedo>' + '\n')
		f.write('		  <emissivity>0.95</emissivity>' + '\n')
		f.write('		  <materials name="Default">' + '\n')
		f.write('			<names>' + '\n')
		f.write('			  <item>asphalt</item>' + '\n')
		f.write('			</names>' + '\n')
		f.write('			<thermalConductivity>' + '\n')
		f.write('			  <item>1</item>' + '\n')
		f.write('			</thermalConductivity>' + '\n')
		f.write('			<volumetricHeatCapacity>' + '\n')
		f.write('			  <item>1600000</item>' + '\n')
		f.write('			</volumetricHeatCapacity>' + '\n')
		f.write('			<thickness>1.25</thickness>' + '\n')
		f.write('		  </materials>' + '\n')
		f.write('		  <vegetationCoverage>%.3f</vegetationCoverage>' % settings.vegetation_cover + '\n')
		f.write('		  <inclination>1</inclination>' + '\n')
		f.write('		  <initialTemperature>-0.3</initialTemperature>' + '\n')
		f.write('		</urbanRoad>' + '\n')
		f.write('	</urbanArea>' + '\n')
		
		# reference site data
		f.write('	<referenceSite>' + '\n')
		f.write('		<latitude>43.67720</latitude>' + '\n')
		f.write('		<longitude>-79.63060</longitude>' + '\n')
		f.write('		<averageObstacleHeight>3.0</averageObstacleHeight>' + '\n') # used to set roughless (h * 0.1) and displacement (h * 0.5) lengths. Actual average is 20, but this 3m parameter should yield a roughness similar to suburbs. 
		f.write('		<ruralRoad>' + '\n')
		f.write('			<albedo>0.25</albedo>' + '\n')
		f.write('			<emissivity>0.95</emissivity>' + '\n')
		f.write('			<materials name="Default">' + '\n')
		f.write('			  <names>' + '\n')
		f.write('				<item>asphalt</item>' + '\n')
		f.write('			  </names>' + '\n')
		f.write('			  <thermalConductivity>' + '\n')
		f.write('				<item>1</item>' + '\n')
		f.write('			  </thermalConductivity>' + '\n')
		f.write('			  <volumetricHeatCapacity>' + '\n')
		f.write('				<item>1600000</item>' + '\n')
		f.write('			  </volumetricHeatCapacity>' + '\n')
		f.write('			  <thickness>1.25</thickness>' + '\n')
		f.write('			</materials>' + '\n')
		f.write('			<vegetationCoverage>0.41</vegetationCoverage>' + '\n')
		f.write('			<inclination>1</inclination>' + '\n')
		f.write('			<initialTemperature>-0.3</initialTemperature>' + '\n')
		f.write('		  </ruralRoad>' + '\n')
		f.write('	</referenceSite>' + '\n')
		
		# parameter data
		f.write('	<parameter>' + '\n')
		f.write('		<tempHeight>2</tempHeight>' + '\n')
		f.write('		<windHeight>10</windHeight>' + '\n')
		f.write('		<circCoeff>1.2</circCoeff>' + '\n')
		f.write('		<dayThreshold>150</dayThreshold>' + '\n')
		f.write('		<nightThreshold>50</nightThreshold>' + '\n')
		f.write('		<windMin>0.1</windMin>' + '\n')
		f.write('		<windMax>10</windMax>' + '\n')
		f.write('		<wgmax>0.005</wgmax>' + '\n')
		f.write('		<exCoeff>0.3</exCoeff>' + '\n')
		f.write('		<simuStartMonth>1</simuStartMonth>' + '\n')
		f.write('		<simuStartDay>1</simuStartDay>' + '\n')
		f.write('		<simuDuration>365</simuDuration>' + '\n')
		f.write('	</parameter>' + '\n')
		f.write('</xml_input>' + '\n')
		
		f.close()


	# setup new uwg sim w/ settings
	uwg_sim = uwg_settings(directory, name)	
	uwg_sim.height = height
	uwg_sim.density = scr
	uwg_sim.vert_to_horiz = fsr
	
	uwg_sim.vegetated_roof = veg_roof_fraction
	
	uwg_sim.albedo_road = 0.1

	uwg_sim.vegetation_cover = gcr
	uwg_sim.tree_cover = tcr
	
	uwg_sim.base_epw = epws[epw_class]
	
	if type == 'commercial':
		uwg_sim.office_percent = 85
		uwg_sim.residential_percent = 15
	elif type == 'residential':
		uwg_sim.office_percent = 85
		uwg_sim.residential_percent = 15
	elif type == 'mixed':
		uwg_sim.office_percent = 50
		uwg_sim.residential_percent = 50
	
	uwg_sim.material_upgrade = material_upgrade
	
	uwg_sim.roof_albedo = albedo
	uwg_sim.wall_albedo = albedo

	# write simulation files and run
	if not os.path.isfile(uwg_sim.settings_fullpath):
		write_param_file(uwg_sim)
		run_uwg(uwg_sim)
		elapsed_seconds = time.time() - start_time
		print '%s completed calculation in %.1f seconds.' % (name, elapsed_seconds)
	else:
		print '%s already exists!' % name



n = 0
for epw_class in list_morphed_weather:
	for height in [5, 35, 65, 95]: #range(5,95+1, 30):
		for scr in [0.15, 0.35, 0.55]:
			for fsr in [0.2, 1.4, 2.5, 3.7]:
				for gcr in [0.0, 0.3, 0.6]:
					tcr = gcr / 1.7
					for veg_roof_fraction in [0.0, 0.3, 0.6]:
						for material_upgrade in [1.0, 1.5, 2.0]:
							for type in ['commercial', 'residential', 'mixed']:
								for albedo in [0.2, 0.5, 0.8]: # 0.5 already calculated 
									if albedo == 0.5:
										name = '%s_height%i_scr%.1f_fsr%.1f_gcr%.1f_tcr%.1f_vegroof%.1f_mat%s_%s' % (epw_class, height, scr, fsr, gcr, tcr, veg_roof_fraction, material_upgrade, type)
									else:
										name = '%s_height%i_scr%.1f_fsr%.1f_gcr%.1f_tcr%.1f_vegroof%.1f_mat%s_alb%.1f_%s' % (epw_class, height, scr, fsr, gcr, tcr, veg_roof_fraction, material_upgrade, albedo, type)
									
									if fsr / scr < 14.0:
										jobs.append( job_server.submit(uwg_go, (epw_class, height, scr, fsr, gcr, tcr, type, veg_roof_fraction, material_upgrade, albedo, name), (), ('subprocess', 'os', 'shutil', 'time', 'sys', 'threading')) )
									
									n += 1

for job in jobs:
	print job()
	print '\n\n\n'

