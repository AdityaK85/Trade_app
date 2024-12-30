import traceback
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string

##################### send html rendered email
# send attachment email
def send_attachment_email(subject, string, file_path, to_email, file_name):
	try:
		# from_email = settings.EMAIL_HOST_USER
		from_email = f'My Khabar24 <{settings.EMAIL_HOST_USER}>'
		email_msg = EmailMultiAlternatives(subject, string ,from_email, to_email)
		attachment = open(file_path, 'rb')
		email_msg.attach(file_name, attachment.read() , 'application/pdf')
		email_msg.attach_alternative(string, "text/html")
		email_msg.send() 
		return "success"
	except Exception as e:
		print(str(traceback.format_exc()))
		return "error"

'''
Function call
subject = "Thank you!"
string = render_to_string('r_t_s_html_file.html',{'context':context})
file_path = '/home/Khabar24/test.html'
to_email = ['testMail@gmail.com']
file_name = 'TestingFile'
email_status = send_email(subject, string, file_path, to_email, file_name)
'''

### send email with html
def send_html_email(subject, html_content, to_email, pdf_path=None):
    try:
        send_email_to = None
        if type(to_email) == list:
            send_email_to = to_email
        else:
            send_email_to = [to_email]

        for email in send_email_to:
            from_email = f'ALGO TRADE <{settings.EMAIL_HOST_USER}>'
            email_msg = EmailMultiAlternatives(subject, html_content, from_email, [email])

            # Attach HTML content
            email_msg.attach_alternative(html_content, "text/html")

            if pdf_path:
                # Attach PDF file	
                with open(pdf_path, 'rb') as pdf_file:
                    email_msg.attach(pdf_file.name, pdf_file.read(), 'application/pdf')
            email_msg.send()
        
        return "success"
    except Exception as e:
        print(str(traceback.format_exc()))
        return "error"
	
'''
Function call
subject = "Thank you!"
string = render_to_string('r_t_s_html_file.html',{'context':context})
to_email = 'testMail@gmail.com'
email_status = send_email(subject, string, to_email)
'''


#################### send normal email
def send_normal_email(subject, string, to_email_list):
	try:
		from_email = settings.EMAIL_HOST_USER
		email_msg = EmailMultiAlternatives(
        subject, string, from_email=from_email, to=[to_email_list])
		email_msg.attach_alternative(string)
		email_msg.mixed_subtype = 'related'
		email_msg.send()
		return	"success"
	except:
		traceback.print_exc()
		return "error"
'''

def send_normal_email(subject, message, to_email_list):
	try:
		from_email = settings.EMAIL_HOST_USER
		send_mail(subject, message, from_email, to_email_list)
		return	"success"
	except:
		traceback.print_exc()
		return "error"'''

'''
	subject = "Subject string"
	body = f"Message body"
	email_list = ['test@gmail.com']
	email_status = send_normal_email(subject, body, email_list)
'''


def Send_PaymentReceived_Message(user_obj,amount):
	print("-------------")	
	# send email or message when we received payment 
	username = user_obj.display_name if  user_obj.display_name else "User"
	if user_obj.email:
		subject = "Payment Received."
		body = render_to_string('website/email_rts/payment_received.html',{"username":username})
		to_email = user_obj.email
		pdf_path = "static/invoice/subscription.pdf"
		send_html_email(subject, body, to_email,pdf_path)
		
	
	# if user_obj.mobileno:
	# 	message = f"Hello {username},\nWe want to inform you that your payment of ₹{amount} for My Khabar24 subscription has been successfully processed. Thank you for choosing us!\nFor any assistance, contact our support at support@mykhabar24.com.\nBest regards,\nThe My Khabar24 Team"
	# 	SendMobileTextMessage(message,user_obj.mobileno)