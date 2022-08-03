import smtplib

def sendEmail( mailto, date, time, name, report ):
    gmailaddress = "doctorsbot13@gmail.com"
    gmailpassword = "vitalai@001"
    
    sub = "Confirmed: Doctor Appointment Booked"
    if (report == 0): report = "Checkup"
    msag = "Hey " + name + ",\n\nYour Appointment has been Successfully Booked with Dr. Abhishek Jani" + "\n\nDate : " + date + "\nTime : " + time + "\nProblem : " + report + "\n\nThank you for using our Services."
    msg = 'Subject: {}\n\n{}'.format(sub, msag)
    
    sub2 = "Appointment Booked with Doctor Abhishek Jani "+ " on "+ date
    msag2 = "Patient Email: "+ mailto + "\n\nReport: " + report
    msg2 = 'Subject: {}\n\n{}'.format(sub2, msag2)
    
    mailServer = smtplib.SMTP('smtp.gmail.com' , 587)
    mailServer.starttls()
    mailServer.login(gmailaddress , gmailpassword)
    mailServer.sendmail(gmailaddress, mailto , msg)
    print("--------------------\nUser Email Sent!\n--------------------")
    mailServer.sendmail(gmailaddress, gmailaddress , msg2)
    print("\n--------------------\nAdmin Email Sent!\n--------------------")
    mailServer.quit()
    return