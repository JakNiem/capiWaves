import os
import math
from datetime import datetime



filmY = 20

domainX = 60
domainY = filmY*3
domainZ = domainX

temperature = .7 



ls1_exec = '/home/niemann/ls1-mardyn_master/build/src/MarDyn'
work_folder = f"T{temperature}_d{filmY}" #_{str(datetime.now()).replace(' ', '')}
stepName_init = "init"
configName_init = "config_init.xml"

def main():
    step1_init()


def step1_init():
    rhol,rhov = vle_kedia2006(temperature)

    # make sure sphereparams.xml exists
    if not os.path.exists(os.path.normpath("./sphereparams.xml")):
        writeFile(template_sphereparams(), os.path.normpath("./sphereparams.xml"))    

    # create work_folder
    if not os.path.exists(work_folder):
        os.mkdir(work_folder)    
    # create conifg.xml
    bulkConfigText = template_bulk(domainX, domainY, domainZ, temperature, rhol)
    writeFile(bulkConfigText, os.path.join(work_folder, configName_init))

    # create bash (only stirling so far)
    bashText = template_bash(ls1_exec, configName_init, stepName_init)
    writeFile(bashText, os.path.join(work_folder, 'stirling_init.sh'))
    os.system(f'chmod +x {os.path.join(work_folder, "stirling_init.sh")}')


    os.system(f'cd {work_folder}; sbatch stirling_init.sh')
    os.system('cd ..')


    return 0

def step2_removeParticles(rhov, rhol):
    in_file_path = os.path.join(work_folder, 'cp_binary_bulk-1.restart.dat')
    file_path_equi_start = os.path.join(work_folder, 'cp_binary_equi.start.dat')





    os.system(f'cd {work_folder}; sbatch stirling_equi.sh')



def vle_kedia2006(T):
    '''
    Get saturated densities of DROPLET by Vrabec et al., Molecular Physics 104 (2006). Equation numbers refer this paper.
    :param float T: Temperature
    :return: float rhol, float rhov: Saturated liquid and vapor density
    '''
    Tc = 1.0779
    rc = 0.3190

    dT = (Tc-T)

    a,b,c=0.5649,0.1314,0.0413
    rhol=rc+a*dT**(1/3.)+b*dT+c*dT**(3/2.)       # equation 4
    a,b,c=0.5649,0.2128,0.0702
    rhov=rc-a*dT**(1/3.)+b*dT+c*dT**(3/2.)       # equation 5

    return rhol,rhov









def writeFile(content, outfilepath):
    f = open(outfilepath, 'w')
    f.write(content)
    f.close


#################### TEMPLATES ####################
def template_bash(ls1Exec, configName, stepName, nodes = 1, nTasks = 1, ntasksPerNode = 1, cpusPerTask = 1):
    return f"""#!/bin/sh

#SBATCH -J ReplaceJobName
#SBATCH --nodes={nodes}

### 1*8 MPI ranks
#SBATCH --ntasks={nTasks}

### 128/16 MPI ranks per node
#SBATCH --ntasks-per-node={ntasksPerNode}

### tasks per MPI rank
#SBATCH --cpus-per-task={cpusPerTask}

#SBATCH -e ./err_{stepName}.%j.log
#SBATCH -o ./out_{stepName}.%j.log

{ls1Exec} --final-checkpoint=1 {configName} 
    """       




def template_sphereparams():
    return f"""<?xml version='1.0' encoding='UTF-8'?>
<spheres>
    <!-- 1CLJTS -->
    <site id="1">
        <radius>0.5</radius>
        <color>
            <r>0</r>
            <g>0</g>
            <b>155</b>
            <alpha>255</alpha>
        </color>
    </site>
</spheres>
    """        
	

	
