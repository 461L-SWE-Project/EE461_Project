from datetime import datetime
from flask import Blueprint, Flask, request
from flask_pymongo import PyMongo
from . import init
from . import encryption


project = Blueprint('project', __name__)

#figure out what to do with this
ID = 1


@project.route('/projects_homepage' ,methods=['GET'])
def getProjectInfo():
    username = request.form.get["Username"]
    mongo = init.getDatabase()
    users = mongo.db.user_authentication
    projects = mongo.db.project_information
    hardware = mongo.db.hardware_resources

    hashed_username = encryption.hash_string(username)
    user_info = users.find_one({"Username": hashed_username})
    """
        User:
            Username : ""
            Password : ""
            Email : "__@.__com"
            Checked_out_hardware : {
                "HW1" : 0
                "Hw2" : 0
            }
            Projects = []
    
    
    """
    returnObj = {
        "Username" : username,
        "Total Hardware Allocation" : {},
        "Projects" : []
    }
   
   #find user's total HW allocations
    checkedOutHW = user_info["Checked_out_hardware"] #should also be dictionary form
    returnObj["Total Hardware Allocation"] = checkedOutHW


    #List of user's projects and hardware checked out for each project
    #only one user per project 
    projectIds = user_info["Projects"]
    for Id in projectIds:
        project = projects.find_one({"ID": Id})
        projectName = project["Name"]
        #dictionary of dictionaries or list of dictionaries ???

        projectAlloc = project["HW Allocation"] #should be a dictionary 

        projectAlloc["Project Name"]  = projectName
        projectAlloc["Project ID"]  = Id
        """
        Format:
        {
            "Name": ProjectName,
            "HW1": 40,
            "HW2: 30,
        }

        Each dictionary is stored in a list (can make it a dictionary of dictionaries later if necessary)
        """
        returnObj["Projects"].append(projectAlloc)



    #If multiple users per project
    # for Id in projectIds:
    #     project = projects.find_one({"Project_id": Id})
    #     team_alloc_info = project["Team Members"] #should be a dictionary
       
    #     user_alloc_info = team_alloc_info[hashed_username]
    #     user_alloc_info["Project Name"] = project["Name"]
    #     user_alloc_info["Project ID"]  = Id
    #     returnObj["Projects"].append(user_alloc_info)

    #don't know how I should return this?
    hardware_allocations={}
    #this should be fine
    for document in hardware:
        key = document["Name"]
        capacity = document["Capacity"]
        availability = document["Availability"]
        value = {
            "Capacity" : capacity,
            "Availability" : availability
        }
        hardware_allocations[key] = value
        """
        Format of this :
        {
            "HW1" : {
                "Capacity" : 50
                "Availability": 40
            }
            "HW2" : {
                "Capacity" : 40
                "Availability" : 35
            }
        }
        """

    return returnObj
    

        
@project.route('/create_project' ,methods=['POST'])
def createProject():       
    username = request.form.get["Username"]
    mongo = init.getDatabase()
    users = mongo.db.user_authentication
    projects = mongo.db.project_information
    hardware = mongo.db.hardware_resources


    hashed_username = encryption.hash_string(username)
    user_info = users.find_one({"Username": hashed_username})


    if request.method == "POST":
        #do we want unique project names, or is it fine bc we have project IDs
        projectName = request.form["Name"]
        dateCreated = datetime.date.today() #vs datetime.datetime.now()
        creator = username
        hardware_allocation = {}
        projectMembers = {}

        #how is hardware checkout info going to be sent to backend ?
        HWDict = request.form["HW_Alloc"]

        #im assuming its gonna come in a dictionary format : e.g {HW1: 20, HW2: 40}
        user_HW = user_info["Checked_out_hardware"]
        for key in HWDict:
            #check if amount checked out is available -- 
            doc = hardware.find_one({"Name":key})
            
            if doc["Availability"] < HWDict[key]:
                errorMessage = "Not enough hardware available: " +key
                return {"Response" : "Fail", "Message" : errorMessage}
            else:
                avail = doc["Availability"]
                avail-=HWDict[key]
                
                #udpate hardware collection 
                query = {"Name": key}
                update = {"$set": {"Availability": avail}}
                hardware.update_one(query,update)

                #update user information

                user_HW[key]= user_HW[key]+HWDict[key]


        #after looping succesfully, post hardware updates to database at once
        query = {"Username":hashed_username}
        update = {"$set": {"Checked_out_hardware": user_HW}}
        users.update_one(query,update)

                


        hardware_allocation = HWDict
        projectMembers[username] = HWDict #first member = creator :)

        post = {
            "Name" : projectName,
            "ID" : ID,
            "Creator": username,
            "Date Created" : dateCreated,
            "HW_Allocation" : HWDict,
            "Project Members" : projectMembers

        }

        projects.insert_one(post)
        #update ID for next project creation
        ID = ID + 1
        return  {"Response": "Success" , "Message": "Succesfully Created Project"}
     



