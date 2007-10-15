## @file
# process data section generation
#
#  Copyright (c) 2007, Intel Corporation
#
#  All rights reserved. This program and the accompanying materials
#  are licensed and made available under the terms and conditions of the BSD License
#  which accompanies this distribution.  The full text of the license may be found at
#  http://opensource.org/licenses/bsd-license.php
#
#  THE PROGRAM IS DISTRIBUTED UNDER THE BSD LICENSE ON AN "AS IS" BASIS,
#  WITHOUT WARRANTIES OR REPRESENTATIONS OF ANY KIND, EITHER EXPRESS OR IMPLIED.
#

##
# Import Modules
#
import Section
from GenFdsGlobalVariable import GenFdsGlobalVariable
import subprocess
from Ffs import Ffs
import os
from CommonDataClass.FdfClassObject import DataSectionClassObject
import shutil

## generate data section
#
#
class DataSection (DataSectionClassObject):
    ## The constructor
    #
    #   @param  self        The object pointer
    #
    def __init__(self):
        DataSectionClassObject.__init__(self)
    
    ## GenSection() method
    #
    #   Generate compressed section
    #
    #   @param  self        The object pointer
    #   @param  OutputPath  Where to place output file
    #   @param  ModuleName  Which module this section belongs to
    #   @param  SecNum      Index of section
    #   @param  KeyStringList  Filter for inputs of section generation
    #   @param  FfsInf      FfsInfStatement object that contains this section data
    #   @param  Dict        dictionary contains macro and its value
    #   @retval tuple       (Generated file name list, section alignment)
    #    
    def GenSection(self, OutputPath, ModuleName, SecNum, keyStringList, FfsInf = None, Dict = {}):
        #
        # Prepare the parameter of GenSection
        #
        if FfsInf != None:
            self.Alignment = FfsInf.__ExtendMarco__(self.Alignemnt)
            self.SecType = FfsInf.__ExtendMarco__(self.SecType)
            self.SectFileName = FfsInf.__ExtendMarco__(self.SectFileName)
        else:
            self.SectFileName = GenFdsGlobalVariable.ReplaceWorkspaceMarco(self.SectFileName)
            
        self.SectFileName = GenFdsGlobalVariable.MacroExtend(self.SectFileName, Dict)
        
        """Check Section file exist or not !"""

        if not os.path.exists(self.SectFileName):
            self.SectFileName = os.path.join (GenFdsGlobalVariable.WorkSpaceDir,
                                              self.SectFileName)
        if self.SecType == 'TE':
            TeFile = os.path.join( OutputPath, ModuleName + 'Te.raw')
            GenTeCmd = 'GenFW -t '    + \
                       ' -o '         + \
                        TeFile        + \
                        ' '           + \
                       GenFdsGlobalVariable.MacroExtend(self.SectFileName, Dict)
            GenFdsGlobalVariable.CallExternalTool(GenTeCmd, "GenFw Failed !")
            """Copy Map file to Ffs output"""
            Filename = GenFdsGlobalVariable.MacroExtend(self.SectFileName)
            if Filename[(len(Filename)-4):] == '.efi':
                MapFile = Filename.replace('.efi', '.map')
                if os.path.exists(MapFile):
                    CopyMapFile = os.path.join(OutputPath, ModuleName + '.map')
                    shutil.copyfile(MapFile, CopyMapFile)
            self.SectFileName = TeFile
           
            
                 
        OutputFile = os.path.join (OutputPath, ModuleName + 'SEC' + SecNum + Ffs.SectionSuffix.get(self.SecType))
        OutputFile = os.path.normpath(OutputFile)
        
        GenSectionCmd = 'GenSec -o '                                     + \
                         OutputFile                                      + \
                         ' -s '                                          + \
                         Section.Section.SectionType.get (self.SecType)  + \
                         ' '                                             + \
                         self.SectFileName
                         
        """Copy Map file to Ffs output"""
        Filename = self.SectFileName
        if Filename[(len(Filename)-4):] == '.efi':
             MapFile = Filename.replace('.efi', '.map')
             if os.path.exists(MapFile):
                 CopyMapFile = os.path.join(OutputPath, ModuleName + '.map')
                 shutil.copyfile(MapFile, CopyMapFile)
        #
        # Call GenSection
        #
        
        GenFdsGlobalVariable.CallExternalTool(GenSectionCmd, "GenSection Failed!")
        FileList = [OutputFile]
        return FileList, self.Alignment
