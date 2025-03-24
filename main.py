import uvicorn, os, json, uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import Optional
from connector import get_connection
from fastapi.middleware.cors import CORSMiddleware
import send_email, time
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
def check_delay():
    time.sleep(5)
    connection=get_connection()
    cursor=connection.cursor()
    try:   
        projects="""select Project_ID, Project_Name, Project_Owner_Email, Project_Owner_Name, Project_Date, Project_Status from projects """
        cursor.execute(projects)
        ids=cursor.fetchall()

        for id in ids:
            if (id["Project_Date"]) and (id["Project_Status"] != 'Closed'):
                expected_date = datetime.strptime(id["Project_Date"], "%Y-%m-%d")
                current_date = datetime.now()
                delay = (current_date - expected_date).days 
                if delay == 1:
                    status=f"""update projects set project_status='Delayed' where project_id='{id['Project_ID']}'"""
                    cursor.execute(status)
                    connection.commit()
                    cursor.close()
                    connection.close
                    print("Delayed by 1 day.")
                    send_email.project_delay_user(user_email=id["Project_Owner_Email"], user_name=id["Project_Owner_Name"], project_name=id["Project_Name"], delayed_days=delay, reason=None, project_url=None)
                    send_email.project_delay_admin(project_name=id["Project_Name"], user_email=id["Project_Owner_Email"], due_date=id["Project_Date"], timestamp='None', project_url='url',delay_days=delay, reason=None)
                elif delay == 3:
                    status=f"""update projects set project_status='Delayed' where project_id='{id['Project_ID']}'"""
                    cursor.execute(status)
                    connection.commit()
                    cursor.close()
                    connection.close
                    print("Delayed by 3 days.")
                    send_email.project_delay_user(user_email=id["Project_Owner_Email"], user_name=id["Project_Owner_Name"], project_name=id["Project_Name"], delayed_days=delay, reason=None, project_url=None)
                    send_email.project_delay_admin(project_name=id["Project_Name"], user_email=id["Project_Owner_Email"], due_date=id["Project_Date"], timestamp='None', project_url='url',delay_days=delay, reason=None)
                    
                elif delay == 7:
                    status=f"""update projects set project_status='Delayed' where project_id='{id['Project_ID']}'"""
                    cursor.execute(status)
                    connection.commit()
                    cursor.close()
                    connection.close
                    print(f"Delayed by {delay} days.")
                    send_email.project_delay_user(user_email=id["Project_Owner_Email"], user_name=id["Project_Owner_Name"], project_name=id["Project_Name"], delayed_days=delay, reason=None, project_url=None)
                    send_email.project_delay_admin(project_name=id["Project_Name"], user_email=id["Project_Owner_Email"], due_date=id["Project_Date"], timestamp='None', project_url='url',delay_days=delay, reason=None)
                elif delay == 15:
                    status=f"""update projects set project_status='Delayed' where project_id='{id['Project_ID']}'"""
                    cursor.execute(status)
                    connection.commit()
                    cursor.close()
                    connection.close
                    print(f"Delayed by {delay} days.")
                    send_email.project_delay_user(user_email=id["Project_Owner_Email"], user_name=id["Project_Owner_Name"], project_name=id["Project_Name"], delayed_days=delay, reason=None, project_url=None)
                    send_email.project_delay_admin(project_name=id["Project_Name"], user_email=id["Project_Owner_Email"], due_date=id["Project_Date"], timestamp='None', project_url='url',delay_days=delay, reason=None)
                elif delay > 0:
                    status=f"""update projects set project_status='Delayed' where project_id='{id['Project_ID']}'"""
                    cursor.execute(status)
                    connection.commit()
                    cursor.close()
                    connection.close
            else:
                pass
        check_due()
        milestone_delay()
    except:
        cursor.close()
        connection.close()
        return {"message":"connection error"}

# *******************************************************************************************

