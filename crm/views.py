"""
CRM Platform API views.

Provides endpoints for user authentication, sales pipeline management,
customer/affiliate CRUD, notes, notifications, email sending,
and Excel report generation.
"""
import json
import hashlib
from io import BytesIO
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from rest_framework.decorators import api_view
from .models import (
    Company, User, UserRole, Pipeline, Stage, Customer,
    Affiliate, CustomerNote, AffiliateNote, Notification, EmailTemplate,
)


@api_view(['POST'])
def log_in(request):
    """Authenticate a CRM user by email and password hash."""
    data = request.data
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return JsonResponse({"error": "Email and password required"}, status=400)

    try:
        user = User.objects.get(email=email, password=password)
        return JsonResponse({
            "success": True,
            "user_id": user.id,
            "company_id": user.company.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.role_name,
        })
    except User.DoesNotExist:
        return JsonResponse({"error": "Invalid credentials"}, status=401)


@api_view(['GET'])
def dashboard(request):
    """
    Load the sales dashboard for a company.
    Returns pipelines with stages and customer counts.
    """
    company_id = request.GET.get("company_id")
    if not company_id:
        return JsonResponse({"error": "Missing company_id"}, status=400)

    pipelines = Pipeline.objects.all()
    pipeline_data = []
    for pipeline in pipelines:
        stages = Stage.objects.filter(pipeline=pipeline)
        stage_data = []
        for stage in stages:
            customers = Customer.objects.filter(
                company_id=company_id, pipeline=pipeline,
                stage=stage, deleted=False
            )
            customer_list = [{
                "id": c.id, "name": c.name, "email": c.email,
                "phone": c.phone, "price": c.price, "state": c.state,
            } for c in customers]
            stage_data.append({
                "stage_id": stage.stage_id,
                "stage_name": stage.stage_name,
                "customers": customer_list,
                "count": len(customer_list),
            })
        pipeline_data.append({
            "pipeline_id": pipeline.pipeline_id,
            "pipeline_name": pipeline.pipeline_name,
            "stages": stage_data,
        })

    return JsonResponse({"pipelines": pipeline_data})


@api_view(['POST'])
def change_customer_stage(request):
    """Move a customer to a different pipeline stage."""
    data = request.data
    customer_id = data.get("customer_id")
    new_stage_id = data.get("stage_id")
    try:
        customer = Customer.objects.get(id=customer_id)
        stage = Stage.objects.get(stage_id=new_stage_id)
        customer.stage = stage
        customer.save()
        return JsonResponse({"success": True})
    except (Customer.DoesNotExist, Stage.DoesNotExist):
        return JsonResponse({"error": "Customer or stage not found"}, status=404)


