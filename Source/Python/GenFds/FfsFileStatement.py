## @file
# process FFS generation from FILE statement
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
import Ffs
import Rule
from GenFdsGlobalVariable import GenFdsGlobalVariable
import os
import StringIO
import subprocess
from CommonDataClass.FdfClassObject import FileStatementClassObject

## generate FFS from FILE
#
#
class FileStatement (FileStatementClassObject) :
    ## The constructor
    #
    #   @param  self        The object pointer
    #
    def __init__(self):
        FileStatementClassObject.__init__(self)
    
    ## GenFfs() method
    #
    #   Generate FFS
    #
    #   @param  self        The object pointer
    #   @param  Dict        dictionary contains macro and value pair
    #   @retval string      Generated FFS file name
    #    
    def GenFfs(self, Dict = {}):
        OutputDir = os.path.join(GenFdsGlobalVariable.FfsDir, self.NameGuid)
        if not os.path.exists(OutputDir):
             os.makedirs(OutputDir)

        Dict.update(self.DefineVarDict)
        
        if self.FvName != None :
            Buffer = StringIO.StringIO('')
            if self.FvName.upper() not in GenFdsGlobalVariable.FdfParser.Profile.FvDict.keys():
                raise Exception ("FV (%s) is NOT described in FDF file!" % (self.FvName))
            Fv = GenFdsGlobalVariable.FdfParser.Profile.FvDict.get(self.FvName.upper())
            FileName = Fv.AddToBuffer(Buffer)
            SectionFiles = ' -i ' + FileName
            
        elif self.FdName != None:
            if self.FdName.upper() not in GenFdsGlobalVariable.FdfParser.Profile.FdDict.keys():
                raise Exception ("FD (%s) is NOT described in FDF file!" % (self.FdName))
            Fd = GenFdsGlobalVariable.FdfParser.Profile.FdDict.get(self.FdName.upper())
            FvBin = {}
            FileName = Fd.GenFd(FvBin)
            SectionFiles = ' -i ' + FileName
        
        elif self.FileName != None:
            self.FileName = GenFdsGlobalVariable.ReplaceWorkspaceMacro(self.FileName)
            SectionFiles = ' -i ' + GenFdsGlobalVariable.MacroExtend(self.FileName, Dict)
            
        else:
            SectionFiles = ''
            Index = 0
            for section in self.SectionList :
                Index = Index + 1
                SecIndex = '%d' %Index
                sectList, align = section.GenSection(OutputDir, self.NameGuid, SecIndex, self.KeyStringList, None, Dict)
                if sectList != []:
                    for sect in sectList:
                        SectionFiles = SectionFiles  + \
                                       ' -i '        + \
                                       sect
                        if align != None:
                            SectionFiles = SectionFiles  + \
                                           ' -n '        + \
                                           align
                               
        #
        # Prepare the parameter
        #
        if self.Fixed != False:
                Fixed = ' -x '
        else :
                Fixed = ''
        if self.CheckSum != False :
                CheckSum = ' -s '
        else :
                CheckSum = ''
        if self.Alignment != None and self.Alignment !='':
            Alignment = ' -a ' + '%s' %self.Alignment
        else :
            Alignment = ''

        if not (self.FvFileType == None):
            FileType = ' -t ' + Ffs.Ffs.FdfFvFileTypeToFileType.get(self.FvFileType)
        else:
            FileType = ''

        FfsFileOutput = os.path.join(OutputDir, self.NameGuid + '.ffs')


        GenFfsCmd = 'GenFfs'       +  \
                     FileType      +  \
                     Fixed         +  \
                     CheckSum      +  \
                     Alignment     +  \
                     ' -o '        +  \
                     FfsFileOutput +  \
                     ' -g '        +  \
                     self.NameGuid +  \
                     SectionFiles

        GenFdsGlobalVariable.CallExternalTool(GenFfsCmd,"GenFfs Failed !")
        return FfsFileOutput
        

