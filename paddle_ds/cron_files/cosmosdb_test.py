import pydocumentdb.documents as documents
import pydocumentdb.document_client as document_client
import pydocumentdb.errors as errors
import datetime

#from jsonmerge import merge

import config as cfg

# ----------------------------------------------------------------------------------------------------------
# Prerequistes - 
# 
# 1. An Azure DocumentDB account - 
#    https:#azure.microsoft.com/en-us/documentation/articles/documentdb-create-account/
#
# 2. Microsoft Azure DocumentDB PyPi package - 
#    https://pypi.python.org/pypi/pydocumentdb/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a Database resource for Azure DocumentDB
#
# 1. Query for Database (QueryDatabases)
#
# 2. Create Database (CreateDatabase)
#
# 3. Get a Database by its Id property (ReadDatabase)
#
# 4. List all Database resources on an account (ReadDatabases)
#
# 5. Delete a Database given its Id property (DeleteDatabase)
# ----------------------------------------------------------------------------------------------------------

"""
azuredocumentdbsettings = {
    'host': 'https://videokenoffshore.documents.azure.com:443/',
    'master_key': '##==',
    'database_id': 'com.videoken.development.jobqueues',
    'ds_job_collection_id': 'DeepSpeechJobQueue'
}
"""

HOST = cfg.azuredocumentdbsettings['host']
MASTER_KEY = cfg.azuredocumentdbsettings['master_key']
DATABASE_ID = cfg.azuredocumentdbsettings['database_id']
COURSE_COLLECTION_ID = cfg.azuredocumentdbsettings['course_collection_id']
VIDEOS_COLLECTION_ID = cfg.azuredocumentdbsettings['videos_collection_id']

database_link = 'dbs/' + DATABASE_ID
course_collection_link = database_link + '/colls/' + COURSE_COLLECTION_ID
videos_collection_link = database_link + '/colls/' + VIDEOS_COLLECTION_ID

class IDisposable:
    """ A context manager to automatically close an object with a close method
    in a with statement. """

    def __init__(self, obj):
        self.obj = obj

    def __enter__(self):
        return self.obj # bound to target

    def __exit__(self, exception_type, exception_val, trace):
        # extra cleanup in here
        self = None

class DocumentManagement:
    
    @staticmethod
    def CreateNewCourseEntry(client, courseJSON):
        print('Creating a new course in DB')

        # Create a SalesOrder object. This object has nested properties and various types including numbers, DateTimes and strings.
        # This can be saved as JSON as is without converting into rows/columns.
        #sales_order = DocumentManagement.GetSalesOrder("SalesOrder1")
        client.CreateDocument(course_collection_link, courseJSON)

    @staticmethod
    def UpdateCourseEntry(client, courseJSON):
        print('Creating a new course in DB')

        # Create a SalesOrder object. This object has nested properties and various types including numbers, DateTimes and strings.
        # This can be saved as JSON as is without converting into rows/columns.
        #sales_order = DocumentManagement.GetSalesOrder("SalesOrder1")
        client.UpsertDocument(course_collection_link, courseJSON)

    @staticmethod
    def CreateNewVideoEntry(client, videoJSON):
        print('Creating a new video object in DB')
        client.CreateDocument(videos_collection_link, videoJSON) 

    @staticmethod
    def UpdateVideoEntry(client, videoJSON):
        print('Updating a new video object in DB')
        client.UpsertDocument(videos_collection_link, videoJSON) 

    @staticmethod
    def ReadCourse(client, course_id):
        print('\n1.2 Reading Document by Id\n')

        # Note that Reads require a partition key to be spcified. This can be skipped if your collection is not
        # partitioned i.e. does not have a partition key definition during creation.
        doc_link = course_collection_link + '/docs/' + doc_id
        response = client.ReadDocument(doc_link)

        print('Document read by Id {0}'.format(doc_id))
        print('Account Number: {0}'.format(response.get('account_number')))


    @staticmethod
    def GetAllCourses(client):
        print('\n1.3 - Reading all documents in a collection\n')

        # NOTE: Use MaxItemCount on Options to control how many documents come back per trip to the server
        #       Important to handle throttles whenever you are doing operations such as this that might
        #       result in a 429 (throttled request)
        #documentlist = list(client.ReadDocuments(course_collection_link), {'maxItemCount':10})
        documentlist = client.ReadDocuments(course_collection_link)

        allcourses = []
        for document in documentlist:
            #print "Document name ", document['coursename']
            allcourses.append(document)
        #print('Found {0} documents'.format(documentlist.__len__()))

        #print "Document list length ", len(documentlist)
        
       # for doc in documentlist:
       #     print('Document Id: {0}'.format(doc.get('id')))

        return allcourses


    @staticmethod
    def GetAllVideos(client):
        print('\n1.3 - Reading all documents in a collection\n')

        documentlist = client.ReadDocuments(videos_collection_link)

        allvideos = []
        for document in documentlist:
            #print "Document name ", document['coursename']
            allvideos.append(document)
        #print('Found {0} documents'.format(documentlist.__len__()))

        #print "Document list length ", len(documentlist)
        
       # for doc in documentlist:
       #     print('Document Id: {0}'.format(doc.get('id')))

        return allvideos


    @staticmethod
    def QueryDocumentsWithCustomQuery(client, collection_link, query_with_optional_parameters):
        try:
            results = list(client.QueryDocuments(collection_link, query_with_optional_parameters))
            print("Query results are : ", len(results))
            for doc in results:
                print(doc)
            return results
        except errors.DocumentDBError as e:
            if e.status_code == 404:
                print("Document doesn't exist")
            elif e.status_code == 400:
                # Can occur when we are trying to query on excluded paths
                print("Bad Request exception occured: ", e)
                pass
            else:
                raise
        finally:
            print()

    

