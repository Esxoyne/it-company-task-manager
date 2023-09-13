def theme(request):
    is_dark_mode = request.session.get("is_dark_mode", False)
    return {"is_dark_mode": is_dark_mode}
