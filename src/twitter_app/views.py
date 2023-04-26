from django.shortcuts import render

def custom_instructions(request):
    return render(request, 'admin/custom_instructions.html')