def template_bulk(boxx, boxy, boxz, temperature, rhol):
    simsteps = 1000
    writefreq = int(simsteps/2)
    density  = rhol*1.1
    return f"""<?xml version='1.0' encoding='UTF-8'?>
<mardyn version="20100525" >

<refunits type="SI">
    <length unit="nm">0.1</length>
    <mass unit="u">1</mass>
    <energy unit="K">1</energy>
</refunits>

<simulation type="MD" >            
    <integrator type="Leapfrog" >
        <timestep unit="reduced" >0.004</timestep>
    </integrator>

    <run>
        <currenttime>0</currenttime>
        <production>
            <steps>{simsteps}</steps>
        </production>
    </run>

    <ensemble type="NVT">
        <temperature unit="reduced" >{temperature}</temperature>
        <domain type="box">
            <lx>{boxx}</lx>
            <ly>{boxy}</ly>
            <lz>{boxz}</lz>
        </domain>

        <components>
            <!-- 1CLJTS -->
            <moleculetype id="1" name="1CLJTS">
                <site type="LJ126" id="1" name="LJTS">
                    <coords> <x>0.0</x> <y>0.0</y> <z>0.0</z> </coords>
                    <mass>1.0</mass>
                    <sigma>1.0</sigma>
                    <epsilon>1.0</epsilon>
                    <shifted>true</shifted>
                </site>
                <momentsofinertia rotaxes="xyz" >
                    <Ixx>0.0</Ixx>
                    <Iyy>0.0</Iyy>
                    <Izz>0.0</Izz>
                </momentsofinertia>
            </moleculetype>
        </components>
    
        <phasespacepoint>
            <generator name="CubicGridGenerator">
                <specification>density</specification>
                <density>{density}</density>
                <binaryMixture>false</binaryMixture>
            </generator>
        </phasespacepoint>

    </ensemble>

    <algorithm>
        <parallelisation type="DomainDecomposition">
            <!--<MPIGridDims> <x>2</x> <y>2</y> <z>2</z> </MPIGridDims>-->
        </parallelisation>
        <datastructure type="LinkedCells">
            <cellsInCutoffRadius>1</cellsInCutoffRadius>
        </datastructure>
        <cutoffs type="CenterOfMass" >
            <defaultCutoff unit="reduced" >2.5</defaultCutoff>
            <radiusLJ unit="reduced" >2.5</radiusLJ>
        </cutoffs>
        <electrostatic type="ReactionField" >
            <epsilon>1.0e+10</epsilon>
        </electrostatic>

        <longrange type="none">
        </longrange>


        <thermostats>
            <thermostat type="TemperatureControl">
                <control>
                    <start>0</start>
                    <frequency>1</frequency>
                    <stop>1000000000</stop>
                </control>
                <regions>
                    <region>
                        <coords>
                            <lcx>0.0</lcx> <lcy>0.0</lcy> <lcz>0.0</lcz>
                            <ucx>box</ucx> <ucy>box</ucy> <ucz>box</ucz>
                        </coords>
                        <target>
                            <temperature>{temperature}</temperature>
                            <component>0</component>
                        </target>
                        <settings>
                            <numslabs>12</numslabs>
                            <exponent>0.4</exponent>
                            <directions>xyz</directions>
                        </settings>
                        <writefreq>100</writefreq>
                        <fileprefix>temp_log</fileprefix>
                    </region>
                </regions>
            </thermostat>
        </thermostats> 
    </algorithm>

    <output>
        <outputplugin name="CheckpointWriter">
            <type>binary</type>
            <writefrequency>{writefreq}</writefrequency>
            <outputprefix>cp_binary</outputprefix>
        </outputplugin>
    </output>
    
    <plugin name="DriftCtrl">
        <control>
            <start>0</start>
            <stop>20000000</stop>
            <freq>
                <sample>100</sample>
                <control>100</control>
                <write>100</write>
            </freq>
        </control>
        <target>
            <cid>1</cid>
            <drift> <vx>0.0</vx> <vy>0.0</vy> <vz>0.0</vz> </drift>
        </target>
        <range>
            <yl>0</yl> <yr>24</yr>
            <subdivision>
                <binwidth>24</binwidth>
            </subdivision>
        </range>
    </plugin>

</simulation>
</mardyn>
"""

#################### END OF TEMPLATES ####################










#################### CALLING MAIN ####################
# Call main() at the bottom, after all the functions have been defined.
if __name__ == '__main__':

    # # ARGUMENTS: give arguments like the following:
    # # m1: => use procedure for machine 1 (stirling)
    # # "init": => run step "init"
    # # T1 or T.8,.9,1: => TList = ...
    # # r8 or r8,9,10: => rList = ...


    # ### Reading Arguments
    # for arg in sys.argv[1:]:    #argument #0 is always [scriptname].py
    #     if arg == 'init':
    #         execStep = 'init'
    #     elif arg == 'equi':
    #         execStep = 'equi'
    #     elif arg == 'prod':
    #         execStep = 'prod'
    #     elif arg == 'test':
    #         work_folder = os.path.join(work_folder, f'test')  
    #     elif arg.startswith('m'):
    #         machine = int(eval(arg[1:]))
    #         if machine in [0,1,2]:
    #             print(f'argument {arg} interpreted as machine = {machine}')
    #         else:
    #             print(f'invalid machine argument [{machine}]. setting machine = 3')
    #             machine = 3
    #     elif arg.startswith('T'):  
    #         if len(arg) < 3 or type(eval(arg[1:])) == type(1) or type(eval(arg[1:]))== type(.7): arg+=',' 
    #         TList= list(eval(arg[1:]))
    #         print(f'argument {arg} interpreted as TList = {TList}')
    #     elif arg.startswith('r'):
    #         if len(arg) < 3 or type(eval(arg[1:])) == type(1) or type(eval(arg[1:]))== type(.7): arg+=',' 
    #         rList= list(eval(arg[1:]))
    #         print(f'argument {arg} interpreted as rList = {rList}')
    #     else:
    #         print(f'arg {arg} not a valid argument')
    
    main()