def SearchVideosByYouTubeID(videoid):

    with IDisposable(document_client.DocumentClient(HOST, {'masterKey': MASTER_KEY} )) as client:
        query = {
                "query": "SELECT * FROM r WHERE r.videoid=@videoid",
                "parameters": [ { "name":"@videoid", "value": videoid } ]
            }
        results = DocumentManagement.QueryDocumentsWithCustomQuery(client, videos_collection_link, query)

        if len(results) == 0:
            return None

        print "Video search results are  ", len(results)

        return results


def SearchCoursesByName(coursename):

    with IDisposable(document_client.DocumentClient(HOST, {'masterKey': MASTER_KEY} )) as client:
        query = {
                "query": "SELECT * FROM r WHERE r.coursename=@coursename",
                "parameters": [ { "name":"@coursename", "value": coursename } ]
            }
        results = DocumentManagement.QueryDocumentsWithCustomQuery(client, course_collection_link, query)

        #print "Course search results are  ", len(results)

        if len(results) == 0:
            return None

        return results 
   

def AddCoursesToAzureDocumentDB(courseJSONList):

    totalCourses = len(courseJSONList)
    course_added = 0
    with IDisposable(document_client.DocumentClient(HOST, {'masterKey': MASTER_KEY} )) as client:
        for eachcourseJSON in courseJSONList:
            #print('Creating a new video object in DB')
            #try:
            existingCourseJSON = SearchCoursesByName(eachcourseJSON['coursename'])
            #resultantJSON = merge(existingCourseJSON, eachcourseJSON)
            if existingCourseJSON == None:
                #DocumentManagement.CreateNewCourseEntry(client, eachcourseJSON) 
                course_added = course_added + 1
            else:
                print "A course with the same name already exist ", str(eachcourseJSON['coursename'])
                mergedCourseJSON = MergeCourseObjects(existingCourseJSON, eachcourseJSON)
                print "Merged course JSON is ", str(mergedCourseJSON)
                #DocumentManagement.UpdateCourseEntry(client, mergedCourseJSON) 

            
            #DocumentManagement.CreateNewCourseEntry(client, eachcourseJSON)             
            #except Exception as e:
            #    print "Exception encountered while inserting the course ", str(e)

    print "Total number of added course vs total courses ", str(course_added), str(totalCourses)

def MergeCourseObjects(existingCourseJSON, newCourseJSON):

    for eachkey, eachvalue in existingCourseJSON.items():
        if (eachkey in newCourseJSON and (existingCourseJSON[eachkey] == None or len(existingCourseJSON[eachkey]))==0):
            existingCourseJSON[eachkey] = newCourseJSON[eachkey]

        if eachkey == 'videoids' and len(existingCourseJSON['videoids'] < len(newCourseJSON['videoids'])):
            allVideosIDs = []
            allVideosIDs.extend(existingCourseJSON['videoids'])
            allVideosIDs.extend(newCourseJSON['videoids'])
            uniqueVideoIDs = list(set(allVideosIDs))
            existingCourseJSON[eachkey] = uniqueVideoIDs

    return existingCourseJSON


def AddVideosToAzureDocumentDB(videoJSONList):

    totalVideos = len(videoJSONList)
    video_added = 0
    with IDisposable(document_client.DocumentClient(HOST, {'masterKey': MASTER_KEY} )) as client:
        for eachvideoJSON in videoJSONList:
            #print('Creating a new video object in DB')
            #try:
            searchResults = SearchVideosByYouTubeID(eachvideoJSON['videoid'])
            if searchResults == None:
                DocumentManagement.CreateNewVideoEntry(client, eachvideoJSON) 
                video_added = video_added + 1
            else:
                print "Video id already exist ", str(eachvideoJSON['videoid'])
            
            #except Exception as e:
            #    print "Exception encountered while inserting the course ", str(e)

    print "Total number of added videos vs total videos ", str(video_added), str(totalVideos)


