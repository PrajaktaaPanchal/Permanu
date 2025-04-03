from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import Optional
from connector import get_connection
from fastapi.middleware.cors import CORSMiddleware
import send_email,uvicorn, os, json, uuid, logging, signal, sys,time
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://122.179.156.11:3000" ]

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

# *******************************************************************************************

logging.basicConfig(
        filename='main_log.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

# *******************************************************************************************
job_running = False
def check_delay():
    time.sleep(5)
    global job_running
    if job_running:
        print("Job is already running. Skipping execution.")
        return  
    job_running = True
    connection=get_connection()
    cursor=connection.cursor()
    try:   
        projects="""select Project_ID, Project_Name, Project_Owner_Email, Project_Owner_Name, Delivery_Date, Project_Status from projects """
        cursor.execute(projects)
        ids=cursor.fetchall()
        for id in ids:
            if (id["Delivery_Date"]) and (id["Project_Status"] != 'Closed'):
                expected_date = datetime.strptime(id["Delivery_Date"], "%Y-%m-%d")
                current_date = datetime.now()
                delay = (current_date - expected_date).days
            
                if delay == 1:
                    print("Delayed by 1 day.")
                    send_email.project_delay_user(user_email=id["Project_Owner_Email"], user_name=id["Project_Owner_Name"], project_name=id["Project_Name"], delayed_days=delay, reason=None, project_url=None)
                    send_email.project_delay_admin(project_name=id["Project_Name"], user_email=id["Project_Owner_Email"], due_date=id["Delivery_Date"], timestamp='None', project_url='url',delay_days=delay, reason=None)

                if delay == 3:
                    logging.warning(f"3-day delay detected for {id['Project_Name']}")
                    status=f"""update projects set project_status='Delayed' where project_id='{id['Project_ID']}'"""
                    cursor.execute(status)
                    connection.commit()
                    
                    print("Delayed by 3 days.")
                    send_email.project_delay_user(user_email=id["Project_Owner_Email"], user_name=id["Project_Owner_Name"], project_name=id["Project_Name"], delayed_days=delay, reason=None, project_url=None)
                    send_email.project_delay_admin(project_name=id["Project_Name"], user_email=id["Project_Owner_Email"], due_date=id["Delivery_Date"], timestamp='None', project_url='url',delay_days=delay, reason=None)
                    
                if delay == 7:
                    logging.warning(f"7-day delay detected for {id['Project_Name']}")
                    status=f"""update projects set project_status='Delayed' where project_id='{id['Project_ID']}'"""
                    cursor.execute(status)
                    connection.commit()
                    
                    print(f"Delayed by {delay} days.")
                    send_email.project_delay_user(user_email=id["Project_Owner_Email"], user_name=id["Project_Owner_Name"], project_name=id["Project_Name"], delayed_days=delay, reason=None, project_url=None)
                    send_email.project_delay_admin(project_name=id["Project_Name"], user_email=id["Project_Owner_Email"], due_date=id["Delivery_Date"], timestamp='None', project_url='url',delay_days=delay, reason=None)
                if delay == 15:
                    logging.warning(f"15-day delay detected for {id['Project_Name']}")
                    status=f"""update projects set project_status='Delayed' where project_id='{id['Project_ID']}'"""
                    cursor.execute(status)
                    connection.commit()

                    print(f"Delayed by {delay} days.")
                    send_email.project_delay_user(user_email=id["Project_Owner_Email"], user_name=id["Project_Owner_Name"], project_name=id["Project_Name"], delayed_days=delay, reason=None, project_url=None)
                    send_email.project_delay_admin(project_name=id["Project_Name"], user_email=id["Project_Owner_Email"], due_date=id["Delivery_Date"], timestamp='None', project_url='url',delay_days=delay, reason=None)
                
                elif delay > 0:
                    print("delay is more than 15 days")
                    logging.warning(f"{delay}-day delay detected for {id['Project_Name']}")
                    status=f"""update projects set project_status='Delayed' where project_id='{id['Project_ID']}'"""
                    cursor.execute(status)
                    connection.commit()
            else:
                continue      
        logging.info("checking delay completed successfully")
        job_running = False 

        check_due()
        milestone_delay()
        filter_logs()
        return {"message": "Success"}
        
    except Exception as e:
        logging.error(f"Error occurred during project monitoring: {str(e)}")
        cursor.close()
        connection.close()
        return {"message":"connection error"}
    finally:
        cursor.close()
        connection.close()
# *******************************************************************************************

def check_due():
    connection=get_connection()
    cursor=connection.cursor()
    logging.info("Started to checking due projects")
    try:   
        projects="""select Project_Name, Project_Owner_Email,Project_Owner_Name, Delivery_Date, Project_Status from projects """
        cursor.execute(projects)
        ids=cursor.fetchall()

        for id in ids:
            if (id["Delivery_Date"]) and (id["Project_Status"] != 'Closed'):
                expected_date = datetime.strptime(id["Delivery_Date"], "%Y-%m-%d")
                current_date = datetime.now()

                reminder_date = expected_date - timedelta(days=2)
                
                logging.debug(f"Processing project: {id['Project_Name']} "
                            f"(Due: {id['Delivery_Date']}, Status: {id['Project_Status']})")
                
                if current_date.date() == reminder_date.date() :
                    logging.info(f"Sending 2-day reminder for project: {id['Project_Name']}")
                    send_email.due_reminder_user(user_email=id["Project_Owner_Email"], user_name=id["Project_Owner_Name"], project_name=id["Project_Name"], due_date=id["Delivery_Date"], project_url=None, days_remaining=2)
                    logging.debug(f"2-day reminder email sent to '{id["Project_Owner_Email"]}'")
        
                if current_date.date() == expected_date.date():
                    logging.info(f"Sending due date reminder for project: {id['Project_Name']}")
                    send_email.due_reminder_user(user_email=id["Project_Owner_Email"], user_name=id["Project_Owner_Name"], project_name=id["Project_Name"], due_date=id["Delivery_Date"], project_url=None, days_remaining=0)
                    logging.debug(f"Due date reminder email sent to '{id["Project_Owner_Email"]}'")
            else:
                logging.info("Project end date or project status mismatched")
        
        logging.info("Project due date check completed successfully")
        return {"message": "Success"}
    except Exception as e:
        logging.error(f"Error occurred during project monitoring: {str(e)}")
        cursor.close()
        connection.close()
        return {"message": "connection error"}
    finally:
        cursor.close()
        connection.close()
# *******************************************************************************************

def milestone_delay():
    connection=get_connection()
    cursor=connection.cursor()
    logging.info("Started to checking delay of milestones")
    try:
        miles="""select MilestonesID, Milestones_Due_Date, Status from project_milestones """
        cursor.execute(miles)
        
        ids=cursor.fetchall()
        for id in ids:
            if (id["Milestones_Due_Date"]) and (id["Status"] != 'Closed'):
                expected_date = datetime.strptime(id["Milestones_Due_Date"], "%Y-%m-%d")
                current_date = datetime.now()
                delay = (current_date - expected_date).days 
                logging.debug(f"Processing milestone: {id['MilestonesID']} "
                            f"(Due: {id['Milestones_Due_Date']}, Status: {id['Status']})")
                if delay > 0:
                    logging.warning(f"Milestone {id['MilestonesID']} is delayed by {delay} days")
                    status=f"""update project_milestones set status='Delayed' where MilestonesID='{id['MilestonesID']}'"""
                    cursor.execute(status)
                    connection.commit()
                    logging.info(f"Updated status to 'Delayed' for milestone {id['MilestonesID']}")
        logging.info("Checking of milestones delay completed")
        return {"message": "Success"}
    except Exception as e:
        logging.error(f"Error occurred during milestone monitoring: {str(e)}")
        cursor.close()
        connection.close()
        return {"message": "connection error"}
    finally:
        cursor.close()
        connection.close()        

# *******************************************************************************************
def project_staus(Project_ID):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        logging.info(f"Starting to check  project status for Project_ID: {Project_ID}")
        sql="""SELECT Status from project_milestones where Project_ID=%s"""
        cursor.execute(sql,(Project_ID,))
        results=cursor.fetchall()
        statuses = [row["Status"] for row in results]

        project_info=f"""select project_name, project_owner_name, last_edited_date from projects where project_id='{Project_ID}'"""
        cursor.execute(project_info)
        info=cursor.fetchall()
        if not info:
            logging.error(f"No project found with Project_ID: {Project_ID}")
            return {"message": "Project not found"}
        
        if statuses and all(status == "Closed" for status in statuses):
            sql = "UPDATE projects SET Project_Status = 'Closed' WHERE Project_ID = %s"
            cursor.execute(sql, (Project_ID,))
            conn.commit()
            logging.info(f"Updated project status to 'Closed' for Project_ID: {Project_ID}")
            send_email.send_project_completed_email(info[0]["project_owner_name"], info[0]["project_name"], info[0]["last_edited_date"], project_url=None)
            logging.info("Sent project completion email")
            return {"message": "Project status updated to Closed"}
        else:
            sql = "UPDATE projects SET Project_Status = 'In progress' WHERE Project_ID = %s"
            cursor.execute(sql, (Project_ID,))
            conn.commit()
            logging.info(f"Updated project status to 'In progress' for Project_ID: {Project_ID}")
            return {"message": "Not all milestones are closed, project status unchanged"}
    except Exception as e:
        logging.error(f"Error occurred during project status update: {str(e)}")
        return {"message": "Error updating project status"}
    
    finally:
        cursor.close()
        conn.close()
# *******************************************************************************************

@app.post("/project_creation")
async def project_creation(
    project_data: str = Form(...), 
    Documents_PO_Copy: Optional[UploadFile] = File(None), 
    Documents_BOM: Optional[UploadFile] = File(None)):
    logging.info("Starting project creation process")

    project_dict = json.loads(project_data)
    files=[]
    connection = get_connection()
    cursor = connection.cursor()
    try:
        project_id=str(uuid.uuid4().hex)[:16]
        if Documents_PO_Copy:
            document_path = f"documents/{project_id}/Documents_PO_Copy/"
            os.makedirs(document_path, exist_ok=True)
            po_copy_path = os.path.join(document_path, Documents_PO_Copy.filename)
                    
            with open(po_copy_path, "wb") as f:
                f.write(await Documents_PO_Copy.read()) 
            project_dict["Documents_PO_Copy"] = po_copy_path
            files.append(project_dict["Documents_PO_Copy"])
            logging.info(f"Saved PO Copy document to: {po_copy_path}")
            
        if Documents_BOM:
            document = f"documents/{project_id}/Documents_BOM/"
            os.makedirs(document, exist_ok=True)
            bom_path = os.path.join(document, Documents_BOM.filename)
                    
            with open(bom_path, "wb") as f:
                f.write(await Documents_BOM.read()) 
            project_dict["Documents_BOM"] = bom_path
            files.append(project_dict["Documents_BOM"])
            logging.info(f"Saved BOM document to: {bom_path}")
        
        current_date=datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        query = """
        INSERT INTO projects (Project_Id,Project_Name, Project_Location, Project_Contract_Number, Delivery_Date, Project_Total_Value, 
                            Project_Capex, Project_Opex, Project_Owner_ID, Project_Owner_Name, Project_Owner_Email, 
                            Project_Scope, 
                            Customer_Contact_Person, Customer_Phone_Number, Customer_Email_Address, 
                            Customer_Fax_Number, Customer_Address, Documents_Del_Challan, Documents_Train_Cert,
                            Documents_PO_Copy,Documents_BOM,Project_Account_Manager,Account_Manager_ID,Account_Manager_Email, Project_Date, Project_Status) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, 
        (project_id,
        project_dict.get("Project_Name", None), 
        project_dict.get("Project_Location", None), 
        project_dict.get("Project_Contract_Number", None),
        project_dict.get("Delivery_Date", None), 
        project_dict.get("Project_Total_Value", None), 
        project_dict.get("Project_Capex", None),
        project_dict.get("Project_Opex", None), 
        project_dict.get("Project_Owner_ID", None), 
        project_dict.get("Project_Owner_Name", None),
        project_dict.get("Project_Owner_Email", None), 
        project_dict.get("Project_Scope", None), 
        project_dict.get("Customer_Contact_Person", None),
        project_dict.get("Customer_Phone_Number", None), 
        project_dict.get("Customer_Email_Address", None), 
        project_dict.get("Customer_Fax_Number", None),
        project_dict.get("Customer_Address", None), 
        project_dict.get("Documents_Del_Challan", None), 
        project_dict.get("Documents_Train_Cert", None),
        project_dict.get("Documents_PO_Copy", None),
        project_dict.get("Documents_BOM", None),
        project_dict.get("Project_Account_Manager", None),
        project_dict.get("Account_Manager_ID", None),
        project_dict.get("Account_Manager_Email", None),
        current_date,
        'Open'))
        connection.commit()
        logging.info(f"Created project with ID: {project_id}")

        if "Milestone" in project_dict and isinstance(project_dict["Milestone"], list):
            milestone_query = """
            INSERT INTO project_milestones 
            (Project_ID, Owner_ID, Milestone_Name, Milestones_Due_Date, Milestones_T_Days, 
            Pay_Milestone, Percentage_Payment, Amount, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for milestone in project_dict["Milestone"]:
                milestone_values = (
                    project_id,
                    project_dict.get("Project_Owner_ID"), 
                    milestone.get("Milestone_Name"),
                    milestone.get("Milestones_Due_Date"),
                    milestone.get("Milestones_T_Days"),
                    milestone.get("Pay_Milestone"),
                    milestone.get("Percentage_Payment"),
                    milestone.get("Amount"),
                    'Open'
                )

                cursor.execute(milestone_query, milestone_values)
                connection.commit()
                milestone_id = cursor.lastrowid  

                if "Submilestones" in milestone and isinstance(milestone["Submilestones"], list):
                    submilestone_query = """
                    INSERT INTO sub_milestones 
                    (Project_ID, Owner_ID, MilestonesID, Sub_Task_Name, Sub_Task_Desc, Due_Date, 
                        Sub_Creation_Date, Sub_Target_Date) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                    submilestone_values = [
                        (
                            project_id, 
                            project_dict.get("Project_Owner_ID"), 
                            milestone_id,  
                            sub.get("Sub_Task_Name", ""),   
                            sub.get("Sub_Task_Desc", None), 
                            sub.get("Due_Date", None), 
                            current_date, 
                            sub.get("Sub_Target_Date", None) 
                        )
                        for sub in milestone["Submilestones"] if sub.get("Sub_Task_Name") 
                    ]
                    if submilestone_values:
                        cursor.executemany(submilestone_query, submilestone_values)
                        connection.commit()
                        logging.info(f"Created {len(submilestone_values)} submilestones for Milestone ID: {milestone_id}")
                    else:
                        print("not")
        logging.info("Sent project allocation email")
        return {"message": "Project created successfully"}
        
    except Exception as e:
        logging.error(f"Error during project creation: {str(e)}")
        return {"message": "Error creating project"}

# *******************************************************************************************
def filter_logs(max_age_days=2):
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    log_path='main_log.log'
    recent_entries = []
    try:
        with open(log_path, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    timestamp_str = line[:19].strip()
                    entry_date = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    if entry_date >= cutoff_date:
                        recent_entries.append({
                            'date': entry_date,
                            'content': line.strip()[19:].strip()
                        })
                except (ValueError, IndexError):
                    continue
    
        with open(log_path, 'w', encoding='utf-8') as file:
            for entry in recent_entries:
                formatted_line = f"{entry['date'].strftime('%Y-%m-%d %H:%M:%S')} {entry['content']}\n"
                file.write(formatted_line)
                
    except FileNotFoundError:
        print(f"Error: Log file not found - {log_path}")
    except Exception as e:
        print(f"Error processing log file: {str(e)}")

# *******************************************************************************************
@app.get("/all_team")
async def get_team():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT Owner_ID,Owner_Name,Email_ID,Category FROM login_team"
            cursor.execute(sql)
            team=cursor.fetchall()
            logging.info(f"Retrieved {len(team)} team members")
            admin_data = []
            client_data = []
            account_manager_data = []
            for i in team:
                member = {
                    "Owner_ID": i["Owner_ID"],
                    "Owner_Name": i["Owner_Name"],
                    "Email_ID": i["Email_ID"],
                    "Category": i["Category"]
                }
                if i["Category"] == "admin":
                    admin_data.append(member)
                elif i["Category"] == "client":
                    client_data.append(member)    
                else:
                    account_manager_data.append(member)       
            logging.info(f"Team distribution - Admins: {len(admin_data)}, Clients: {len(client_data)}, Account Managers: {len(account_manager_data)}")
            
            return {
                "admin": admin_data,
                "client": client_data,
                "account_manager": account_manager_data}
    
    except Exception as e:
        logging.error(f"Error retrieving team information: {str(e)}")
        return {"error": "Failed to retrieve team information"}
    
    finally:
        conn.close()
        
# ********************************************************************************
        
@app.put("/edit_project/{project_id}")
async def edit_project(project_id:str, project_details: str = Form (...)):
    connection=get_connection()
    cursor=connection.cursor()
    project_details= json.loads(project_details)
    logging.debug(f"Loaded project details: {project_details}")
    try:
        sql=f"""update projects set project_location='{project_details['Project_Location']}',
        Project_Contract_Number='{project_details['Project_Contract_Number']}', 
        project_total_value='{project_details['Project_Total_Value']}', project_capex='{project_details['Project_Capex']}', 
        Project_Opex='{project_details['Project_Opex']}', project_scope='{project_details['Project_Scope']}' where project_id='{project_id}'"""
        cursor.execute(sql)
        connection.commit()
        logging.info(f"Project {project_id} updated successfully")
        return {"message":"Project Edited successfully"}
    
    except Exception as e:
        logging.error(f"Error editing project {project_id}: {str(e)}")
        return {"message": "Project not edited"}
        
    finally:
        cursor.close()
        connection.close()
        
# ********************************************************************************
@app.put("/edit_customer_details/{project_id}")
async def edit_customer_details(project_id:str, customer_details:str=Form(...) ):
    connection=get_connection()
    cursor=connection.cursor()
    customer_details= json.loads(customer_details)
    logging.debug(f"Loaded customer details: {customer_details}")
    try:
        sql=f"""update projects set Customer_Contact_Person='{customer_details['Customer_Contact_Person']}',
        Customer_Phone_Number='{customer_details['Customer_Phone_Number']}', 
        Customer_Email_Address='{customer_details['Customer_Email_Address']}', Customer_Fax_Number='{customer_details['Customer_Fax_Number']}', 
        Customer_Address='{customer_details['Customer_Address']}' where project_id='{project_id}'"""
        cursor.execute(sql)
        connection.commit()
        logging.info(f"Customer details updated successfully for project {project_id}")
        return {"message":"Customer details Edited successfully"}
    
    except Exception as e:
        logging.error(f"Error editing customer details for project {project_id}: {str(e)}")
        return {"message": "Customer details not edited"}
        
    finally:
        cursor.close()
        connection.close()
        
# ********************************************************************************    
@app.post("/add_member/{name}/{email}/{category}")
def add_member(name:str, email:str, category:str):
    connection=get_connection()
    cursor=connection.cursor()
    try:
        query = "INSERT INTO login_team (owner_name, email_id, category) VALUES (%s, %s, %s)"
        cursor.execute(query, (name, email, category))
        connection.commit()
        logging.info(f"Team member {name} added to database successfully")
        try:
            status=send_email.send_welcome_email(user_email=email, user_name=name, login_url='http://192.168.60.7:3000/')
            if status==1:
                logging.info(f"Welcome email sent successfully to {email}")
                return {"message":"Team member added successfully"}    
            else:
                logging.warning(f"Failed to send welcome email to {email}")
                return {"message":"Please check email id"}
        except Exception as e:
            logging.error(f"Error sending welcome email to {email}: {str(e)}")
            return {"message": "Please check email id"}
    
    except Exception as e:
        logging.error(f"Error adding team member {name}: {str(e)}")
        return {"message": "Team member name or email already exist"}
        
    finally:
        cursor.close()
        connection.close()
        
# ********************************************************************************
@app.delete("/delete_member/{member_id}")
def delete_member(member_id:int):
    connection=get_connection()
    cursor=connection.cursor()
    try:    
        project=f"select project_name from projects where project_owner_id={member_id} or account_manager_id={member_id}"
        cursor.execute(project)
        num=cursor.fetchall()
        logging.debug(f"Found {len(num)} projects owned by member")
        if len(num) == 0:
            sql=f"delete from login_team where owner_id ={member_id}"
            cursor.execute(sql)
            connection.commit()
            logging.info(f"Team member {member_id} deleted successfully")
            return {"message":"Team member removed successfully"}
        else:
            logging.info(f"Cannot delete member {member_id} - has {len(num)} projects assigned")
            return {"message":"Please assign the project to another owner"}

    except Exception as e:
        logging.error(f"Error deleting team member {member_id}: {str(e)}")
        return {"message": "Team member not removed"}
        
    finally:
        cursor.close()
        connection.close()
        logging.info("Database connection closed")
        
# ********************************************************************************
@app.put("/edit_member/{Owner_ID}")
async def edit_member(Owner_ID:int,login_details:str=Form(...) ):
    connection=get_connection()
    cursor=connection.cursor()
    try:
        logging.info(f"Starting member edit for Owner_ID: {Owner_ID}")
        login_data = json.loads(login_details)
        sql = """
        UPDATE login_team 
        SET Owner_Name = %s, Email_ID = %s, Category = %s 
        WHERE Owner_ID = %s
        """
        cursor.execute(sql, (
            login_data['Owner_Name'], 
            login_data['Email_ID'], 
            login_data['Category'], 
            Owner_ID
        ))
        connection.commit()
        logging.info(f"Member {Owner_ID} details updated successfully")
        return {"message": "Details Edited Successfully"}
    
    except Exception as e:
        logging.error(f"Error editing member {Owner_ID}: {str(e)}")
        return {"message": "Login_team details not edited"}
        
    finally:
        cursor.close()
        connection.close()
        logging.info("Database connection closed")

# ********************************************************************************
@app.post("/update_milestone_status/{Status}/{MilestoneID}/{Project_ID}")
def update_milestones_status(Status: str, MilestoneID: int, Project_ID: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if Status == "Closed":
            update_query = """
                UPDATE project_milestones 
                SET Status = %s
                WHERE MilestonesID = %s 
                AND Project_ID = %s
            """
            cursor.execute(update_query, (Status, MilestoneID, Project_ID))
            conn.commit()
            logging.info(f"Updated milestone status to 'Closed' for MilestoneID: {MilestoneID}")

            update_query2 = """
                UPDATE project_milestones 
                SET milestone_comp_date = %s
                WHERE MilestonesID = %s 
                AND Project_ID = %s
            """
            cursor.execute(update_query2, (datetime.today().strftime('%Y-%m-%d'), MilestoneID, Project_ID))
            conn.commit()
            update_query3 = """
                UPDATE projects 
                SET Last_Edited_Date = %s
                WHERE Project_ID = %s
            """
            cursor.execute(update_query3, (datetime.today().strftime('%Y-%m-%d'),Project_ID))
            conn.commit()
            logging.info(f"Updated last edited date for Project_ID: {Project_ID}")

            project_staus(Project_ID)
        else:
            logging.info(f"Processing milestone status update to '{Status}' for MilestoneID: {MilestoneID}")

            update_query = """
                UPDATE project_milestones 
                SET Status = %s, milestone_comp_date = NULL
                WHERE MilestonesID = %s 
                AND Project_ID = %s
            """
            cursor.execute(update_query, (Status, MilestoneID, Project_ID))
            conn.commit()
            update_query1 = """
                UPDATE projects 
                SET Last_Edited_Date = %s
                WHERE Project_ID = %s
            """
            cursor.execute(update_query1, (datetime.today().strftime('%Y-%m-%d'),Project_ID))
            conn.commit()
            logging.info(f"Calling project_status for Project_ID: {Project_ID}")

            project_staus(Project_ID)
        conn.close()
        return {"message": "Milestone status updated successfully"}

    except Exception as e:
        logging.error(f"Error updating milestone status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
# ********************************************************************************
@app.get("/bubbles")
def bubbles():
    logging.info("Starting bubbles endpoint execution")
    connection=get_connection()
    cursor=connection.cursor()
    try:
        owner="select * from login_team where category='client'"
        cursor.execute(owner)
        data=cursor.fetchall()
        main=[]
        for i in data:
            project=f"select count(*) from projects where project_owner_id={i['Owner_ID']}"
            cursor.execute(project)
            value=cursor.fetchall()
            main.append({'Owner_Name': i['Owner_Name'], 'Email_ID': i['Email_ID'], 'Projects': value[0]['count(*)']})
        result=sorted(main,key=lambda x:x['Projects']>0,reverse=True)
        logging.info("Successfully completed bubbles endpoint execution")
        return result
    except Exception as e:
        logging.exception(f"Error in bubbles endpoint: {str(e)}")
        return {"message": "connection error"}
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
            
# ********************************************************************************
@app.get("/graph")
def graph():
    connection=get_connection()
    cursor=connection.cursor()
    try:
        owner="select * from login_team where category='client'"
        cursor.execute(owner)
        data=cursor.fetchall()
        main=[]
        for i in data:
            op=f"select count(*) from projects where Project_Owner_ID={i['Owner_ID']} and project_status='Open'"
            cursor.execute(op)
            open=cursor.fetchall()
            inpro=f"select count(*) from projects where Project_Owner_ID={i['Owner_ID']} and project_status='In progress'"
            cursor.execute(inpro)
            inprogress=cursor.fetchall()
            close=f"select count(*) from projects where Project_Owner_ID={i['Owner_ID']} and project_status='Closed'"
            cursor.execute(close)
            closed=cursor.fetchall()
            delay=f"select count(*) from projects where Project_Owner_ID={i['Owner_ID']} and project_status='Delayed'"
            cursor.execute(delay)
            delayed=cursor.fetchall()
        
            main.append({'Owner_Name':i['Owner_Name'],'Email_ID': i['Email_ID'],'Open':open[0]['count(*)'],'In progress':inprogress[0]['count(*)'],'Completed':closed[0]['count(*)'],'Delayed':delayed[0]['count(*)']})
        result = sorted(main, key=lambda x: (x['Open'] > 0 or x['In progress'] > 0 or x['Completed'] > 0 or x['Delayed'] > 0), reverse=True)
        logging.info("Successfully completed graph endpoint execution")
        return result
    
    except Exception as e:
        logging.exception(f"Error in graph endpoint: {str(e)}")
        return {"message": "connection error"}, 500
    
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'connection' in locals(): connection.close()
        
# ********************************************************************************       
@app.get("/calender")
def calender():
    connection=get_connection()
    cursor=connection.cursor()
    try:
        owner="select Owner_ID, Owner_Name from login_team where category='client'"
        cursor.execute(owner)
        owners=cursor.fetchall()
        main=[]
        for i in owners:
            miles=f"select Milestone_Name, Milestones_Due_Date from project_milestones where Owner_ID={i['Owner_ID']}"
            cursor.execute(miles)
            data=cursor.fetchall()
            for date in data:
                today = datetime.today().strftime('%Y-%m') 
                milestone_due_date = datetime.strptime(date['Milestones_Due_Date'], '%Y-%m-%d').date()
                due = milestone_due_date.strftime('%Y-%m') == today 
                if due == True:
                    main.append({'Owner_Name':i['Owner_Name'],'Milestone_Name':date['Milestone_Name'],'Milestones_Due_Date':date['Milestones_Due_Date']})
        logging.info("Successfully completed calendar endpoint execution")
        return main
    
    except Exception as e:
        logging.exception(f"Error in calendar endpoint: {str(e)}")
        return {"message": "connection error"}, 500
    
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'connection' in locals(): connection.close()
        
# ********************************************************************************   
@app.get("/Miles_delayed")
def Miles_delayed():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        logging.info("Starting Miles_delayed endpoint execution")
        query = """
            SELECT 
                pm.Milestone_Name,
                p.Project_Name,
                p.Project_Owner_Name AS Owner,
                pm.Milestones_Due_Date AS Target_date,
                pm.Status,
                DATEDIFF(CURDATE(), STR_TO_DATE(pm.Milestones_Due_Date, '%Y-%m-%d')) AS Delayed_by
            FROM project_milestones pm
            JOIN projects p ON pm.Project_ID = p.Project_ID
            WHERE pm.Status IN ('Delayed')
              AND STR_TO_DATE(pm.Milestones_Due_Date, '%Y-%m-%d') < CURDATE()
            ORDER BY Delayed_by DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        delayed_milestones = []
        for row in rows:
            delayed_milestones.append({
                "Milestone_name": row["Milestone_Name"],
                "Project_name": row["Project_Name"],
                "Owner": row["Owner"],
                "Delayed_by": f"{row['Delayed_by']} days",
                "Target_date": row["Target_date"],
                "Status": row["Status"]
            })

        result = {
            "Delayed_count": str(len(delayed_milestones)),
            "Delayed_milestones": delayed_milestones
        }
        logging.info(f"Successfully processed {len(delayed_milestones)} delayed milestones")
        return result
    except Exception as e:
        logging.exception(f"Error in Miles_delayed endpoint: {str(e)}")
        return {"error": str(e)}, 500
    
    finally:
        if 'conn' in locals():
            conn.close()
           
# ********************************************************************************   
@app.get("/target")
def target():
    connection=get_connection()
    cursor=connection.cursor()
    try:
        target="""select DATE_FORMAT(Delivery_Date, '%b-%y') AS Month, COUNT(Project_ID) AS Total,
        SUM(CASE WHEN Project_Status = 'Closed' THEN 1 ELSE 0 END) AS Completed
        from projects WHERE Project_Status != 'Delayed' 
        AND Delivery_Date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
        GROUP BY YEAR(Delivery_Date),
        MONTH(Delivery_Date), Month ORDER BY YEAR(Delivery_Date) DESC, MONTH(Delivery_Date) DESC"""
        
        cursor.execute(target)
        data=cursor.fetchall()
        
        logging.info(f"Successfully retrieved {len(data)} records")
        return data
    
    except Exception as e:
        logging.exception(f"Error in target endpoint: {str(e)}")
        return {"message": "connection error"}, 500
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
           
# ********************************************************************************  
@app.get("/account_managers")
def account_managers():
    connection=get_connection()
    cursor=connection.cursor()
    try:
        owner="select * from login_team where category='Account_Manager'"
        cursor.execute(owner)
        data=cursor.fetchall()
        main=[]
        for i in data:
            total=f"select count(*) from projects where Account_Manager_ID={i['Owner_ID']} "
            cursor.execute(total)
            to=cursor.fetchall()

            op=f"select count(*) from projects where Account_Manager_ID={i['Owner_ID']} and (project_status='Open' or project_status='In progress' or project_status='Delayed')"
            cursor.execute(op)
            incom=cursor.fetchall()

            close=f"select count(*) from projects where Account_Manager_ID={i['Owner_ID']} and project_status='Closed'"
            cursor.execute(close)
            com=cursor.fetchall()
        
            main.append({'Owner_Name':i['Owner_Name'],'Email_ID': i['Email_ID'],'In progress':incom[0]['count(*)'],'Completed':com[0]['count(*)'],'Total':to[0]['count(*)']})
        result = sorted(main, key=lambda x: ( x['In progress'] > 0 or x['Completed'] > 0 or x['Total'] > 0), reverse=True)
        logging.info("Successfully completed graph endpoint execution")
        return result
    
    except Exception as e:
        logging.exception(f"Error in graph endpoint: {str(e)}")
        return {"message": "connection error"}, 500
    
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'connection' in locals(): connection.close()

# if __name__=="__main__":
#     uvicorn.run("main:app",host="0.0.0.0",port=8020)

scheduler = BackgroundScheduler(daemon=True)

job_id = 'check_delay_job'

if not any(job.id == job_id for job in scheduler.get_jobs()):
    # Schedule the job to run once at a specific time (14:33:05)
    scheduler.add_job(check_delay, 'cron', hour=23, minute=59, second=59, id=job_id, max_instances=1)
    print("Job scheduled successfully.")
else:
    print("Job is already scheduled.")

scheduler.start()

def shutdown_scheduler():
    scheduler.shutdown()
    sys.exit(0) 

signal.signal(signal.SIGINT, shutdown_scheduler)
signal.signal(signal.SIGTERM, shutdown_scheduler)

try:
    uvicorn.run(app, host="0.0.0.0", port=8020)

except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown() 