from calendar import monthrange
import datetime
from django.shortcuts import render
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import status
from datetime import date
from django.core.mail import send_mail
import smtplib
from django.conf import settings
import calendar
from .models import current_year, year_choices



from rest_framework import viewsets

from payroll_app.models import PayrollManagement, User
from payroll_app.seralizer import PayrollCalculationSerializer, PayrollManagementSerializer, UserSerializer,UserAnnualSalaryRevisionSerializer

from payroll_app.models import Employer
from payroll_app.seralizer import EmployerSerializer

from payroll_app.models import Position
from payroll_app.seralizer import PositionSerializer

from payroll_app.seralizer import UserLoginSerializer

from payroll_app.seralizer import EmployerLoginSerializer
# from payroll_app.seralizers import VerifyUsersByIdSerializer

from payroll_app.models import LeaveManage
from payroll_app.seralizer import LeaveManageSerializer
from payroll_app.seralizer import LeaveApplySerializer

from payroll_app.seralizer import UpdateStatusSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class EmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer
    
class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    
class PositionViewSet(viewsets.ModelViewSet):
    queryset = LeaveManage.objects.all()
    serializer_class = LeaveManageSerializer

class PayrollManagementViewSet(viewsets.ModelViewSet):
    queryset = PayrollManagement.objects.all()
    serializer_class = PayrollManagementSerializer


    

@swagger_auto_schema(methods=['post'], request_body=UserSerializer) 
@api_view(['POST'])
def user_signup(request): 
    if request.method == 'POST': 
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(): 
            # employer = serializer.save(password=make_password(serializer.validated_data))
            user = serializer.save()
            return Response({'payload': 'registration successfull'}, status=status.HTTP_201_CREATED)
        return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