@api_view(['POST'])
def add_customer(request):
    """Add a new customer to the CRM."""
    data = request.data
    try:
        customer = Customer.objects.create(
            company_id=data["company_id"],
            pipeline_id=data["pipeline_id"],
            stage_id=data["stage_id"],
            name=data["name"],
            email=data["email"],
            phone=data.get("phone", ""),
            state=data.get("state", ""),
            street=data.get("street", ""),
            zip_code=data.get("zip_code", ""),
            price=data.get("price"),
            assigned_to_id=data.get("assigned_to"),
        )
        return JsonResponse({"success": True, "customer_id": customer.id}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@api_view(['POST'])
def add_customer_note(request):
    """Add a note to a customer record."""
    data = request.data
    try:
        note = CustomerNote.objects.create(
            customer_id=data["customer_id"],
            note_title=data["note_title"],
            note_text=data["note_text"],
            datetime=data.get("datetime"),
        )
        return JsonResponse({"success": True, "note_id": note.id}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@api_view(['DELETE'])
def delete_customer_note(request):
    """Delete a customer note."""
    note_id = request.data.get("note_id")
    try:
        CustomerNote.objects.get(id=note_id).delete()
        return JsonResponse({"success": True})
    except CustomerNote.DoesNotExist:
        return JsonResponse({"error": "Note not found"}, status=404)


@api_view(['GET'])
def load_customer_data(request, customer_id):
    """Load full customer profile with notes and affiliates."""
    try:
        c = Customer.objects.get(id=customer_id)
        notes = CustomerNote.objects.filter(customer=c).order_by('-datetime')
        affiliates = Affiliate.objects.filter(customer=c)
        return JsonResponse({
            "customer": {
                "id": c.id, "name": c.name, "email": c.email,
                "phone": c.phone, "state": c.state, "street": c.street,
                "zip_code": c.zip_code, "price": c.price,
                "stage_id": c.stage.stage_id,
                "pipeline_id": c.pipeline.pipeline_id,
            },
            "notes": [{"id": n.id, "title": n.note_title, "text": n.note_text,
                       "datetime": n.datetime.isoformat() if n.datetime else None}
                      for n in notes],
            "affiliates": [{"id": a.id, "name": a.name, "email": a.email,
                           "phone": a.phone_number, "state": a.state}
                          for a in affiliates],
        })
    except Customer.DoesNotExist:
        return JsonResponse({"error": "Customer not found"}, status=404)


@api_view(['PUT'])
def edit_customer(request):
    """Update customer information."""
    data = request.data
    try:
        c = Customer.objects.get(id=data["customer_id"])
        for field in ["name", "email", "phone", "state", "street", "zip_code", "price"]:
            if field in data:
                setattr(c, field, data[field])
        c.save()
        return JsonResponse({"success": True})
    except Customer.DoesNotExist:
        return JsonResponse({"error": "Customer not found"}, status=404)


@api_view(['POST'])
def send_email(request):
    """Send an email to a customer."""
    data = request.data
    try:
        send_mail(
            subject=data["subject"],
            message=data["message"],
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[data["to_email"]],
            fail_silently=False,
        )
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['GET'])
def get_users(request, company_id):
    """List all users in a company."""
    users = User.objects.filter(company_id=company_id)
    return JsonResponse({
        "users": [{"id": u.id, "first_name": u.first_name, "last_name": u.last_name,
                   "email": u.email, "role": u.role.role_name}
                  for u in users]
    })


@api_view(['POST'])
def add_user(request):
    """Add a new CRM user to a company."""
    data = request.data
    try:
        user = User.objects.create(
            company_id=data["company_id"],
            role_id=data["role_id"],
            email=data["email"],
            password=data["password"],
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            phone=data.get("phone", ""),
        )
        return JsonResponse({"success": True, "user_id": user.id}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@api_view(['GET'])
def contacts(request, company_id):
    """List all customers for a company (contacts view)."""
    customers = Customer.objects.filter(company_id=company_id, deleted=False)
    return JsonResponse({
        "contacts": [{"id": c.id, "name": c.name, "email": c.email,
                      "phone": c.phone, "stage": c.stage.stage_name}
                     for c in customers]
    })


@api_view(['POST'])
def add_affiliate(request):
    """Add an affiliate to a customer."""
    data = request.data
    try:
        affiliate = Affiliate.objects.create(
            customer_id=data["customer_id"],
            name=data["name"],
            email=data["email"],
            phone_number=data["phone_number"],
            state=data.get("state", ""),
            street=data.get("street", ""),
            zip_code=data.get("zip_code", ""),
        )
        return JsonResponse({"success": True, "affiliate_id": affiliate.id}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@api_view(['GET'])
def notifications(request):
    """Get all notifications for a company."""
    company_id = request.GET.get("company_id")
    notifs = Notification.objects.filter(company_id=company_id).order_by('-generated_datetime')
    return JsonResponse({
        "notifications": [{"id": n.id, "title": n.notification_title,
                          "text": n.notification_text, "read": n.read,
                          "datetime": n.generated_datetime.isoformat()}
                         for n in notifs]
    })


@api_view(['POST'])
def mark_notifications_read(request):
    """Mark all notifications as read for a company."""
    company_id = request.data.get("company_id")
    Notification.objects.filter(company_id=company_id).update(read=True)
    return JsonResponse({"success": True})


@api_view(['GET'])
def excel_report(request):
    """Generate an Excel report of all customers for a company."""
    import xlsxwriter
    company_id = request.GET.get("company_id")
    customers = Customer.objects.filter(company_id=company_id, deleted=False)

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("Customers")

    headers = ["Name", "Email", "Phone", "Stage", "State", "Price"]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    for row, c in enumerate(customers, start=1):
        worksheet.write(row, 0, c.name)
        worksheet.write(row, 1, c.email)
        worksheet.write(row, 2, c.phone or "")
        worksheet.write(row, 3, c.stage.stage_name)
        worksheet.write(row, 4, c.state or "")
        worksheet.write(row, 5, c.price or 0)

    workbook.close()
    output.seek(0)

    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="customers_report.xlsx"'
    return response
