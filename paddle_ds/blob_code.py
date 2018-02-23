
from azure.storage.blob import BlockBlobService
import os
#from config import *
import shutil
from datetime import datetime


AZURE_CONTAINER_NAME = 'com-videoken-deployment'   #for production use this container 
#AZURE_CONTAINER_NAME = 'com-videoken-deployment-testing'  #for testing, use this container
AZURE_DIRECTORY_NAME = 'com.videoken/videos/'
AZURE_ACCOUNT_NAME = 'videokenoffshore'
AZURE_ACCOUNT_KEY = '###=='


class AzureStorageInterface:

    def __init__(self):
        
        self.block_blob_service = BlockBlobService(AZURE_ACCOUNT_NAME, AZURE_ACCOUNT_KEY)

    
    def updateSRTFiles (self, videoid, srtFilePath):
        #.2017-05-22T15:18:29.573

        self.createBlob(videoid, srtFilePath)
        print("Updated SRT file for videoid ", videoid, srtFilePath)

        timedSRTFILEPATH = srtFilePath + '.' + str(datetime.utcnow().isoformat()[:-3])

        shutil.copy(srtFilePath, timedSRTFILEPATH)

        self.createBlob(videoid, timedSRTFILEPATH)
        print("Updated SRT file for videoid ", videoid, timedSRTFILEPATH)        


    def getVideoFilesFromAzureStorage(self, videoid, videodirpath):
        
        videoblobname = AZURE_DIRECTORY_NAME + videoid + '/' + videoid + '.mp4'
        
        if not os.path.exists(videodirpath):
            os.makedirs(videodirpath)

        videopath =  videodirpath +"/"+ videoid + '.mp4'
        if self.block_blob_service.exists(AZURE_CONTAINER_NAME, videoblobname):
            self.getBlob(videoblobname, videopath)
        if os.path.exists (videopath):
            return True, videopath
        else:
            return False, ''


    def isSRTExist(self, videoid):

        srtblobname =  AZURE_DIRECTORY_NAME + videoid + '/' + videoid + '.en.srt'
        
        issrtexist = self.block_blob_service.exists(AZURE_CONTAINER_NAME, srtblobname)

        return issrtexist


    def deleteBlob(self, blobname):

        self.block_blob_service.delete_blob(AZURE_CONTAINER_NAME, blobname)

    def getBlob(self, blobname, filepath):

        self.block_blob_service.get_blob_to_path(AZURE_CONTAINER_NAME, blobname,filepath)
        

    def createBlob(self, videoid, filepath):

        path, filename = os.path.split(filepath)

        blobname = AZURE_DIRECTORY_NAME + videoid + '/' + filename 

        self.block_blob_service.create_blob_from_path(AZURE_CONTAINER_NAME, blobname, filepath)
    

    def isVideoExist(self, videoid):
        videoblobname =  AZURE_DIRECTORY_NAME + videoid + '/' + videoid + ".mp4"
        isvideoexist = self.block_blob_service.exists(AZURE_CONTAINER_NAME, videoblobname)
        return isvideoexist

#allfiles = getFilteredFilesFromDirectory('/datadrive/videos/PLpherdrLyny8YN4M24iRJBMCXkLcGbmhY/7GfyRrPYKG0/')
#print "filtered list is ", len(allfiles), allfiles

if __name__=='__main__': 

    instance = AzureStorageInterface()

    instance.getVideoFilesFromAzureStorage('Xev-PDZh9qg', '/home/dalonlobo/deepspeech_models/asr/paddle_ds/tmp')

    instance.isSRTExist('M8WOYjk7hKo')
    instance.isVideoExist('M8WOYjk7hKo')
#    instance.updateSRTFiles('3WX7bweJK-k','/home/kuldeep/Downloads/ekstep_srt_10/3WX7bweJK-k.en.srt')

    #pcdObj = instance.getJSONPhraseDataOutput('PWm2-4iAOIY')
    #pctObj = instance.getJSONPhraseTimesOutput('PWm2-4iAOIY')

    #print "phrase data is ", str(pcdObj), str(pctObj)