import datetime
from flask import Blueprint, Flask, request
from flask_pymongo import PyMongo
from . import init
from . import encryption
from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity


project = Blueprint('project', __name__)



#WORKING 
@project.route('/projects_homepage' ,methods=['POST'])
@jwt_required()
def getProjectInfo():
    
    active_col = mongo.db.active_users 
    current_user_id = get_jwt_identity()
    if(active_col.find_one({'username': current_user_id}) == None):
        return {"Response": False, "Message": "User not found"}
    
    username = current_user_id
    mongo = init.getDatabase()
    users = mongo.db.user_authentication
    projects = mongo.db.project_information
    hardware = mongo.db.hardware_resources

    #hashed_username = encryption.hash_string(username)
    user_info = users.find_one({"username": username})
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
        "username" : username,
        "user total hardware allocation" : {},
        "projects" : []
    }
   
   #find user's total HW allocations
    checkedOutHW = user_info["checked_out_hardware"] #should also be dictionary form
    returnObj["user total hardware allocation"] = checkedOutHW


    #List of user's projects and total hardware checked out for each project
    projectIds = user_info["projects"]
    for Id in projectIds:
        project = projects.find_one({"id": Id})
        projectName = project["name"]

        projectAlloc = project["total_hw"] #should be a dictionary containing total hw allocation

        projectAlloc["name"]  = projectName #Add project name and ID to that dictionary 
        projectAlloc["id"]  = Id
        """
        Format:
        {
            "name": ProjectName,
            "id" : ID
            "HW1": 40,
            "HW2: 30,
        }

      
        """
        #list of dictionaries
        returnObj["projects"].append(projectAlloc)



    #If multiple users per project
    # for Id in projectIds:
    #     project = projects.find_one({"id": Id})
    #     team_alloc_info = project["team_members"] #should be a dictionary
       
    #     user_alloc_info = team_alloc_info[username]
    #     user_alloc_info["name"] = project["Name"]
    #     user_alloc_info["id"]  = Id
    #     returnObj["Projects"].append(user_alloc_info)

    #don't know how I should return this?
    hardware_allocations={}
    #this should be fine
    for document in hardware.find():
        key = document["name"]
        capacity = document["capacity"]
        availability = document["availability"]
        value = {
            "capacity" : capacity,
            "availability" : availability
        }
        hardware_allocations[key] = value
        """
        Might have to change this so that each HWSet is its own field -- should be able to do that p easily 
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
    returnObj["general hardware info"] = hardware_allocations
    return returnObj
    

#WORKING AS OF RIGHT NOW with JWT 
@project.route('/create_project' ,methods=['POST'])
@jwt_required()
def createProject():
    # do jwt check here
    mongo = init.getDatabase()
    active_col = mongo.db.active_users 
    current_user_id = get_jwt_identity()
    if(active_col.find_one({'username': current_user_id}) == None):
        return {"Response": False, "Message": "User not found"}
         
    # username = request.json["username"]
    mongo = init.getDatabase()
    users = mongo.db.user_authentication
    projects = mongo.db.project_information
    hardware = mongo.db.hardware_resources


    #hashed_username = encryption.hash_string(username)
    user_info = users.find_one({"username":current_user_id})
    print(user_info)


    if request.method == "POST":
        #do we want unique project names, or is it fine bc we have project IDs
        projectName = request.json["Name"]
        dateCreated = datetime.date.today() #vs datetime.datetime.now()
        creator = current_user_id
        hardware_allocation = {}
        projectMembers = {}
        ID = projectName + "_" + creator


        if projects.find_one({"id":ID}) != None:
            return {"Response": False, "Message" : "Project Name already being used"}

        #how is hardware checkout info going to be sent to backend ?
        HW1 = request.json["HWSet1Alloc"]
        HW2 = request.json["HWSet2Alloc"] 

        
        HWDict = {
            "HW1": HW1,
            "HW2" : HW2
        }
        print("HW DICTIONARY " )
        print(HWDict)

        #im assuming its gonna come in a dictionary format : e.g {HW1: 20, HW2: 40}
        user_HW = user_info["checked_out_hardware"]
        for key in HWDict:
            #check if amount checked out is available -- 
            doc = hardware.find_one({"name":key})
            
            if int(doc["availability"]) < int(HWDict[key]):
                errorMessage = "Not enough hardware available: " +key
                return {"Response" : False, "Message" : errorMessage}
            else:
                avail = int(doc["availability"])
                avail-= int(HWDict[key])
                print(avail)
                #udpate hardware collection 
                query = {"name": key}
                update = {"$set": {"availability": avail}}
                hardware.update_one(query,update)

                #update user information

                user_HW[key]= int(user_HW[key])+int(HWDict[key])

        user_projects = user_info["projects"]
        
        user_projects.append(ID)
        #after looping succesfully, post hardware updates to database at once
        query = {"username":current_user_id}
        update = {"$set": {"checked_out_hardware": user_HW, "projects":user_projects}}
        users.update_one(query,update)

                


        hardware_allocation = HWDict
        projectMembers[current_user_id] = HWDict #first member = creator :)

        
        post = {
            "name" : projectName,
            "id" : ID,
            "creator": creator,
            "date_Created" : str(dateCreated),
            "total_hw" : HWDict,
            "project_members" : projectMembers

        }

        projects.insert_one(post)
        #update ID for next project creation
        return  {"Response": "Success" , "Message": "Succesfully Created Project"}
     


# working with jwt
@project.route('/delete_project' ,methods=['POST'])
@jwt_required()
def deleteProject(): 
    
    mongo = init.getDatabase()
    active_col = mongo.db.active_users 
    current_user_id = get_jwt_identity()
    if(active_col.find_one({'username': current_user_id}) == None):
        return {"Response": False, "Message": "User not found"}
    
    
    #need to send request object so I can get access to multiple pieces of data
    projectID = request.json["projectID"] #?
    username = current_user_id

    mongo = init.getDatabase()
    users = mongo.db.user_authentication
    projects = mongo.db.project_information
    hardware = mongo.db.hardware_resources

    if projects.find_one({"id": projectID}) == None:
            return {"Response" : False, "Message": "Project ID does not exist"}

    projectToDelete = projects.find_one({"id": projectID})
    if projectToDelete["creator"] != username:
        return {"Response": False, "Message": "Can only delete project if you are the creator"}

    projectMembers = projectToDelete["project_members"]


    #THINGS NEEDED TO BE UPDATED IN THE DATABASE:
        #HWSET COLLECTION (check hardware back in)
        #AMOUNT CHECKED OUT IN EACH USERS DOCUMENT
    for member in projectMembers:
        print(member)
        checkedOut = projectMembers[member] #dictionary of user's checked out hw for that project
        user = users.find_one({"username": member})
        userHW = user["checked_out_hardware"] #dictionary of user's total checked out hw
        userProjects = user["projects"]

        userProjects.remove(projectID)#remove name from their list of projects

        for hwSet in checkedOut:
            HWDoc = hardware.find_one({"name": hwSet})

            amt = int(checkedOut[hwSet])
            availability = int(HWDoc["availability"]) + amt

            userHW[hwSet] = int(userHW[hwSet]) - amt
            query = {"name": hwSet}
            update = {"$set": {"availability":availability}}
            hardware.update_one(query,update)

        query = {"username":member}
        update = {"$set": {"checked_out_hardware": userHW, "projects":userProjects}}
        users.update_one(query, update)


    #FINALLY DELETE THE PROJECT
    projects.delete_one({"id":projectID})
    return {"Response": True, "Message": "Successfully deleted project"}

@project.route('/join_project', methods = ['POST'])
@jwt_required()
def join_project():
    if request.method == 'POST':
        
        mongo = init.getDatabase()
        active_col = mongo.db.active_users 
        current_user_id = get_jwt_identity()
        if(active_col.find_one({'username': current_user_id}) == None):
            return {"Response": False, "Message": "User not found"}

        mongo = init.getDatabase()
        users = mongo.db.user_authentication
        hardware = mongo.db.hardware_resources
        projects = mongo.db.project_information
        active_users = mongo.db.active_users


        #check if user is still logged in
        # token = request.json['token']
        # if active_users.find_one({"token_id": token}) == None:
        #     return {"Response": False, "Message" : "User is no longer logged in. "}
        
        # find_user = active_users.find_one({"token_id": token})
        # username = find_user["username"]

        username = current_user_id
        project_to_join = request.json["projectID"] #?




        #check if project exists
        if projects.find_one({"id": project_to_join}) == None:
            return {"Response" : False, "Message": "Project ID does not exist"}

        #add project to their list of projects
        user = users.find_one({"username":username})
        user_projects = user["projects"]
        user_projects.append(project_to_join)
        query = {"username":username}
        update = {"$set": {"projects":user_projects}}
        users.update_one(query, update)
       
        project = projects.find_one({"id": project_to_join})
        projectMembers = project["project_members"]
        #now add user to the project -- have no hw allocated to them as of now

        user_HW = {}
        #amt checked out for each hardware is 0
        for document in hardware.find():
            key = document["name"]
            user_HW[key] = 0
        
        projectMembers[username] = user_HW

        query = {"id":project_to_join}
        update = {"$set": {"project_members":projectMembers}}
        projects.update_one(query, update)

        return {"Response": True, "Message": "Successfully joined project"}




        
#stuff malvika wrote (for debugging purposes)
        
#update existing project
@project.route('/update_project', methods =['POST'])
@jwt_required()
def update_project():

    #figure out how we're doing this
    if request.method == 'POST':
        
        mongo = init.getDatabase()
        active_col = mongo.db.active_users 
        current_user_id = get_jwt_identity()
        if(active_col.find_one({'username': current_user_id}) == None):
            return {"Response": False, "Message": "User not found"}
        
        
        user = current_user_id
        project_id = request.json["projectID"]
        actionType = request.json["action"]
        h1_alloc = request.json["HWSet1Alloc"]
        h2_alloc = request.json["HWSet2Alloc"]

        HWDict = {
            "HW1": h1_alloc,
            "HW2" : h2_alloc
        }
    

        #change to fit format of the database
        mongo = init.getDatabase()
        hardware_col = mongo.db.hardware_resources
        projects_col = mongo.db.project_information 
        user_col = mongo.db.user_authentication

        if projects_col.find_one({"id": project_id}) == None:
            return {"Response": False, "Message": "No project id"}
        project = projects_col.find_one({"id": project_id})
        #project's total HW info
        project_HW = project["total_hw"]
        #get users hw info for given project
        projectMembers = project["project_members"]
        currentUser = projectMembers[user]
        print(currentUser)

        #user's document
        user_info = user_col.find_one({"username": user})
        #user's total HW info
        user_HW = user_info["checked_out_hardware"]

        for key in HWDict:
            #check if amount checked out is available -- 
            doc = hardware_col.find_one({"name":key})
            if(actionType == "check-out"):                            
                if int(doc["availability"]) < int(HWDict[key]):
                    errorMessage = "Not enough hardware available: " +key
                    return {"Response" : False, "Message" : errorMessage}
                else:
                    avail = int(doc["availability"])
                    avail-= int(HWDict[key])
                
                #udpate hardware collection 
                    query = {"name": key}
                    update = {"$set": {"availability": avail}}
                    hardware_col.update_one(query,update)

                #update user information

                    user_HW[key]= int(user_HW[key])+int(HWDict[key])

                #update project info 

                    currentUser[key] = int(currentUser[key]) + int(HWDict[key])
                    project_HW[key] = int(project_HW[key]) + int(HWDict[key])

            elif (actionType == "check-in"):
                avail = int(doc["availability"])
                avail+= int(HWDict[key])
                
                #udpate hardware collection 
                query = {"name": key}
                update = {"$set": {"availability": avail}}
                hardware_col.update_one(query,update)

                #update user information

                user_HW[key]= int(user_HW[key])-int(HWDict[key])
                if user_HW[key] < 0:
                    user_HW[key] = 0

                #update project info 
                currentUser[key] = int(currentUser[key]) - int(HWDict[key])
                if currentUser[key] < 0:
                    currentUser[key] = 0
                project_HW[key] = int(project_HW[key]) - int(HWDict[key])
                if project_HW[key] < 0:
                    project_HW[key] = 0
                


        #after looping succesfully, post hardware updates to database at once
        query = {"username":user}
        update = {"$set": {"checked_out_hardware": user_HW}}
        user_col.update_one(query,update)

        print(currentUser)
        projectMembers[user] = currentUser
        query = {"id":project_id}
        update = {"$set": {"project_members": projectMembers, "total_hw": project_HW}}
        projects_col.update_one(query,update)


        return {'Response': True, 'Message': 'Successfully Updated Project'}

        # project_entry = projects_col.update({"id": project_id}, {"$set": {"HWSet1Alloc": h1_alloc, "HWSet2Alloc": h2_alloc}})
        
        # # now update hardware collection
        
        # cursor = hardware_col.find({})
        # #id_hardware = "HWSet1Alloc"
        # hardware_allocations = [h1_alloc, h2_alloc]
        # index = 0
        # for document in cursor:
        #     id_hardware = document["id"]
        #     # if they have allocated too much, sends error code 
        #     if document["allocation"] - hardware_allocations[index] < 0:
        #         return {'Response': 'Fail', 'Message': 'Allocated too much hardware'}
        #     hardware_col.update_one({"id" : id_hardware}, {"$set": {"allocation" : document["allocation"] - hardware_allocations[index]}})
        #     index = index + 1
        # return {'Response': 'Success', 'Mesage': 'Successfully Allocated Hardware'}
            
#retrieving all hardware sets
@project.route('/get_hardware',methods =['GET', 'POST'])
def send_hardware():
    if request.method == 'GET':
        mongo = init.getDatabase()
        hardware_col = mongo.db.hardware_resources
        
        cursor = hardware_col.find({})
        dictToSend = {}
        for elem in cursor:
            dictToSend.update(elem['id'], elem)
    return dictToSend





    





    




