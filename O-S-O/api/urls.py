from django.urls import path
from . import views

urlpatterns = [
    path("send-otp/", views.send_otp, name="send_otp"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("check-profile/", views.check_profile, name="check_profile"),  # ✅ 
    path("save-profile/", views.save_profile, name="save_profile"), 
     

]