def check_due():
    connection=get_connection()
    cursor=connection.cursor()
    try:   
        projects="""select Project_Name, Project_Owner_Email,Project_Owner_Name, Project_Date, Project_Status from projects """
        cursor.execute(projects)
        ids=cursor.fetchall()

        for id in ids:
            if (id["Project_Date"]) and (id["Project_Status"] != 'Closed'):
                expected_date = datetime.strptime(id["Project_Date"], "%Y-%m-%d")
                current_date = datetime.now()

                reminder_date = expected_date - timedelta(days=2)
                
                if current_date.date() == reminder_date.date() :
                    send_email.due_reminder_user(user_email=id["Project_Owner_Email"], user_name=id["Project_Owner_Name"], project_name=id["Project_Name"], due_date=id["Project_Date"], project_url=None, days_remaining=2)
                    print("Reminder: Today is the expected date")
                if current_date.date() == expected_date.date():
                    send_email.due_reminder_user(user_email=id["Project_Owner_Email"], user_name=id["Project_Owner_Name"], project_name=id["Project_Name"], due_date=id["Project_Date"], project_url=None, days_remaining=0)
        cursor.close()
        connection.close
    except:
        cursor.close()
        connection.close()
        return {"message":"connection error"}
# *******************************************************************************************

def milestone_delay():
    connection=get_connection()
    cursor=connection.cursor()
    try:
        miles="""select MilestonesID, Milestones_Due_Date, Status from project_milestones """
        cursor.execute(miles)
        ids=cursor.fetchall()
        for id in ids:
            if (id["Milestones_Due_Date"]) and (id["Status"] != 'Closed'):
                expected_date = datetime.strptime(id["Milestones_Due_Date"], "%Y-%m-%d")
                current_date = datetime.now()
                delay = (current_date - expected_date).days 
                print(delay)
                if delay > 0:
                    status=f"""update project_milestones set status='Delayed' where MilestonesID='{id['MilestonesID']}'"""
                    cursor.execute(status)
                    connection.commit()
        cursor.close()
        connection.close()
    except:
        cursor.close()
        connection.close()
        return {"message":"connection error"}
                

# *******************************************************************************************
scheduler = BackgroundScheduler()
scheduler.add_job(check_delay, "cron", hour=23, minute=59, second=59)
scheduler.start()

# *******************************************************************************************
def project_staus(Project_ID):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql="""SELECT Status from project_milestones where Project_ID=%s"""
        cursor.execute(sql,(Project_ID,))
        results=cursor.fetchall()
        print(results)
        statuses = [row["Status"] for row in results]

        project_info=f"""select project_name, project_owner_name, last_edited_date from projects where project_id='{Project_ID}'"""
        cursor.execute(project_info)
        info=cursor.fetchall()
        if statuses and all(status == "Closed" for status in statuses):
            sql = "UPDATE projects SET Project_Status = 'Closed' WHERE Project_ID = %s"
            cursor.execute(sql, (Project_ID,))
            conn.commit()
            send_email.send_project_completed_email(info[0]["project_owner_name"], info[0]["project_name"], info[0]["last_edited_date"], project_url=None)
            return {"message": "Project status updated to Closed"}
        else:
            sql = "UPDATE projects SET Project_Status = 'In Progress' WHERE Project_ID = %s"
            cursor.execute(sql, (Project_ID,))
            conn.commit()
            return {"message": "Not all milestones are closed, project status unchanged"}
    finally:
        cursor.close()
        conn.close()
# *******************************************************************************************

