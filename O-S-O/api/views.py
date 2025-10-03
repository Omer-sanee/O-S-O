# api/views.py
# from django.core.mail import send_mail   # ❌ remove this
from .email_utils import send_otp_email, generate_otp  # ✅ add thisfrom django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json, random, redis
from django.contrib.auth.models import User
from .models import UserProfile
import redis
import os

# Use the environment variable REDIS_URL from Render
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
redis_client = redis.from_url(REDIS_URL)

# Redis connection
@csrf_exempt
@require_POST
def send_otp(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        phone = data.get('phone')
        
        if not email or not phone:
            return JsonResponse({'error': 'Email and phone are required'}, status=400)

        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Prevent duplicate phone
        if UserProfile.objects.filter(phone=clean_phone).exclude(user__email=email).exists():
            return JsonResponse({'error': 'Phone already registered'}, status=400)

        otp = generate_otp()
        # ⏱ Store OTP + phone in Redis with 2 minutes (120 seconds) expiry
        redis_client.setex(f'otp:{email}', 120, otp)
        redis_client.setex(f'phone:{email}', 120, clean_phone)

        # Send OTP email
        # Send OTP email (beautiful HTML)
        send_otp_email(email, otp, clean_phone)

        return JsonResponse({'message': 'OTP sent successfully'})
    except Exception as mail_error:
        print(f"⚠️ Failed to send OTP email: {mail_error}")
        return JsonResponse({'error': str(mail_error)}, status=500)


@csrf_exempt
@require_POST
def verify_otp(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        otp = data.get('otp')

        if not email or not otp:
            return JsonResponse({'error': 'Email and OTP are required'}, status=400)

        stored_otp = redis_client.get(f'otp:{email}')
        stored_phone = redis_client.get(f'phone:{email}')

        if not stored_otp or stored_otp.decode() != otp:
            return JsonResponse({'error': 'Invalid OTP'}, status=400)

        clean_phone = stored_phone.decode() if stored_phone else ''

        user, created = User.objects.get_or_create(
            email=email,
            defaults={'username': email}
        )
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={'phone': clean_phone}
        )
        profile.phone = clean_phone
        profile.save()

        redis_client.delete(f'otp:{email}')
        redis_client.delete(f'phone:{email}')

        return JsonResponse({
            'message': 'OTP verified successfully',
            'user_id': user.id,
            'email': user.email,
            'phone': clean_phone,
            'is_new_user': created
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def check_profile(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        phone = data.get('phone')
        
        if not email or not phone:
            return JsonResponse({'error': 'Email and phone are required'}, status=400)
        
        try:
            user = User.objects.get(email=email)
            profile = UserProfile.objects.get(user=user)
            
            return JsonResponse({
                'exists': True,
                'profile': {
                    'display_name': profile.display_name,
                    'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
                    'phone': profile.phone,
                    'created_at': profile.created_at.isoformat()
                }
            })
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            return JsonResponse({'exists': False})
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def save_profile(request):
    try:
        # Detect JSON or multipart request
        if request.content_type.startswith("application/json"):
            data = json.loads(request.body)
            email = data.get("email")
            phone = data.get("phone")
            display_name = data.get("display_name")
            date_of_birth = data.get("date_of_birth")
            age = data.get("age")
            profile_picture = None
        else:
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            display_name = request.POST.get("display_name")
            date_of_birth = request.POST.get("date_of_birth")
            age = request.POST.get("age")
            profile_picture = request.FILES.get("profile_picture")

        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)

        user = User.objects.get(email=email)
        profile, _ = UserProfile.objects.get_or_create(user=user)

        if phone:
            profile.phone = phone
        if display_name:
            profile.display_name = display_name
        if date_of_birth:
            profile.date_of_birth = date_of_birth
        if age:
            if int(age) < 13:
                return JsonResponse({"error": "User must be at least 13 years old"}, status=400)
            profile.age = int(age)
        if profile_picture:
            profile.profile_picture = profile_picture

        profile.save()

        return JsonResponse({
            "message": "Profile saved successfully",
            "profile": {
                "display_name": profile.display_name,
                "profile_picture": profile.profile_picture.url if profile.profile_picture else None,
                "phone": profile.phone,
                "date_of_birth": profile.date_of_birth,
                "age": profile.age
            }
        })

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