@swagger_auto_schema(methods=['post'],request_body=UserLoginSerializer)
@api_view(['POST'])
def user_login(request):
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.get(email = email)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        if user:
            if user.verified:
                if user.password == password:
                    return Response({'payload': 'Login successful'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'error': 'User is not verified'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    
@swagger_auto_schema(methods=['post'], request_body=EmployerSerializer) 
@api_view(['POST'])
def employer_signup(request): 
    if request.method == 'POST': 
        serializer = EmployerSerializer(data=request.data)
        if serializer.is_valid(): 
            # employer = serializer.save(password=make_password(serializer.validated_data))
            employer = serializer.save()
            return Response({'payload': 'registration successfull'}, status=status.HTTP_201_CREATED)
        return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    

@swagger_auto_schema(methods=['post'],request_body=EmployerLoginSerializer)
@api_view(['POST'])
def employer_login(request):
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        employer = Employer.objects.get(email = email)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        if employer:
            if employer.password == password:
                return Response({'payload': 'Login successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            # Employer does not exist
            return Response({'error': 'Employer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
@swagger_auto_schema(methods=['get'])
@api_view(['GET'])
def get_verified_users(request):
    if request.method == 'GET':
        # Query the User table to retrieve verified users
        verified_users = User.objects.filter(verified=True)

        # Serialize the retrieved data
        serializer = UserSerializer(verified_users, many=True)

        # Return the serialized data as a response
        return Response(serializer.data, status=status.HTTP_200_OK)
    
@swagger_auto_schema(methods=['get'])
@api_view(['GET'])
def get_unverified_users(request):
    if request.method == 'GET':
        # Query the User table to retrieve verified users
        unverified_users = User.objects.filter(verified=False)

        # Serialize the retrieved data
        serializer = UserSerializer(unverified_users, many=True)

        # Return the serialized data as a response
        return Response(serializer.data, status=status.HTTP_200_OK)
    
@swagger_auto_schema(methods=['put'], request_body= UserAnnualSalaryRevisionSerializer )
@api_view(['PUT'])
def verify_users_by_id(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if user.verified == False:
        serializer=UserAnnualSalaryRevisionSerializer(data=request.data)
        if serializer.is_valid():
            user.verified = True 
            user.annual_salary = serializer._validated_data['annual_salary'] 
            user.save()
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response("User already verified", status=status.HTTP_400_BAD_REQUEST)

    
    
    
    
        
        
@swagger_auto_schema(methods=['post'],request_body=LeaveApplySerializer)
@api_view(['POST'])
def leave_apply(request):
    if request.method == 'POST':
        serializer = LeaveManageSerializer(data=request.data)
        if serializer.is_valid():
            user = request.data.get('user')
            entered_date = serializer.validated_data['date']
            leaves_data = User.objects.get(pk = user)
            
            leave_exists = LeaveManage.objects.filter(user = user, date = entered_date).exists()
            
            if leaves_data.verified:
                
                if entered_date < date.today():
                    return Response(
                        {'detail': 'Leave cannot be applied for past dates'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
                if leaves_data.leaves <= 0:
                    return Response({'detail': 'user has no leaves left'},status=status.HTTP_400_BAD_REQUEST)
                    
                if leave_exists:
                    return Response(
                        {'detail': 'Record already exists for this user with the same date and status'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
                serializer.save()  # Save the new leave application
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response({'detail': 'user is not verified yet'},status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
@swagger_auto_schema(methods=['get'])
@api_view(['GET'])  
def get_approved_leave_manage(request):
    if request.method == 'GET':
        approved_users = LeaveManage.objects.filter(status = "approved")
        serializer = LeaveManageSerializer(approved_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({'payload': 'NO DATA'}, status=status.HTTP_200_OK)

@swagger_auto_schema(methods=['get'])
@api_view(['GET'])  
def get_pending_leave_manage(request):
    if request.method == 'GET':
        pending_users = LeaveManage.objects.filter(status = "pending")
        serializer = LeaveManageSerializer(pending_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({'payload': 'NO DATA'}, status=status.HTTP_200_OK)

@swagger_auto_schema(methods=['get'])
@api_view(['GET'])  
def get_rejected_leave_manage(request):
    if request.method == 'GET':
        rejected_users = LeaveManage.objects.filter(status = "rejected")
        serializer = LeaveManageSerializer(rejected_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({'payload': 'NO DATA'}, status=status.HTTP_200_OK)

def send_leave_email(user_email, status_recieved):
    subject = f'Leave Request {status_recieved}'
    message = f'Your Leave Request have been {status_recieved}! Thank You for your patience.'
    from_mail = settings.EMAIL_HOST_USER
    html_message = f"""
    <!Doctype html>
    <html lang ="en">
    <head>
        <meta charset = "UTF-8">
        <title> Leave Request {status_recieved} </title>
    
    </head>
    <body>
        <h1> Your Leave Request has been {status_recieved}! </h1>
        <p>Thank You for your patience.</p>
    </body>
    </html>
    """
    send_mail(subject, message, from_mail, [user_email], html_message = html_message)
    return Response({'message': 'Email sent'}, status=status.HTTP_200_OK)
    
@swagger_auto_schema(methods=['patch'], request_body=UpdateStatusSerializer)
@api_view(['PATCH']) 
def update_leave_status(request, user_id):
    try:
        leave_status = request.data.get('status')
        leaves_data = LeaveManage.objects.get(pk = user_id)
    except LeaveManage.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PATCH':
        if leave_status not in ['approved', 'rejected', 'pending']:
            return Response({'It is not a valid choice'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = LeaveManageSerializer(leaves_data, data=request.data, partial = True)
        if serializer.is_valid(): 
            user = leaves_data.user
            status_value = serializer.validated_data.get('status')
            
            if status_value == 'approved':
                if user.leaves > 0:
                    user.leaves -= 1
                    user.save()
                    send_leave_email(user.email, "Approved")
                else: 
                    return Response({"detail" : "User does not have enough leaves"}, status=status.HTTP_400_BAD_REQUEST)
            
            elif status_value == 'rejected':
                send_leave_email(user.email, "Rejected")
            
        
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(methods=['post'],request_body=LeaveApplySerializer)
@api_view(['POST'])
def loss_of_pay(request):
    if request.method == 'POST':
        serializer = LeaveManageSerializer(data=request.data)
        if serializer.is_valid():
            user = request.data.get('user')
            entered_date = serializer.validated_data['date']
            leaves_data = User.objects.get(pk = user)
            
            leave_exists = LeaveManage.objects.filter(user = user, date = entered_date).exists()
            
            if leaves_data.verified:
                if leaves_data.leaves == 0:
                    
                    if entered_date < date.today():
                        return Response(
                            {'detail': 'Leave cannot be applied for past dates'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                        
                    if leave_exists:
                        return Response(
                            {'detail': 'Record already exists for this user with the same date and status'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                        
                    serializer.save()  # Save the new leave application
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                
                return Response({'detail': 'user still have leaves left, go apply normally'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'user is not verified yet'},status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(methods=['put'], request_body=UserAnnualSalaryRevisionSerializer)
@api_view(['PUT'])
def user_annual_salary_revision(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)
    
    if not user.verified:
        return Response("User is not verified", status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'PUT':
        serializer=UserAnnualSalaryRevisionSerializer(data=request.data)
        if serializer.is_valid(): 
            user.annual_salary = serializer._validated_data['annual_salary'] 
            user.save()
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)  
    
        
    
@swagger_auto_schema(methods=['post'], request_body=PayrollCalculationSerializer)
@api_view(['POST'])
def payroll_calculation(request):
    try:
        serializer = PayrollCalculationSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user']
            user = User.objects.get(pk=user_id)
            year = serializer.validated_data['year']
            month = serializer.validated_data['month']
            # leaves_data = User.objects.get(pk = user)
            
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if user.verified:
        
        valid_years = year_choices()
        current_year_val = current_year()
        current_month = datetime.date.today().month
            
        if year not in [yr[0] for yr in valid_years]:  
            return Response({'error': 'Entered year is not a valid choice'},status=status.HTTP_400_BAD_REQUEST)
        elif year == current_year_val and month >= current_month:
            return Response({'error': 'Cannot calculate payroll for current or future months'},status=status.HTTP_400_BAD_REQUEST)
            
        monthly_salary = user.annual_salary / 12
        provident_fund = monthly_salary * 0.04
        
        if monthly_salary <= 7500:
            professional_tax = 0
        elif 7501 <= monthly_salary <= 10000:
            professional_tax = 175
        else:
            professional_tax = 200
            
        num_days_in_month = calendar.monthrange(year, month)[1]
        
        net_salary = monthly_salary - provident_fund - professional_tax
        
        pay_per_day = net_salary / num_days_in_month
        
        loss_of_pay = 0
        
        if user.leaves <= 0:
            loss_of_pay = user.leaves * pay_per_day
            
        net_salary += loss_of_pay
        
        serializer = PayrollManagementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['gross_salary'] = "{:.2f}".format(monthly_salary)
            serializer.validated_data['provident_fund'] = "{:.2f}".format(provident_fund)
            serializer.validated_data['professional_tax'] = "{:.2f}".format(professional_tax)
            serializer.validated_data['net_salary'] = "{:.2f}".format(net_salary)
            serializer.validated_data['loss_of_pay'] = "{:.2f}".format(loss_of_pay)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        return Response("User is not verified", status=status.HTTP_400_BAD_REQUEST)
    

    
    




























































