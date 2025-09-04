from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum
from django.shortcuts import render, redirect
from .models import BankStatementUpload, Transaction
from .forms import UploadForm
import pandas as pd
from .ml_utils import categorize_expenses  # AI categorizer
from .utils import normalize_statement

def upload_bank_statement(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.user = request.user
            upload.save()

            # Read as Excel or CSV depending on filename
            f = upload.file
            name = f.name.lower()
            if name.endswith(".csv"):
                raw_df = pd.read_csv(f)
            else:
                # .xlsx / .xls → needs openpyxl/xlrd as appropriate
                raw_df = pd.read_excel(f, engine='openpyxl')  # you installed openpyxl

            df = normalize_statement(raw_df)

            # Run your categorizer on the normalized DF
            # Expecting a list/series of predicted category strings
            preds = categorize_expenses(df["narration"])

            # Build Transaction objects
            objs = []
            for i, row in df.iterrows():
                objs.append(Transaction(
                    user=request.user,
                    date=row["date"],                  # <-- proper date object
                    narration=row["narration"],
                    withdrawal=float(row["withdrawal"] or 0),
                    deposit=float(row["deposit"] or 0),
                    balance=(None if pd.isna(row["balance"]) else float(row["balance"])),
                    predicted_category=(preds[i] if isinstance(preds, (list, pd.Series)) else ""),
                ))
            Transaction.objects.bulk_create(objs)

            return redirect('dashboard')
    else:
        form = UploadForm()
    return render(request, 'upload.html', {'form': form})

@login_required
def dashboard_view(request):
    transactions = Transaction.objects.filter(user=request.user)

    # Group by predicted_category
    category_summary = transactions.values('predicted_category').annotate(
        total_spent=Sum('withdrawal')
    ).order_by('-total_spent')

    # Monthly filter (optional)
    months = transactions.dates('date', 'month', order='DESC')

    context = {
        'category_summary': category_summary,
        'months': months,
        'transactions': transactions[:10],  # latest 10
    }
    return render(request, 'dashboard.html', context)

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login after signup
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})