def UpdateVideosToAzureDocumentDB(videoJSONList):

    totalVideos = len(videoJSONList)
    video_added = 0
    with IDisposable(document_client.DocumentClient(HOST, {'masterKey': MASTER_KEY} )) as client:
        for eachvideoJSON in videoJSONList:
            #print('Creating a new video object in DB')
            #try:
            DocumentManagement.UpdateVideoEntry(client, eachvideoJSON) 
            video_added = video_added + 1
            #except Exception as e:
            #    print "Exception encountered while inserting the course ", str(e)

    print "Total number of added videos vs total videos ", str(video_added), str(totalVideos)


def UpdateCoursesToAzureDocumentDB(courseJSONList):

    totalCourses = len(courseJSONList)
    course_added = 0
    with IDisposable(document_client.DocumentClient(HOST, {'masterKey': MASTER_KEY} )) as client:
        for eachcourseJSON in courseJSONList:
            #print('Creating a new video object in DB')
            DocumentManagement.UpdateCourseEntry(client, eachcourseJSON) 
            course_added = course_added + 1
            #except Exception as e:
            #    print "Exception encountered while inserting the course ", str(e)

    print "Total number of added course vs total courses ", str(course_added), str(totalCourses)
    

    #print "Total number of updated course vs total courses ", str(course_added)#, str(totalCourses)


def GetAllCoursesFromAzureDocumentDB():
    
    with IDisposable(document_client.DocumentClient(HOST, {'masterKey': MASTER_KEY} )) as client:
        
        courseList = DocumentManagement.GetAllCourses(client) 
            #except Exception as e:
            #    print "Exception encountered while inserting the course ", str(e)

    return courseList
    #print "Total number of courses are ", len(courseList)#, str(totalCourses)


def GetAllVideosFromAzureDocumentDB():
    
    with IDisposable(document_client.DocumentClient(HOST, {'masterKey': MASTER_KEY} )) as client:
        
        videoList = DocumentManagement.GetAllVideos(client) 
            #except Exception as e:
            #    print "Exception encountered while inserting the course ", str(e)
        print "number of videos are ", len(videoList)

    return videoList
    #print "Total number of courses are ", len(courseList)#, str(totalCourses)



def run_sample():
    with IDisposable(document_client.DocumentClient(HOST, {'masterKey': MASTER_KEY} )) as client:
        try:
			# setup database for this sample
            try:
                client.CreateDatabase({"id": DATABASE_ID})

            except errors.DocumentDBError as e:
                if e.status_code == 409:
                    pass
                else:
                    raise errors.HTTPFailure(e.status_code)

            # setup collection for this sample
            try:
                client.CreateCollection(database_link, {"id": COURSE_COLLECTION_ID})
                print('Collection with id \'{0}\' created'.format(COURSE_COLLECTION_ID))

            except errors.DocumentDBError as e:
                if e.status_code == 409:
                    print('Collection with id \'{0}\' was found'.format(COURSE_COLLECTION_ID))
                else:
                    raise errors.HTTPFailure(e.status_code)

            DocumentManagement.CreateDocuments(client)
            DocumentManagement.ReadDocument(client,'SalesOrder1')
            DocumentManagement.ReadDocuments(client)

        except errors.HTTPFailure as e:
            print('\nrun_sample has caught an error. {0}'.format(e.message))
        
        finally:
            print("\nrun_sample done")

if __name__ == '__main__':

    #SearchVideosByYouTubeID("9obR8HGDW2w")

    #SearchCoursesByName("Introduction to Machine Learning")

    courseList = []
    coursedict = {}
    coursedict['coursename'] = "Introduction to Machine Learning"
    coursedict['disciplineid'] = 1234

    courseList.append(coursedict)

    UpdateCoursesToAzureDocumentDB(courseList)

    """
    videoList = GetAllVideosFromAzureDocumentDB()

    with open('nptel_all_videoids.csv', 'w') as f:
        for video in videoList:            
            f.write (video["videoid"] + '\n')

    """
    
    """
    try:     
        
        courseList = GetAllCoursesFromAzureDocumentDB()

        for eachCourse in courseList:
            print "name of the course is ", str(eachCourse)
        
    except Exception as e:
        print("Top level Error: args:{0}, message:N/A".format(e.args))
    """