@app.post("/project_creation")
async def project_creation(
    project_data: str = Form(...), 
    Documents_PO_Copy: Optional[UploadFile] = File(None), 
    Documents_BOM: Optional[UploadFile] = File(None)):

    project_dict = json.loads(project_data)
    files=[]
    connection = get_connection()
    cursor = connection.cursor()

    project_id=str(uuid.uuid4().hex)[:16]
    if Documents_PO_Copy:
        document_path = f"documents/{project_id}/Documents_PO_Copy/"
        os.makedirs(document_path, exist_ok=True)
        po_copy_path = os.path.join(document_path, Documents_PO_Copy.filename)
                
        with open(po_copy_path, "wb") as f:
            f.write(await Documents_PO_Copy.read()) 
        project_dict["Documents_PO_Copy"] = po_copy_path
        files.append(project_dict["Documents_PO_Copy"])
        
    if Documents_BOM:
        document = f"documents/{project_id}/Documents_BOM/"
        os.makedirs(document, exist_ok=True)
        bom_path = os.path.join(document, Documents_BOM.filename)
                
        with open(bom_path, "wb") as f:
            f.write(await Documents_BOM.read()) 
        project_dict["Documents_BOM"] = bom_path
        files.append(project_dict["Documents_BOM"])
    
    current_date=datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    query = """
    INSERT INTO projects (Project_Id,Project_Name, Project_Location, Project_Contract_Number, Project_Date, Project_Total_Value, 
                        Project_Capex, Project_Opex, Project_Owner_ID, Project_Owner_Name, Project_Owner_Email, 
                        Project_Scope, 
                        Customer_Contact_Person, Customer_Phone_Number, Customer_Email_Address, 
                        Customer_Fax_Number, Customer_Address, Documents_Del_Challan, Documents_Train_Cert,
                        Documents_PO_Copy,Documents_BOM,Project_Account_Manager,Account_Manager_ID,Account_Manager_Email,Created_date,Project_Status) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.execute(query, (project_id,
        project_dict["Project_Name"], project_dict["Project_Location"], project_dict["Project_Contract_Number"],
        project_dict["Project_Date"], project_dict["Project_Total_Value"], project_dict["Project_Capex"],
        project_dict["Project_Opex"], project_dict["Project_Owner_ID"], project_dict["Project_Owner_Name"],
        project_dict["Project_Owner_Email"], project_dict["Project_Scope"], project_dict["Customer_Contact_Person"],
        project_dict["Customer_Phone_Number"], project_dict["Customer_Email_Address"], project_dict["Customer_Fax_Number"],
        project_dict["Customer_Address"], project_dict["Documents_Del_Challan"], project_dict["Documents_Train_Cert"],
        project_dict["Documents_PO_Copy"],project_dict["Documents_BOM"],project_dict["Project_Account_Manager"],project_dict["Account_Manager_ID"],project_dict["Account_Manager_Email"],current_date,'Open'))
    connection.commit()
   
    if "Milestone" in project_dict and isinstance(project_dict["Milestone"], list):
        milestone_query = """
        INSERT INTO project_milestones 
        (Project_ID, Owner_ID, Milestone_Name, Milestones_Due_Date, Milestones_T_Days, 
        Pay_Milestone, Percentage_Payment, Amount, status) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """        
        milestone_values = []
        for milestone in project_dict["Milestone"]:
            milestone_values.append((
                project_id,
                project_dict.get("Project_Owner_ID"), 
                milestone.get("Milestone_Name"),
                milestone.get("Milestones_Due_Date"),
                milestone.get("Milestones_T_Days"),
                milestone.get("Pay_Milestone"),
                milestone.get("Percentage_Payment"),
                milestone.get("Amount"),
                'Open'))
                
        if milestone_values: 
            cursor.executemany(milestone_query, milestone_values)
            connection.commit()        
        cursor.close()
        connection.close()
         
        send_email.allocation(project_dict["Project_Name"], project_dict["Project_Owner_Name"], project_dict["Project_Owner_Email"], project_dict["Project_Scope"], project_dict["Project_Date"], "task_url", files)
        return {"message": "Project, milestones, and documents inserted successfully!"}

# *******************************************************************************************
@app.get("/all_team")
async def get_team():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT Owner_ID,Owner_Name,Email_ID,Category FROM login_team"
            cursor.execute(sql)
            team=cursor.fetchall()
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
            return {
                "admin": admin_data,
                "client": client_data,
                "account_manager": account_manager_data}
    finally:
        conn.close()
# ********************************************************************************
        
@app.put("/edit_project/{project_id}")
async def edit_project(project_id:str, project_details: str = Form (...)):
    connection=get_connection()
    cursor=connection.cursor()
    project_details= json.loads(project_details)
    try:
        sql=f"""update projects set project_location='{project_details['Project_Location']}',
        Project_Contract_Number='{project_details['Project_Contract_Number']}', 
        project_total_value='{project_details['Project_Total_Value']}', project_capex='{project_details['Project_Capex']}', 
        Project_Opex='{project_details['Project_Opex']}', project_scope='{project_details['Project_Scope']}' where project_id='{project_id}'"""
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        connection.close()
        return {"message":"Project Edited successfully"}
    except:
        cursor.close()
        connection.close()
        return {"message":"Project not edited"}
    
# ********************************************************************************
@app.put("/edit_customer_details/{project_id}")
async def edit_customer_details(project_id:str, customer_details:str=Form(...) ):
    connection=get_connection()
    cursor=connection.cursor()
    customer_details= json.loads(customer_details)
    try:
        sql=f"""update projects set Customer_Contact_Person='{customer_details['Customer_Contact_Person']}',
        Customer_Phone_Number='{customer_details['Customer_Phone_Number']}', 
        Customer_Email_Address='{customer_details['Customer_Email_Address']}', Customer_Fax_Number='{customer_details['Customer_Fax_Number']}', 
        Customer_Address='{customer_details['Customer_Address']}' where project_id='{project_id}'"""
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        connection.close()
        return {"message":"Customer details Edited successfully"}
    except:
        cursor.close()
        connection.close()
        return {"message":"Customer details not edited"}
    
# ********************************************************************************    
@app.post("/add_member/{name}/{email}/{category}")
def add_member(name:str, email:str, category:str):
    connection=get_connection()
    cursor=connection.cursor()
    try:
        query = "INSERT INTO login_team (owner_name, email_id, category) VALUES (%s, %s, %s)"
        cursor.execute(query, (name, email, category))
        connection.commit()
        cursor.close()
        connection.close()
        try:
            status=send_email.send_welcome_email(user_email=email, user_name=name, login_url=None)
            if status==1:
                return {"message":"Team member added successfully"}    
            else:
                return {"message":"Please check email id"}
        except:
            pass
    except:
        cursor.close()
        connection.close()
        return {"message":"Team member name or email already exist"}
    
# ********************************************************************************
@app.delete("/delete_member/{member_id}")
def delete_member(member_id:int):
    connection=get_connection()
    cursor=connection.cursor()
    try:    
        project=f"select project_name from projects where project_owner_id={member_id}"
        cursor.execute(project)
        num=cursor.fetchall()
        if len(num) == 0:
            sql=f"delete from login_team where owner_id ={member_id}"
            cursor.execute(sql)
            connection.commit()
            cursor.close()
            connection.close()
            return {"message":"Team member removed successfully"}
        else:
            cursor.close()
            connection.close()
            return {"message":"Please assign the project to another owner"}
    except:
        cursor.close()
        connection.close()
        return {"message":"Team member not removed"}

# ********************************************************************************
@app.put("/edit_member/{Owner_ID}")
async def edit_member(Owner_ID:int,login_details:str=Form(...) ):
    connection=get_connection()
    cursor=connection.cursor()
    try:
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
        return {"message": "Login team details edited successfully"}
    except:
        cursor.close()
        connection.close()
        return {"message":"Login_team details not edited"}
    
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
            # project_staus(Project_ID)
        else:
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
            project_staus(Project_ID)
        conn.close()
        return {"message": "Milestone status updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ********************************************************************************
@app.get("/bubbles")
def bubbles():
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
            count=cursor.fetchall()
            main.append({'Owner_Name': i['Owner_Name'], 'Email_ID': i['Email_ID'], 'Count': count[0]['count(*)']})        
        return main
    except:
        cursor.close()
        connection.close()
        return {"message":"connection error"}
    
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
            inpro=f"select count(*) from project_milestones where Owner_ID={i['Owner_ID']} and status='In progress' or status='Open'"
            cursor.execute(inpro)
            inprogress=cursor.fetchall()
            close=f"select count(*) from project_milestones where Owner_ID={i['Owner_ID']} and status='Closed'"
            cursor.execute(close)
            closed=cursor.fetchall()
            delay=f"select count(*) from project_milestones where Owner_ID={i['Owner_ID']} and status='Delayed'"
            cursor.execute(delay)
            delayed=cursor.fetchall()
            main.append({'Owner_Name':i['Owner_Name'],'Email_ID': i['Email_ID'],'In progress':inprogress[0]['count(*)'],'Completed':closed[0]['count(*)'],'Delayed':delayed[0]['count(*)']})
        return main
    except:
            cursor.close()
            connection.close()
            return {"message":"connection error"}
        
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
        return main
    except :
            cursor.close()
            connection.close()
            return {"message":"connection error"}
    
if __name__=="__main__":
  
    uvicorn.run("main:app",host="0.0.0.0",port=8020)