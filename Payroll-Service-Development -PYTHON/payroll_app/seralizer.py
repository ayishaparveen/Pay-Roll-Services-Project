from rest_framework import serializers
from payroll_app.models import PayrollManagement, User
from payroll_app.models import Employer
from payroll_app.models import Position
from payroll_app.models import LeaveManage

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        
class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = '__all__'
        
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
class EmployerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'
        
class LeaveManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveManage
        fields = '__all__'
        
class LeaveApplySerializer(serializers.Serializer):
    date = serializers.DateField()
    user = serializers.IntegerField()
    
class UpdateStatusSerializer(serializers.Serializer):
    status = serializers.CharField()

class UserAnnualSalaryRevisionSerializer(serializers.Serializer):
    annual_salary = serializers.IntegerField()

class PayrollManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollManagement
        fields = '__all__'

class PayrollCalculationSerializer(serializers.Serializer):
    user = serializers.IntegerField()
    year = serializers.IntegerField()
    month = serializers.IntegerField()

















































