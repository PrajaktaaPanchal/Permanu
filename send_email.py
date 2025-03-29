import  os,configparser, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

config = configparser.ConfigParser()
config.read('configurator.yml')

def server_conn(toMail):
    if "MailServer" in config:
        config.set("MailServer", "toMail", toMail) 

        with open("configurator.ini", "w") as file:
            config.write(file)
        print("INI file updated successfully!")
    else:
        print("Error: Section [MailServer] not found in the INI file.")

    if 'MailServer' in config:
        MailServer = config['MailServer']
        userid = MailServer['userid']
        passcode = MailServer['passcode']
    return(userid,passcode)

# *****************************************************************************************
def smtp_conn(message,toMail):
    userid,passcode=server_conn(toMail)
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(userid, passcode)
            smtp.send_message(message)
        print(f"Email sent to {toMail} successfully.")
    except:
        print("Unable to generate mail connection.")
# *****************************************************************************************

def send_welcome_email(user_email, user_name, login_url):
    subject = "🎉 Welcome to Our Platform!"

    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to Our Platform</title>
        <style type="text/css">
            body {{
                font-family: Arial, sans-serif;
                background-color: #f5f8fa;
                margin: 0;
                padding: 0;
            }}
            .email-container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background-color: #00A4BD;
                color: white;
                text-align: center;
                padding: 20px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-size: 24px;
                font-weight: bold;
            }}
            .content {{
                padding: 20px;
                font-size: 16px;
                color: #333333;
            }}
            .button {{
                display: block;
                text-align: center;
                background-color: #00A4BD;
                color: white;
                padding: 12px;
                text-decoration: none;
                font-size: 16px;
                border-radius: 5px;
                margin: 20px auto;
                width: 50%;
            }}
            .footer {{
                text-align: center;
                font-size: 12px;
                color: #777777;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                🎉 Welcome to Our Platform!
            </div>
            <div class="content">
                <p>Hello <strong>{user_name}</strong>,</p>
                <p>You have been successfully added to our platform by an administrator.</p>
                
                <p>Please log in and check as soon as possible.</p>
                <a href="{login_url}" class="button">Login Now</a>
                <p style="font-size: 12px; color: #777;">If you did not expect this email, please contact the administrator.</p>
            </div>
            <div class="footer">
                &copy; 2025 Our Platform. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
    status=0
    try:
        admin_email="prajakta.p@pelorus.in"
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = "prajakta.p@pelorus.in"
        message['To'] = user_email
        message.attach(MIMEText(body.encode('utf-8').decode('utf-8'), "html", "utf-8"))
        smtp_conn(message,user_email)
        status=1
        return status
    except Exception as e:
        return status

def allocation(project_name, user_name, user_email, description, due_date, task_url, files):
    subject = f"📌 New Project Assigned: {project_name}"
    body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>New Project Assigned</title>
                <style type="text/css">
                    body {{ font-family: Arial, sans-serif; background-color: #f5f8fa; margin: 0; padding: 0; }}
                    .email-container {{ max-width: 600px; margin: 20px auto; background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); }}
                    .header {{ background-color: #00A4BD; color: white; text-align: center; padding: 20px; border-top-left-radius: 10px; border-top-right-radius: 10px; font-size: 24px; font-weight: bold; }}
                    .content {{ padding: 20px; font-size: 16px; color: #333333; }}
                    .task-info {{ background-color: #f1f1f1; padding: 15px; border-radius: 5px; margin: 15px 0; font-size: 14px; }}
                    .button {{ display: block; text-align: center; background-color: #00A4BD; color: white; padding: 12px; text-decoration: none; font-size: 16px; border-radius: 5px; margin: 20px auto; width: 50%; }}
                    .footer {{ text-align: center; font-size: 12px; color: #777777; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="header">
                        📌 New Project Assigned!
                    </div>
                    <div class="content">
                        <p>Hello <strong>{user_name}</strong>,</p>
                        <p>A new project has been assigned to you by Admin.</p>
                        <div class="task-info">
                            <p><strong>Project Name:</strong> {project_name}</p>
                            <p><strong>Description:</strong> {description}</p>
                            <p><strong>Due Date:</strong> {due_date}</p>
                        </div>
                        <p>Please log in to review and complete your task.</p>
                        <a href="{task_url}" class="button">View Task</a>
                        <p style="font-size: 14px; color: #777;">Note: If you have any questions, please contact your administrator.</p>
                    </div>
                    <div class="footer">
                        &copy; 2025 Task Management System. All rights reserved.
                    </div>
                </div>
            </body>
            </html>
            """

    try:
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = "prajakta.p@pelorus.in"
        message['To'] = user_email
        message.attach(MIMEText(body.encode('utf-8').decode('utf-8'), "html", "utf-8"))
            
        if len(files)> 0:
            for file in files:
                filename = os.path.basename(file) 
                with open(file, 'rb') as f:
                    attachment = MIMEApplication(f.read(), Name=filename)  
                    attachment.add_header('Content-Disposition', 'attachment', filename=filename) 
                    message.attach(attachment)
        else:
            pass
        return (smtp_conn(message,user_email))
    
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# *****************************************************************************************

def project_delay_admin( project_name, user_email, due_date, timestamp, project_url,delay_days, reason=None):
    delay_text = f"{delay_days} day(s) delayed" if delay_days > 0 else "Due today"

    subject = f"🚨 Project Delayed Alert: {project_name} ({delay_text})"
    reason_section = f"""
        <div class="status-box" style="background: #fff3cd; color: #856404;">
            <p><strong>Reason for Delay:</strong> {reason}</p>
        </div>
    """ if reason else ""

    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🚨 Project Delayed Alert</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f5f8fa;
                padding: 20px;
                text-align: center;
            }}
            .email-container {{
                max-width: 600px;
                margin: auto;
                background: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: #00A4BD;
                color: #fff;
                padding: 20px;
                text-align: center;
                font-size: 20px;
                font-weight: bold;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                padding: 20px;
                color: #333;
                font-size: 16px;
            }}
            .status-box {{
                background: #ffe6e6;
                padding: 15px;
                border-radius: 5px;
                margin: 15px 0;
                font-size: 14px;
                font-weight: bold;
                color: red;
            }}
            .button {{
                display: block;
                text-align: center;
                background: #00A4BD;
                color: white;
                padding: 12px;
                text-decoration: none;
                font-size: 16px;
                border-radius: 5px;
                margin: 20px auto;
                width: 50%;
            }}
            .footer {{
                text-align: center;
                font-size: 12px;
                color: #777;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">🚨 Project Delayed Alert!</div>
            <div class="content">
                <p>Hello <strong>Admin</strong>,</p>
                <p>The project <strong>{project_name}</strong>, assigned to <strong>{user_email}</strong>, has been <span style="color: red; font-weight: bold;">delayed</span>.</p>
                <div class="status-box">
                    <p><strong>Status:</strong> Delayed</p>
                    <p><strong>Due Date:</strong> {due_date} ({delay_text})</p>
                    <p><strong>Last Updated:</strong> {timestamp}</p>
                </div>
                {reason_section}
                <p>Please log in to review and take necessary action.</p>
                <a href="{project_url}" class="button">View Project</a>
                <p style="font-size: 12px; color: #777;">If you have any questions, please contact the user.</p>
            </div>
            <div class="footer">
                &copy; 2025 Project Management System. All rights reserved.
            </div>
    </body>
    </html>
    """
    try:
        admin_email="prajakta.p@pelorus.in"
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = "prajakta.p@pelorus.in"
        message['To'] = admin_email
        message.attach(MIMEText(body.encode('utf-8').decode('utf-8'), "html", "utf-8"))

        return(smtp_conn(message,admin_email))
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# *****************************************************************************************
def project_delay_user(user_email, user_name, project_name, delayed_days, reason, project_url):
    subject = f"⚠️ Project Delay Notification: {project_name}"
    reason_html = f"<p><strong>Reason for Delay:</strong> {reason}</p>" if reason else ""
    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Project Delay Notification</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f8f8f8;
                margin: 0;
                padding: 0;
            }}
            .email-container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background-color: #00A4BD;
                color: white;
                text-align: center;
                padding: 20px;
                border-radius: 10px 10px 0 0;
                font-size: 22px;
                font-weight: bold;
            }}
            .content {{
                padding: 20px;
                font-size: 16px;
                color: #333333;
                text-align: center;
            }}
            .status-box {{
                background: #FFDDCC;
                padding: 15px;
                border-radius: 5px;
                margin: 15px 0;
                font-size: 16px;
                font-weight: bold;
                color: red;
            }}
            .button {{
                display: block;
                text-align: center;
                background-color: #00A4BD;
                color: white;
                padding: 12px;
                text-decoration: none;
                font-size: 16px;
                border-radius: 5px;
                margin: 20px auto;
                width: 50%;
            }}
            .footer {{
                text-align: center;
                font-size: 12px;
                color: #777777;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                ⚠️ Project Delayed
            </div>
            <div class="content">
                <p>Hello <strong>{user_name}</strong>,</p>
                <p>Your project <strong>{project_name}</strong> has been delayed by <strong>{delayed_days} days</strong>.</p>
                <div class="status-box">
                    Project Delay: {delayed_days} days
                </div>
                {reason_html}
                <p>Please review the project and take necessary actions.</p>
                <a href="{project_url}" class="button">View Project</a>
                <p style="font-size: 12px; color: #777;">If you have any questions, please contact the administrator.</p>
            </div>
            <div class="footer">
                &copy; 2025 Project Management System. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
    status=0
    try:
        admin_email="prajakta.p@pelorus.in"
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = "prajakta.p@pelorus.in"
        message['To'] = user_email
        message.attach(MIMEText(body.encode('utf-8').decode('utf-8'), "html", "utf-8"))
        smtp_conn(message,user_email)
        status=1
        return status
    except Exception as e:
        return status
    
# *****************************************************************************************
def due_reminder_user(user_email, user_name, project_name, due_date, project_url, days_remaining):
    if days_remaining == 2:
        subject = f"⏳ Reminder: {project_name} is due in 2 days!"
        due_message = f"Your project <strong>{project_name}</strong> is due in <strong>2 days</strong>. Please ensure all work is completed on time."
    elif days_remaining == 0:
        subject = f"⚠️ Urgent: {project_name} is due today!"
        due_message = f"Your project <strong>{project_name}</strong> is due <strong>today</strong>. Please submit it as soon as possible."
    else:
        return 

    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Project Due Reminder</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f8f8f8;
                margin: 0;
                padding: 0;
            }}
            .email-container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background-color: #00A4BD;
                color: white;
                text-align: center;
                padding: 20px;
                border-radius: 10px 10px 0 0;
                font-size: 22px;
                font-weight: bold;
            }}
            .content {{
                padding: 20px;
                font-size: 16px;
                color: #333333;
                text-align: center;
            }}
            .status-box {{
                background: #FFF5CC;
                padding: 15px;
                border-radius: 5px;
                margin: 15px 0;
                font-size: 16px;
                font-weight: bold;
                color: #FF8800;
            }}
            .button {{
                display: block;
                text-align: center;
                background-color: #00A4BD;
                color: white;
                padding: 12px;
                text-decoration: none;
                font-size: 16px;
                border-radius: 5px;
                margin: 20px auto;
                width: 50%;
            }}
            .footer {{
                text-align: center;
                font-size: 12px;
                color: #777777;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                ⏳ Project Due Reminder
            </div>
            <div class="content">
                <p>Hello <strong>{user_name}</strong>,</p>
                <p>{due_message}</p>
                <div class="status-box">
                    Due Date: <strong>{due_date}</strong>
                </div>
                <p>Please review your project and complete it before the deadline.</p>
                <a href="{project_url}" class="button">View Project</a>
                <p style="font-size: 12px; color: #777;">If you have any questions, please contact the administrator.</p>
            </div>
            <div class="footer">
                &copy; 2025 Project Management System. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
    status=0
    try:
        admin_email="prajakta.p@pelorus.in"
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = "prajakta.p@pelorus.in"
        message['To'] = user_email
        message.attach(MIMEText(body.encode('utf-8').decode('utf-8'), "html", "utf-8"))
        smtp_conn(message,user_email)
        status=1
        return status
    except Exception as e:
        return status
# *****************************************************************************************

def send_project_completed_email( user_name, project_name, completed_date, project_url):
    subject = f"🎉 Project Completed: {project_name}"

    # HTML Email Body
    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Project Completion Notification</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f8f8f8;
                margin: 0;
                padding: 0;
            }}
            .email-container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background-color: #00A4BD;
                color: white;
                text-align: center;
                padding: 20px;
                border-radius: 10px 10px 0 0;
                font-size: 22px;
                font-weight: bold;
            }}
            .content {{
                padding: 20px;
                font-size: 16px;
                color: #333333;
                text-align: center;
            }}
            .status-box {{
                background: #D4EDDA;
                padding: 15px;
                border-radius: 5px;
                margin: 15px 0;
                font-size: 16px;
                font-weight: bold;
                color: #155724;
            }}
            .button {{
                display: block;
                text-align: center;
                background-color: #00A4BD;
                color: white;
                padding: 12px;
                text-decoration: none;
                font-size: 16px;
                border-radius: 5px;
                margin: 20px auto;
                width: 50%;
            }}
            .footer {{
                text-align: center;
                font-size: 12px;
                color: #777777;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                🎉 Project Completed Successfully!
            </div>
            <div class="content">
                <p>Hello <strong>Admin</strong>,</p>
                <p>The project <strong>{project_name}</strong> has been successfully completed by <strong>{user_name}</strong>.</p>
                <div class="status-box">
                    Completion Date: <strong>{completed_date}</strong>
                </div>
                <p>Please review and archive the project if necessary.</p>
                <a href="{project_url}" class="button">View Project</a>
                <p style="font-size: 12px; color: #777;">If you have any questions, please contact the user.</p>
            </div>
            <div class="footer">
                &copy; 2025 Project Management System. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
    try:
        admin_email="prajakta.p@pelorus.in"
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = "prajakta.p@pelorus.in"
        message['To'] = admin_email
        message.attach(MIMEText(body.encode('utf-8').decode('utf-8'), "html", "utf-8"))

        return(smtp_conn(message,admin_email))
    except Exception as e:
        print(f"❌ Error sending email: {e}")