@project.route('/delete_project' ,methods=['POST'])
def deleteProject(username): 
    #need to send request object so I can get access to multiple pieces of data
    projectName = request.form.get["Name"]
    username = request.form.get["Username"]

    mongo = init.getDatabase()
    users = mongo.db.user_authentication
    projects = mongo.db.project_information
    hardware = mongo.db.hardware_resources

    projectToDelete = projects.find_one({"Name": projectName})
    projectMembers = projectToDelete["Project Members"]


    #THINGS NEEDED TO BE UPDATED IN THE DATABASE:
        #HWSET COLLECTION (check hardware back in)
        #AMOUNT CHECKED OUT IN EACH USERS DOCUMENT
    for member in projectMembers:
        checkedOut = projectMembers[member]
        user = users.find_one({"Name": member})
        userHW = user["Checked out hardware"] #dictionary
        userProjects = user["Projects"]
        userProjects.remove(projectName)#remove name from their list of projects

        for hwSet in checkedOut:
            HWDoc = hardware.find_one({"Name": hwSet})

            amt = checkedOut[hwSet]
            availability = HWDoc["Availability"] + amt

            userHW[hwSet] = userHW[hwSet] - amt

            query = {"Name": hwSet}
            update = {"$set": {"Availability":availability}}
            hardware.update_one(query,update)

        query = {"Username":member}
        update = {"$set": {"Checked out hardware": userHW, "Projects":userProjects}}
        users.update_one(query, update)




        #FINALLY DELETE THE PROJECT
        projects.delete_one({"Name", projectName})
        
#stuff malvika wrote (for debugging purposes)
        
#update existing project
@projects.route('/update_project', methods =['POST'])
def update_project():
    if request.method == 'POST':
        user = request.form['UserID']
        project_id = request.form["ID"]
        h1_alloc = request.form["HWSet1Alloc"]
        h2_alloc = request.form["HWSet2Alloc"]
        hashed_value_user = hash_string(user)
        
        db = get_db()
        projects_col = db.project_information 
        project_entry = projects_col.update({"id": project_id}, {"$set": {"HWSet1Alloc": h1_alloc, "HWSet2Alloc": h2_alloc}})
        
        # now update hardware collection
        hardware_col = db.hardware_resources
        cursor = hardware_col.find({})
        id_hardware = "HWSet1Alloc"
        hardware_allocations = [h1_alloc, h2_alloc]
        index = 0
        for document in cursor:
            id_hardware = document["id"]
            # if they have allocated too much, sends error code 
            if document["allocation"] - hardware_allocations[index] < 0:
                return {'Response': 'Fail', 'Message': 'Allocated too much hardware'}
            hardware_col.update_one({"id" : id_hardware}, {"$set": {"allocation" : document["allocation"] - hardware_allocations[index]}})
            index = index + 1
        return {'Response': 'Success', 'Mesage': 'Successfully Allocated Hardware'}
            
#retrieving all hardware sets
@projects.route('/get_hardware',methods =['GET', 'POST'])
def send_hardware():
    if request.method == 'GET':
        db = get_db()
        hardware_col = db.hardware_resources
        
        cursor = hardware_col.find({})
        dictToSend = {}
        for elem in cursor:
            dictToSend.update(elem['id'], elem)
    return dictToSend





    





    




